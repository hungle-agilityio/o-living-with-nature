# Spec: match the build to the design (epic)

## Summary

The home page `/` is brought in line with the approved design card and the design E tour video. T1 fixes the layout: the chapters get back their container and side padding, a stray template comment leaves the page, and the headings, the price line, the travel list and the end of the page match the card. T2 turns the "Ở" hero from a scroll-driven stage into an intro that plays by itself on load and ends on the full-screen loop with the title. T3 adds the calm load and reveal motion of the tour video.

Design, timings and sizes: `docs/specs/design-match/design.md`. Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change".

## Acceptance criteria

### Layout and small fixes (T1)

- **AC1.** With JavaScript on and off, at 1440×900 every chapter's marker, chapter word, `h2` and first content block start at x = 80px (the 1360px container with 40px sides), and at 390×844 at x = 18px. The hero still spans the full width of the screen. Nothing is wider than the screen at 390px.
- **AC2.** The rule that removes the container of `.site-main` while the hero flies (`html.hero-flight .site-main { max-width: none; padding: 0 }` in `site.css`) no longer applies to the chapters. The hero keeps its full-bleed frame by its own rules.
- **AC3.** No template comment shows as page text: the response of `/` contains neither `{#` nor `#}`. Every `{# #}` comment in `src/` templates fits on one line, or is a `{% comment %}` block.
- **AC4.** The `h2` of House, Hòa Xuân and Rent read "The house", "Hòa Xuân" and "The rent" as text, with the accent word in `<span class="accent">` (house, Xuân, rent), drawn like the accent of "Will you stay?".
- **AC5.** The rent price line (`p.rent__line.big`) is set in Be Vietnam Pro 300 at 84px on desktop and 44px at 760px or less. When the price line ends with "a month", those two words are wrapped in `<span class="accent">` and drawn in Cormorant italic. The text of the line is unchanged ("From 13–14 million VND a month", or "Ask me about the rent").
- **AC6.** Each row of the Hòa Xuân travel list is a plain `<li>` with the place on the left and the time on the right as a label (11px capitals, 0.22em spacing, Stone). The separator " · " stays in the markup but is not shown (`aria-hidden="true"` and hidden by CSS), so the text of each row stays "Supermarket · across the road" and so on.
- **AC7.** The Contact band ends where the Ink footer starts: no Paper gap between them at 1440px and at 390px.

### The "Ở" plays by itself (T2)

- **AC8.** With JavaScript, at the top of the page and without `prefers-reduced-motion: reduce`, the hero plays the intro of design.md once on load, in about 4 s: rest (0–0.4 s), the letter grows until the loop fills the screen (0.4–3.2 s), then the shade, the Paper header row and the heading rise in (3.2–4.0 s). The growth uses the epic 1 curve (scale up to about 70 times, progress to the power 2.4) driven by time, not by scroll.
- **AC9.** The hero is one screen high (`100svh`) during and after the intro; there is no 330vh stage and no sticky frame. After the intro the loop keeps playing full screen behind "Living with nature" and its line, and the cue "Scroll, and come in ↓" shows. The loop pauses when the hero leaves the screen and plays again when it comes back.
- **AC10.** A wheel, touch, key or pointer press during the intro jumps to the end state at once. The page never blocks scrolling. A page loaded below the top or at a chapter address (`/#rent`) shows the end state at once.
- **AC11.** The intro plays on every load of `/` (no storage of any kind is used).
- **AC12.** Under `prefers-reduced-motion: reduce`, without JavaScript, or with no hero files, the hero is the still hero of epic 1, unchanged (letter filled with the poster or Sand, the dictionary line, the heading and its line in the page flow, no video plays).
- **AC13.** The heading "Living with nature" and its line rise line by line at the end of the intro: each line moves 30px up from hidden, 0.15 s after the one before.
- **AC14.** The "Illustrative video" chip sits at the top right of the hero, 24px from the top and the right, in every state.
- **AC15.** `hero.js` stays one small plain script (under 12 000 bytes, no library, deferred).

### Load and reveal motion (T3)

- **AC16.** A small plain script `src/static/js/reveal.js` (deferred, no library, under 6 000 bytes) and a stylesheet `src/static/css/motion.css`, both linked from `base.html`, add the motion of design.md only when JavaScript runs and the visitor has not asked for less motion. The script sets a class on `<html>`; every hiding rule in `motion.css` needs that class.
- **AC17.** The header fades in and moves 12px down into place in 0.9 s, after 0.2 s.
- **AC18.** In each chapter, the marker, the chapter word, the `h2`, and each paragraph, list, media slot and the floor plan start 42px lower and hidden, and fade and rise into place in 1.1 s with `cubic-bezier(.2,.7,.2,1)` when 12% of the block is on screen (IntersectionObserver), then stay. Blocks with the same parent start 0.12 s apart, at most 5 steps.
- **AC19.** Photos (`img` in media slots) zoom slowly from scale 1.02 to 1.09 over 22 s, back and forth, clipped by their slot. The Sand empty slot does not move.
- **AC20.** Without JavaScript or under `prefers-reduced-motion: reduce`, every block shows at once, with no transform and no animation.
- **AC21.** The menu jump to a chapter (`/#faq`) lands on the chapter with its blocks shown (blocks already on screen at load are shown at once).

### All tasks

- **AC22.** `/` still makes exactly one query; every other address none.
- **AC23.** The browser check of each task captures `/` at 1440×900 and 390×844 in the states its issue names.

## Edge cases

- Empty: no hero files → still Sand letter, no intro (AC12). A missing photo → Sand slot, no zoom (AC19).
- Large data: none; the page has a fixed set of chapters.
- Permissions: public page; no new data, no storage, no cookies.
- Slow network: the intro starts when the page loads, with the poster in the letter until the loop can play (as epic 1).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 How does the "Ở" play? | Once on load, about 4 s, ending on the full-screen loop and the heading | Loop forever (grow and shrink) | Reads like a short film, then the visitor can read at once; matches the approved tour video |
| Q2 When does it replay? | Every load of `/`, any input skips it | Only the first load of a session | Short and skippable; no storage needed |
| Q3 Load motion | All of the tour video: header fade, heading line by line, blocks rise on scroll, slow photo zoom | Only the hero intro | Matches the design E tour the owner approved; inspired by loiseau.framer.website, not copied |
| Lane | Full lane, one epic of three tasks | Fast lane | Several tasks, users see it, new motion code |

## Design

`docs/specs/design-match/design.md`

## Open questions
