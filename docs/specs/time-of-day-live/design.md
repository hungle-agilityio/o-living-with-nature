# Design: the time of day, live

Design card (owner chose every recommended answer on 2026-11-13): https://claude.ai/artifact/FjxJtNxyiqCba2JgV6Fw91

- Board 1: today's intro and the new intro side by side, with the size of the letter over time.
- Board 2: the night letter, today and with the Paper outline.
- Board 3: a page that runs its clock fast from 16:58 to 19:01, with switches for the `?t=dusk` preview, less motion and missing hero files.

For the hero timings, this file and `spec.md` replace the table "Hero: the Ở intro" of `docs/specs/design-match/design.md`. Everything else of that file stays.

## Intro (T1)

| Time | What happens |
|---|---|
| 0 – 0.6 s | The letter Ở at rest, filled with the theme's loop (poster until the video plays). The dictionary line shows bottom left. |
| 0.6 – 5.6 s | The letter grows around the thick left stroke of its bowl until the loop fills the screen. Size = `maxScale` to the power `e`, where `e` is the sine ease-in-out of the time of the growth (0 → 1): the size is multiplied by about the same ratio every moment. The anchor moves to the centre of the screen by the same `e`. The dictionary line fades out in the first sixth. |
| 5.6 – 7.0 s | The shade fades in and the heading rises line by line, 0.15 s apart, each line in 1.0 s. |
| 6.9 s | The cue "Scroll, and come in ↓" fades in, in 0.5 s. |

`maxScale` stays: 70, or more on a very wide screen so the stroke still covers it. Skipping, the end state, the still hero and the loop pausing off screen stay as in design-match.

## Night letter (T1)

- Night theme only: the letter Ở has a 1.5px outline in Paper at 55% (`rgba(233, 226, 211, 0.55)`).
- The still letter (no script, less motion) gets it from CSS.
- During the intro the canvas draws the same outline (1.5 CSS px wide on screen at any size) over the letter. Its opacity falls from 0.55 to 0 over the first fifth of the growth. It is never drawn in the other three themes.

## Live theme (T2)

- On load the server picks the theme, as today. A small script then keeps Đà Nẵng time: the server's time sent with the page plus the time since load.
- At 05:00, 08:00, 17:00 and 19:00 Đà Nẵng time, and whenever the tab becomes visible again after a boundary passed, the page takes the new theme:
  - `body[data-daypart]` changes, so the colours fade in 0.9 s (the existing transition; none under reduced motion);
  - the header line reads the new time and label, for example "It's 17:00 in Hòa Xuân · Dusk";
  - the letter takes the new theme's loop. The old picture stays until the new poster has loaded, so the letter never flashes Sand. With less motion it shows the new poster and no video.
- The header clock moves every minute, on the minute.
- With `?t=<theme>` the theme stays the preview theme; only the clock moves.
- Without the script the page keeps the theme the server chose. With no hero files the letter is Sand in every theme and only the colours change.
