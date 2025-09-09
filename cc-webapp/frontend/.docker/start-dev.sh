#!/bin/sh
set -euo pipefail

cd /app

echo "[start-dev] booting..."

# Ensure node_modules exists in the mounted volume
if [ ! -x node_modules/.bin/next ]; then
  echo "[start-dev] node_modules missing or incomplete. Hydrating..."
  # Prefer warm copy from image cache to speed up first run
  if [ -d /opt/node_modules_cache ] && [ -z "$(ls -A node_modules 2>/dev/null || true)" ]; then
    echo "[start-dev] copying cached node_modules from image..."
    cp -a /opt/node_modules_cache/. node_modules/
  fi

  # If still missing next binary, fall back to install
  if [ ! -x node_modules/.bin/next ]; then
    if [ -f package-lock.json ]; then
      echo "[start-dev] running npm ci (legacy-peer-deps) ..."
      npm ci --legacy-peer-deps --no-audit --no-fund
    else
      echo "[start-dev] running npm install (legacy-peer-deps) ..."
      npm install --legacy-peer-deps --no-audit --no-fund
    fi
  fi
fi

# Safety: ensure react and react-dom are present (seen missing in logs)
if [ ! -d node_modules/react ] || [ ! -d node_modules/react-dom ]; then
  echo "[start-dev] ensuring react/react-dom present..."
  npm install react@19.1.0 react-dom@19.1.0 --no-audit --no-fund
fi

# Fix: stale or partial .next cache causing routes-manifest.json ENOENT in dev
if [ -d .next ] && [ ! -f .next/routes-manifest.json ]; then
  echo "[start-dev] detected stale .next without routes-manifest.json → cleaning .next ..."
  rm -rf .next || true
fi

# Safety: if .next exists but critical manifests are missing, clean it up
if [ -d .next ] && [ ! -f .next/BUILD_ID ]; then
  echo "[start-dev] missing .next/BUILD_ID → cleaning .next ..."
  rm -rf .next || true
fi

echo "[start-dev] starting Next dev server..."
exec npm run dev -- -H 0.0.0.0
