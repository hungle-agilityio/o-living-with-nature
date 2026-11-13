# Tasks: search-ready

One task, no epic: both parts change the `<head>` in `src/templates/base.html` and `src/pages/seo.py`, so they cannot run in parallel, and together they stay well under 400 lines.

## Query budget

| Page | Queries on main | After T1 |
|---|---|---|
| `/` | 1 | 1 |
| `/sitemap.xml`, `/robots.txt`, the old addresses (301), a 404 | 0 | 0 |

T1 keeps every "one query" test of `/` on `main` unchanged (for example `src/pages/tests/test_one_page.py::test_home_page_makes_one_query` and `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query`).

## T1: Get the home page ready for Search Console

- **ACs:** AC1–AC13
- **Matrix rows:** M1–M14
- **Files likely touched:** `src/config/settings.py`, `src/pages/seo.py`, `src/pages/views.py`, `src/templates/base.html`, `src/pages/templates/pages/home.html`, `render.yaml`, `src/pages/tests/test_search_ready.py` (NEW), `src/pages/tests/test_layout.py`, `docs/specs/search-ready/decisions/T1.md` (NEW)
- **Existing tests that change:** `src/pages/tests/test_layout.py::test_page_uses_no_javascript` (the script list gains `'<script type="application/ld+json">'` first)
- **Depends on:** none
- **Risk:** low
- **needs-ui:** no
- **Label:** `agent:ready`
