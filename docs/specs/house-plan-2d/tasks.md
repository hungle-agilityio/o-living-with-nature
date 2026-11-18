# Tasks: house-plan-2d

One epic of two tasks, in order: T1 draws the house and lists the rooms (works without JavaScript); T2 makes a tap open one room at a time. They share `src/static/css/chapters/house.css`, so T2 waits for T1. Each task's issue lists its existing tests that change (found with `pinned_tests.py`) before it gets `agent:ready`.

## Query budget

| Page | Queries on main | After T1 | After T2 |
|---|---|---|---|
| `/` | 1 | 1 | 1 |
| `/vi/` | 1 | 1 | 1 |

T1 adds the query-cap test `src/pages/tests/test_house_drawing.py::test_home_page_still_makes_one_query`; T2 does not change it.

## T1: Draw the house as a 2D plan with its room list

- **ACs:** AC1–AC9, AC14, AC15
- **Matrix rows:** M1–M12, M20, M22
- **Files likely touched:** `src/pages/floor_plan.py`, `src/pages/texts/house.py`, `src/templates/includes/floor_plan.html`, `src/pages/templatetags/photos.py`, `src/static/css/chapters/house.css`, `src/pages/tests/test_house_drawing.py` (NEW), `docs/specs/house-plan-2d/decisions/T1.md` (NEW); plus the existing tests it changes (mainly `src/pages/tests/test_floor_plan.py`)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/#floor-plan` at 1440x1000 → `#floor-plan` (design `plan`); `/#floor-plan` at 390x844 → `#floor-plan .plan__paper` (design `plan-phone`)
- **Label:** `agent:ready`

## T2: Open a room from the plan: side panel on desktop, bottom sheet on phones

- **ACs:** AC10–AC13, AC14, AC15
- **Matrix rows:** M13–M19, M21, M22
- **Files likely touched:** `src/static/js/floor-plan.js`, `src/static/css/chapters/house.css`, `src/pages/tests/test_house_drawing_panel.py` (NEW), `docs/specs/house-plan-2d/decisions/T2.md` (NEW); plus the existing tests it changes (the floor-plan script tests)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#floor-plan` at 1440x1000 after a click on `a.plan__room[data-room="light-well"]` → `#floor-plan` (design `plan-room`); `/#floor-plan` at 390x844 after a click on `a.plan__room[data-room="veranda"]` (in the upright plan) → `.plan__panel` (design `plan-phone-sheet`)
- **Label:** `agent:ready`
