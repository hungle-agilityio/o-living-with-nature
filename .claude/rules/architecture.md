# Architecture rules

Code is split by feature, not by layer: `src/{feature}/` holds everything one feature needs (a Django app: views, URLs, its templates in `src/{feature}/templates/`), and its tests in `src/{feature}/tests/`. The Django project is `src/config/`; templates and static files shared by every feature are in `src/templates/` and `src/static/`. The overview is `docs/architecture.md`.

## Layers

- **Views** (`src/pages/views.py`): read the request, call a service when there is logic, render a template. No business rule in a view or a template.
- **Services** (for example `src/pages/daypart.py`, `src/pages/seo.py`): plain typed functions or service objects that hold the logic and are unit tested.
- **Models**: phase 1 stores a small amount of data: the site settings the owner edits (price range, contact values, first name, reply time), photos and videos with their labels, and the visit and click counters. A new model is a decision for an issue, never a side effect.
- **Templates** (`src/{feature}/templates/`, shared ones in `src/templates/`, reusable parts in `src/templates/includes/`): presentation only; every page extends `base.html`.
- **Settings** (`src/config/settings.py`): values that differ per environment come from environment variables (`DATABASE_URL`, `SITE_BASE_URL`, `INDEXING_ENABLED`, the Cloudinary keys); secrets are never committed.

## Data and files

- **Database:** Postgres on Neon (free plan) in production through `DATABASE_URL`; SQLite in development and tests. Render's free disk is wiped on every deploy, so nothing that must last is written to it.
- **Uploaded photos and videos:** Cloudinary (free plan) through Django's storage setting; local files in development; tests never call Cloudinary.
- **Static files** (CSS, the small hero script, the site's own images, the illustrative hero loops in `src/static/media/hero/`): WhiteNoise, collected at build time.

## Dependencies

- Python 3.11, Django 5; served by gunicorn and WhiteNoise on Render (`render.yaml`, branch `deploy`, free plan).
- Allowed for phase 1, each added by the issue that first needs it: a Postgres driver (`psycopg`), `dj-database-url`, and a Cloudinary storage package.
- Fonts from Google Fonts (`fonts.googleapis.com`); no other third-party script or tracker.
- No CMS, no JavaScript framework, no front-end build step. Small progressive enhancements in plain JavaScript are allowed when an issue asks for them; every page works without JavaScript.
- A new dependency needs a reason in the issue.

## Why

The site is a handful of pages with a few owner-editable values, so the structure stays as small as Django allows, while logic stays out of views so it can be tested. Free hosting forces data and uploads off Render's disk.
