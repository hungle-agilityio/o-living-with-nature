# Tasks: match the build to the design (epic)

Epic: one epic issue and three task issues on the epic branch (ADR-021, ADR-022).

- T1 fixes the layout and the small differences. It changes `site.css`, so it runs first.
- T2 (hero intro) and T3 (load and reveal motion) both follow T1 and share no file, so they run in parallel.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `/` | 1 | 1 | 1 | 1 |
| `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` (301) | 0 | 0 | 0 | 0 |
| `/sitemap.xml`, `/robots.txt`, a 404 | 0 | 0 | 0 | 0 |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query` and `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query` unchanged.

## T1: Container, padding and small layout fixes

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC22, AC23
- **Files likely touched:**
  - `src/static/css/site.css`
  - `src/static/css/chapters/rent.css`
  - `src/static/css/chapters/hoa_xuan.css`
  - `src/static/css/chapters/contact.css`
  - `src/pages/templates/pages/chapters/house.html`
  - `src/pages/templates/pages/chapters/hoa_xuan.html`
  - `src/pages/templates/pages/chapters/rent.html`
  - `src/pages/templates/pages/chapters/faq.html`
  - `src/pages/templatetags/price.py` (NEW, only if a filter is needed to wrap "a month")
  - `src/pages/tests/test_design_match_layout.py` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#house`, `#hoa-xuan`, `#rent`, `#faq`, `#contact`, `footer`
- **Label:** `agent:ready`

## T2: The "Ở" plays by itself

- **ACs:** AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC22, AC23
- **Files likely touched:**
  - `src/static/js/hero.js`
  - `src/templates/includes/hero.html`
  - `src/static/css/site.css` (hero rules only)
  - `src/pages/tests/test_home_hero.py` (existing tests of the scroll stage, listed in the issue)
  - `src/pages/tests/test_hero_intro.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#hero` at load, and after 5 s (end state)
- **Label:** `agent:ready`

## T3: Load and reveal motion

- **ACs:** AC16, AC17, AC18, AC19, AC20, AC21, AC22, AC23
- **Files likely touched:**
  - `src/templates/base.html`
  - `src/static/js/reveal.js` (NEW)
  - `src/static/css/motion.css` (NEW)
  - `src/pages/tests/test_reveal_motion.py` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#house` after scrolling to it, `/#faq`
- **Label:** `agent:ready`
