Short-term dev instructions — legacy peer deps policy

This file documents the short-term policy to allow the frontend to build under React 19 while we plan long-term dependency upgrades.

Policy
- For now, use `--legacy-peer-deps` when installing dependencies in `cc-webapp/frontend`.
- This is a temporary measure (recommended duration: a few weeks to one month) while we prepare upgrades for incompatible packages such as `next-themes`.

Local setup (Windows PowerShell)
1. Install dependencies (clean):

```powershell
cd c:\Users\bdbd\0003\0801\cc-webapp\frontend
npm ci --legacy-peer-deps
```

2. Build (production-type check + compile):

```powershell
npm run build
```

3. Start the production server (optional):

```powershell
npm run start
```

4. Smoke checks
- Quick manual ping (PowerShell):

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/health -UseBasicParsing
Invoke-WebRequest -Uri http://127.0.0.1:3000/api/smoke-refresh -UseBasicParsing
```

- Or run the provided smoke script (requires Node 18+ or optional node-fetch installed):

```powershell
node ./scripts/smoke.js
```

CI notes
- GitHub Actions workflow `cc-webapp/.github/workflows/frontend-build.yml` is configured to run `npm ci --legacy-peer-deps` and `npm run build`.
- To run smoke tests in CI, set `BACKEND_URL` and `FRONTEND_URL` as environment variables/secrets in the workflow.

Long-term plan
- During this window we will prepare a dependency upgrade plan (identify incompatible packages, test upgrades one-by-one, and replace with alternatives if needed).
- When ready, remove `--legacy-peer-deps` usage and update CI accordingly.

Contact
- If you're blocked by an install or a failing smoke check, capture the console output and attach it to an issue with the tag `infra:legacy-peer-deps`.
