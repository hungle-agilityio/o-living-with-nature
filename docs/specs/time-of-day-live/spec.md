# Spec: the time of day, live (epic)

## Summary

The home page `/` keeps its four time-of-day themes in Đà Nẵng time (`src/pages/daypart.py`) and changes in three ways:

- the "Ở" intro is slower (about 7 s) and grows at an even pace;
- at night the letter Ở has a faint Paper outline, so it can be seen;
- while the page stays open, the theme, the loop in the letter and the header clock follow Đà Nẵng time.

Design, timings and values: `docs/specs/time-of-day-live/design.md` and its design card. Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change".

## Acceptance criteria

### Intro and night letter (T1)

- **AC1.** With JavaScript, at the top of `/` and without `prefers-reduced-motion: reduce`, the intro runs on the timings of design.md: `GROW_START = 0.6`, `GROW_END = 5.6`, `INTRO_END = 7.0`, `LINE_DELAY = 0.15`, `LINE_TIME = 1.0`, `CUE_START = 6.9`, `FOOT_END = 1 / 6`.
- **AC2.** The size of the letter is `Math.pow(maxScale, e)` with `e` the sine ease-in-out of the time of the growth, `-(Math.cos(Math.PI * t) - 1) / 2`. The anchor moves to the centre by the same `e`. `MAX_SCALE` stays 70 and the wide-screen rule stays. The constant `POWER` and the cubic ease of the growth are gone.
- **AC3.** In a browser at 1440×900, the size of the letter at 1.6 s, 3.1 s and 4.6 s is within 15% of maxScale^0.095, maxScale^0.5 and maxScale^0.905 (with maxScale = 70: about ×1.5, ×8.4 and ×46.7). No time step of 1/60 s during the growth multiplies the size by more than 1.06.
- **AC4.** Skipping on wheel, touch, key, pointer press or scroll, the end state for a page opened lower or at a chapter, the still hero, the paused loop off screen and the header states stay as on `main` (design-match AC8 to AC11).
- **AC5.** With `body[data-daypart="night"]` the still letter `.hero__letter` has `-webkit-text-stroke: 1.5px rgba(233, 226, 211, 0.55)`. In the other three themes it has no stroke.
- **AC6.** During the intro, in the night theme only, the canvas strokes the letter in `rgba(233, 226, 211, a)` with a line 1.5 CSS px wide on screen, where `a` falls from 0.55 at the start of the growth to 0 at one fifth of it. The script reads the theme from `body[data-daypart]` on every frame, so a live change (T2) is followed.
- **AC7.** `hero.js` stays one plain deferred script with no library, under 14 000 bytes (raised from 12 000).

### Live theme (T2)

- **AC8.** The header line `.site-header__time` carries `data-now`, the server's time of the response in milliseconds since 1970-01-01 UTC, and, when the request has a valid `?t=`, `data-preview`. The `<body>` tag stays exactly `<body data-daypart="<theme>">`. The response of `/` still makes one database query.
- **AC9.** A new deferred script `src/static/js/daypart.js` (plain, no library, under 4 000 bytes, no storage, no network request) keeps Đà Nẵng time as `data-now` plus the time since load (UTC+7, no daylight saving).
- **AC10.** At 05:00, 08:00, 17:00 and 19:00 Đà Nẵng time, without `data-preview`, it sets `body[data-daypart]` to the theme of `theme_for` (dawn, day, dusk, night) within 2 s, and at once when the page becomes visible again (`visibilitychange`, `pageshow`) after a boundary passed. It then dispatches the event `daypart` on `document` with `detail.theme`.
- **AC11.** The header line `.site-header__time` changes on every minute, within 2 s, to "It's HH:MM in Hòa Xuân · Label" (24-hour clock with leading zeros, label = the shown theme with a capital). The server-rendered text of the header stays as on `main`.
- **AC12.** With `data-preview` the theme and its label never change; only the clock moves.
- **AC13.** On the `daypart` event the hero takes the new theme's files:
  - the page carries the files of every theme that has all three (poster, mp4, webm), from `hero.media_for`, as hashed static URLs;
  - with the intro running or over, `hero.js` loads the new poster first, then sets the video's sources to the new loop and plays it; until the new poster has loaded the canvas keeps the old picture, so it never shows Sand;
  - the still letter `.hero__letter` takes the new poster as its background image;
  - under `prefers-reduced-motion: reduce` no video plays, only the poster changes;
  - a theme with missing files shows the Sand letter and no "Illustrative video" chip, as on load.
- **AC14.** The colours change with the existing 0.9 s transition, and at once under reduced motion. Without JavaScript nothing changes after load.

### Both tasks

- **AC15.** `bash scripts/check.sh` passes. Every test on `main` passes unchanged, except the tests listed in the task.
- **AC16.** In the browser check at 1440×900 and 390×844 nothing is wider than the screen, and the console shows no error.

## Edge cases

- Empty: no hero files for a theme → the Sand letter, no video, no chip; the colours still change.
- A wrong device clock: no effect, the time comes from the server.
- A tab asleep for hours: on return the theme and clock catch up at once.
- A page restored from the back-forward cache: `pageshow` catches up the same way.
- `?t=` with a value that is not a theme: ignored as today, so the page follows the clock.
- Large data: none.
- Permissions: none; every visitor sees the same page.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1. Theme already follows the time; what more? | Keep Đà Nẵng time, fix the night letter, switch live | Visitor's clock; night fix only; leave it | "It's 10:32 in Hòa Xuân" is the brand idea (epic 1, Q2); the night letter and the stale theme are what visitors notice |
| Q2. Night letter | 1.5px Paper outline at 55%, night only | Brighten the night video | Keeps the "lit house in the dark" mood |
| Q3. Crossing a boundary with the page open | Colours fade, loop changes, clock moves every minute | Colours and clock only | The letter is the theme's main picture |
| Q4. Preview `?t=` | Stays on the preview theme, clock moves | Follows the real time | A preview link must show what it names |
| Q5. Intro length | About 7 s, growth 5 s | About 9 s; about 5.5 s | Slow enough to feel calm; any input still skips |
| Q6. Growth curve | Size = 70 to the power of a sine-eased time | Today's curve, stretched | Even zoom, no rush at the end |

## Design

`docs/specs/time-of-day-live/design.md` (design card https://claude.ai/artifact/FjxJtNxyiqCba2JgV6Fw91).

## Open questions
