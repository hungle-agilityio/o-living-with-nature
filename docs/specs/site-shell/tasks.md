# Tasks: site shell and look (epic 1)

Epic: one epic issue, five task issues on the epic branch (ADR-021, ADR-022). T2 and T3 run one after the other because they share `base.html`, `settings.py` and the header and footer; T4 shares no file with T2 or T3 and can run beside them.

Before any issue gets `agent:ready`, two hand-built changes must be merged on `main` (they touch `.claude/`, ADR-023): the browser check that runs the site with debug off (T4 needs it), and the updated `domain.md` and `architecture.md` rules (every task reads them). Before T5 gets `agent:ready`, the four hero loops and posters of `media-credits.md` are added by hand to `src/static/media/hero/`.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 | After T4 |
|---|---|---|---|---|---|
| `/` | 0 | 0 | 0 | 0 | 0 |
| `/house/` | — (404) | — | — | 0 | 0 |
| `/hoa-xuan/` | — (404) | — | — | 0 | 0 |
| `/faq/` | — (404) | — | — | 0 | 0 |
| `/contact/` | — (404) | — | — | 0 | 0 |
| `/sitemap.xml` | — | — | — | 0 | 0 |
| `/robots.txt` | — | — | — | 0 | 0 |
| an unknown page (404) | 0 | 0 | 0 | 0 | 0 |

T5 changes no query count (0 on `/`).

T3 adds the query-cap test (`src/pages/tests/test_pages_and_seo.py`); T4 keeps it passing.

## T1: Shared layout, type and media slot

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC20
- **Files likely touched:** `src/config/settings.py`, `src/templates/base.html`, `src/templates/includes/header.html` (NEW), `src/templates/includes/footer.html` (NEW), `src/templates/includes/media.html` (NEW), `src/static/css/site.css`, `src/pages/tests/test_layout.py` (NEW)
- **Depends on:** the two hand-built changes above
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` → `header`; `/` → `footer`; `/` at 390px → `header details`
- **Label:** `agent:ready`

## T2: Colours that follow the time of day in Hòa Xuân

- **ACs:** AC8, AC9, AC10, AC11, AC12, AC20
- **Files likely touched:** `src/pages/daypart.py` (NEW), `src/pages/context_processors.py` (NEW), `src/config/settings.py`, `src/templates/base.html`, `src/templates/includes/header.html`, `src/templates/includes/footer.html`, `src/static/css/site.css`, `src/pages/tests/test_daypart.py` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=dawn` → `body`; `/?t=day` → `body`; `/?t=dusk` → `body`; `/?t=night` → `body`
- **Label:** `agent:ready`

## T3: The five page addresses and the search groundwork

- **ACs:** AC13, AC14, AC15, AC16, AC17, AC18, AC20
- **Files likely touched:** `src/config/settings.py`, `src/config/urls.py`, `src/pages/urls.py`, `src/pages/views.py`, `src/pages/seo.py` (NEW), `src/templates/base.html`, `src/pages/templates/pages/home.html`, `src/pages/templates/pages/house.html` (NEW), `src/pages/templates/pages/hoa_xuan.html` (NEW), `src/pages/templates/pages/faq.html` (NEW), `src/pages/templates/pages/contact.html` (NEW), `src/pages/tests/test_pages_and_seo.py` (NEW)
- **Depends on:** T2
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` → `main`; `/house/` → `main`; `/contact/` → `main`
- **Label:** `agent:ready`

## T4: "Page not found" in the new look

- **ACs:** AC19, AC20
- **Files likely touched:** `src/templates/404.html` (NEW), `src/pages/tests/test_not_found_page.py` (NEW)
- **Depends on:** T1, and the hand-built browser check change (debug off)
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/this-page-does-not-exist/` with debug off and status 404 → `main`
- **Label:** `agent:ready`. Replaces issue #4, which is closed as superseded when this issue is created.

## T5: Home hero "Through the Ở"

- **ACs:** AC21, AC22, AC23, AC24, AC25, AC20
- **Files likely touched:** `src/pages/templates/pages/home.html`, `src/templates/includes/hero.html` (NEW), `src/static/js/hero.js` (NEW), `src/static/css/site.css`, `src/pages/tests/test_home_hero.py` (NEW)
- **Depends on:** T3, and the hand-added hero media in `src/static/media/hero/` (see design.md, Media used in epic 1)
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/?t=day` → `#hero` at the top; `/?t=night` → `#hero` at the top; `/` with reduced motion → `#hero`; `/` at 390px → `#hero`
- **Label:** `agent:ready`
