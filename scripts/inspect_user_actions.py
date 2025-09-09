import sqlite3, os, sys, json

DB_PATH = os.path.join('cc-webapp', 'backend', 'test_app.db')

def main():
    print('[inspect_user_actions] path=', DB_PATH)
    if not os.path.exists(DB_PATH):
        print('DB 파일이 존재하지 않습니다.')
        return 1
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_actions'")
    row = cur.fetchone()
    print('\n-- DDL --')
    print(row[0] if row else 'NOT FOUND')
    cur.execute("PRAGMA table_info(user_actions)")
    cols = cur.fetchall()
    print('\n-- COLUMNS --')
    for c in cols:
        print(c)
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='user_actions'")
    print('\n-- INDEXES --')
    for name, sql in cur.fetchall():
        print(name, sql)
    summary = {
        'has_created_at': any(c[1] == 'created_at' for c in cols),
        'has_timestamp': any(c[1] == 'timestamp' for c in cols),
        'columns': [c[1] for c in cols],
    }
    print('\n-- SUMMARY --')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    con.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
