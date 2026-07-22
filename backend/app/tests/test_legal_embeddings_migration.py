from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
import unittest

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa


MIGRATION = "20260721_add_legal_embeddings"


def _load_migration_module() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "alembic" / "versions" / f"{MIGRATION}.py"
    spec = importlib.util.spec_from_file_location(MIGRATION, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("No se pudo cargar la migracion de embeddings juridicos.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LegalEmbeddingsMigrationTests(unittest.TestCase):
    def test_upgrade_y_downgrade_crean_y_eliminan_tabla(self):
        module = _load_migration_module()
        engine = sa.create_engine("sqlite:///:memory:")
        connection = engine.connect()
        original_op = module.op
        try:
            module.op = Operations(MigrationContext.configure(connection))
            module.upgrade()
            inspector = sa.inspect(connection)
            self.assertIn("legal_embeddings", inspector.get_table_names())

            module.downgrade()
            inspector = sa.inspect(connection)
            self.assertNotIn("legal_embeddings", inspector.get_table_names())
        finally:
            module.op = original_op
            connection.close()
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
