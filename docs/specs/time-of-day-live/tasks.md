# Tasks: the time of day, live (epic)

Epic: one epic issue and two task issues on the epic branch (ADR-021, ADR-022). Both tasks change `src/static/js/hero.js`, so T2 runs after T1.

## Query budget

| Page | Queries on main | After T1 | After T2 |
|---|---|---|---|
| `/` | 1 | 1 | 1 |
| `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` (301) | 0 | 0 | 0 |
| `/sitemap.xml`, `/robots.txt`, a 404 | 0 | 0 | 0 |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`, `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query` and `src/pages/tests/test_hero_intro.py::test_home_page_still_makes_one_query` unchanged.

## T1: A slower, even intro and the night letter

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC15, AC16
- **Files likely touched:**
  - `src/static/js/hero.js`
  - `src/static/css/site.css` (the night letter rule only)
  - `src/pages/tests/test_hero_intro.py` (existing tests of the timings, the curve and the size cap, listed in the issue)
  - `src/pages/tests/test_home_hero.py` (existing test of the timings, listed in the issue)
  - `src/pages/tests/test_intro_pace_and_night_letter.py` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=night` at 1440×900 and 390×844 → `#hero`; `/?t=day` at 1440×900 → `#hero` at 3 s
- **Label:** `agent:ready`

## T2: The theme follows the clock while the page is open

- **ACs:** AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16
- **Files likely touched:**
  - `src/static/js/daypart.js` (NEW)
  - `src/static/js/hero.js`
  - `src/templates/base.html`
  - `src/templates/includes/header.html`
  - `src/templates/includes/hero.html`
  - `src/pages/context_processors.py`
  - `src/pages/views.py`
  - `src/pages/hero.py`
  - `src/pages/tests/test_live_daypart.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` at 1440×900 → `.site-header` and `#hero`; `/?t=dusk` at 390×844 → `.site-header`
- **Label:** `agent:ready`
