# Design: site shell and look (epic 1)

Design canvas (owner approved the direction on 2026-11-11): https://claude.ai/artifact/6VKS19imzGdUfsABh44J7S

The canvas is private to the owner; the build reads the values below, which are the contract.

| Board | What it shows | Used by |
|---|---|---|
| 2b · Home — editorial v2 | The approved look: uppercase light sans headlines mixed with italic serif words, wide air, photo-led layout | T1 (type, spacing, header, footer); epic 3 (home sections) |
| Concept A · The site follows the day | The four time-of-day themes | T2 |
| Concept B · Walk through the floor plan | Plan as navigation on The house | epic 3 |
| 4 · States | 404 page, empty photo, menu open on a phone | T1, T4 |
| Media map | Every photo and video place, ratio and content | T1 (media slot), epics 2–3 |
| 1 · Style | First palette and type sheet (base values below) | T1 |

## Tokens

### Fonts (Google Fonts, both with Vietnamese glyphs)

- Display and headings: **Be Vietnam Pro 300**, uppercase, letter-spacing −0.02em, line-height 0.92.
- Accent words inside headings, quotes, captions: **Cormorant Garamond** italic 300/400, normal case, letter-spacing 0.
- Body: **Be Vietnam Pro 400**, 16px, line-height 1.7.
- Labels and navigation: Be Vietnam Pro 400–500, 11px, uppercase, letter-spacing 0.2em.
- Load with one `link` to `fonts.googleapis.com/css2` with `display=swap`, preceded by `preconnect` to `fonts.googleapis.com` and `fonts.gstatic.com`.

### Type scale

| Name | Desktop | Phone (≤ 760px) |
|---|---|---|
| hero | 178px | 64px |
| big | 120px | 52px |
| mid | 76px | 40px |
| quote | 40px | 28px |
| body | 16px | 16px |
| label | 11px | 11px |

### Colour themes (time of day, Đà Nẵng time)

| Theme | Hours | Ground | Ink | Muted | Contrast ink / muted |
|---|---|---|---|---|---|
| dawn | 05:00–07:59 | #EFE3D6 | #2B2620 | #5E5348 | 11.9 / 5.9 |
| day | 08:00–16:59 | #F4F0E8 | #1F2A22 | #5C6358 | 13.1 / 5.5 |
| dusk | 17:00–18:59 | #E4BE97 | #2A1E16 | #4E3A2C | 9.4 / 6.2 |
| night | 19:00–04:59 | #151D18 | #E9E2D3 | #B9B2A2 | 13.3 / 8.2 |

Fixed in every theme: Line #D9D2C3 (on night: rgba(233,226,211,.18)), Sand band #E9E2D3 on day, the footer and price band in Ink #1F2A22 with Paper #F4F0E8 text. The colours change with a 0.9s ease transition, none when the visitor prefers reduced motion.

### Shape and space

- Spacing steps 8, 16, 24, 32, 48, 64, 120 px; sections 112–128px apart on desktop, 72px on phones. Content max width 1360px, side padding 40px (18px on phones).
- Photos and videos: square corners. Buttons and labels: fully round (999px), at least 48px tall.
- Primary button: Ink fill, ground-colour text. Secondary: 1px Ink outline.

## Components

- **Header:** top strip "Hòa Xuân · Đà Nẵng — a whole garden house, by the month" (label, ink on ground reversed); then left nav "The house · Hòa Xuân", centre wordmark "Ở" (Cormorant Garamond 500, 40px, links home), right nav "FAQ · Contact". On phones: wordmark left, a "Menu" button right that opens the four links as a list (HTML `details`, no script).
- **Footer:** "Hòa Xuân, Đà Nẵng", the four links, a big line "Ở *living with* nature", the line `Photos marked "Illustrative" are stock photos standing in until the house is finished.`, and the time-of-day preview line "See Ở at dawn · day · dusk · night" (T2).
- **Media slot** (`includes/media.html`): a fixed ratio box (`aspect-ratio`) that holds a photo or a muted looping video.
  - Photo: `img` with `alt`, `loading="lazy"` except the first on a page, `width`/`height` set.
  - Video: `video muted loop playsinline autoplay preload="metadata" poster=…`; with `prefers-reduced-motion: reduce` the poster photo shows instead.
  - Illustrative flag on: the chip "Illustrative photo" bottom-left (10px label, Paper text on rgba(31,42,34,.78), round) and a caption under it with the credit.
  - Empty (no file yet): a Sand #E9E2D3 block of the same ratio with a centred "Ở" in Cormorant Garamond, colour #B8AE98; no chip, no caption, no broken image.
- **404 page:** see States board: label "404", heading "This path leads nowhere — the garden is this way.", line "The page you were looking for isn't here. It may have moved, or the link has a typo.", buttons "Back to the home page" (primary) and "Contact Bún" (secondary, to /contact/).

## States

- Normal: Home v2 board.
- Empty: media slot empty state above; a page with no content yet shows only its heading.
- Error: 404 page.
- Narrow screen: phone sizes in the type scale, menu as a list, grids become one column, buttons full width.
