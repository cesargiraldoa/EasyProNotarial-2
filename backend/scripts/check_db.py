import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:JuanV1959%2F%2F%2A@db.egwdrdgtgmogcahhdtdy.supabase.co:5432/postgres'
from sqlalchemy import create_engine, text
engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    r = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='case_document_versions' ORDER BY ordinal_position"
    )).fetchall()
    print("COLUMNAS:", [x[0] for x in r])
    r2 = conn.execute(text(
        "SELECT storage_path FROM case_document_versions ORDER BY id DESC LIMIT 3"
    )).fetchall()
    for row in r2:
        print("storage_path:", row[0])