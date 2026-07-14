from app.db.session import engine
import sqlalchemy as sa
with engine.connect() as conn:
    r1 = conn.execute(sa.text("SELECT COUNT(*) FROM notarial_field_catalog WHERE is_active = true AND scope = 'global' AND notary_id IS NULL"))
    print('global+null:', r1.scalar())
    r2 = conn.execute(sa.text("SELECT COUNT(*) FROM notarial_field_catalog WHERE is_active = true"))
    print('total activos:', r2.scalar())
