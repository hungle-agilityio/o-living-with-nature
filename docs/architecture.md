# Architecture

Phase 1 is a small bilingual (VI/EN) site on one page: `/` with the hero and five chapters (house, Hòa Xuân, rent, FAQ, contact). Rules for code: `.claude/rules/architecture.md` and `.claude/rules/django.md`.

## Modules

```
src/config/        settings (environment), root URLs, WSGI
  └─ urls.py ──► src/pages/urls.py
src/pages/         the public pages (one feature = one Django app)
  ├─ urls.py       "/" home, "/healthz/" health check (more pages come with the first epic)
  ├─ views.py      thin: render a template; logic goes to services.py when it appears
  ├─ services.py   (created with the first rule)
  ├─ templates/    pages/*.html (all visible text, VI and EN)
  └─ tests/        the feature's tests (protected on main)
src/templates/     base.html, shared by every feature
src/static/        CSS, images shared by every feature
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
issue (agent:ready) ──► loop on the Mac mini (.flow/loop/, plugin agent-flow in .flow/plugin/) ──► pull request into main
main ──► release branch "deploy" (.flow/loop/release.py) ──► Render deploys after the Checks workflow passes
```

TODO: the URL scheme for the two languages and the page list's URLs come with the first epic.
