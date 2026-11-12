# Tasks: the site as one page (epic 3)

Epic: one epic issue and six task issues on the epic branch (ADR-021, ADR-022).

- T1 builds the frame: the chapters, the menu, the redirects, the `photo` tag, the `owner` context, and one empty template and one stylesheet per chapter.
- T2, T3, T4 and T5 each fill only their own chapter's template, stylesheet and test file, so they run in parallel after T1.
- T6 adds the floor plan to the house chapter, so it follows T3.

Before T1 gets `agent:ready`, these must be merged into `main`:

- epic 2 (#26: the settings service of #28 and the photo list of #29);
- PR #25;
- PR #32 (the browser check allows the owner's number).

Before any task gets `agent:ready`, one change is made by hand (ADR-023, "Exception: .claude/"): `.claude/rules/domain.md` says that phase 1 is one page at `/` with five chapters, and that the old addresses redirect to them.

## Query budget

| Page | Queries on main (after epic 2) | After T1 | After T2–T6 |
|---|---|---|---|
| `/` | 0 | 1 (the site settings) | 1 |
| `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` | 0 (200) | 0 (301) | 0 |
| `/sitemap.xml`, `/robots.txt` | 0 | 0 | 0 |
| an unknown page (404) | 0 | 0 | 0 |

T1 changes the home page's cap from 0 to 1 in the existing query-cap tests, and lists them below. T2 to T6 keep `/` at exactly 1. Each of them names the cap test T1 changed, `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`, as one that stays unchanged.

## T1: One page, its menu and the old addresses

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8
- **Files likely touched:**
  - `src/pages/views.py`
  - `src/pages/urls.py`
  - `src/pages/seo.py`
  - `src/pages/templatetags/__init__.py` (NEW)
  - `src/pages/templatetags/photos.py` (NEW)
  - `src/pages/templates/pages/home.html`
  - `src/pages/templates/pages/chapters/house.html` (NEW)
  - `src/pages/templates/pages/chapters/hoa_xuan.html` (NEW)
  - `src/pages/templates/pages/chapters/rent.html` (NEW)
  - `src/pages/templates/pages/chapters/faq.html` (NEW)
  - `src/pages/templates/pages/chapters/contact.html` (NEW)
  - `src/pages/templates/pages/house.html` (removed)
  - `src/pages/templates/pages/hoa_xuan.html` (removed)
  - `src/pages/templates/pages/faq.html` (removed)
  - `src/pages/templates/pages/contact.html` (removed)
  - `src/templates/includes/nav_links.html`
  - `src/static/css/site.css`
  - `src/static/css/chapters/house.css` (NEW)
  - `src/static/css/chapters/hoa_xuan.css` (NEW)
  - `src/static/css/chapters/rent.css` (NEW)
  - `src/static/css/chapters/faq.css` (NEW)
  - `src/static/css/chapters/contact.css` (NEW)
  - `src/pages/tests/test_one_page.py` (NEW)
- **Existing tests that change** (the issue gives the exact list from `pinned_tests.py`):
  - in `src/pages/tests/test_pages_and_seo.py`: the tests on the inner pages, their titles, canonicals, Open Graph tags, robots tags and header marks, the five-address sitemap test, and `test_page_asks_the_database_nothing`;
  - in `src/pages/tests/test_layout.py`: the four-link header and phone menu tests, and the current-link test;
  - in `src/pages/tests/test_home_hero.py`: `test_home_page_asks_the_database_nothing` (0 to 1).
- **Depends on:** #28, #29, PR #25, PR #32, the hand-built rule change
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` → `header`; `/` → `#house`; `/` at 390px → `header details`
- **Label:** `agent:ready`

## T2: Rent and contact, with the phone bar

- **ACs:** AC9, AC10, AC11, AC12
- **Files likely touched:**
  - `src/templates/includes/contact_buttons.html` (NEW)
  - `src/pages/templates/pages/chapters/rent.html`
  - `src/pages/templates/pages/chapters/contact.html`
  - `src/static/css/chapters/rent.css`
  - `src/static/css/chapters/contact.css`
  - `src/static/js/contact-bar.js` (NEW)
  - `src/pages/tests/test_rent_and_contact.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` → `#rent`; `/` → `#contact`; `/` at 390px → `nav[aria-label="Contact"]`
- **Label:** `agent:ready`

## T3: The house chapter

- **ACs:** AC13
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/house.html`
  - `src/static/css/chapters/house.css`
  - `src/pages/tests/test_house_chapter.py` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` → `#house`; `/` at 390px → `#house`
- **Label:** `agent:ready`

## T4: The Hòa Xuân chapter

- **ACs:** AC14
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/hoa_xuan.html`
  - `src/static/css/chapters/hoa_xuan.css`
  - `src/pages/tests/test_hoa_xuan_chapter.py` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` → `#hoa-xuan`
- **Label:** `agent:ready`

## T5: The FAQ chapter

- **ACs:** AC15
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/faq.html`
  - `src/static/css/chapters/faq.css`
  - `src/pages/tests/test_faq_chapter.py` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` → `#faq`
- **Label:** `agent:ready`

## T6: Walk through the house (schematic floor plan)

- **ACs:** AC16, AC17
- **Files likely touched:**
  - `src/templates/includes/floor_plan.html` (NEW)
  - `src/pages/templates/pages/chapters/house.html`
  - `src/static/css/chapters/house.css`
  - `src/static/js/floor-plan.js` (NEW)
  - `src/pages/tests/test_floor_plan.py` (NEW)
- **Depends on:** T3
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` → `#floor-plan`; `/` at 390px → `#floor-plan`
- **Label:** `agent:ready`
