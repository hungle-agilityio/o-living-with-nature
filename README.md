# Ở — Living with Nature

Bilingual (Vietnamese and English) website of a rental garden house in Hòa Xuân, Đà Nẵng. Django 5, Python 3.11, [uv](https://docs.astral.sh/uv/).

## Run it

```
uv sync
cp .env.example .env        # optional; the defaults work for development
uv run python manage.py runserver
```

Open http://localhost:8000/ (health check: `/healthz/`).

## Check it

```
bash scripts/check.sh       # lint, format, types, tests (same as CI and the loop)
uv run python .claude/skills/check-in-browser/browser_check.py   # pages in a headless browser
```

## Deploy

Render service `o-living-web` from `render.yaml`: it deploys the `deploy` branch after the `Checks` workflow passes. Set `SITE_BASE_URL` in the Render dashboard. A release moves `main` to `deploy` (`.flow/loop/release.py`).

## More

- How the project is built and worked on: [`CLAUDE.md`](CLAUDE.md), [`.claude/`](.claude/)
- Architecture: [`docs/architecture.md`](docs/architecture.md)
- Decisions: [`docs/decisions/`](docs/decisions/README.md)
- Code: `src/<feature>/` with its tests in `src/<feature>/tests/`; the agent flow: `.flow/`
