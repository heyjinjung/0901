import os,sys
try:
    import psycopg2
except Exception as e:
    print('psycopg2 import error:', e)
    sys.exit(1)

host = os.environ.get('POSTGRES_SERVER','postgres')
user = os.environ.get('POSTGRES_USER','cc_user')
db = os.environ.get('POSTGRES_DB','cc_webapp')
password = os.environ.get('POSTGRES_PASSWORD','cc_password')
print('connecting to', host, db, user)
try:
    conn = psycopg2.connect(host=host, dbname=db, user=user, password=password)
except Exception as e:
    print('connection error:', e)
    sys.exit(1)
cur = conn.cursor()
print('== alembic_version ==')
try:
    cur.execute("SELECT version_num FROM alembic_version;")
    rows = cur.fetchall()
    print(rows)
except Exception as e:
    print('alembic_version query error:',e)

print('\n== public tables ==')
try:
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
    for r in cur.fetchall():
        print(r[0])
except Exception as e:
    print('public tables query error:',e)

conn.close()
