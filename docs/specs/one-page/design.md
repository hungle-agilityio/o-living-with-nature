# Design: the site as one page (epic 3)

Design card (approved by the owner on 2026-11-12): https://claude.ai/artifact/8Kk9W7BQzsfWuGUWWhNAVf. It has three boards: desktop in the day theme, phone at 390px with the contact bar, and the empty states with the night theme. The floor plan drawn on the card is an early sketch. Where it differs from AC16 of the spec, the spec wins.

The look is design E of `docs/specs/site-shell/design.md`, with its tokens, chapter marker, chapter word sizes, media slot, chip, buttons, Ink band and time-of-day themes. Nothing new is added to the tokens.

## Layout

- Chapters are 136px apart on desktop and 72px on phones. Each opens with the marker, the chapter word (Cormorant italic, 200px desktop and 96px phone) and the `h2` (Be Vietnam Pro 300, uppercase, 64px desktop and 40px phone, with the accent word in Cormorant italic). FAQ has no chapter word, and its `h2` "FAQ" is 150px desktop and 60px phone.
- Desktop uses a 12-column grid, 24px gaps and 40px sides. Phones use one column with 18px sides.
- House: intro text (columns 1–5) beside the veranda photo (columns 7–12). Then the four-photo gallery (3 / 4 each), the layout list and "Included" (columns 1–5) beside the floor plan (columns 7–12). On phones the gallery is a sideways-scrolling row of 240px cards inside its own box.
- Hòa Xuân: the area loop (16 / 9, columns 1–7) beside the line, the travel list and the Maps button (columns 9–12). Then three photos (4 / 3).
- Rent: the price line in the "big" size (84px desktop, 44px phone) with the buttons under it (columns 1–6), beside the terms list (columns 8–12).
- FAQ: a column at most 880px wide. Each question is a row with a `+` (closed) or `–` (open) in Cormorant on the right.
- Contact: the Ink band, full width, with Paper text. The Call button is primary (Paper fill) and the others are outline.
- Phone contact bar: Ink at 96%, three equal 44px pill buttons, safe-area padding at the bottom.

## Texts (English, as shown)

### The house

- Owner line: "{greeting} I built a small garden house in Hòa Xuân, and I'd love for someone to make it home for a while."
- Why Ở: "I wanted a house that feels good to live in every day, not just in photos: a little garden, morning light, a veranda to sit on. Ở is that house."
- Points:
  - 01 "A private garden and a covered veranda"
  - 02 "Light and air through a light well"
  - 03 "Live like at home, for a month or more"
- Layout (label "The layout"):
  - Two bedrooms
  - One bathroom
  - Living room and kitchen
  - Mezzanine
  - Light well
  - Front and back gardens
  - Covered veranda
  - Laundry, drying and storage area
- Included (label "Included"): "Basic furniture. Garden care once a week. Cleaning can be arranged."

### Hòa Xuân

- Line: "Everything you need day to day is close by."
- Travel list: Supermarket · across the road; Market · about 10 min; Beach · about 10 min; Airport · about 15 min.
- Link: "Hòa Xuân on Google Maps ↗".

### FAQ (first open)

1. What is the minimum stay? → "One month."
2. Can I rent a room, not the whole house? → "No. The house is rented whole."
3. How much is the rent? → "{price_line}." or "Ask me about the rent."
4. How much is the deposit? → "Two months' rent."
5. Are electricity and water included? → "Up to 300 kWh of electricity and 10 m³ of water each month. Anything above is charged at the official rate."
6. Can I bring a pet? → "Let's talk. Tell me about your pet."
7. Do you help with temporary residence registration? → "Yes. I take care of temporary residence registration for you."
8. Can I visit before I decide? → "Yes. Send me a message and we'll find a time."

### Contact

- Heading "Will you *stay?*". The line is "{greeting} {reply_line}". With no channel, it reads "Contact details are on their way."

## States

- **Normal:** the owner's values (13–14 million, three channels), the photos of epic 2, in each of the four time-of-day themes.
- **Empty:** a cleared price shows "Ask me about the rent". No channels means no buttons, no bar, and the "on their way" line. A missing file shows the Sand slot with Ở.
- **Error:** the page takes no input. Old addresses redirect, and other unknown addresses get the epic 1 404 page.
- **Narrow (390px):** one column, a sideways gallery inside its box, the phone menu, and the contact bar after the hero. Nothing is wider than the screen.
