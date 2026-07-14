from app.db.session import engine
import sqlalchemy as sa
with engine.connect() as conn:
    result = conn.execute(sa.text("SELECT COUNT(*), scope FROM notarial_field_catalog GROUP BY scope"))
    for row in result:
        print(row)
