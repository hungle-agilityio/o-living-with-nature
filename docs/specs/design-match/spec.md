# Spec: match the build to the design (epic)

## Summary

The home page `/` is rebuilt on the approved prototype of design E "Through the Ở" (https://claude.ai/artifact/KGHzvGFPmKt8jEd95cxnEG, source `docs/specs/design-match/prototype.html`). The chapters, ids, texts and data of epic 3 stay. What changes is the layout and the motion:

- the chapters get back their container and side padding;
- the chapter heads get one shared pattern;
- the header becomes a solid bar after the hero;
- the "Ở" plays by itself on load and ends on the full-screen loop with the heading;
- the house chapter gets the room collage and the facts row;
- Hòa Xuân becomes a full-width video band;
- the rent chapter gets the caps price line and the tea photo with the owner's quote;
- the contact band becomes one row;
- the page opens and reveals its blocks with the motion of the tour video.

Design, sizes, texts and timings: `docs/specs/design-match/design.md`. Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change".

## Acceptance criteria

### Frame and chapter heads (T1)

- **AC1.** With JavaScript on and off, at 1440×900 the content of every chapter starts at x = 80px (the 1360px container with 40px sides), and at 390×844 at x = 18px. The hero, the Hòa Xuân band and the Contact band span the full width. Nothing is wider than the screen at 390px.
- **AC2.** The rule `html.hero-flight .site-main { max-width: none; padding: 0 }` is gone. The full-width parts get their width from their own rules.
- **AC3.** The response of `/` contains neither `{#` nor `#}`. Every `{# #}` comment in `src/` templates fits on one line, or is a `{% comment %}` block.
- **AC4.** Each chapter opens with the head of design.md, "Frame". The label reads "̉ 01 · at home", "̉ 02 · close by", "̉ 03 · to stay a long while", "̉ 04 · questions" or "̉ 05". Then come the chapter word (none for FAQ) and the `h2`. The `h2` text stays "The house", "Hòa Xuân", "The rent", "FAQ", "Will you stay?", with the accent word (house, Xuân, rent, stay?) in `<span class="accent">`, drawn in Cormorant italic.
- **AC5.** No Paper gap between the Contact band and the Ink footer, at 1440px and at 390px.

### Hero intro and header (T2)

- **AC6.** With JavaScript, at the top of the page and without `prefers-reduced-motion: reduce`, the hero plays the intro of design.md once on load, in about 4 s. It grows the letter with the epic 1 curve (scale up to about 70 times, progress to the power 2.4), driven by time with an ease-in-out, not by scroll.
- **AC7.** The hero is one screen high (`100svh`, at least 560px). There is no 330vh stage and no sticky frame. After the intro, the loop keeps playing behind the two-line heading ("Living" left, "with nature" right, 150px / 60px), its line, and the cue "Scroll, and come in ↓". The loop pauses while the hero is off screen.
- **AC8.** A wheel, touch, key, pointer press or scroll during the intro jumps to the end state. The page never blocks scrolling. A page loaded below the top or at a chapter address shows the end state at once. The intro plays on every load, with no storage of any kind.
- **AC9.** Under `prefers-reduced-motion: reduce`, without JavaScript, or with no hero files, the still hero of design.md shows. No video plays, and the `h1` and its line are in the page in every case.
- **AC10.** The header is fixed. Over the hero it is transparent, and its text turns Paper once the loop covers the screen. Once the hero has left the screen, it is a solid bar (Paper at 94%, Line border, Ink text). It is the solid bar from the start without the script or under reduced motion. The phone "Menu" of epic 1 still works without a script.
- **AC11.** The "Illustrative video" chip sits at the top right of the hero, under the header, in every state.
- **AC12.** `hero.js` stays one small plain script (under 12 000 bytes, no library, deferred).

### Load and reveal motion (T3)

- **AC13.** A small plain script `src/static/js/reveal.js` (deferred, no library, under 6 000 bytes) and `src/static/css/motion.css`, both linked from `base.html`, add the motion only when JavaScript runs and the visitor has not asked for less motion. The script sets a class on `<html>`, and every hiding rule in `motion.css` needs that class.
- **AC14.** The header fades in and moves 12px down into place in 0.9 s, after 0.2 s.
- **AC15.** Every element with the class `reveal` starts 42px lower and hidden. When 12% of it is on screen (IntersectionObserver), it fades and rises into place in 1.1 s with `cubic-bezier(.2,.7,.2,1)`, then stays. Siblings start 0.12 s apart, at most 5 steps. Elements on screen at load show at once, so the menu jump to `/#faq` lands on a visible chapter.
- **AC16.** Photos in media slots zoom slowly from scale 1.02 to 1.09 over 22 s, back and forth, clipped by their slot. The Sand empty slot does not move.
- **AC17.** Without JavaScript or under reduced motion, every element shows at once, with no transform and no animation.

### The house (T4)

- **AC18.** The house chapter shows, in this order:
  - the head;
  - the owner line, with "home for a while." in the accent, and the "Why Ở" paragraph;
  - the room collage of design.md: bedroom, lightwell, veranda, kitchen and garden-evening, through the `photo` tag, with their labels and the given columns, heights and offsets;
  - the facts row 2 "bedrooms", 2 "gardens", 1 "light well", 1 "household at a time";
  - "The layout", "Included" and the floor plan of epic 3, unchanged.
- **AC19.** The three numbered points, the separate veranda slot and the mezzanine photo are no longer in the chapter.
- **AC20.** At 760px or less, the collage is a row of 240px-wide, 320px-high cards that scrolls sideways inside its own box (scroll snap), and the facts row has two columns.
- **AC21.** Every element of the chapter named in design.md "Load and reveal motion" carries the class `reveal`.

### Hòa Xuân band (T5)

- **AC22.** `#hoa-xuan` is a full-width band, 100vh high and at least 680px. The area loop of epic 2 covers it, under the veil of design.md. It keeps the "Illustrative video" chip and the credit, and shows only the poster under reduced motion. The loop plays only while the band is on screen.
- **AC23.** The head sits at the top of the band. At the bottom are the line "Everything you need day to day is close by." and the four travel facts as columns (place as a label, time in Cormorant italic), with two columns at 760px or less. The text of each travel row stays "Supermarket · across the road" and so on: the " · " stays in the markup, hidden from view.
- **AC24.** Under the band, in the container, come the market, street and beach-sunset photos (4 / 3), then the Google Maps button of epic 3, unchanged.
- **AC25.** Every element of the chapter named in design.md "Load and reveal motion" carries the class `reveal`.

### Rent, FAQ and contact (T6)

- **AC26.** The rent chapter shows the head. Then the price line in Be Vietnam Pro 300 capitals at 84px (44px at 760px or less), with "million" and "a month" wrapped in `<span class="accent">`. The text stays as written ("From 13–14 million VND a month", or "Ask me about the rent"). Then the contact buttons and the terms list of epic 3, in columns 1–6.
- **AC27.** In columns 8–12, the rent chapter shows the tea photo (560px high, 4 / 5 at 760px or less), then the quote "I wanted a house that feels good to live in every day, not just in photos." with "not just in photos." in the accent, followed by "— {first name}". `owner_content.services.site_settings()` gains a `first_name` field, the owner's first name of the site settings.
- **AC28.** The FAQ keeps its eight questions as they are, in a column at most 880px wide, under its head.
- **AC29.** The contact band is one row that wraps: the `h2` and the line "{greeting} {reply_line}" on the left, the buttons on the right. The empty state of epic 3 stays ("Contact details are on their way.", no buttons, no bar).
- **AC30.** Every element of the three chapters named in design.md "Load and reveal motion" carries the class `reveal`.

### All tasks

- **AC31.** `/` still makes exactly one query, and every other address none.
- **AC32.** Each task's browser check captures `/` at 1440×900 and 390×844 in the states its issue names. Nothing is wider than the screen at 390px.

## Edge cases

- Empty: no hero files means no intro, only the still Sand letter. A missing photo gives the Sand slot with Ở and its label. No price gives "Ask me about the rent". No channel gives no buttons and no bar.
- Large data: none; the page has a fixed set of chapters.
- Permissions: public page; no new data, no storage, no cookies.
- Slow network: the intro starts on load with the poster in the letter until the loop can play.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 How does the "Ở" play? | Once on load, about 4 s, ending on the full-screen loop and the heading | Loop forever (grow and shrink) | Reads like a short film, and the visitor can read at once |
| Q2 When does it replay? | Every load of `/`, any input skips it | Only the first load of a session | Short and skippable; no storage |
| Q3 Load motion | All of the tour video: header fade, heading line by line, blocks rise on scroll, slow photo zoom | Only the hero intro | Matches design E; inspired by loiseau.framer.website, not copied |
| Q4 Which layout? | The "Through the Ở" prototype, built from the design E video (owner approved it 2026-11-12) | The epic 3 card layout | The owner wants the site to look like the video |
| Content the prototype changes | Facts row (2 · 2 · 1 · 1, "household at a time") instead of the three numbered points; garden-evening instead of mezzanine; quote under the tea photo | Keep the epic 3 house content | Shown in the approved prototype and the approved design E |
| Lane | Full lane, one epic of six tasks | Fast lane | Many files, users see it, new motion code |

## Design

`docs/specs/design-match/design.md`, prototype `docs/specs/design-match/prototype.html`.

## Open questions
