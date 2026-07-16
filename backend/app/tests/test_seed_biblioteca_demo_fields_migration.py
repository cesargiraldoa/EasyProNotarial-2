from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

import sqlalchemy as sa


def _load_migration_module():
    path = Path(__file__).resolve().parents[2] / "alembic" / "versions" / "20260716_seed_biblioteca_demo_fields.py"
    spec = importlib.util.spec_from_file_location("seed_biblioteca_demo_fields", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar la migracion de demo.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SeedBibliotecaDemoFieldsMigrationTests(unittest.TestCase):
    def test_upgrade_and_downgrade_seed_catalog_definitions_and_aliases(self):
        module = _load_migration_module()
        engine = sa.create_engine("sqlite:///:memory:")
        metadata = sa.MetaData()
        sa.Table(
            "notarial_field_catalog",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("code", sa.String),
            sa.Column("label", sa.String),
            sa.Column("field_type", sa.String),
            sa.Column("category", sa.String),
            sa.Column("description", sa.Text),
            sa.Column("options_json", sa.Text),
            sa.Column("scope", sa.String),
            sa.Column("notary_id", sa.Integer),
            sa.Column("is_active", sa.Boolean),
            sa.Column("created_by_user_id", sa.Integer),
            sa.Column("metadata_json", sa.Text),
        )
        sa.Table(
            "field_definitions",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("field_code", sa.String),
            sa.Column("display_name", sa.String),
            sa.Column("data_type", sa.String),
            sa.Column("field_group", sa.String),
            sa.Column("legal_role", sa.String),
            sa.Column("act_type", sa.String),
            sa.Column("description", sa.Text),
            sa.Column("status", sa.String),
            sa.Column("confidence", sa.Float),
            sa.Column("source", sa.String),
            sa.Column("metadata_json", sa.Text),
        )
        sa.Table(
            "field_aliases",
            metadata,
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("raw_field_code", sa.String),
            sa.Column("canonical_field_code", sa.String),
            sa.Column("field_definition_id", sa.Integer),
            sa.Column("frequency", sa.Integer),
            sa.Column("status", sa.String),
            sa.Column("source", sa.String),
            sa.Column("metadata_json", sa.Text),
        )
        metadata.create_all(engine)

        with engine.begin() as connection:
            original_op = module.op
            module.op = SimpleNamespace(get_bind=lambda: connection)
            try:
                module.upgrade()
                module.upgrade()

                catalog_count = connection.execute(sa.text("SELECT count(*) FROM notarial_field_catalog")).scalar_one()
                definition_count = connection.execute(sa.text("SELECT count(*) FROM field_definitions")).scalar_one()
                alias_target = connection.execute(
                    sa.text("SELECT canonical_field_code FROM field_aliases WHERE raw_field_code = 'CEDULA_CATRASTAL'")
                ).scalar_one()

                self.assertEqual(catalog_count, len(module.FIELDS))
                self.assertEqual(definition_count, len(module.FIELDS))
                self.assertEqual(alias_target, "CEDULA_CATASTRAL")

                module.downgrade()

                self.assertEqual(connection.execute(sa.text("SELECT count(*) FROM notarial_field_catalog")).scalar_one(), 0)
                self.assertEqual(connection.execute(sa.text("SELECT count(*) FROM field_definitions")).scalar_one(), 0)
                self.assertEqual(connection.execute(sa.text("SELECT count(*) FROM field_aliases")).scalar_one(), 0)
            finally:
                module.op = original_op


if __name__ == "__main__":
    unittest.main()
