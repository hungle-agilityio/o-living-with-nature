# Design: match the build to the design

Design card (approved for epic 3, 2026-11-12): https://claude.ai/artifact/8Kk9W7BQzsfWuGUWWhNAVf, boards Main (desktop 1440) and Phone (390). Motion reference: the design E tour video, `epic-1-site-shell/tour/mau-5-qua-chu-o.mp4` in the project files, and its build script `tour/src/build.py` (TOUR_CSS, TOUR_JS). Audit with screenshots of `main` at e23078b: `design-audit/gap-list.md` and `design-audit/shots/` in the project files.

Nothing new is added to the tokens. The layout, sizes and texts of `docs/specs/one-page/design.md` stay; this file only adds what was missing.

## Layout fixes

- Every chapter sits in the container of epic 1: at most 1360px wide, centred, 40px sides on desktop and 18px on phones (`--content-max`, `--side`). On a 1440px screen, the left edge of each chapter's marker, word, heading and content is at x = 80px; on a 390px screen at x = 18px.
- The hero stays full bleed (edge to edge) and the Contact band stays full width; its text sits in the same container.
- The Contact band runs straight into the Ink footer, with no Paper strip between them.
- Headings with an accent word, in Cormorant italic at the heading's real size, like "Will you *stay?*": The *house*, Hòa *Xuân*, The *rent*.
- Rent: the price line is Be Vietnam Pro 300 at the "big" size (84px desktop, 44px phone), letter spacing -0.03em, line height 0.95, and its last words "a month" are in Cormorant italic.
- Hòa Xuân travel list: each row has the place on the left (body text) and the time on the right as a small caps label (11px, 0.22em, Stone). The " · " between them stays in the page for readers but is not shown.
- Hero chip "Illustrative video": top right of the hero, 24px from the top and the right side.

## The "Ở" intro (plays by itself)

The hero is one screen high (100svh). When the page loads with JavaScript and the visitor has not asked for less motion:

| Time | What happens |
|---|---|
| 0 – 0.4 s | The letter Ở at rest, filled with the theme's loop (poster until the video plays). The dictionary line and the cue show. The header fades in. |
| 0.4 – 3.2 s | The letter grows around the thick left stroke of its bowl, as in epic 1 (scale up to about 70 times, rising with progress to the power 2.4), until the loop fills the screen. The dictionary line and the cue fade out in the first sixth. |
| 3.2 – 4.0 s | The shade fades in, the header row turns Paper, and the heading "Living *with* nature" and its line rise into place line by line (each line 30px up and from hidden, 0.15 s apart). |
| after | The loop keeps playing full screen behind the heading. The cue "Scroll, and come in ↓" shows at the bottom. |

- It plays on every load of `/`, and only at the top of the page. A page opened at a chapter (`/#rent`) shows the end state at once.
- Any wheel, touch, key or click during the intro jumps to the end state at once, and the page scrolls normally. The page is never locked.
- Under `prefers-reduced-motion: reduce`, or without JavaScript, the hero is the still hero of epic 1, unchanged.
- With no hero files (Sand letter), there is no growth: the still hero shows.

## Load and reveal motion (from the tour video)

Only with JavaScript and when the visitor has not asked for less motion:

- Header: fades in and moves 12px down into place, 0.9 s, after 0.2 s.
- Chapter blocks (the marker, the chapter word, the heading, each paragraph, list, photo and the floor plan): hidden 42px lower until 12% of the block is on screen, then fade and rise into place in 1.1 s, easing `cubic-bezier(.2,.7,.2,1)`. Blocks side by side start 0.12 s apart, at most 5 steps.
- Photos in media slots: a slow zoom from 1.02 to 1.09 over 22 s, back and forth, inside their frame (nothing grows out of the slot).
- Without JavaScript, or under reduced motion, everything shows at once with no movement. A block is never hidden unless the script runs.

## States

- **Normal:** as above, in each of the four time-of-day themes.
- **Empty:** a missing hero file gives the still Sand letter; a missing photo gives the Sand slot with Ở, without zoom.
- **Error:** unchanged (404 page of epic 1).
- **Narrow (390px):** same intro, the letter sized to the screen; nothing wider than the screen; the phone contact bar still shows only after the hero.
