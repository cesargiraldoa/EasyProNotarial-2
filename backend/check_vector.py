import sqlalchemy as sa
import os
url = os.environ.get('DATABASE_URL', '')
engine = sa.create_engine(url)
with engine.connect() as conn:
    result = conn.execute(sa.text("select exists (select 1 from pg_extension where extname = 'vector')")).scalar()
    print('pgvector disponible:', result)
