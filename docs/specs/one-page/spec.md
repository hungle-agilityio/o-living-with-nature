# Spec: the site as one page (epic 3)

## Summary

The home page `/` becomes the whole site. Under the epic 1 hero come five chapters, each a `section` with an id:

| Order | id | Chapter word | Heading | Marker |
|---|---|---|---|---|
| 1 | `house` | ở nhà | The house | ̉ 01 |
| 2 | `hoa-xuan` | ở gần | Hòa Xuân | ̉ 02 |
| 3 | `rent` | ở lâu | The rent | ̉ 03 |
| 4 | `faq` | (none) | FAQ | ̉ 04 |
| 5 | `contact` | ở lại? | Will you stay? | ̉ 05 |

The header links jump to these ids. `/house/`, `/hoa-xuan/`, `/faq/` and `/contact/` answer with a permanent redirect to their chapter, and the sitemap lists only `/`. The price line and the contact buttons come from the site settings of epic 2 (`owner_content.services.site_settings()`), and the photos from the photo list of epic 2 (`pages.photos`). On a phone, a bar with the three contact buttons stays at the bottom of the screen after the hero. The house chapter ends with a walk-through floor plan, labelled "Schematic" until the architect's plan exists.

Design and texts: `docs/specs/one-page/design.md`. Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change".

## Acceptance criteria

### One page, its menu and the old addresses (T1)

- **AC1.** `/` shows, in this order: the hero of epic 1, then five `section` elements with the ids, chapter markers, chapter words and headings of the table above. The page has exactly one `h1` (the hero's). Each chapter heading is an `h2`.
- **AC2.** The header links read "The house", "Hòa Xuân", "Rent", "FAQ" and "Contact" and point to `/#house`, `/#hoa-xuan`, `/#rent`, `/#faq` and `/#contact`. The phone menu (`details`, no script) holds the same five links. No link carries `aria-current`.
- **AC3.** `/house/`, `/hoa-xuan/`, `/faq/` and `/contact/` answer 301, with `Location` set to `/#house`, `/#hoa-xuan`, `/#faq` and `/#contact`. They make no query.
- **AC4.** `sitemap.xml` lists only the canonical address of `/`. `robots.txt`, the noindex switch, the title and description of `/`, its canonical and Open Graph tags stay as in epic 1.
- **AC5.** The view of `/` puts the site settings of epic 2 in the template context as `owner`. `/` makes exactly one query; every other address still makes none.
- **AC6.** A template tag `{% photo "{key}" ratio="4 / 3" %}` renders the media slot of epic 1 (`includes/media.html`) for a photo of `pages.photos`. It passes the photo's path, alt text, width, height, the illustrative flag and the credit. The first photo of the page is not lazy. An unknown or missing photo gives the slot's empty state.
- **AC7.** Each chapter is its own template, `src/pages/templates/pages/chapters/{id}.html`, included by `home.html`, with its own stylesheet `src/static/css/chapters/{id}.css` linked from `home.html`. The four old page templates are removed.
- **AC8.** No part of the page is wider than the screen at 390px.

### Rent and contact, with the phone bar (T2)

- **AC9.** A reusable include `includes/contact_buttons.html` renders one link button per channel in `owner.channels`, in the order Call, WhatsApp, Zalo, with the channel's label and link. Each button carries `data-channel="{key}"` and `data-place="{chapter id, or bar}"`, for epic 4. The first button is the primary one. WhatsApp and Zalo open in a new tab with `rel="noopener"`; Call does not. With no channel, the include renders nothing.
- **AC10.** The rent chapter shows `owner.price_line` in the "big" size, or "Ask me about the rent" when it is `None`. Under it come the contact buttons and this list, as written:
  - "Whole house, by the month"
  - "Minimum stay one month"
  - "Two months' deposit"
  - "Included each month: up to 300 kWh of electricity and 10 m³ of water. Anything above is charged at the official rate."
  - "I take care of temporary residence registration for you"
- **AC11.** The contact chapter is the Ink band of design.md. It shows "Will you stay?", then the line "{{ owner.greeting }} {{ owner.reply_line }}" (for example "Hi, I'm Bún. I usually reply within an hour."), then the contact buttons. With no channel it shows "Contact details are on their way." instead of the buttons.
- **AC12.** At 760px wide or less, a `nav` with `aria-label="Contact"` holding the contact buttons (`data-place="bar"`) is fixed to the bottom of the screen. A small plain script (`src/static/js/contact-bar.js`, deferred, no library) shows it only after the hero has left the screen, and hides it while the contact chapter is on screen. Without JavaScript, the bar always shows on phones. With no channel there is no bar. The bar never shows above 760px.

### The house (T3)

- **AC13.** The house chapter shows, as written in design.md:
  - the owner's line "{{ owner.greeting }} I built a small garden house in Hòa Xuân, and I'd love for someone to make it home for a while.";
  - the "Why Ở" paragraph;
  - the three numbered points;
  - the veranda photo;
  - a gallery of four photos (lightwell, bedroom, kitchen, mezzanine), which scrolls sideways inside its own box at 760px or less;
  - the layout list of eight lines;
  - the "Included" line.

### Hòa Xuân (T4)

- **AC14.** The Hòa Xuân chapter shows:
  - the area loop of epic 2 in a media slot (16 / 9), with the "Illustrative video" chip and the credit, and only its poster under `prefers-reduced-motion: reduce`;
  - the line "Everything you need day to day is close by.";
  - the travel list "Supermarket · across the road", "Market · about 10 min", "Beach · about 10 min", "Airport · about 15 min";
  - three photos (market, street, beach-sunset);
  - the link "Hòa Xuân on Google Maps ↗" to `https://www.google.com/maps/search/?api=1&query=H%C3%B2a%20Xu%C3%A2n%2C%20%C4%90%C3%A0%20N%E1%BA%B5ng`, opening in a new tab with `rel="noopener"`. No map is embedded.

### FAQ (T5)

- **AC15.** The FAQ chapter shows the eight questions of design.md, in order, each as a `details` element whose `summary` is the question. All are closed, except the first, which is open. No script is used. The rent answer shows `owner.price_line`, or "Ask me about the rent." when it is `None`.

### Floor plan (T6)

- **AC16.** After the layout list, the house chapter shows "Walk through the house": a schematic drawn in HTML and CSS (`id="floor-plan"`), with no image file. It shows the parts of the house as blocks, front garden first and back garden last: Front garden, Living room and kitchen, Light well, Bedroom 1, Bedroom 2, Bathroom, Mezzanine, Covered veranda, Back garden, and Laundry, drying and storage. It does not claim which floor or wall a room is on. The chip "Schematic" sits on it, with the caption "Schematic until the architect's plan: the rooms of the house, not their real layout."
- **AC17.** A block that has a photo in `pages.photos` is a link to it: Living room and kitchen → kitchen, Light well → lightwell, Bedroom 1 and Bedroom 2 → bedroom, Mezzanine → mezzanine, Covered veranda → veranda. The others are not links. With a script, the photo opens in a `dialog` with its "Illustrative photo" chip, its credit and a close button. Without a script, the link goes to the photo file. The script is plain, deferred and has no library (`src/static/js/floor-plan.js`).

## Edge cases

- **Empty:**
  - No settings record, or a cleared price: "Ask me about the rent".
  - No channel: no buttons, no phone bar, and "Contact details are on their way." in the contact chapter.
  - A missing photo file: the Sand empty slot.
- **Large data:** fixed content, fifteen media at most. Photos after the first are lazy, so the page stays light.
- **Permissions:** everything is public. No cookie is set. The owner's number is public on purpose: the browser check allows it (issue #31).
- **Old links:** `/house/` and the others keep working through the 301. Unknown addresses still get the epic 1 "page not found".

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| One page or five pages | One page, menu to `#id`, old addresses 301 to their chapter, sitemap only `/` | Hybrid (keep FAQ and Hòa Xuân pages); keep five pages | The goal is contacts, not SEO; one scroll fits design E; less to build; `/vi/` later is one page too |
| Chapters and ids | `house`, `hoa-xuan`, `rent`, `faq`, `contact` | Price inside the house chapter | Keeps the four ở chapters of design E; the price is what visitors ask first |
| FAQ | `details` per question, first open | All open | The page is already long |
| Who writes the texts | Claude from the owner's facts in `docs/intent/website.md`; owner approved the design card on 2026-11-12 | Owner writes them | Every fact already exists |
| Contact buttons | In the rent and contact chapters, plus a phone bar after the hero | Only in the chapters | The goal is contacts; on a phone the buttons stay at hand |
| Floor plan | Last task, HTML schematic labelled "Schematic" | Wait for the architect's plan | Not blocking; the real plan replaces it |

## Design

`docs/specs/one-page/design.md`, with the design card (desktop, phone at 390px with the contact bar, empty states, night theme).

## Open questions
