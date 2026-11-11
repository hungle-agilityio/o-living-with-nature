# Architecture

Phase 1 is a small bilingual (VI/EN) site of five pages (Home, House, Hòa Xuân area, FAQ, Contact). Rules for code: `.claude/rules/architecture.md` and `.claude/rules/django.md`.

## Modules

```
config/            settings (environment), root URLs, WSGI
  └─ urls.py ──► apps/pages/urls.py
apps/pages/        the public pages
  ├─ urls.py       "/" home, "/healthz/" health check (more pages come with the first epic)
  ├─ views.py      thin: render a template; logic goes to services.py when it appears
  └─ services.py   (created with the first rule)
templates/         base.html + pages/*.html (all visible text, VI and EN)
static/            CSS, images
tests/             app tests (protected on main)
```

## Request flow

```
visitor ──HTTPS──► Render (o-living-web) ──► gunicorn ──► Django
   SecurityMiddleware → WhiteNoise (static files) → LocaleMiddleware (VI/EN)
   → CommonMiddleware → CsrfViewMiddleware → view → template → HTML
```

No database reads in phase 1; SQLite exists for Django itself. The health check `/healthz/` answers `ok` and is exempt from the HTTPS redirect.

## Delivery flow

```
issue (agent:ready) ──► loop on the Mac mini (ops/, plugin agent-flow) ──► pull request into main
main ──► release branch "deploy" (ops/release.py) ──► Render deploys after the Checks workflow passes
```

TODO: the URL scheme for the two languages and the page list's URLs come with the first epic.
