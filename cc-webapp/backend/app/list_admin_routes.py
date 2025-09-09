from app.main import app

for r in app.routes:
    path = getattr(r, 'path', '')
    if '/admin/content' in path:
        print(path, sorted(getattr(r, 'methods', [])))
