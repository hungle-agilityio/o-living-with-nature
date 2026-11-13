# Tasks: the contact counter (epic)

Epic: one epic issue and three task issues on the epic branch (ADR-021, ADR-022). T2 and T3 need the model and the address of T1, and share no file, so they run in parallel after T1.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `/` | 1 | 1 | 1 | 1 |
| `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` (301) | 0 | 0 | 0 | 0 |
| `/sitemap.xml`, `/robots.txt`, a 404 | 0 | 0 | 0 | 0 |
| `POST /count/` (visitor) | – | ≤ 2 | ≤ 2 | ≤ 2 |
| the report in `/owner/` | – | – | – | same with 1 or 400 rows |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`, `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query` and `src/pages/tests/test_hero_intro.py::test_home_page_still_makes_one_query` unchanged. T2 and T3 keep the query test of `/count/` that T1 adds in `src/counter/tests/test_count_endpoint.py`.

## T1: Store daily counts and take them at /count/

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC21
- **Files likely touched:**
  - `src/counter/__init__.py` (NEW)
  - `src/counter/apps.py` (NEW)
  - `src/counter/models.py` (NEW)
  - `src/counter/forms.py` (NEW)
  - `src/counter/services.py` (NEW)
  - `src/counter/views.py` (NEW)
  - `src/counter/urls.py` (NEW)
  - `src/counter/migrations/__init__.py` (NEW)
  - `src/counter/migrations/0001_initial.py` (NEW)
  - `src/counter/tests/__init__.py` (NEW)
  - `src/counter/tests/test_count_endpoint.py` (NEW)
  - `src/config/settings.py` (`INSTALLED_APPS` only)
  - `src/config/urls.py`
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** no
- **Label:** `agent:ready`

## T2: Report views and button presses from the page

- **ACs:** AC9, AC10, AC11, AC12, AC21
- **Files likely touched:**
  - `src/static/js/count.js` (NEW)
  - `src/pages/templates/pages/home.html`
  - `src/pages/tests/test_count_script.py` (NEW)
  - `src/pages/tests/test_layout.py` (existing script-list test, listed in the issue)
  - `src/pages/tests/test_home_hero.py` (existing script-list test, listed in the issue)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** no (nothing visible changes)
- **Label:** `agent:ready`

## T3: The contact counts report in the admin

- **ACs:** AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21
- **Files likely touched:**
  - `src/counter/admin.py` (NEW)
  - `src/counter/report.py` (NEW)
  - `src/counter/templates/admin/counter/report.html` (NEW)
  - `src/counter/tests/test_report.py` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/owner/counter/dailycount/` at 1440×900 and 390×844 → `#content` (with demo counts), and with no counts → `#content`
- **Label:** `agent:ready`
