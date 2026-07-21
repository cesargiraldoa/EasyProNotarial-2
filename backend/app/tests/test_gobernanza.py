from __future__ import annotations

from datetime import date
import unittest

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 - load all model metadata for create_all
from app.models.base import Base
from app.models.legal_norma import LegalNorma, LegalNormaRelacion
from app.models.legal_regla import LegalRegla
from app.services.legal_corpus import normas_vigentes, reglas_vigentes
from app.services.legal_gobernanza import impacto_de_norma, registrar_cambio


def _norma(slug: str, *, desde: date | None = None, hasta: date | None = None, texto: str = "Texto de prueba") -> LegalNorma:
    return LegalNorma(
        tipo="Ley",
        numero="999",
        anio=2026,
        articulo="art. 1",
        materia="compraventa",
        autoridad="Congreso",
        estado="vigente",
        vigencia_formal="vigente",
        aplicabilidad_operativa="vigente",
        vigencia_desde=desde,
        vigencia_hasta=hasta,
        url_oficial=None,
        confianza="alta",
        fecha_verificacion=date(2026, 7, 21),
        texto=texto,
        notas=None,
        slug=slug,
    )


class LegalGobernanzaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = sa.create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = self.Session()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_norma_con_vigencia_hasta_pasada_no_aplica_despues(self):
        norma = _norma("ley-999-2026-art-1", desde=date(2026, 1, 1), hasta=date(2026, 1, 31))
        self.session.add(norma)
        self.session.commit()

        before = {item.slug for item in normas_vigentes(self.session, "compraventa", date(2026, 1, 31))}
        after = {item.slug for item in normas_vigentes(self.session, "compraventa", date(2026, 2, 1))}

        self.assertIn("ley-999-2026-art-1", before)
        self.assertNotIn("ley-999-2026-art-1", after)

    def test_regla_nueva_no_aplica_antes_de_su_vigencia(self):
        regla = LegalRegla(
            acto_code="compraventa",
            codigo="regla-futura",
            condicion_json={"campo": "valor"},
            efecto="revisar",
            severidad="WARN",
            mensaje="Regla futura",
            vigencia_desde=date(2026, 7, 1),
            vigencia_hasta=None,
        )
        self.session.add(regla)
        self.session.commit()

        before = {item.codigo for item in reglas_vigentes(self.session, "compraventa", date(2026, 6, 30))}
        after = {item.codigo for item in reglas_vigentes(self.session, "compraventa", date(2026, 7, 1))}

        self.assertNotIn("regla-futura", before)
        self.assertIn("regla-futura", after)

    def test_registrar_cambio_versiona_norma_y_reglas_sin_romper_historia(self):
        anterior = _norma("ley-999-2026-art-1-original", desde=date(2026, 1, 1))
        self.session.add(anterior)
        self.session.flush()
        self.session.add(
            LegalRegla(
                acto_code="compraventa",
                codigo="regla-version-original",
                condicion_json={"campo": "anterior"},
                efecto="bloquear",
                severidad="BLOCK",
                mensaje="Regla anterior",
                norma_id=anterior.id,
                vigencia_desde=date(2026, 1, 1),
                vigencia_hasta=None,
            )
        )
        self.session.commit()

        cambio = registrar_cambio(
            self.session,
            anterior.id,
            tipo="modifica",
            fecha_efecto=date(2026, 7, 1),
            nueva_norma={"slug": "ley-999-2026-art-1-version-2", "texto": "Texto version dos"},
            reglas_nuevas=[
                {
                    "codigo_origen": "regla-version-original",
                    "codigo": "regla-version-nueva",
                    "condicion_json": {"campo": "nuevo"},
                    "efecto": "revisar",
                    "severidad": "WARN",
                    "mensaje": "Regla nueva",
                }
            ],
            reindexar=False,
        )
        self.session.commit()

        normas_viejas = {item.slug for item in normas_vigentes(self.session, "compraventa", date(2026, 6, 30))}
        normas_nuevas = {item.slug for item in normas_vigentes(self.session, "compraventa", date(2026, 7, 1))}
        reglas_viejas = {item.codigo for item in reglas_vigentes(self.session, "compraventa", date(2026, 6, 30))}
        reglas_nuevas = {item.codigo for item in reglas_vigentes(self.session, "compraventa", date(2026, 7, 1))}

        self.assertIn("ley-999-2026-art-1-original", normas_viejas)
        self.assertNotIn("ley-999-2026-art-1-version-2", normas_viejas)
        self.assertNotIn("ley-999-2026-art-1-original", normas_nuevas)
        self.assertIn("ley-999-2026-art-1-version-2", normas_nuevas)
        self.assertIn("regla-version-original", reglas_viejas)
        self.assertNotIn("regla-version-nueva", reglas_viejas)
        self.assertNotIn("regla-version-original", reglas_nuevas)
        self.assertIn("regla-version-nueva", reglas_nuevas)

        relacion = self.session.execute(select(LegalNormaRelacion).where(LegalNormaRelacion.id == cambio.relacion_id)).scalar_one()
        self.assertEqual(relacion.tipo, "modifica")
        self.assertEqual(relacion.norma_destino_id, anterior.id)

        impacto = impacto_de_norma(self.session, anterior.id)
        self.assertEqual([item["codigo"] for item in impacto["reglas"]], ["regla-version-original"])


if __name__ == "__main__":
    unittest.main()
