# Ở — Living with Nature

A small bilingual (Vietnamese and English) website for one rental garden house in Hòa Xuân, Đà Nẵng. Phase 1 exists to start search-engine visibility early, before the house is built: five static pages and a way to contact the owner. No booking, no accounts, no CMS.

## Layout

| Folder | What lives there |
|---|---|
| `src/config/` | Django project: settings, root URLs, WSGI |
| `src/pages/` | The public pages (one feature, one Django app): views, URLs, `templates/pages/` |
| `src/pages/tests/` | The feature's tests (protected: the loop never edits a test already on `main`) |
| `src/templates/`, `src/static/` | Templates (`base.html`) and CSS shared by every feature |
| `.flow/loop/` | The loop (tick, launchd, release); its config is `.flow/flow.toml` |
| `.flow/plugin/` | This repository's own flow plugin (hooks, skills, commands, sub-agents) |
| `docs/` | `intent/`, `specs/`, `plans/`, `decisions/` (ADRs), `templates/` (spec and issue templates), `architecture.md` |

## Commands

```
bash scripts/setup.sh
uv run python manage.py runserver
bash scripts/check.sh
uv run python .claude/skills/check-in-browser/browser_check.py
```

## Workflow

Requests go through the Claude Project (analyse, grill-me, spec, issues); the loop on the Mac mini builds `agent:ready` issues and opens pull requests; the owner merges. Details: `rules/workflow.md`, `rules/git.md`, `rules/issues.md`, `project-instructions.md`.

## Where things go

- Page logic in `src/pages/` (views stay thin; anything beyond rendering goes to a service module, see `rules/architecture.md`).
- Text a visitor reads exists in Vietnamese and English (`rules/domain.md`).
- The public base URL is `SITE_BASE_URL` in `src/config/settings.py`, nowhere else.
- Decisions: `docs/decisions/` (ADRs).
