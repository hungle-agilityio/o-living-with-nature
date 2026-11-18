# Spec: house-plan-2d

## Summary

On the home page `/` and `/vi/`, chapter 01 (`#house`), the block "Walk through the house" (`figure#floor-plan`, today ten HTML boxes and a photo dialog) becomes:

1. A drawing on a paper card: a long section of the house (decoration only) above a clickable plan of the plot, front garden to back garden, drawn as inline SVG with ink lines and watercolour washes, the style of the owner's sketch. The plan is laid out sideways on wide screens and upright (front garden at the top) at 860 px wide or less. A chip "Sketch · not to scale" and the caption "Drawn from the cardboard model of the house, not the architect's plan."
2. Ten rooms, each a link on the plan. Without JavaScript the rooms are a list beside (desktop) or under (phone) the drawing, each with its number, name, photo (or the empty Sand block with Ở) and text. With JavaScript (`js/floor-plan.js`) one room shows at a time: beside the drawing on desktop, in a bottom sheet on phones, with previous / next and close.

The look, the layout and the motion are those of the prototype states listed under Design. The drawing code of the prototype is in [drawing-reference.txt](drawing-reference.txt) (a Python script, kept as text so the linters skip it) (the script that drew those states): the build ports its geometry, sketch-line method, markup, CSS and script to Django; the result must match the prototype states visually, not byte for byte. No database query is added; the owner pages do not change.

## User story

As a visitor thinking of renting Ở, I want to see how the rooms of the house sit together and tap a room to see it and read about it, so that I can picture living there before I contact the owner.

## Acceptance criteria

Phone means 390 by 844 px; desktop means 1440 by 1000 px. "The plan" is the clickable SVG; plan units run along the plot from the lane (u = 0) to the back fence (u = 250) and across it (v = 0 to 80).

### The rooms (T1)

The ten rooms, in this order (walking order), with their kind, rectangle in plan units (u0–u1, v0–v1), photo key of `pages/photos.py` and texts. EN name / VI name; EN text / VI text.

| # | key | EN name | VI name | kind | rect u0–u1, v0–v1 | photo |
|---|---|---|---|---|---|---|
| 1 | front-garden | Front garden | Vườn trước | garden | 0–50, 0–80 | none |
| 2 | veranda | Covered veranda | Hiên có mái che | room | 50–90, 34–80 | veranda |
| 3 | light-well | Light well | Giếng trời | room | 50–90, 0–34 | lightwell |
| 4 | living-kitchen | Living room and kitchen | Phòng khách và bếp | room | 90–155, 0–80 | kitchen |
| 5 | mezzanine | Mezzanine | Gác lửng | loft (dashed, drawn over 4) | 96–126, 4–42 | mezzanine |
| 6 | bedroom-1 | Bedroom 1 | Phòng ngủ 1 | room | 155–200, 0–34 | bedroom |
| 7 | bathroom | Bathroom | Phòng tắm | wet (hatched) | 155–182, 34–50 | none |
| 8 | bedroom-2 | Bedroom 2 | Phòng ngủ 2 | room | 155–200, 50–80 | bedroom |
| 9 | laundry | Laundry, drying and storage | Giặt, phơi và kho | wet (hatched) | 200–218, 0–80 | none |
| 10 | back-garden | Back garden | Vườn sau | garden | 218–250, 0–80 | garden-evening |

Texts:
1. "The way in: a small walled garden between the lane and the house, so the rooms sit back from the street and stay quiet." / "Lối vào: một khoảng vườn nhỏ có tường bao giữa ngõ và nhà, để các phòng lùi xa mặt đường và luôn yên tĩnh."
2. "A deep roof over the front of the house, open to the garden: a place to sit with a coffee and watch the rain." / "Mái hiên sâu phía trước nhà, mở ra vườn: chỗ ngồi uống cà phê và ngắm mưa."
3. "Open to the sky, with a curved wall and a round opening. It brings daylight and air into the middle of the house." / "Mở lên trời, có vách cong và một ô tròn. Giếng trời đưa ánh sáng và gió vào giữa nhà."
4. "One open room under the high roof, lit from above. A real kitchen for everyday cooking and a table to eat together." / "Một không gian mở dưới mái cao, lấy sáng từ trên. Bếp thật để nấu mỗi ngày và bàn để cùng ăn."
5. "A loft above the living room: a quiet corner to read or work." / "Gác lửng phía trên phòng khách: một góc yên để đọc sách hay làm việc."
6. "A calm bedroom at the back of the house, away from the lane." / "Phòng ngủ yên tĩnh ở phía sau nhà, xa ngõ."
7. "One bathroom, between the two bedrooms." / "Một phòng tắm, nằm giữa hai phòng ngủ."
8. "The second bedroom, also at the back: for a guest, a study or someone who keeps different hours." / "Phòng ngủ thứ hai, cũng ở phía sau: cho khách, làm phòng đọc, hay cho người có giờ giấc khác."
9. "A practical corner at the back: wash, dry clothes out of the rain, and keep things out of sight." / "Góc tiện ích phía sau: giặt, phơi đồ không sợ mưa, và cất đồ gọn gàng."
10. "A quiet garden behind the house, easy to look after. Garden care once a week is included." / "Khu vườn yên tĩnh sau nhà, dễ chăm. Đã bao gồm chăm vườn mỗi tuần một lần."

- **AC1.** `pages.floor_plan.rooms(language)` returns the ten rooms of the table in that order, each with its key, kind, rectangle, name and text in the language (English by default) and its `photos.Photo` (None for "none", and None when the photo's file is missing, as `photos.photo` does today). The names and texts live in `pages/texts/house.py` (EN and VI).

### The drawing (T1)

- **AC2.** Given a desktop and `/`, when the visitor scrolls to "Walk through the house", then the block runs across the whole chapter width under the layout list and "Included": on the left (8 of 12 parts) the paper card (`#f3ece0`, 1 px border `#ddd2bf`) holding the section and the sideways plan, on the right (4 of 12 parts) the room panel; this matches the prototype state `plan`.
- **AC3.** Given the plan, then each room of the table is drawn at its rectangle (sideways: x from u, y from v; upright: x from v, y from u, front garden at the top) with: two-stroke ink walls with a slight hand wobble (gardens: dashed fence), a watercolour wash (rooms terracotta `#e2bfa4`, wet rooms `#d8c6b4` plus 45° hatching, gardens green `#b9c58f` with small round trees, loft: a dashed outline only, no wash), the room name in Cormorant Garamond italic at its centre (laundry turned 90° on the sideways plan, living room and kitchen on two lines). Details as in the prototype: the round green opening of the light well, two dashed skylights and the counter and table in the living room, a bed in each bedroom, the loft stairs, round trees outside the plot and an arrow with "lane" / "ngõ" at the front. The section above (hills, trees, the veranda lean-to with its round opening, the gable with two skylights, two small figures, the back lean-to with an arch, the word "Section" / "Mặt cắt") has `aria-hidden="true"`. The drawing is SVG in the page: no image file and no new library; the wobble is deterministic (the same page every time).
- **AC4.** Given a phone and `/`, when the visitor scrolls to the block, then the upright plan fills the card width (at most 420 px, centred), the sideways plan is hidden, the section stays above it, and each room's tap area is at least 44 px in both directions; this matches `plan-phone`.
- **AC5.** Given the plan, then each room is `<a class="plan__room" href="#room-<key>" data-room="<key>" aria-label="<name>">` holding a transparent `rect.plan__hit` over its rectangle and its label; the SVG has `role="group"` and the label "Plan of the house: tap a room" (VI "Mặt bằng căn nhà: chạm vào một phòng"). Hover tints the room moss (`rgba(63, 90, 58, .12)`), keyboard focus shows a dashed moss outline.
- **AC6.** Given the block, then it has the heading "Walk through the house" (VI "Đi một vòng quanh nhà", unchanged), the chip "Sketch · not to scale" (VI "Phác thảo · không theo tỉ lệ") at the bottom left of the card, and under the card the caption "Drawn from the cardboard model of the house, not the architect's plan." (VI "Vẽ theo mô hình bìa của căn nhà, chưa phải bản vẽ của kiến trúc sư."). The words "Schematic" / "Sơ đồ" and the old caption no longer appear.

### The rooms list without JavaScript (T1)

- **AC7.** Given `/` without JavaScript, when the visitor opens the block, then the panel shows the hint "Tap a room on the plan to look inside." (VI "Chạm vào một phòng trên bản vẽ để xem bên trong.") and the ordered list `ol.plan__rooms` of the ten rooms, each `li.plan-room#room-<key>` with "01 of 10" … "10 of 10" (VI "01 / 10"), the name as `h4`, the photo and the text; tapping a room on the plan jumps to its item.
- **AC8.** Given a room with a photo (for example Light well), then its item shows the photo at 4 / 3 (cover) with the chip "Illustrative photo" (VI "Ảnh minh hoạ") and its credit ("Photo: Fatmanur Üzüm / Pexels", VI "Ảnh: Fatmanur Üzüm / Pexels"), the alt text of `pages/photos.py` in the page's language, `loading="lazy"`. Given a room with no photo (Front garden, Bathroom, Laundry) or whose file is missing, then the item shows the Sand block with a large Ở and the caption "No photo of this room yet" (VI "Chưa có ảnh phòng này"); this matches `plan-room-empty`.
- **AC9.** The old dialog `dialog.floor-plan__dialog`, its Close button and the ↗ links to photo files are gone; the block keeps `id="floor-plan"` and the page still links `js/floor-plan.js` once with `defer`.

### Opening a room (T2)

- **AC10.** Given a desktop with JavaScript and no room open, when the visitor clicks Light well on the plan, then Light well is tinted moss with a 3 px moss outline and its label bold, `aria-current="true"` is on its link, the hint hides and the panel shows only the Light well item ("03 of 10", photo, chip, credit, text) with a 0.3 s fade-up, and two round 44 px buttons ← (label "Previous room", VI "Phòng trước") and → ("Next room", VI "Phòng sau") above it; this matches `plan-room`. The panel stays in view while the page scrolls past the drawing (sticky under the header).
- **AC11.** Given a room open, when the visitor presses → (or the → key), then the next room in the table's order opens (after Back garden comes Front garden); ← (or the ← key) opens the previous one (before Front garden comes Back garden); Esc closes the room: no room tinted, the hint shows again and focus returns to that room's link.
- **AC12.** Given a phone with JavaScript, when the visitor taps Covered veranda, then the page scrolls so the room sits just under the header, and a bottom sheet slides up (0.3 s) holding ←, → and ✕ (label "Close", VI "Đóng") in a sticky row and the Covered veranda item ("02 of 10", photo, chip, credit, text); the sheet is at most 76% of the screen high, scrolls inside, covers the phone contact bar and has rounded top corners; ✕ closes it; this matches `plan-phone-sheet` (VI `vi-plan-phone-sheet`).
- **AC13.** Given the visitor asked for less motion, then the fade-up and the sheet's slide do not run and the page jumps instead of scrolling smoothly. The script is plain JavaScript in `src/static/js/floor-plan.js` (no library), stores nothing, and is under 4,000 bytes.

### All tasks

- **AC14.** `/` and `/vi/` still make exactly one database query each; the owner pages and the 404 page are unchanged.
- **AC15.** Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change" in its issue, changed only as listed there. `bash scripts/check.sh` passes.

## Edge cases

- Empty: a room with no photo, or whose photo file is missing, shows the Sand block with Ở and "No photo of this room yet" (AC8); the room is still on the plan and in the list.
- Large data: always ten rooms (fixed in code); nothing grows with data.
- Narrow screens: at 320 px the upright plan scales down with the card; the tap areas of the smallest room (Bathroom) stay at least 44 px (AC4).
- Themes: the paper card keeps its own paper colour and ink in all four times of day (dawn, day, dusk, night); the panel uses the theme's colours.
- No JavaScript: the full list of ten rooms shows; links jump to the items (AC7).
- Permissions: public page, no sign-in.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Where does the layout come from? | The owner's cardboard model of the real house, the 10 rooms kept; the watercolour sketch gives the style only | The curved plan of the sketch | The model is the house being built; the sketch is a different concept |
| Q2 Form of the drawing | A small section above a clickable plan, ink and watercolour | Plan only; 2.5D axonometric | Closest to the owner's sketch, and a flat plan is easy to tap |
| Q3 Label | "Sketch · not to scale" | No label | It is still not the architect's plan |
| Q4 What a tap shows | Room tinted, panel with name, photo (stock, labelled) or empty block, 1–2 sentences, ← → | Only the photo, as today | The owner asked for photo and information per room |
| Q5 Room texts | Drafted by Claude from the owner's facts, approved by the owner in the prototype ("Prototype ổn", 2026-11-18); no sizes | The owner writes them | Faster; nothing invented beyond what the owner said |
| Q6 Cardboard model photos on the site | Not on the site (owner, after seeing the prototype, 2026-11-18) | Three photos labelled "Cardboard model" (first answer) | The owner removed the strip; the drawing alone shows the house |
| Q7 Phone | Plan upright, front garden at the top, tap areas ≥ 44 px, room in a bottom sheet | Sideways plan with sideways scroll | Fits a phone without sideways scrolling |
| Q8 Vietnamese | Same drawing with Vietnamese labels on `/vi/` | — | One drawing for both languages |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html` (Artifact https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j), group "Site · walk through the house (2D drawing)", approved with "Prototype ổn" on 2026-11-18:

- `#plan`: desktop, no room open.
- `#plan-room`: desktop, Light well open.
- `#plan-room-empty`: desktop, Bathroom open, no photo.
- `#plan-phone`: phone, the upright plan.
- `#plan-phone-sheet`: phone, Covered veranda in the bottom sheet.
- `#vi-plan`, `#vi-plan-phone-sheet`: the same on `/vi/`.

## Open questions
