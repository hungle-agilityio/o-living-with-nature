# Tasks: owner-editable content and storage (epic 2)

Epic: one epic issue and three task issues on the epic branch (ADR-021, ADR-022). T2 needs T1's app and admin. T3 shares no file with T1 or T2 and can run beside them.

Two changes are made by hand before the issues they block get `agent:ready`:

- **H1, before any issue:** the rules `.claude/rules/domain.md` and `.claude/rules/architecture.md` say that photos and videos are static files in the repository, that the owner edits only the site settings in the admin at `/owner/`, and that Cloudinary is dropped (ADR-023, "Exception: .claude/"). Every task reads them.
- **H2, before T3:** the fourteen photos and the area loop of `media-credits.md` are committed to `src/static/media/photos/` and `src/static/media/area/` from the project files `epic-2-owner-content/media/`.

Before the epic is released, the owner creates the free Neon database and sets `DATABASE_URL`, `OWNER_USERNAME` and `OWNER_PASSWORD` in Render's environment.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `/` | 0 | 0 | 0 | 0 |
| `/house/` | 0 | 0 | 0 | 0 |
| `/hoa-xuan/` | 0 | 0 | 0 | 0 |
| `/faq/` | 0 | 0 | 0 | 0 |
| `/contact/` | 0 | 0 | 0 | 0 |
| `/sitemap.xml` | 0 | 0 | 0 | 0 |
| `/robots.txt` | 0 | 0 | 0 | 0 |
| an unknown page (404) | 0 | 0 | 0 | 0 |

The admin at `/owner/` is not in the budget. The query-cap tests on `main` (`src/pages/tests/test_pages_and_seo.py`, `src/pages/tests/test_home_hero.py`, `src/pages/tests/test_not_found_page.py`) pass unchanged after every task. T2 adds the one-query test of `site_settings()` in `src/owner_content/tests/test_site_settings.py`.

## T1: A lasting database and the owner's sign-in

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6
- **Files likely touched:** `pyproject.toml`, `uv.lock`, `render.yaml`, `.env.example`, `src/config/settings.py`, `src/config/urls.py`, `src/owner_content/__init__.py` (NEW), `src/owner_content/apps.py` (NEW), `src/owner_content/checks.py` (NEW), `src/owner_content/management/__init__.py` (NEW), `src/owner_content/management/commands/__init__.py` (NEW), `src/owner_content/management/commands/ensure_owner.py` (NEW), `src/owner_content/tests/__init__.py` (NEW), `src/owner_content/tests/test_database_and_owner.py` (NEW)
- **Depends on:** H1
- **Risk:** high (production settings, new dependencies, start command)
- **needs-ui:** no
- **Label:** `agent:ready`

## T2: Site settings the owner edits

- **ACs:** AC7, AC8, AC9, AC10, AC11, AC12
- **Files likely touched:** `src/owner_content/models.py` (NEW), `src/owner_content/admin.py` (NEW), `src/owner_content/services.py` (NEW), `src/owner_content/migrations/__init__.py` (NEW), `src/owner_content/migrations/0001_initial.py` (NEW), `src/owner_content/migrations/0002_owner_values.py` (NEW), `src/owner_content/tests/test_site_settings.py` (NEW)
- **Depends on:** T1
- **Risk:** medium (first model and migrations)
- **needs-ui:** no
- **Label:** `agent:ready`

## T3: The list of illustrative photos

- **ACs:** AC13, AC14, AC15, AC16
- **Files likely touched:** `src/pages/photos.py` (NEW), `src/pages/tests/test_photos.py` (NEW)
- **Depends on:** H1, H2
- **Risk:** low
- **needs-ui:** no
- **Label:** `agent:ready`
