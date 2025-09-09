#!/usr/bin/env python3
"""Simple SQLite backup script.

Usage: python scripts/db_backup.py [source_db_path] [dest_folder]
Defaults: source=auth.db, dest=./backups

For Postgres production, replace with pg_dump strategy (documented separately).
"""
from __future__ import annotations
import os, sys, datetime, shutil

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'auth.db'
    dest_dir = sys.argv[2] if len(sys.argv) > 2 else 'backups'
    if not os.path.exists(src):
        print(f"Source DB not found: {src}")
        return 1
    os.makedirs(dest_dir, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dest = os.path.join(dest_dir, f"{os.path.basename(src)}.{ts}.bak")
    shutil.copy2(src, dest)
    print(f"Backup created: {dest}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
