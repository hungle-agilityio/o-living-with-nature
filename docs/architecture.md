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

## Environment variables

Set by hand, never committed. The values are not written here or anywhere in the repository.

| Name | Purpose | Where it is set |
|---|---|---|
| `DATABASE_URL` | The address of the Postgres database on Neon that keeps the owner's settings. Without it the app uses the SQLite file, which Render wipes on every deploy and wake-up (`manage.py check` then warns `config.W001`). | Render, in the environment of the service `o-living-web`. Not set in development and tests (SQLite). |
| `OWNER_USERNAME` | The sign-in name of the owner's account for the admin at `/owner/`. `manage.py ensure_owner` creates the account at every start. | Render, in the environment of the service `o-living-web`. |
| `OWNER_PASSWORD` | The password of that account, at least 12 characters. `manage.py ensure_owner` sets it at every start, so changing it on Render changes the password. | Render, in the environment of the service `o-living-web`. |

## Delivery flow

```
issue (agent:ready) ──► loop on the Mac mini (.flow/loop/, plugin agent-flow in .flow/plugin/) ──► pull request into main
main ──► release branch "deploy" (.flow/loop/release.py) ──► Render deploys after the Checks workflow passes
```

TODO: the URL scheme for the two languages and the page list's URLs come with the first epic.
