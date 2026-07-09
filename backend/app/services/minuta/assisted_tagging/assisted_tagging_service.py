from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.assisted_tagging import AssistedTaggingField, AssistedTaggingJob
from app.models.document_template import DocumentTemplate
from app.models.template_field import TemplateField
from app.services.minuta.assisted_tagging.approved_template_parser import ApprovedTemplateParser
from app.services.minuta.assisted_tagging.docx_red_writer import DocxRedWriter
from app.services.minuta.assisted_tagging.docx_structure_extractor import DocxStructureExtractor
from app.services.minuta.assisted_tagging.llm_tagging_client import LlmTaggingClient
from app.services.minuta.assisted_tagging.tagging_response_validator import TaggingResponseValidator, normalize_code
from app.services.storage import CASE_STORAGE, download_storage_bytes, sanitize_storage_filename

DOCX_MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class AssistedTaggingService:
    def __init__(self) -> None:
        self.extractor = DocxStructureExtractor()
        self.llm = LlmTaggingClient()
        self.validator = TaggingResponseValidator()
        self.red_writer = DocxRedWriter()
        self.approved_parser = ApprovedTemplateParser()

    def create_job(
        self,
        db: Session,
        *,
        filename: str,
        content: bytes,
        document_type: str,
        notary_id: int,
        user_id: int,
    ) -> AssistedTaggingJob:
        job_uuid = str(uuid.uuid4())
        source_filename = sanitize_storage_filename(filename or "minuta.docx")
        storage_path = self._save_bytes(notary_id, job_uuid, f"original_{source_filename}", content)
        job = AssistedTaggingJob(
            job_uuid=job_uuid,
            status="uploaded",
            notary_id=notary_id,
            created_by_user_id=user_id,
            document_type=document_type.strip(),
            source_filename=source_filename,
            original_docx_storage_path=storage_path,
            warnings_json="[]",
            structure_json="{}",
            llm_response_json="{}",
            audit_json="{}",
        )
        db.add(job)
        db.flush()
        return job

    def run_job(self, db: Session, job: AssistedTaggingJob) -> AssistedTaggingJob:
        job.status = "processing"
        db.flush()
        try:
            original = download_storage_bytes(job.original_docx_storage_path)
            with tempfile.TemporaryDirectory(prefix="easypro-assisted-") as tmp_dir:
                tmp = Path(tmp_dir)
                input_path = tmp / "input.docx"
                output_path = tmp / "pretagged.docx"
                input_path.write_bytes(original)

                structure = self.extractor.extract(input_path)
                llm_response = self.llm.propose(structure, job.document_type)
                validation = self.validator.validate(llm_response, structure)
                audit = self.red_writer.write(input_path, output_path, validation.fields)
                pretagged_bytes = output_path.read_bytes()

            job.structure_json = json.dumps(structure.to_dict(), ensure_ascii=False)
            job.llm_response_json = json.dumps(llm_response, ensure_ascii=False)
            job.warnings_json = json.dumps(validation.warnings, ensure_ascii=False)
            job.audit_json = json.dumps(audit, ensure_ascii=False)
            job.pretagged_docx_storage_path = self._save_bytes(
                job.notary_id,
                job.job_uuid,
                f"preetiquetada_{job.source_filename}",
                pretagged_bytes,
            )
            job.status = "human_review"
            db.query(AssistedTaggingField).filter(AssistedTaggingField.job_id == job.id).delete(synchronize_session=False)
            for index, field in enumerate(validation.fields, start=1):
                db.add(
                    AssistedTaggingField(
                        job_id=job.id,
                        field_code=field.field_code,
                        label=field.label,
                        original_text=field.text,
                        section=field.section,
                        confidence=field.confidence,
                        occurrences=field.occurrences,
                        status="proposed",
                        source=field.source,
                        warning="; ".join(field.warnings) if field.warnings else None,
                        metadata_json=json.dumps({"block_id": field.block_id, "reason": field.reason, "order": index}, ensure_ascii=False),
                    )
                )
            db.flush()
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            db.flush()
        return job

    def approve_job(self, db: Session, job: AssistedTaggingJob, *, user_id: int) -> AssistedTaggingJob:
        if not job.pretagged_docx_storage_path:
            raise ValueError("El job no tiene DOCX pre-etiquetado.")
        content = download_storage_bytes(job.pretagged_docx_storage_path)
        with tempfile.TemporaryDirectory(prefix="easypro-assisted-approve-") as tmp_dir:
            input_path = Path(tmp_dir) / "approved.docx"
            input_path.write_bytes(content)
            parsed = self.approved_parser.parse(input_path)
        if not parsed.fields:
            raise ValueError("El documento aprobado no contiene variables en rojo.")

        technical_path = self._save_bytes(
            job.notary_id,
            job.job_uuid,
            f"plantilla_tecnica_{job.source_filename}",
            parsed.technical_docx,
        )
        template = self._save_template(db, job, technical_path, parsed.fields)
        job.approved_docx_storage_path = job.pretagged_docx_storage_path
        job.technical_template_storage_path = technical_path
        job.template_id = template.id
        job.status = "saved_to_library"
        job.approved_at = datetime.utcnow()
        job.approved_by_user_id = user_id
        job.warnings_json = json.dumps(parsed.warnings, ensure_ascii=False)
        job.audit_json = json.dumps(parsed.to_dict(), ensure_ascii=False)

        db.query(AssistedTaggingField).filter(AssistedTaggingField.job_id == job.id).delete(synchronize_session=False)
        for index, field in enumerate(parsed.fields, start=1):
            db.add(
                AssistedTaggingField(
                    job_id=job.id,
                    field_code=field.field_code,
                    label=field.label,
                    original_text=field.text,
                    section=field.section,
                    confidence=1.0,
                    occurrences=field.occurrences,
                    status="approved",
                    source="human_red",
                    metadata_json=json.dumps({"order": index}, ensure_ascii=False),
                )
            )
        db.flush()
        return job

    def reject_job(self, db: Session, job: AssistedTaggingJob, reason: str | None) -> AssistedTaggingJob:
        job.status = "rejected"
        job.rejected_at = datetime.utcnow()
        job.error_message = (reason or "").strip() or None
        db.flush()
        return job

    def _save_template(self, db: Session, job: AssistedTaggingJob, storage_path: str, parsed_fields: list) -> DocumentTemplate:
        base_slug = normalize_code(f"{job.document_type}_{Path(job.source_filename).stem}")
        slug = base_slug
        suffix = 2
        while db.query(DocumentTemplate.id).filter(DocumentTemplate.slug == slug).first() is not None:
            slug = f"{base_slug}_{suffix}"
            suffix += 1
        template = DocumentTemplate(
            name=f"{job.document_type.strip() or 'Minuta'} - plantilla inteligente",
            slug=slug,
            case_type="escritura",
            document_type=job.document_type.strip() or "minuta",
            description="Plantilla aprobada desde etiquetado asistido con variables en rojo.",
            scope_type="notary",
            notary_id=job.notary_id,
            is_active=True,
            source_filename=f"plantilla_tecnica_{job.source_filename}",
            storage_path=storage_path,
            internal_variable_map_json=json.dumps(
                {
                    "source": "assisted_tagging",
                    "job_uuid": job.job_uuid,
                    "visual_rule": "black_fixed_red_variable",
                },
                ensure_ascii=False,
            ),
        )
        db.add(template)
        db.flush()

        for index, item in enumerate(parsed_fields, start=1):
            code = normalize_code(str(item.field_code or f"campo_{index}"))
            template.fields.append(
                TemplateField(
                    field_code=code,
                    label=str(item.label or code.replace("_", " ").title()),
                    field_type="text",
                    section=str(item.section or "general"),
                    is_required=True,
                    placeholder_key=code.upper(),
                    step_order=index,
                )
            )
        return template

    def _save_bytes(self, notary_id: int, job_uuid: str, filename: str, content: bytes) -> str:
        safe_name = sanitize_storage_filename(filename)
        directory = CASE_STORAGE / "assisted_tagging" / f"notary_{notary_id}" / job_uuid
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / safe_name
        target.write_bytes(content)
        return str(target)
