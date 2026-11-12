# Tasks: match the build to the design (epic)

Epic: one epic issue and six task issues on the epic branch (ADR-021, ADR-022).

- T1 lays the frame: the container fix, the shared chapter head in all five chapter templates, the comment fix, and the end of the page. It runs first.
- After T1, T2 (hero and header), T3 (motion), T4 (house), T5 (Hòa Xuân) and T6 (rent, FAQ, contact) share no file and can run in parallel.
- T4, T5 and T6 add the class `reveal`. T3 gives it its meaning. Without T3, the class does nothing.

## Query budget

| Page | Queries on main | After T1 | After T2–T6 |
|---|---|---|---|
| `/` | 1 | 1 | 1 |
| `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` (301) | 0 | 0 | 0 |
| `/sitemap.xml`, `/robots.txt`, a 404 | 0 | 0 | 0 |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query` and `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query` unchanged.

## T1: Frame and chapter heads

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC31, AC32
- **Files likely touched:**
  - `src/static/css/site.css`
  - `src/pages/templates/pages/chapters/house.html`
  - `src/pages/templates/pages/chapters/hoa_xuan.html`
  - `src/pages/templates/pages/chapters/rent.html`
  - `src/pages/templates/pages/chapters/faq.html`
  - `src/pages/templates/pages/chapters/contact.html`
  - `src/pages/tests/test_design_match_frame.py` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#house`, `#rent`, `#faq`, `#contact`, `footer`
- **Label:** `agent:ready`

## T2: The "Ở" plays by itself, and the header

- **ACs:** AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC31, AC32
- **Files likely touched:**
  - `src/static/js/hero.js`
  - `src/templates/includes/hero.html`
  - `src/templates/includes/header.html`
  - `src/static/css/site.css` (hero and header rules only)
  - `src/pages/tests/test_home_hero.py` (existing tests of the scroll stage, listed in the issue)
  - `src/pages/tests/test_hero_intro.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#hero` at load and after 5 s; `/#rent` (solid header)
- **Label:** `agent:ready`

## T3: Load and reveal motion

- **ACs:** AC13, AC14, AC15, AC16, AC17, AC31, AC32
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

## T4: The house: collage and facts

- **ACs:** AC18, AC19, AC20, AC21, AC31, AC32
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/house.html`
  - `src/static/css/chapters/house.css`
  - `src/pages/tests/test_house_chapter.py` (existing tests of the points, the veranda slot and the gallery, listed in the issue)
  - `src/pages/tests/test_house_collage.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#house`
- **Label:** `agent:ready`

## T5: Hòa Xuân band

- **ACs:** AC22, AC23, AC24, AC25, AC31, AC32
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/hoa_xuan.html`
  - `src/static/css/chapters/hoa_xuan.css`
  - `src/static/js/area-band.js` (NEW, only if the loop needs a script to play on screen)
  - `src/pages/tests/test_hoa_xuan_chapter.py` (existing tests of the media slot layout, listed in the issue)
  - `src/pages/tests/test_hoa_xuan_band.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#hoa-xuan`
- **Label:** `agent:ready`

## T6: Rent, FAQ and contact

- **ACs:** AC26, AC27, AC28, AC29, AC30, AC31, AC32
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/rent.html`
  - `src/static/css/chapters/rent.css`
  - `src/pages/templates/pages/chapters/faq.html`
  - `src/static/css/chapters/faq.css`
  - `src/pages/templates/pages/chapters/contact.html`
  - `src/static/css/chapters/contact.css`
  - `src/pages/templatetags/price.py` (NEW)
  - `src/owner_content/services.py`
  - `src/pages/tests/test_rent_and_contact.py` (existing layout tests, listed in the issue)
  - `src/pages/tests/test_rent_quote_and_contact_row.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` at 1440×900 and 390×844 → `#rent`, `#faq`, `#contact`
- **Label:** `agent:ready`
