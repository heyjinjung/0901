from sqlalchemy import create_engine, text

engine = create_engine('postgresql://cc_user:cc_password@postgres:5432/cc_webapp')
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name LIKE '%balance%'
    """))
    columns = [row[0] for row in result]
    print("Balance columns in users table:")
    for col in columns:
        print(f"  - {col}")
