# Design: match the build to the design ("Through the Ở" one page)

Approved prototype (owner, 2026-11-12): https://claude.ai/artifact/KGHzvGFPmKt8jEd95cxnEG. Its source is `docs/specs/design-match/prototype.html`, with media paths pointing to `src/static/media/`. It is the reference for look, sizes and motion. It comes from the design E tour video (`epic-1-site-shell/tour/mau-5-qua-chu-o.mp4` in the project files). Where the prototype and this file differ, this file wins. The review-only button "Xem lại intro" is not built.

It replaces the layout of the epic 3 card (`docs/specs/one-page/design.md`). The tokens, fonts, time-of-day themes, chips, buttons, chapter order, ids and texts of epic 3 stay, except where this file says otherwise. Audit of `main` at e23078b: `design-audit/gap-list.md` in the project files.

## Frame

- Container: at most 1360px, centred, sides 40px (18px at 760px or less). Every chapter's content sits in it. The hero, the Hòa Xuân band and the Contact band run full width, and their text sits in the container.
- Chapter gap 136px (88px on phones).
- Chapter head, the same in all five chapters:
  - label: hook + number + a short English gloss, 11px capitals at 0.22em, Stone. The texts are "̉ 01 · at home", "̉ 02 · close by", "̉ 03 · to stay a long while", "̉ 04 · questions" and "̉ 05";
  - chapter word: Cormorant italic 300, 200px (96px on phones), line height 0.8 (FAQ has none);
  - `h2`: Be Vietnam Pro 300 capitals, 64px (40px on phones), letter spacing -0.03em, with the accent word in Cormorant italic: The *house*, Hòa *Xuân*, The *rent*, Will you *stay?*. FAQ's `h2` is "FAQ" at 150px (60px on phones).
- No Paper gap between the Contact band and the Ink footer.

## Header

- Fixed to the top over the hero, 64px row, transparent. Its text turns Paper once the loop covers the screen.
- Once the hero has left the screen, it becomes a solid bar: Paper at 94%, 1px Line border below, Ink text.
- Desktop: logo "Ở", the clock line, then The house · Hòa Xuân · Rent · FAQ · Contact (Contact underlined). Phones: logo and the "Menu" pill (details, no script).
- Under reduced motion or without the script: the solid bar from the start.

## Hero: the "Ở" intro (plays by itself)

The hero is one screen high (100svh, at least 560px). With JavaScript, and when the visitor has not asked for less motion:

| Time | What happens |
|---|---|
| 0 – 0.4 s | The letter Ở at rest, filled with the theme's loop (poster until the video plays). The dictionary line shows bottom left. The header fades in. |
| 0.4 – 3.2 s | The letter grows around the thick left stroke of its bowl with an ease-in-out curve (scale up to about 70 times, progress to the power 2.4), until the loop fills the screen. The dictionary line fades out in the first sixth. |
| 3.2 – 4.0 s | The shade fades in, and the heading rises line by line: "LIVING" on the left, "*with* NATURE" on the right, Be Vietnam Pro 300 capitals at 150px (60px on phones). Each line moves up from hidden, 0.15 s after the one before. Under them is the line "A garden house in Hòa Xuân, Đà Nẵng. Two bedrooms, two gardens, *rented whole, by the month.*" in Cormorant at 26px (20px on phones). |
| after | The loop keeps playing behind the heading. The cue "Scroll, and come in ↓" shows bottom right, in Paper. |

- The intro plays on every load of `/`, and only at the top of the page. A page opened lower or at a chapter address shows the end state at once.
- Any wheel, touch, key, pointer press or scroll during the intro jumps to the end state. The page is never locked.
- The loop pauses while the hero is off screen.
- Under `prefers-reduced-motion: reduce`, without JavaScript, or with no hero files, the still hero shows: the letter filled with the poster (or Sand), the dictionary line, then the heading and its line in Ink, in the page flow.
- The "Illustrative video" chip sits top right, under the header (84px from the top, 16px from the right).

## 01 ở nhà (#house)

- Head in columns 1–7. In columns 8–12, aligned to the bottom: the owner line in Cormorant 28px, "{greeting} I built a small garden house in Hòa Xuân, and I'd love for someone to make it *home for a while.*", then the "Why Ở" paragraph in Stone.
- Room collage on a 12-column grid with 18px gaps, 72px below. Each photo has its label under it (11px capitals):
  - bedroom: columns 1–5, 620px high, "Bedrooms · two";
  - lightwell: columns 6–9, 460px, 160px lower, "Light well";
  - veranda: columns 10–12, 340px, 60px lower, "Veranda";
  - kitchen: columns 2–6, 380px, "Living & kitchen";
  - garden-evening: columns 8–12, 460px, 120px higher, "Back garden".
- Facts row, 96px below: a 1px Ink rule, then four columns, each a Cormorant number at 80px (56px on phones) over a label: 2 "bedrooms", 2 "gardens", 1 "light well", 1 "household at a time". On phones it has two columns.
- 96px below: "The layout" list and "Included" (columns 1–5), and the floor plan of epic 3, unchanged (columns 7–12).
- The three numbered points, the separate veranda photo and the mezzanine photo leave this chapter.
- Phones: one column. The collage becomes a row of 240px-wide cards, each 320px high, that scrolls sideways in its own box with snap.

## 02 ở gần (#hoa-xuan)

- A full-width band, 100vh high and at least 680px, starting 136px below the house chapter. The area loop covers it, under a veil (Ink at 55% at the top, 15% at 40%, 72% at the bottom). Text is Paper. Only the poster shows under reduced motion, and the loop plays only while the band is on screen.
- Top of the band, 72px in: the head (label, word, `h2` 44px below the word).
- Bottom of the band, 56px from the edge: the line "Everything you need day to day is close by." in Cormorant 28px, then four columns, each with a Paper rule at 60% and 14px above it, the place as a label and the time in Cormorant italic 32px (24px on phones): Supermarket · across the road, Market · about 10 min, Beach · about 10 min, Airport · about 15 min. On phones there are two columns.
- The "Illustrative video" chip is bottom right, with the credit kept in the page.
- Under the band, 48px below, in the container: the market, street and beach-sunset photos (4 / 3, columns of 4), then the "Hòa Xuân on Google Maps ↗" outline button.

## 03 ở lâu (#rent)

- Columns 1–6: the head, then the price line in Be Vietnam Pro 300 capitals at 84px (44px on phones), line height 0.95, with "million" and "a month" in Cormorant italic, 56px below the `h2`. "Ask me about the rent" when there is no price. Then the contact buttons, 36px below, and the terms list of epic 3, 48px below.
- Columns 8–12: the tea photo, 560px high (4 / 5 on phones), then the quote in Cormorant 24px: "I wanted a house that feels good to live in every day, *not just in photos.*" followed by "— {first name}" as a Stone label.

## 04 FAQ (#faq)

The head (label "̉ 04 · questions", `h2` "FAQ"), then the eight questions of epic 3, unchanged, in a column at most 880px wide.

## 05 ở lại? (#contact)

An Ink band, 128px top and 112px bottom. The label, the word, then one row that wraps: on the left the `h2` "Will you *stay?*" and the line "{greeting} *{reply_line}*" in Cormorant 30px, and on the right the contact buttons (Call filled Paper, the others outline). The empty state of epic 3 stays.

## Load and reveal motion

Only with JavaScript and when the visitor has not asked for less motion:

- Header: fades in and moves 12px down into place, 0.9 s, after 0.2 s.
- Chapter blocks (label, word, `h2`, each text, list, photo, facts row, floor plan, FAQ list): hidden 42px lower until 12% of the block is on screen, then fade and rise into place in 1.1 s with `cubic-bezier(.2,.7,.2,1)`. Siblings start 0.12 s apart, at most 5 steps. Blocks already on screen at load show at once.
- Photos in media slots: a slow zoom from 1.02 to 1.09 over 22 s, back and forth, inside their frame. A Sand empty slot does not move.
- Without JavaScript, or under reduced motion, everything shows at once.

## States

- **Normal:** as above, in each of the four time-of-day themes (the bands keep Paper text).
- **Empty:** no hero files gives the still Sand letter; a missing photo gives the Sand slot with Ở and its label; no price gives "Ask me about the rent"; no channel gives no buttons, no bar and "Contact details are on their way." (epic 3).
- **Error:** unchanged (404 page of epic 1).
- **Narrow (390px):** one column, the collage scrolls sideways in its box, nothing is wider than the screen, and the phone contact bar shows after the hero and hides over Contact (epic 3).
