# Architecture rules

Code is split by feature, not by layer: `src/<feature>/` holds everything one feature needs (a Django app: views, URLs, its templates in `src/<feature>/templates/`), and its tests in `src/<feature>/tests/`. The Django project is `src/config/`; templates and static files shared by every feature are in `src/templates/` and `src/static/`. The overview is `docs/architecture.md`.

## Layers

- **Views** (`src/pages/views.py`): read the request, call a service when there is logic, render a template. No business rule in a view or a template.
- **Services** (`src/pages/services.py`, created when the first rule appears): plain typed functions or service objects that hold the logic and are unit tested.
- **Models**: only when a page needs stored data. Phase 1 stores nothing; a model is a decision for an issue, never a side effect.
- **Templates** (`src/<feature>/templates/`, shared ones in `src/templates/`): presentation only; every page extends `base.html`.
- **Settings** (`src/config/settings.py`): values that differ per environment come from environment variables; secrets are never committed.

## Dependencies

- Python 3.11, Django 5, SQLite in development; served by gunicorn and whitenoise on Render (`render.yaml`, branch `deploy`).
- No CMS, no JavaScript framework, no front-end build step in phase 1.
- A new dependency needs a reason in the issue.

## Why

The site is a handful of static pages, so the structure stays as small as Django allows, while still keeping logic out of views so it can be tested when the site grows (more pages, a contact form, a later booking flow are not in scope today).

TODO: confirm with the owner once `idea.md` is written (hosting plan, image storage, analytics).
