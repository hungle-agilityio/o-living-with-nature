# Ở — Living with Nature

A small bilingual (Vietnamese and English) website for one rental garden house in Hòa Xuân, Đà Nẵng. Phase 1 exists to start search-engine visibility early, before the house is built: five static pages and a way to contact the owner. No booking, no accounts, no CMS.

## Layout

| Folder | What lives there |
|---|---|
| `config/` | Django project: settings, root URLs, WSGI |
| `apps/pages/` | The one Django app: views and URLs of the public pages |
| `templates/` | Page templates (`base.html`, `pages/`) |
| `static/` | CSS and images |
| `tests/` | All app tests (protected: the loop never edits a test already on `main`) |
| `ops/` | The loop (tick, launchd, flow config `ops/flow.toml`) |
| `plugins/agent-flow/` | This repository's own flow plugin (hooks, skills, commands, sub-agents) |
| `specs/`, `docs/app/templates/` | Specs and issue templates |

## Commands

```
uv sync
uv run python manage.py runserver
uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest -q
uv run pytest plugins/agent-flow .claude/skills -q --no-cov -p no:cacheprovider
uv run python .claude/skills/check-in-browser/browser_check.py
```

## Workflow

Requests go through the Claude Project (analyse, grill-me, spec, issues); the loop on the Mac mini builds `agent:ready` issues and opens pull requests; the owner merges. Details: `rules/workflow.md`, `rules/git.md`, `rules/issues.md`, `project-instructions.md`.

## Where things go

- Page logic in `apps/pages/` (views stay thin; anything beyond rendering goes to a service module, see `rules/architecture.md`).
- Text a visitor reads exists in Vietnamese and English (`rules/domain.md`).
- The public base URL is `SITE_BASE_URL` in `config/settings.py`, nowhere else.
- Decisions: `knowledge/decisions/` (ADRs).
