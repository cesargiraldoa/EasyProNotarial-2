from app.db.session import engine
import sqlalchemy as sa
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='notarial_field_catalog'"))
    print('Tabla existe:', result.scalar())
