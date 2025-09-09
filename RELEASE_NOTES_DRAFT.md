# Release Notes Draft

## Unreleased

### Auth / Invite Codes
- Added usage report and operational snapshot for permanent invite code 5858.
- Added Prometheus alert rules (`monitoring/invite_code_alerts.yml`) for:
  - Excessive unknown invite code attempts (critical)
  - Low legacy 5858 usage (<5% over 24h) (warning)
  - Low adoption of new codes in first hour (info)
- Documentation updates: `api docs/20250841-002.md` checklist all marked complete, `INVITE_5858_USAGE_REPORT_20250817.md` archived.
- Git tag created: `invite-5858-ops-20250817`.

## Previous
...existing code...