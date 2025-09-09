#!/usr/bin/env python
import hashlib, json, os, sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(BASE_DIR, 'cc-webapp', 'frontend')
TARGET_EXT = {'.tsx','.ts','.jsx','.js','.css','.scss','.json'}
EXCLUDE_DIR_NAMES = {'node_modules','.next','dist','build'}

def iter_files():
    for root, dirs, files in os.walk(FRONTEND_DIR):
        # prune excluded dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in TARGET_EXT:
                full = os.path.join(root, f)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    continue
                if size == 0:
                    # skip empty files
                    continue
                yield full, size

def file_hash(path):
    h = hashlib.sha256()
    with open(path,'rb') as fp:
        for chunk in iter(lambda: fp.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

groups = {}
for path,size in iter_files():
    try:
        h = file_hash(path)
    except Exception as e:
        print(f"WARN: hash failed {path}: {e}", file=sys.stderr)
        continue
    groups.setdefault(h, []).append({'path': path, 'size': size})

dups = [ {'hash':h,'count':len(files),'files':files} for h,files in groups.items() if len(files) > 1 ]

# Sort for deterministic output
dups.sort(key=lambda x: (-x['count'], x['hash']))

report = {
    'base': FRONTEND_DIR,
    'duplicate_group_count': len(dups),
    'duplicate_files_total': sum(g['count'] for g in dups),
    'groups': dups,
}

out_path = os.path.join(BASE_DIR,'frontend_duplicates_report.json')
with open(out_path,'w',encoding='utf-8') as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print(json.dumps(report, ensure_ascii=False, indent=2))
print(f"\nSaved JSON report to {out_path}")
