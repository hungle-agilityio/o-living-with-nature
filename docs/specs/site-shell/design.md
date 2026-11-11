# Design: site shell and look (epic 1)

Chosen by the owner on 2026-11-11: design E, "Through the Ở", after five tour videos were compared. The tour video and the design source are kept with the owner, outside this public repository; the values below are the contract.

## The idea

The name is the door. The home page opens on one giant letter "Ở" on a paper ground, and the letter is a window: inside it plays a short garden loop for the real time of day in Hòa Xuân. Under the letter, a dictionary line teaches the word to a foreign visitor:

> *ở* · verb · Vietnamese · say "uh?"
> 1. to stay. 2. to live somewhere. 3. *to be at home.*

Scrolling flies the camera through the letter, as if stepping through a door, until the loop fills the screen and "LIVING *with* NATURE" rises over it. The rest of the site is named after phrases with ở: *ở nhà* (at home, the house), *ở gần* (close by, Hòa Xuân), *ở lâu* (to stay a long while, the rent), *ở lại?* (will you stay?, contact). Epic 1 builds the hero and the shared look; the chapters are epic 3.

## Tokens

### Fonts (Google Fonts, both with Vietnamese glyphs)

- The letter, chapter words, accent words, quotes: **Cormorant Garamond** 300 (italic for chapter words and accents), 500 for the hero letter and the wordmark.
- Headlines: **Be Vietnam Pro 300**, uppercase, letter-spacing −0.03em, line-height 0.9, with accent words in Cormorant italic, normal case ("LIVING *with* NATURE").
- Body: **Be Vietnam Pro 400**, 16px, line-height 1.7.
- Labels and navigation: Be Vietnam Pro 400, 11px, uppercase, letter-spacing 0.22em.
- Load with one `link` to `fonts.googleapis.com/css2` with `display=swap`, preceded by `preconnect` to `fonts.googleapis.com` and `fonts.gstatic.com`.

### Type scale

| Name | Desktop | Phone (at most 760px) |
|---|---|---|
| hero letter | 70% of the screen height, at most 105% of its width | same rule |
| headline (h1 over the video) | 150px | 60px |
| chapter word ("ở nhà") | 200px italic | 96px italic |
| big (price line) | 84px | 44px |
| gloss (dictionary line) | 26px | 22px |
| quote | 24–30px | 22px |
| body | 16px | 16px |
| label | 11px | 11px |

### Colour themes (time of day, Đà Nẵng time)

| Theme | Hours | Ground | Ink | Muted | Contrast ink / muted | Loop inside the Ở |
|---|---|---|---|---|---|---|
| dawn | 05:00–07:59 | #EFE3D6 | #2B2620 | #5E5348 | 11.9 / 5.9 | first sun through leaves |
| day | 08:00–16:59 | #F4F0E8 | #1F2A22 | #5C6358 | 13.1 / 5.5 | morning light in the leaves |
| dusk | 17:00–18:59 | #E4BE97 | #2A1E16 | #4E3A2C | 9.4 / 6.2 | waves at sunset |
| night | 19:00–04:59 | #151D18 | #E9E2D3 | #B9B2A2 | 13.3 / 8.2 | a lit house in the dark |

Fixed in every theme: Line #D9D2C3 (on night: rgba(233,226,211,.18)); the contact band and the footer in Ink #1F2A22 with Paper #F4F0E8 text. Colours change with a 0.9s ease transition, none when the visitor prefers reduced motion.

### Shape and space

- Spacing steps 8, 16, 24, 32, 48, 64, 136 px; sections 120–136px apart on desktop, 72px on phones. Content max width 1360px, side padding 40px (18px on phones).
- Photos and videos: square corners. Buttons and labels: fully round (999px), at least 48px tall, uppercase 13px labels with 0.16em spacing.
- Primary button: Paper fill on Ink bands, Ink fill on paper. Secondary: 1px outline.
- Chapter marker: the hook of the letter ở (combining hook above, U+0309) in Cormorant 28px, then the number, for example "̉ 01".

## Components

- **Home hero "Through the Ở"** (T5):
  - A stage about 3.3 screens tall whose inner frame stays fixed (`position: sticky`) for one screen.
  - At the top of the scroll: the paper ground, the letter "Ở" centred and filled with the theme's loop (a `canvas` draws the playing `video` through the letter shape), the header row above it, and at the bottom the dictionary line (left) and "Scroll, and come in ↓" (right).
  - While scrolling through the stage: the letter grows around the inside of its bowl (scale rises with scroll progress to the power 2.4, up to about 70 times) and moves to the centre until the loop fills the screen. The dictionary line fades out in the first sixth of the scroll; the header row turns Paper once the loop covers most of the screen.
  - In the last fifth: a dark gradient fades in, and the `h1` "LIVING *with* NATURE" plus the line "A garden house in Hòa Xuân, Đà Nẵng. Two bedrooms, two gardens, *rented whole, by the month.*" rise 30px into place over the loop.
  - The chip "Illustrative video" bottom-right.
  - Without JavaScript, or with `prefers-reduced-motion: reduce`: no stage and no flight. The letter "Ở" is filled with the theme's poster photo (CSS `background-clip: text`), the dictionary line sits under it, and the `h1` with its line follows below on the paper ground. Nothing moves and nothing is hidden.
  - With no loop file: the letter is filled with Sand #E9E2D3 and no chip shows.
- **Header** (every page): one label row. Left: the wordmark "Ở" (Cormorant 500, 22px, links home) and "It's HH:MM in Hòa Xuân · Theme". Right: "The house · Hòa Xuân · FAQ · Contact", Contact underlined. On the home hero the row sits over the letter and turns Paper over the video. On phones: wordmark and time on the left, a "Menu" button on the right that opens the four links as a list (HTML `details`, no script).
- **Footer** (every page, Ink band): "Ở  a word for staying · Hòa Xuân, Đà Nẵng", the time-of-day preview line "See Ở at dawn · day · dusk · night" (T2), and the line `Photos and videos marked "Illustrative" are stand-ins until the house is finished.`
- **Media slot** (`includes/media.html`): a fixed ratio box (`aspect-ratio`) that holds a photo or a muted looping video.
  - Photo: `img` with `alt`, `loading="lazy"` except the first on a page, `width` and `height` set.
  - Video: `video muted loop playsinline autoplay preload="metadata" poster=…`; with `prefers-reduced-motion: reduce` the poster photo shows instead.
  - Illustrative flag on: the chip "Illustrative" bottom-left (10px label, Paper text on rgba(20,26,22,.72), round) and a caption under it with the credit.
  - Empty (no file yet): a Sand #E9E2D3 block of the same ratio with a centred "Ở" in Cormorant Garamond, colour #B8AE98; no chip, no caption, no broken image.
- **Inner page heading** (The house, Hòa Xuân, FAQ, Contact in epic 1): the chapter marker, then the chapter word in Cormorant italic ("ở nhà", "ở gần", none for FAQ, "ở lại?"), then the English `h1`.
- **404 page:** label "404", heading "This path leads nowhere — the garden is this way.", line "The page you were looking for isn't here. It may have moved, or the link has a typo.", buttons "Back to the home page" (primary) and "Contact Bún" (secondary, to /contact/).

## Media used in epic 1

The four hero loops (10 s, muted, 1280x720, mp4 H.264 plus WebM, each at most 2.6 MB) and a poster photo for each (the loop's first frame, JPEG, 1280x720), from Pexels (Pexels License, free for commercial use), labelled "Illustrative video". Sources: `docs/specs/site-shell/media-credits.md`. They live in `src/static/media/hero/` as `dawn`, `day`, `dusk` and `night` (`.mp4`, `.webm`, `.jpg`), added by hand before T5 starts, and are replaced by the owner's own clips in epic 2.

## States

- Normal: the hero as above; inner pages show their heading.
- Empty: the media slot empty state; the hero letter in Sand when a loop is missing.
- Error: the 404 page.
- No JavaScript or reduced motion: the still hero described above.
- Narrow screen: phone sizes in the type scale, menu as a list, grids become one column, buttons full width.
