from __future__ import annotations

from datetime import date
import importlib.util
import json
from pathlib import Path
from types import ModuleType
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models.legal_clausula import LegalClausula
from app.models.legal_jurisprudencia import LegalJurisprudencia
from app.models.legal_norma import LegalNorma, LegalNormaRelacion
from app.models.legal_regla import LegalRegla
from app.models.legal_tarifa import LegalTarifa
from app.seeds.seed_corpus import seed_corpus
from app.services.legal_corpus import normas_vigentes

MIGRATION = "20260721_add_legal_corpus_tables"
LEGAL_TABLES = {
    "legal_normas",
    "legal_norma_relaciones",
    "legal_clausulas",
    "legal_reglas",
    "legal_tarifas",
    "legal_jurisprudencias",
}
REPO_DIR = Path(__file__).resolve().parents[3]
CORPUS_DIR = REPO_DIR / "corpus-juridico"


def _load_migration_module() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "alembic" / "versions" / f"{MIGRATION}.py"
    spec = importlib.util.spec_from_file_location(MIGRATION, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar la migración del corpus jurídico.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_op(module: ModuleType, connection) -> object:
    original_op = module.op
    context = MigrationContext.configure(connection)
    module.op = Operations(context)
    return original_op


def _json_count(filename: str) -> int:
    return len(json.loads((CORPUS_DIR / filename).read_text(encoding="utf-8")))


class LegalCorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = _load_migration_module()
        self.engine = sa.create_engine("sqlite:///:memory:")
        self.connection = self.engine.connect()
        self.original_op = _install_op(self.module, self.connection)
        self.module.upgrade()
        SessionLocal = sessionmaker(bind=self.connection)
        self.session = SessionLocal()

    def tearDown(self) -> None:
        self.session.close()
        self.module.op = self.original_op
        self.connection.close()
        self.engine.dispose()

    def _seed(self) -> None:
        seed_corpus(self.session)

    def _norma_by_slug(self, slug: str) -> LegalNorma:
        norma = self.session.execute(select(LegalNorma).where(LegalNorma.slug == slug)).scalar_one()
        return norma

    def _norma_slug(self, norma_id: int | None) -> str | None:
        if norma_id is None:
            return None
        return self.session.get(LegalNorma, norma_id).slug

    def test_migration_upgrade_and_downgrade_create_only_legal_tables(self):
        engine = sa.create_engine("sqlite:///:memory:")
        connection = engine.connect()
        module = _load_migration_module()
        original_op = _install_op(module, connection)
        try:
            module.upgrade()
            inspector = sa.inspect(connection)
            self.assertTrue(LEGAL_TABLES.issubset(set(inspector.get_table_names())))

            module.downgrade()
            inspector = sa.inspect(connection)
            self.assertTrue(LEGAL_TABLES.isdisjoint(set(inspector.get_table_names())))
        finally:
            module.op = original_op
            connection.close()
            engine.dispose()

    def test_seed_is_idempotent(self):
        first = seed_corpus(self.session)
        second = seed_corpus(self.session)

        self.assertGreater(first["normas"]["created"], 0)
        for counts in second.values():
            self.assertEqual(counts["created"], 0)

        self.assertEqual(self.session.query(LegalNorma).count(), _json_count("normas.json"))
        self.assertEqual(self.session.query(LegalNormaRelacion).count(), _json_count("norma_relaciones.json"))
        self.assertEqual(self.session.query(LegalClausula).count(), _json_count("clausulas.json"))
        self.assertEqual(self.session.query(LegalRegla).count(), _json_count("reglas.json"))
        self.assertEqual(self.session.query(LegalTarifa).count(), _json_count("tarifas.json"))
        self.assertEqual(self.session.query(LegalJurisprudencia).count(), _json_count("jurisprudencia.json"))

    def test_normas_vigentes_compraventa_excludes_inexequible_and_compilada(self):
        self._seed()
        normas = normas_vigentes(self.session, "compraventa", date(2026, 8, 14))
        slugs = {norma.slug for norma in normas}

        self.assertIn("ley-258-1996-art-3", slugs)
        self.assertIn("ley-258-1996-art-6", slugs)
        self.assertIn("ley-1579-2012-art-8", slugs)
        self.assertIn("ley-1579-2012-art-16", slugs)
        self.assertIn("ley-223-1995-art-231", slugs)
        self.assertIn("estatuto-tributario-art-90", slugs)
        self.assertIn("estatuto-tributario-art-398", slugs)
        self.assertIn("estatuto-tributario-art-401", slugs)
        self.assertIn("estatuto-tributario-art-311-1", slugs)
        self.assertNotIn("decreto-ley-2106-2019-arts-59-63", slugs)
        self.assertNotIn("decreto-2148-1983-art-12", slugs)

    def test_c1_registro_dos_meses_e_intereses_usa_ley_223_no_ley_1579(self):
        self._seed()
        ley_223 = self._norma_by_slug("ley-223-1995-art-231")
        ley_1579_28 = self._norma_by_slug("ley-1579-2012-art-28")

        for codigo in (
            "compraventa_registro_dos_meses_intereses_ley_223_231",
            "hipoteca_registro_dos_meses_intereses_ley_223_231",
            "cancelacion_registro_dos_meses_intereses_ley_223_231",
        ):
            regla = self.session.execute(select(LegalRegla).where(LegalRegla.codigo == codigo)).scalar_one()
            self.assertEqual(regla.norma_id, ley_223.id)

        regla_90 = self.session.execute(
            select(LegalRegla).where(LegalRegla.codigo == "hipoteca_registro_90_dias_habiles")
        ).scalar_one()
        self.assertEqual(regla_90.norma_id, ley_1579_28.id)
        self.assertIn("90", ley_1579_28.texto)

        clausulas_dos_meses = self.session.execute(
            select(LegalClausula).where(LegalClausula.titulo.ilike("%dos meses%"))
        ).scalars()
        self.assertTrue(clausulas_dos_meses)
        self.assertTrue(all(clausula.norma_id == ley_223.id for clausula in clausulas_dos_meses))

    def test_c2_firma_fuera_sede_cita_decreto_1069_y_relacion_compila(self):
        self._seed()
        old = self._norma_by_slug("decreto-2148-1983-art-12")
        current = self._norma_by_slug("decreto-1069-2015-art-2-2-6-1-2-1-5")

        relacion = self.session.execute(
            select(LegalNormaRelacion)
            .where(LegalNormaRelacion.norma_origen_id == old.id)
            .where(LegalNormaRelacion.norma_destino_id == current.id)
            .where(LegalNormaRelacion.tipo == "compila")
        ).scalar_one()
        self.assertEqual(relacion.articulo_afectado, "art. 12 Decreto 2148/1983")

        clausulas = list(
            self.session.execute(select(LegalClausula).where(LegalClausula.titulo.ilike("%Firma fuera%"))).scalars()
        )
        self.assertGreaterEqual(len(clausulas), 2)
        self.assertTrue(all(clausula.norma_id == current.id for clausula in clausulas))

    def test_c3_retencion_ramifica_persona_natural_y_juridica(self):
        self._seed()
        natural = self.session.execute(
            select(LegalRegla).where(LegalRegla.codigo == "compraventa_retencion_vendedor_natural_1pct_notario")
        ).scalar_one()
        juridica = self.session.execute(
            select(LegalRegla).where(LegalRegla.codigo == "compraventa_retencion_vendedor_juridico_comprador_no_notario")
        ).scalar_one()

        self.assertEqual(self._norma_slug(natural.norma_id), "estatuto-tributario-art-398")
        self.assertEqual(natural.condicion_json["vendedor_tipo_persona"], "natural")
        self.assertIn("1%", natural.mensaje)

        self.assertEqual(self._norma_slug(juridica.norma_id), "estatuto-tributario-art-401")
        self.assertEqual(juridica.condicion_json["vendedor_tipo_persona"], "juridica")
        self.assertIn("sin_retencion_notarial", juridica.efecto)

    def test_c4_exencion_casa_habitacion_5000_uvt_con_afc(self):
        self._seed()
        regla = self.session.execute(
            select(LegalRegla).where(LegalRegla.codigo == "compraventa_exencion_casa_habitacion_5000_uvt_afc")
        ).scalar_one()
        et_311_1 = self._norma_by_slug("estatuto-tributario-art-311-1")
        ley_2277 = self._norma_by_slug("ley-2277-2022-art-31")

        self.assertEqual(regla.norma_id, et_311_1.id)
        self.assertEqual(regla.condicion_json["exencion_uvt"], 5000)
        self.assertTrue(regla.condicion_json["requiere_cuenta_afc"])
        self.assertIn("pago_credito_hipotecario", regla.condicion_json["destino_admitido"])

        relacion = self.session.execute(
            select(LegalNormaRelacion)
            .where(LegalNormaRelacion.norma_origen_id == ley_2277.id)
            .where(LegalNormaRelacion.norma_destino_id == et_311_1.id)
            .where(LegalNormaRelacion.tipo == "modifica")
        ).scalar_one()
        self.assertEqual(relacion.articulo_afectado, "art. 311-1 E.T.")

    def test_c5_decreto_0732_modifica_dur_1069_no_deroga_1227(self):
        self._seed()
        decreto_0732 = self._norma_by_slug("decreto-0732-2026")
        dur_1069 = self._norma_by_slug("decreto-1069-2015-dur-sector-justicia")

        relacion = self.session.execute(
            select(LegalNormaRelacion)
            .where(LegalNormaRelacion.norma_origen_id == decreto_0732.id)
            .where(LegalNormaRelacion.norma_destino_id == dur_1069.id)
        ).scalar_one()
        self.assertEqual(relacion.tipo, "modifica")

        relaciones_0732 = list(
            self.session.execute(
                select(LegalNormaRelacion).where(LegalNormaRelacion.norma_origen_id == decreto_0732.id)
            ).scalars()
        )
        self.assertTrue(all(not relacion.tipo.startswith("deroga") for relacion in relaciones_0732))
        destinos = {self.session.get(LegalNorma, relacion.norma_destino_id).numero for relacion in relaciones_0732}
        self.assertNotIn("1227", destinos)

        regla = self.session.execute(
            select(LegalRegla).where(LegalRegla.codigo == "transversal_identidad_sexo_cuatro_variables_decreto_0732")
        ).scalar_one()
        self.assertEqual(regla.condicion_json["persona_sexo"]["allowed"], ["F", "M", "NB", "T"])

    def test_ramas_comunes_compraventa_seed(self):
        self._seed()
        ley_1561 = self._norma_by_slug("ley-1561-2012")
        self.assertEqual(ley_1561.confianza, "baja")
        self.assertIn("falsa tradición", ley_1561.materia)

        reglas = {
            row.codigo: row
            for row in self.session.execute(
                select(LegalRegla).where(
                    LegalRegla.codigo.in_(
                        [
                            "compraventa_varios_inmuebles_identificacion_individual",
                            "compraventa_varios_inmuebles_clausula_enumera_folios",
                            "compraventa_estado_folio_especial_advertencia_1579",
                            "compraventa_falsa_tradicion_advertencia_saneamiento",
                            "compraventa_encadena_cancelacion_hipoteca_previa",
                            "compraventa_encadena_cancelacion_patrimonio_familia",
                            "compraventa_encadena_afectacion_vivienda_familiar",
                        ]
                    )
                )
            ).scalars()
        }
        self.assertEqual(len(reglas), 7)
        self.assertEqual(reglas["compraventa_varios_inmuebles_identificacion_individual"].severidad, "BLOCK")
        self.assertEqual(self._norma_slug(reglas["compraventa_falsa_tradicion_advertencia_saneamiento"].norma_id), "ley-1561-2012")

        clausulas = {
            row.titulo
            for row in self.session.execute(
                select(LegalClausula).where(LegalClausula.orden.in_([240, 250, 260, 270, 280, 290]))
            ).scalars()
        }
        self.assertIn("Parágrafo - Varios inmuebles", clausulas)
        self.assertIn("Parágrafo - Falsa tradición", clausulas)
        self.assertIn("Acto previo - Cancelación de hipoteca previa", clausulas)
        self.assertIn("Acto posterior - Afectación a vivienda familiar", clausulas)

    def test_ramas_especiales_compraventa_seed(self):
        self._seed()
        normas_baja = {
            slug: self._norma_by_slug(slug).confianza
            for slug in [
                "ley-9-1991-regimen-cambiario",
                "decreto-1068-2015-regimen-cambiario",
                "resolucion-externa-jdbr-1-2018-regimen-cambiario",
                "circular-dcin-banrep-regimen-cambiario",
                "ley-160-1994-art-39",
                "decreto-1429-2020-apoyos",
            ]
        }
        self.assertEqual(set(normas_baja.values()), {"baja"})

        reglas = {
            row.codigo: row
            for row in self.session.execute(
                select(LegalRegla).where(
                    LegalRegla.codigo.in_(
                        [
                            "compraventa_extranjero_no_residente_identificacion",
                            "compraventa_divisas_declaracion_cambio_banrep",
                            "compraventa_divisas_canalizacion_mercado_cambiario",
                            "compraventa_extranjero_no_residente_registro_inversion",
                            "compraventa_rural_predio_identificacion_sin_ph",
                            "compraventa_rural_supera_uaf_sin_autorizacion",
                            "compraventa_rural_baldio_restriccion_temporal",
                            "compraventa_rural_derecho_preferencia_ant",
                            "compraventa_venta_bien_menor_autorizacion",
                            "compraventa_apoyos_acreditados_ley_1996",
                        ]
                    )
                )
            ).scalars()
        }
        self.assertEqual(len(reglas), 10)
        self.assertEqual(reglas["compraventa_rural_supera_uaf_sin_autorizacion"].severidad, "BLOCK")
        self.assertEqual(self._norma_slug(reglas["compraventa_divisas_declaracion_cambio_banrep"].norma_id), "circular-dcin-banrep-regimen-cambiario")

        clausulas = {
            row.titulo
            for row in self.session.execute(
                select(LegalClausula).where(LegalClausula.orden.in_([300, 310, 320]))
            ).scalars()
        }
        self.assertEqual(
            clausulas,
            {
                "Parágrafo - Extranjería, no residencia y divisas",
                "Parágrafo - Predio rural, UAF y baldíos",
                "Parágrafo - Capacidad, representación y apoyos",
            },
        )

    def test_jurisprudencia_verificada_seed(self):
        self._seed()
        providencias = {
            row.providencia
            for row in self.session.execute(select(LegalJurisprudencia)).scalars()
        }
        self.assertEqual(providencias, {"C-159/2021", "C-193/2016", "SU-214/2016", "C-112/2000", "C-039/2025"})


if __name__ == "__main__":
    unittest.main()
