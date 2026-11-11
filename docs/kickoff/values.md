# Kickoff values

Approved by the owner in the Project chat on 2026-11-11 (Phase 2 of the kickoff).

| Key | Value |
|---|---|
| `NEW_REPO` | `hungle-agilityio/o-living-with-nature` |
| `DISPLAY_NAME` | Ở — Living with Nature |
| `SLUG` | `o-living` |
| `APP_DIR` | `.` |
| `OWNER` | `hungle-agilityio` |
| `NTFY_TOPIC` | `o-living-loop-k7q2` |
| `STACK` | Python 3.11 + Django 5 + SQLite (static bilingual VI/EN pages) |
| `CODE_DIRS` | `apps/`, `config/`, `templates/`, `static/` |
| Hosting | Render service `o-living-web`, branch `deploy`, `autoDeployTrigger: checksPass`, health check `/healthz/` |
| Plugin | `agent-flow@o-living` from the marketplace `o-living` in this repository |
