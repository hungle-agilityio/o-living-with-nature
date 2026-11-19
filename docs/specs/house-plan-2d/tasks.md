# Tasks: house-plan-2d

One epic of three tasks, in order: T1 draws the house and lists the rooms (works without JavaScript) and drops "The layout" list; T2 makes a tap open one room at a time; T3 draws the facts row (and changes its third fact to "1 real kitchen"). They all change `src/static/css/chapters/house.css`, so T2 waits for T1 and T3 waits for T2. Each task's issue lists its existing tests that change (found with `pinned_tests.py`) before it gets `agent:ready`.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `/` | 1 | 1 | 1 | 1 |
| `/vi/` | 1 | 1 | 1 | 1 |

T1 adds the query-cap test `src/pages/tests/test_house_drawing.py::test_home_page_still_makes_one_query`; T2 and T3 do not change it.

## T1: Draw the house as a 2D plan with its room list, and drop "The layout" list

- **ACs:** AC1–AC9, AC16, AC17
- **Matrix rows:** M1–M12, M12b, M20, M22
- **Files likely touched:** `src/pages/floor_plan.py`, `src/pages/texts/house.py`, `src/pages/templates/pages/chapters/house.html`, `src/templates/includes/floor_plan.html`, `src/pages/templatetags/photos.py`, `src/static/css/chapters/house.css`, `src/pages/tests/test_house_drawing.py` (NEW), `docs/specs/house-plan-2d/decisions/T1.md` (NEW); plus the existing tests it changes (mainly `src/pages/tests/test_floor_plan.py`)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/#floor-plan` at 1440x1000 → `#floor-plan` (design `plan`); `/#floor-plan` at 390x844 → `#floor-plan .plan__paper` (design `plan-phone`)
- **Label:** `agent:ready`

## T2: Open a room from the plan: side panel on desktop, bottom sheet on phones

- **ACs:** AC10–AC13, AC16, AC17
- **Matrix rows:** M13–M19, M21, M22
- **Files likely touched:** `src/static/js/floor-plan.js`, `src/static/css/chapters/house.css`, `src/pages/tests/test_house_drawing_panel.py` (NEW), `docs/specs/house-plan-2d/decisions/T2.md` (NEW); plus the existing tests it changes (the floor-plan script tests)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#floor-plan` at 1440x1000 after a click on `a.plan__room[data-room="kitchen"]` → `#floor-plan` (design `plan-room`); `/#floor-plan` at 390x844 after a click on `a.plan__room[data-room="bedroom-1"]` (in the upright plan) → `.plan__panel` (design `plan-phone-sheet`)
- **Label:** `agent:ready`

## T3: Draw the facts row in the style of the sketch

- **ACs:** AC14, AC15, AC16, AC17
- **Matrix rows:** M23–M27, M22
- **Files likely touched:** `src/pages/templates/pages/chapters/house.html`, `src/pages/texts/house.py`, `src/static/css/chapters/house.css`, `src/pages/tests/test_house_facts_drawn.py` (NEW), `docs/specs/house-plan-2d/decisions/T3.md` (NEW); plus the existing tests it changes (the facts row tests of `test_house_chapter.py` and `test_vietnamese_chapters_house_area.py`)
- **Depends on:** T2
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#house` at 1440x1000 → `.house__facts-drawn` (design `house-facts`); `/#house` at 390x844 → `.house__facts-drawn` (design `house-facts-phone`)
- **Label:** `agent:ready`
