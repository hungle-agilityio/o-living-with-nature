# Tasks: mobile-smoothness

One epic of four tasks. They share no file, so they can run in parallel. Each task's issue lists its existing tests that change (found with `pinned_tests.py`) before it gets `agent:ready`.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 | After T4 |
|---|---|---|---|---|---|
| `/` | 1 | 1 | 1 | 1 | 1 |
| `/vi/` | 1 | 1 | 1 | 1 | 1 |

No task adds a query-cap test that a later task must list: each new test file checks one query on `/` and `/vi/`, as the existing ones do.

## T1: Phone photo carousel with page count and dots

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC17, AC18
- **Matrix rows:** M1–M8, M21, M22
- **Files likely touched:** `src/static/css/chapters/house.css`, `src/static/js/house-carousel.js` (NEW), `src/pages/templates/pages/chapters/house.html`, `src/pages/tests/test_house_carousel.py` (NEW), `docs/specs/mobile-smoothness/decisions/T1.md` (NEW); plus the existing tests it changes (the sideways-row test of `test_house_collage.py`, the script-list tests of `test_layout.py` and `test_home_hero.py`)
- **Depends on:** none
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#house` at 390x844 → `.house__collage` and `.house__pager` (design `house-phone-carousel`)
- **Label:** `agent:ready`

## T2: Show the phone contact bar only when no other buttons are on screen

- **ACs:** AC7, AC8, AC9, AC10, AC17, AC18
- **Matrix rows:** M9–M12, M21, M22
- **Files likely touched:** `src/static/js/contact-bar.js`, `src/static/css/chapters/contact.css`, `src/pages/templates/pages/home.html`, `src/pages/tests/test_contact_bar_once.py` (NEW), `docs/specs/mobile-smoothness/decisions/T2.md` (NEW); plus the existing tests it changes
- **Depends on:** none
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#rent` at 390x844 → `#rent` (design `rent-phone-no-bar`); `/#hoa-xuan` at 390x844 → `.contact-bar` (design `hoa-xuan-phone-bar`)
- **Label:** `agent:ready`

## T3: One-line header clock on phones

- **ACs:** AC11, AC12, AC13, AC17, AC18
- **Matrix rows:** M13–M16, M21, M22
- **Files likely touched:** `src/templates/includes/header.html`, `src/static/js/daypart.js`, `src/static/css/site.css`, `src/pages/tests/test_header_short_clock.py` (NEW), `docs/specs/mobile-smoothness/decisions/T3.md` (NEW); plus the existing tests it changes
- **Depends on:** none
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` at 390x844 → `.site-header` (design `header-phone`)
- **Label:** `agent:ready`

## T4: Animate only what is on screen

- **ACs:** AC14, AC15, AC16, AC17, AC18
- **Matrix rows:** M17–M22
- **Files likely touched:** `src/static/css/motion.css`, `src/static/js/reveal.js`, `src/static/js/hero.js`, `src/static/js/lang-switch.js`, `src/pages/tests/test_motion_near_screen.py` (NEW), `docs/specs/mobile-smoothness/decisions/T4.md` (NEW); plus the existing tests it changes
- **Depends on:** none
- **Risk:** medium (hero.js, near its 14,000-byte limit)
- **needs-ui:** no (nothing looks different; the checks are in the code and by hand)
- **Label:** `agent:ready`
