# Spec: mobile-smoothness

## Summary

Four phone fixes on the home page `/` and `/vi/`, all at 760 px wide or less unless said otherwise:

1. The five room photos of chapter 01 ("ở nhà") become a swipe carousel: one card of 84% of the row width at a time, snapping to the centre, with a page count "1 / 5" and five dots under it. Inside the carousel the cards no longer rise and the photos no longer zoom.
2. The phone contact bar (Call, WhatsApp, Zalo) hides while any other set of contact buttons is on screen (rent chapter, FAQ, contact chapter) or the hero is, and it no longer flashes over the hero before its script runs.
3. The header clock is one short line on phones ("14:52 · Day", "14:52 · Ban ngày") and the wordmark Ở is centred in the 64 px header row.
4. Motion only where it is seen: photos zoom only while near the screen, the hero stops drawing frames once its intro is over and it is off screen, and the language switch measures at most once per frame while scrolling.

Desktop (more than 760 px) looks and behaves as on `main`. The owner pages do not change. No database query is added.

## User story

As a visitor on a phone, I want the photos, buttons and header to move smoothly and appear once, so that the site feels calm and I can look at the house and contact the owner without the page jerking.

## Acceptance criteria

Phone means a viewport 390 px wide and 844 px high unless said otherwise. The demo data is the seed of `docs/design/prototype.html` (owner Bún, Call, WhatsApp and Zalo set). The five room photos are, in order: Bedrooms · two, Light well, Veranda, Living & kitchen, Back garden.

### Photo carousel (T1)

- **AC1.** Given a phone and the home page `/` with the five room photos, when the visitor scrolls to chapter 01, then the photos are one sideways row: each card is 84% of the row wide, its photo box has the ratio 4 / 5, the row starts at the 18 px side and runs to the screen edges (the next card shows at the right), and under the row there is the line "1 / 5" on the left and five dots on the right with the first dot filled.
- **AC2.** Given the carousel at "1 / 5", when the visitor swipes left once, then the row comes to rest with the second card centred (`scroll-snap-align: center`, `scroll-snap-stop: always`), the line reads "2 / 5" and the second dot is filled; after four swipes it reads "5 / 5".
- **AC3.** Given the carousel at "1 / 5", when the visitor taps the third dot, then the row scrolls to the third card (smoothly, or at once when the visitor asked for less motion), the line reads "3 / 5" and the third dot is filled. Each dot is a `button` of at least 28 by 28 px with the label "Photo 3" (on `/vi/`: "Ảnh 3"); the filled dot has `aria-current="true"`, the others `aria-current="false"`; the count line has `aria-live="polite"`.
- **AC4.** Given a phone with motion allowed, when the carousel cards come on screen or are swiped, then no card moves up or fades (the `.reveal` rise does not apply inside `.house__collage`) and no photo inside the carousel zooms.
- **AC5.** Given a phone without JavaScript, when the visitor opens chapter 01, then the same row swipes and snaps, with no count line and no dots. Given a desktop 1280 px wide, the collage, its heights and shifts are as on `main` and no count line or dot shows.
- **AC6.** The carousel's script is the new file `src/static/js/house-carousel.js`, linked once with `defer` at the end of `src/pages/templates/pages/chapters/house.html` (so it comes right after `js/floor-plan.js` and before `js/area-band.js` in the page). It builds the pager (`div.house__pager` with `p.house__count` and `ul.house__dots`) right after `ul.house__collage`, reads the language from `document.documentElement.lang` ("vi" gives "Ảnh", anything else "Photo"), updates the count from a passive scroll listener at most once per animation frame, stores nothing, and is under 3,000 bytes with no library.

### Contact bar (T2)

- **AC7.** Given a phone and the home page with Call, WhatsApp and Zalo set, when the rent chapter's buttons (or the FAQ's buttons, or any part of the contact chapter, or the hero) are on screen, then the phone bar is moved out of view (`contact-bar--away`); when none of them is on screen (for example in the middle of the Hòa Xuân band), the bar shows.
- **AC8.** Given a phone with JavaScript, when the page first paints, then the bar is out of view until `js/contact-bar.js` has run and its first check is done (no flash over the hero). Given a phone without JavaScript, the bar always shows, as on `main`.
- **AC9.** `js/contact-bar.js` watches, with one IntersectionObserver, the hero (`getElementById("hero")`), the contact chapter (`getElementById("contact")`) and every `.contact-buttons` that is not inside the bar; it adds the class `contact-bar-ready` to `<html>` after its first callback (at once when IntersectionObserver is missing). `chapters/contact.css` hides the bar at 760 px or less while `<html>` lacks `contact-bar-ready`; `pages/home.html` has, in its styles block (the head), `<noscript><style>.contact-bar { transform: none !important; }</style></noscript>` inside the `{% if owner.channels %}` condition. The bar's own markup (`<nav class="contact-bar" aria-label="…">`) does not change. The script stays under 4,000 bytes.
- **AC10.** Given an owner settings record with no channel, when `/` opens, then there is no bar, no bar script and no noscript style, as on `main`.

### Header clock (T3)

- **AC11.** Given a phone at 14:52 in Đà Nẵng by day, when `/` opens, then the header shows on one line the wordmark Ở, "14:52 · Day", "EN · VI" and the Menu button, and the wordmark is centred vertically in the 64 px row; on `/vi/` the line reads "14:52 · Ban ngày". On a desktop 1280 px wide the header reads "It's 14:52 in Hòa Xuân · Day" as on `main`.
- **AC12.** `includes/header.html` keeps the span `site-header__time label` with its attributes and its text exactly as on `main`, and adds right after it a sibling `<span class="site-header__short label">14:52 · Day</span>` (clock, " · ", the daypart label of the page's language). In `site.css`, at 760 px or less, `.site-header__time` is `display: none`, `.site-header__short` shows with `white-space: nowrap`, and `.site-header__left` has `align-items: center`; above 760 px `.site-header__short` is `display: none`.
- **AC13.** Given the page open across a minute or a daypart change, when `js/daypart.js` updates the long line, then it also sets the short line to the same clock and label (for example "17:00 · Dusk"); a page with no daypart has neither span.

### Motion (T4)

- **AC14.** Given motion allowed, when a photo's box is more than 10% of the screen height above or below the screen, then its slow zoom is paused (`animation-play-state: paused`), and it runs while the box is within that margin (`.media__box.is-near`). `js/reveal.js` sets and removes `is-near` with one IntersectionObserver (`rootMargin: "10% 0px"`) only when it sets the class `motion`. The zoom keyframes and the line `animation: motion-zoom 22s ease-in-out infinite alternate` stay as on `main`.
- **AC15.** Given the intro has ended (or was skipped) and the hero is fully off screen, when the visitor keeps scrolling the chapters, then `js/hero.js` requests no animation frame and reads no layout; when the hero comes back on screen (an IntersectionObserver on `#hero`), the frame loop starts again and the loop video plays, as on `main`. The intro, its timings and the reduced-motion still hero are unchanged. `hero.js` stays under 14,000 bytes (comments may be shortened to make room).
- **AC16.** `js/lang-switch.js` runs its `update()` from the scroll listener at most once per animation frame (`requestAnimationFrame`), and still on `pointerdown`, `focus` and `click` of the link; it stays under 40 lines.

### All tasks

- **AC17.** `/` and `/vi/` still make exactly one database query each; the owner pages and the 404 page are unchanged.
- **AC18.** Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change" in its issue, changed only as listed there. `bash scripts/check.sh` passes.

## Edge cases

- Empty: a room photo whose file is missing renders the empty Sand slot (as on `main`) and still counts as a card ("n / 5"). With no channel there is no bar (AC10). With no daypart there is no clock line (AC13).
- Large data: always five room photos (the list is fixed in `pages/photos.py`); nothing grows with data.
- Narrow screens: 320 px wide phones get the same carousel (84% cards) and the one-line clock.
- Reduced motion: no zoom, no rise (as on `main`); dot taps jump without smooth scrolling; the contact bar has no transition (as on `main`).
- Permissions: public pages only; nothing for the owner changes.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Phone photo row | Swipe carousel, 84% cards, "n / 5" and dots | Page-flip book; vertical stack | Native scroll is the smoothest on phones; a 3D flip is heavy on weak phones (owner, card "OK tất cả đề xuất", 2026-11-17) |
| Q2 Duplicate Call/Zalo | Keep the bar, hide it while other buttons are on screen and until its script ran | Drop the rent/FAQ buttons on phones; drop the bar | Keeps every way to call while never showing two sets (owner, same card) |
| Q3 Header on phones | Short one-line clock "14:52 · Day" | Hide the clock on phones | Keeps the time-of-day idea without wrapping (owner, same card) |
| Q4 Photo zoom | Only near the screen, never inside the carousel | Off on phones; keep as is | Saves work off screen and keeps the swipe still (owner, same card) |
| Short clock markup | A sibling span `site-header__short` | Split the existing span into inner spans | The existing span, its text and its tests stay as they are |
| Bar before its script | `contact-bar-ready` on `<html>` + noscript style | A new class in the bar's markup | The bar's markup and its tests stay as they are; the page still works without JavaScript |
| Dot labels | From `document.documentElement.lang` in the script | New texts in `pages/texts` | Two words in two languages; no template or text-table change |
| Hero loop | Stop requesting frames off screen after the intro | Keep the loop running | The loop was drawing the full-screen video into the canvas every frame for nothing |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html` (Artifact https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j, version 11), approved with "Prototype ổn" on 2026-11-17 07:48 UTC. New states: `#house-phone-carousel`, `#house-phone-carousel-3`, `#vi-house-phone-carousel`, `#vi-house-phone-carousel-3`, `#hoa-xuan-phone-bar`, `#rent-phone-no-bar`, `#header-phone`. Changed: every phone state of the home page now shows the one-line clock and the bar rules (`#intro-phone`, `#house-phone`, `#rent-phone`, `#faq-phone`, `#contact-phone`).

## Open questions
