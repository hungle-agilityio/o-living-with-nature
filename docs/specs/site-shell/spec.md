# Spec: site shell and look (epic 1)

## Summary

Every page of the English site (at the root, phase 1) gets one shared look, design E "Through the Ở": the header, the footer, the editorial type, and colours that follow the time of day in Hòa Xuân. The home page opens on a giant letter "Ở" filled with a garden loop for the time of day, with a dictionary line that teaches the word; scrolling flies through the letter into the loop. The five page addresses exist (`/`, `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/`), each with its own title and description, but only a heading; epic 3 fills them. Every place for a photo or a video shows its empty state until epics 2 and 3 add files, except the four illustrative hero loops. The "page not found" page takes the new look. The search-engine groundwork (canonical address, Open Graph, `sitemap.xml`, `robots.txt`) is in place, and one switch keeps the whole site out of search results. Values and drawings: `docs/specs/site-shell/design.md`.

## Acceptance criteria

### Look and layout (T1)

- **AC1.** Every page is English: `html lang="en"`, and the settings say `LANGUAGE_CODE = "en"` with English as the only language.
- **AC2.** Every page has the header row from design.md: the wordmark "Ở" linking to `/`, the time line of AC10, and the links "The house" (`/house/`), "Hòa Xuân" (`/hoa-xuan/`), "FAQ" (`/faq/`) and "Contact" (`/contact/`). The link of the page being shown carries `aria-current="page"`.
- **AC3.** At 760px wide or less, the four links are inside a `details` element whose `summary` reads "Menu"; opening it shows the four links as a list. No JavaScript is used for it.
- **AC4.** Every page has the footer from design.md, including "Ở  a word for staying · Hòa Xuân, Đà Nẵng" and the line `Photos and videos marked "Illustrative" are stand-ins until the house is finished.`
- **AC5.** The stylesheet defines the fonts, type scale, colours, spacing and buttons of design.md as CSS custom properties (for example `--ink`, `--ground`, `--muted`), and the pages load Be Vietnam Pro and Cormorant Garamond from Google Fonts with `display=swap`.
- **AC6.** A reusable media slot (`src/templates/includes/media.html`) takes a ratio, an optional photo or video, alt text, an illustrative flag and a credit:
  - with a photo and the flag on, it shows the photo, the chip "Illustrative photo" and the credit as a caption;
  - with a video, it renders `video muted loop playsinline autoplay preload="metadata"` with the poster photo, and under `prefers-reduced-motion: reduce` only the poster shows;
  - with no file, it shows the empty state (Sand block, centred "Ở", same ratio, no chip, no caption, no `img`).
- **AC7.** No page scrolls sideways at 390px wide.

### Time of day (T2)

- **AC8.** A service returns the theme for a moment in Đà Nẵng time (Asia/Ho_Chi_Minh): `dawn` from 05:00 to 07:59, `day` from 08:00 to 16:59, `dusk` from 17:00 to 18:59, `night` from 19:00 to 04:59. Tests cover each boundary (04:59, 05:00, 07:59, 08:00, 16:59, 17:00, 18:59, 19:00).
- **AC9.** Every page's `body` carries a `data-daypart` attribute set to the theme name for the current Đà Nẵng time, and the colours of design.md's table apply for that theme.
- **AC10.** The header row shows "It's HH:MM in Hòa Xuân · Theme" with the Đà Nẵng time of the request (24-hour clock) and the theme name with a capital first letter (for example "It's 13:20 in Hòa Xuân · Day").
- **AC11.** The query `?t=dawn`, `?t=day`, `?t=dusk` or `?t=night` shows that theme instead; any other value is ignored and the real theme shows. The footer has the line "See Ở at dawn · day · dusk · night", each word linking to the current page with that `?t=` value.
- **AC12.** The colour change has a 0.9s transition, and none under `prefers-reduced-motion: reduce`.

### Pages and search groundwork (T3)

- **AC13.** `/`, `/house/`, `/hoa-xuan/`, `/faq/` and `/contact/` answer 200. Each shows one `h1`: "Living with nature" (styled as in design.md, "with" in italic serif), "The house", "Hòa Xuân", "FAQ", "Contact". The four inner pages show the inner page heading of design.md (chapter marker, chapter word, `h1`). Until T5, the home page shows its `h1` under a plain letter "Ở" in Sand.
- **AC14.** Each page has this `title` and `meta name="description"`:

  | Page | Title | Description |
  |---|---|---|
  | `/` | Ở — Living with Nature · Garden house for rent in Hòa Xuân, Đà Nẵng | A whole garden house with two bedrooms, rented by the month in Hòa Xuân, Đà Nẵng. From 13–14 million VND a month, minimum stay one month. |
  | `/house/` | The house · Ở, a garden house for rent in Đà Nẵng | Two bedrooms, a mezzanine, a light well, front and back gardens and a covered veranda. Rented whole, by the month. |
  | `/hoa-xuan/` | Hòa Xuân, Đà Nẵng · Living at Ở | A supermarket across the road, the market and the beach about 10 minutes away, the airport about 15 minutes. |
  | `/faq/` | FAQ · Renting Ở in Hòa Xuân, Đà Nẵng | Minimum stay, deposit, electricity and water, pets, and residence registration for foreigners. |
  | `/contact/` | Contact Bún · Ở garden house, Đà Nẵng | Call, WhatsApp or Zalo. I usually reply within an hour. |

- **AC15.** Each page has `link rel="canonical"` equal to `SITE_BASE_URL` plus the page's path, without any query (also when `?t=` is used), and the Open Graph tags `og:title`, `og:description`, `og:url` (the canonical), `og:type` (`website`) and `og:site_name` (`Ở — Living with Nature`). `SITE_BASE_URL` comes from the environment, default `http://localhost:8000`.
- **AC16.** `/sitemap.xml` answers 200 with `application/xml`, listing the five canonical addresses and nothing else.
- **AC17.** `INDEXING_ENABLED` comes from the environment and is off unless set to `1`. Off: every page has `meta name="robots" content="noindex, nofollow"` and `/robots.txt` reads `User-agent: *`, `Disallow: /` and the `Sitemap:` line. On: the meta tag reads `index, follow` and `/robots.txt` reads `User-agent: *`, `Allow: /` and the `Sitemap:` line.
- **AC18.** No page makes a database query (0 queries on each of the five pages, `sitemap.xml` and `robots.txt`); a test checks it.

### Home hero "Through the Ở" (T5)

- **AC21.** The home page opens with the letter "Ở" (Cormorant Garamond 500, sized as in design.md) filled with the loop of the current theme from `src/static/media/hero/` (`mp4` and `webm` sources, the `jpg` poster), and under it the dictionary line: "ở · verb · Vietnamese · say "uh?"" then "1. to stay. 2. to live somewhere. 3. to be at home." (with "ở" and "to be at home." in italic), and "Scroll, and come in ↓". The chip "Illustrative video" shows, and `media-credits.md` lists every loop.
- **AC22.** With JavaScript and no reduced motion, scrolling through the hero stage flies through the letter as described in design.md: the letter grows and centres until the loop fills the screen, the dictionary line fades out in the first sixth, the header row turns Paper over the loop, and in the last fifth the `h1` "LIVING with NATURE" and its line rise into place. Scrolling back up plays it in reverse. The script is one small plain JavaScript file (`src/static/js/hero.js`) loaded with `defer`, with no library.
- **AC23.** Without JavaScript, or under `prefers-reduced-motion: reduce`, the hero is still: the letter is filled with the theme's poster photo through CSS `background-clip: text`, no video plays, and the dictionary line, the `h1` and its line are all visible in the page flow. The `h1` is in the HTML in every case, never drawn only on the canvas.
- **AC24.** With `?t=` (AC11) the hero uses that theme's loop and poster. When a theme's files are missing, the letter is filled with Sand #E9E2D3, no chip shows and nothing breaks.
- **AC25.** The home page stays light: the hero videos use `preload="metadata"`, only the current theme's loop is in the page, the page itself makes 0 database queries, and on a 390px wide screen nothing scrolls sideways.

### Page not found (T4)

- **AC19.** With `DEBUG` off, an unknown address answers 404 with the page of design.md's States board: the header and footer, the label "404", the heading "This path leads nowhere — the garden is this way.", the line "The page you were looking for isn't here. It may have moved, or the link has a typo.", a "Back to the home page" button to `/` and a "Contact Bún" button to `/contact/`. It carries `noindex`.

### Every task

- **AC20.** Every test on `main` passes unchanged. `src/pages/tests/test_health.py::test_home_page_renders` keeps passing because the home `title` still contains "Living with Nature".

## Edge cases

- Empty: every photo or video place shows the empty state; the five pages show only their heading (and the home hero slot). Nothing is invented.
- Large data: none; the pages read no data.
- Time: a request at 04:59:59 is `night`, at 05:00:00 `dawn`. The server clock runs in UTC; the service converts to Đà Nẵng time. A page held open across a boundary keeps its theme until reloaded.
- Query values: `?t=` is checked against the four names only; anything else, upper case included, is ignored and never echoed into the page.
- Caching: themed pages are not cached by the server, so the theme is always current.
- Permissions: every page is public; nothing to sign in to.
- Reduced motion: no colour transition, no autoplay video (poster only), no flight through the letter.
- No JavaScript: every page works; the home hero is the still version of AC23.
- Slow phone: the letter shows the poster until the loop can play; the flight never waits for the video.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Overall look | Design E "Through the Ở": the giant letter as a door, a dictionary line, chapters named ở nhà, ở gần, ở lâu, ở lại?, editorial type (uppercase light sans with italic serif words) | Designs A Atelier, B Field Journal, C Cinematic, D Atelier Cinema, compared as tour videos | Owner chose E: the name itself becomes the experience, so a visitor remembers "Ở" after one visit, and it keeps the time-of-day idea |
| Fly-through animation | One small plain JavaScript file as a progressive enhancement, still hero without it | A JavaScript framework or animation library; CSS only | The architecture allows small plain scripts; a canvas is needed to show video through a letter; every page still works without script |
| Hero loops in epic 1 | Four illustrative Pexels loops as static files, labelled, replaced in epic 2 | Empty hero until epic 2 | The look depends on the loop inside the letter; Pexels License allows it |
| Unique experience | Both: the site follows the time of day, and a walk-through floor plan on The house | Only one of them; another idea | Time of day gives a first impression on every page; the plan helps visitors picture living there |
| Whose clock | Đà Nẵng time, worked out by Django on the server | The visitor's clock (needs JavaScript) | Visitors abroad feel life in Hòa Xuân; no script; the same for search engines |
| Time slots | Dawn 05–08, Day 08–17, Dusk 17–19, Night 19–05 | Day and night only | Four moods give the richest change |
| Preview other times | Footer links with `?t=`, one canonical address | Real time only | Lets a visitor see all four moods; canonical keeps search engines on one page |
| Epic split | Epic 1: shell, type, time of day, 404, SEO, empty media slots; floor plan in epic 3 | Floor plan in epic 1 | The plan belongs to The house page, which epic 3 builds with real content |
| Floor plan drawing | A schematic labelled "Schematic" until the architect's plan is sent | Wait for the real plan | Not blocking; the real plan replaces it |
| Photos and video places | Media map on the design canvas: 4 time-of-day hero loops, an area loop, about 33 photos; walk-through video and room photos in phase 2 | Photos only | Short muted loops make the time-of-day idea come alive; real-house media must wait for the house |
| Fonts | Be Vietnam Pro and Cormorant Garamond from Google Fonts | Self-hosted font files | Free, both carry Vietnamese for /vi/ later; no build step |
| Task #4 (plain English 404) | Replaced by T4 in the new look; #4 is closed as superseded when these issues are created | Rerun #4 as it is | #4 would build a 404 in the old look and touch the same files as T1 |

## Design

`docs/specs/site-shell/design.md`

## Open questions
