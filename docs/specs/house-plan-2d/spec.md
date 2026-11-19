# Spec: house-plan-2d

## Summary

On the home page `/` and `/vi/`, chapter 01 (`#house`), the block "Walk through the house" (`figure#floor-plan`, today ten HTML boxes and a photo dialog) becomes:

1. A drawing on a paper card: a long section of the house (decoration only) above a clickable plan of the 6 × 18 m plot, from the gate to the back garden, drawn as inline SVG with ink lines and watercolour washes, the style of the owner's sketch. The plan is laid out sideways on wide screens and upright (gate at the top) at 860 px wide or less. A chip "Sketch · not to scale" and the caption "A hand sketch of the 6 × 18 m plan, not the architect's drawing."
2. The list "The layout" above it (eight lines from "Two bedrooms" to "Laundry, drying and storage area") is removed: the drawing names the rooms. "Included" stays, now alone above the drawing.
3. Seven rooms, each a link on the plan. Without JavaScript the rooms are a list beside (desktop) or under (phone) the drawing, each with its number, name, photo (or the empty Sand block with Ở) and text. With JavaScript (`js/floor-plan.js`) one room shows at a time: beside the drawing on desktop, in a bottom sheet on phones, with previous / next and close.

The look, the layout and the motion are those of the prototype states listed under Design. The drawing code of the prototype is in [drawing-reference.txt](drawing-reference.txt) (a Python script, kept as text so the linters skip it) (the script that drew those states): the build ports its geometry, sketch-line method, markup, CSS and script to Django; the result must match the prototype states visually, not byte for byte. No database query is added; the owner pages do not change.

## User story

As a visitor thinking of renting Ở, I want to see how the rooms of the house sit together and tap a room to see it and read about it, so that I can picture living there before I contact the owner.

## Acceptance criteria

Phone means 390 by 844 px; desktop means 1440 by 1000 px. "The plan" is the clickable SVG; plan units are decimetres: u runs along the plot from the gate (u = 0) to the back wall (u = 180, 18 m) and v across it (v = 0 on the garden side to v = 60 on the kitchen side, 6 m).

### The rooms (T1)

The layout is the owner's own description of the real plan (2026-11-19): from the gate the 6 m front splits into a garden 3.5 m wide and a kitchen 2.5 m wide, both 9 m deep; then the bathroom (garden side) and the laundry and drying corner (kitchen side) with the hall between them leading to the two bedrooms; then bedroom 1 (garden side) and bedroom 2; a triangle of garden fills the back corner, so the back wall runs on a slant. The sizes of the back half are read from the owner's sketch, not measured.

The seven rooms, in this order (walking order), with their kind, shape in plan units (a rectangle u0–u1, v0–v1, or a polygon of (u, v) points), photo key of `pages/photos.py` and texts. EN name / VI name; EN text / VI text. The hall (u 90–112, v 25–35) is drawn with the word "hall" / "hành lang" but is not a room and not a link.

| # | key | EN name | VI name | kind | shape | photo |
|---|---|---|---|---|---|---|
| 1 | front-garden | Front garden | Vườn trước | garden | rect 0–90, 0–35 | none |
| 2 | kitchen | Kitchen | Bếp | room | rect 0–90, 35–60 | kitchen |
| 3 | bathroom | Bathroom | Phòng vệ sinh | wet (hatched) | rect 90–112, 0–25 | none |
| 4 | laundry | Laundry and drying | Giặt và phơi | wet (hatched) | rect 90–112, 35–60 | none |
| 5 | bedroom-1 | Bedroom 1 | Phòng ngủ 1 | room | polygon (112, 0), (180, 0), (180, 15), (168, 30), (112, 30) | bedroom |
| 6 | bedroom-2 | Bedroom 2 | Phòng ngủ 2 | room | polygon (112, 30), (168, 30), (145, 60), (112, 60) | bedroom |
| 7 | back-garden | Back garden | Vườn sau | garden | polygon (180, 15), (180, 60), (145, 60) | garden-evening |

Texts:
1. "The way in from the gate: a garden 3.5 m wide and 9 m deep, beside the kitchen." / "Lối vào từ cổng: khu vườn rộng 3,5 m, sâu 9 m, nằm cạnh gian bếp."
2. "A long kitchen, 2.5 m wide and 9 m deep, along the garden: a real kitchen for everyday cooking and a table to eat together." / "Gian bếp dài, rộng 2,5 m, sâu 9 m, chạy dọc khu vườn: bếp thật để nấu mỗi ngày và bàn để cùng ăn."
3. "The bathroom, off the corridor that leads to the two bedrooms." / "Phòng vệ sinh, mở ra hành lang dẫn vào hai phòng ngủ."
4. "A corner to wash and dry clothes, across the corridor from the bathroom." / "Góc giặt và phơi đồ, đối diện phòng vệ sinh qua hành lang."
5. "A calm bedroom at the back of the house, away from the gate." / "Phòng ngủ yên tĩnh ở phía sau nhà, xa cổng."
6. "The second bedroom, next to the first, opening onto the back garden." / "Phòng ngủ thứ hai, cạnh phòng thứ nhất, nhìn ra vườn sau."
7. "A small triangle of garden at the back corner, easy to look after. Garden care once a week is included." / "Mảnh vườn tam giác nhỏ ở góc sau nhà, dễ chăm. Đã bao gồm chăm vườn mỗi tuần một lần."

- **AC1.** `pages.floor_plan.rooms(language)` returns the seven rooms of the table in that order, each with its key, kind, shape (as a list of (u, v) points; a rectangle as its four corners), name and text in the language (English by default) and its `photos.Photo` (None for "none", and None when the photo's file is missing, as `photos.photo` does today). The names and texts live in `pages/texts/house.py` (EN and VI).

### The drawing (T1)

- **AC2.** Given a desktop and `/`, when the visitor scrolls to "Walk through the house", then the block runs across the whole chapter width under the layout list and "Included": on the left (8 of 12 parts) the paper card (`#f3ece0`, 1 px border `#ddd2bf`) holding the section and the sideways plan, on the right (4 of 12 parts) the room panel; this matches the prototype state `plan`.
- **AC3.** Given the plan, then each room of the table is drawn at its shape (sideways: x from u, y from v, gate at the left; upright: x from v, y from u, gate at the top) with: two-stroke ink walls with a slight hand wobble along every edge (gardens: dashed fence), a watercolour wash (rooms terracotta `#e2bfa4`, wet rooms `#d8c6b4` plus 45° hatching, gardens green `#b9c58f` with small round trees kept clear of the label), the room name in Cormorant Garamond italic at the middle of its points ("Laundry and drying" on two lines on the sideways plan). Details as in the prototype: the hall's two walls and its word, the kitchen counter along the outer wall and a round table, a bed in each bedroom, a round fixture in the bathroom, three drying lines in the laundry, round trees outside the plot and an arrow with "gate" / "cổng" at the front. The section above (trees, the kitchen lean-to with its round opening, the low bathroom block, the bedroom gable with an arch, two small figures, the word "Section" / "Mặt cắt") has `aria-hidden="true"`. The drawing is SVG in the page: no image file and no new library; the wobble is deterministic (the same page every time).
- **AC4.** Given a phone and `/`, when the visitor scrolls to the block, then the upright plan fills the card width (at most 420 px, centred), the sideways plan is hidden, the section stays above it, and each room's tap area is at least 44 px in both directions; this matches `plan-phone`.
- **AC5.** Given the plan, then each room is `<a class="plan__room" href="#room-<key>" data-room="<key>" aria-label="<name>">` holding a transparent `polygon.plan__hit` over its shape and its label; the SVG has `role="group"` and the label "Plan of the house: tap a room" (VI "Mặt bằng căn nhà: chạm vào một phòng"). Hover tints the room moss (`rgba(63, 90, 58, .12)`), keyboard focus shows a dashed moss outline.
- **AC6.** Given the block, then it has the heading "Walk through the house" (VI "Đi một vòng quanh nhà", unchanged), the chip "Sketch · not to scale" (VI "Phác thảo · không theo tỉ lệ") at the bottom left of the card, and under the card the caption "A hand sketch of the 6 × 18 m plan, not the architect's drawing." (VI "Phác tay mặt bằng 6 × 18 m, chưa phải bản vẽ của kiến trúc sư."). The words "Schematic" / "Sơ đồ" and the old caption no longer appear.

### The rooms list without JavaScript (T1)

- **AC7.** Given `/` without JavaScript, when the visitor opens the block, then the panel shows the hint "Tap a room on the plan to look inside." (VI "Chạm vào một phòng trên bản vẽ để xem bên trong.") and the ordered list `ol.plan__rooms` of the seven rooms, each `li.plan-room#room-<key>` with "01 of 07" … "07 of 07" (VI "01 / 07"), the name as `h4`, the photo and the text; tapping a room on the plan jumps to its item.
- **AC8.** Given a room with a photo (for example Kitchen), then its item shows the photo at 4 / 3 (cover) with the chip "Illustrative photo" (VI "Ảnh minh hoạ") and its credit as `pages/photos.py` gives it ("Photo: Pexels", VI "Ảnh: Pexels"), the alt text of `pages/photos.py` in the page's language, `loading="lazy"`. Given a room with no photo (Front garden, Bathroom, Laundry) or whose file is missing, then the item shows the Sand block with a large Ở and the caption "No photo of this room yet" (VI "Chưa có ảnh phòng này"); this matches `plan-room-empty`.
- **AC9.** Given `/` (and `/vi/`), when the visitor scrolls past the facts row of chapter 01, then there is no "The layout" / "Bố cục" list: `div.house__layout` is gone from `pages/chapters/house.html` and the keys `layout` and `layout_*` from `pages/texts/house.py` (EN and VI); "Included" / "Đã bao gồm" and its line stay, in columns 1–5 with no space above its label, then the drawing under it (prototype state `plan`). The old dialog `dialog.floor-plan__dialog`, its Close button and the ↗ links to photo files are gone; the block keeps `id="floor-plan"` and the page still links `js/floor-plan.js` once with `defer`.

### Opening a room (T2)

- **AC10.** Given a desktop with JavaScript and no room open, when the visitor clicks Kitchen on the plan, then Kitchen is tinted moss with a 3 px moss outline and its label bold, `aria-current="true"` is on its link, the hint hides and the panel shows only the Kitchen item ("02 of 07", photo, chip, credit, text) with a 0.3 s fade-up, and two round 44 px buttons ← (label "Previous room", VI "Phòng trước") and → ("Next room", VI "Phòng sau") above it; this matches `plan-room`. The panel stays in view while the page scrolls past the drawing (sticky under the header).
- **AC11.** Given a room open, when the visitor presses → (or the → key), then the next room in the table's order opens (after Back garden comes Front garden); ← (or the ← key) opens the previous one (before Front garden comes Back garden); Esc closes the room: no room tinted, the hint shows again and focus returns to that room's link.
- **AC12.** Given a phone with JavaScript, when the visitor taps Bedroom 1, then the page scrolls so the room sits just under the header, and a bottom sheet slides up (0.3 s) holding ←, → and ✕ (label "Close", VI "Đóng") in a sticky row and the Bedroom 1 item ("05 of 07", photo, chip, credit, text); the sheet is at most 76% of the screen high, scrolls inside, covers the phone contact bar and has rounded top corners; ✕ closes it; this matches `plan-phone-sheet` (VI `vi-plan-phone-sheet`).
- **AC13.** Given the visitor asked for less motion, then the fade-up and the sheet's slide do not run and the page jumps instead of scrolling smoothly. The script is plain JavaScript in `src/static/js/floor-plan.js` (no library), stores nothing, and is under 4,000 bytes.

### The facts row, drawn (T3)

- **AC14.** Given a desktop and `/`, when the visitor scrolls to the facts row of chapter 01, then the straight 1 px Ink rule above it is a hand-drawn ink line (the same two-stroke sketch line as the plan, inline SVG, `aria-hidden="true"`), and each of the four facts has, on its left, a small watercolour drawing (inline SVG 118 by 77 px, `aria-hidden="true"`, the plan's wash filter and colours): two beds seen from above (2 bedrooms), two round trees (2 gardens), a pot with steam on a counter line (1 real kitchen), a small gable house with a round window and one figure (1 household at a time); the number in Cormorant Garamond italic at 72 px and the label in Cormorant Garamond italic at 20 px under it. The texts are "2 bedrooms", "2 gardens", "1 real kitchen", "1 household at a time" (VI "2 phòng ngủ", "2 khoảng vườn", "1 gian bếp thật", "1 hộ thuê một lúc"): the third fact replaces "1 light well" / "1 giếng trời" of `main`, since the real plan has no light well. This matches the prototype state `house-facts`.
- **AC15.** Given a phone, then the four facts sit in two columns, each drawing (78 by 51 px) above its number (52 px) and label (17 px) (`house-facts-phone`). Given the night theme, the ink lines of the drawings are Paper (`#e9e2d3`); the washes keep their colours.

### All tasks

- **AC16.** `/` and `/vi/` still make exactly one database query each; the owner pages and the 404 page are unchanged.
- **AC17.** Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change" in its issue, changed only as listed there. `bash scripts/check.sh` passes.

## Edge cases

- Empty: a room with no photo, or whose photo file is missing, shows the Sand block with Ở and "No photo of this room yet" (AC8); the room is still on the plan and in the list.
- Large data: always seven rooms (fixed in code); nothing grows with data.
- Narrow screens: at 320 px the upright plan scales down with the card; the tap areas of the smallest rooms (Bathroom, Laundry) stay at least 44 px (AC4).
- Themes: the paper card keeps its own paper colour and ink in all four times of day (dawn, day, dusk, night); the panel uses the theme's colours.
- No JavaScript: the full list of seven rooms shows; links jump to the items (AC7).
- Permissions: public page, no sign-in.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Where does the layout come from? | The owner's description of the real 6 × 18 m plan and their colour sketch (2026-11-19): seven rooms; the watercolour sketch gives the style only | The cardboard model's ten rooms (first answer, 2026-11-18); the curved plan of the style sketch | The owner said the model's layout was not right and described the real one |
| Q2 Form of the drawing | A small section above a clickable plan, ink and watercolour | Plan only; 2.5D axonometric | Closest to the owner's sketch, and a flat plan is easy to tap |
| Q3 Label | "Sketch · not to scale" | No label | It is still not the architect's plan |
| Q4 What a tap shows | Room tinted, panel with name, photo (stock, labelled) or empty block, 1–2 sentences, ← → | Only the photo, as today | The owner asked for photo and information per room |
| Q5 Room texts | Drafted by Claude from the owner's facts, approved by the owner in the prototype ("Prototype ổn", 2026-11-19); only the sizes the owner gave (3.5, 2.5 and 9 m) | The owner writes them | Faster; nothing invented beyond what the owner said |
| Q6 Cardboard model photos on the site | Not on the site (owner, after seeing the prototype, 2026-11-18) | Three photos labelled "Cardboard model" (first answer) | The owner removed the strip; the drawing alone shows the house |
| Q7 Phone | Plan upright, gate at the top, tap areas ≥ 44 px, room in a bottom sheet | Sideways plan with sideways scroll | Fits a phone without sideways scrolling |
| Q9 The list "The layout" | Removed (owner, after seeing the prototype, 2026-11-18) | Kept beside the drawing | The drawing names every room; the list repeated it |
| Q10 The facts row | Drawn in the style of the sketch: hand-drawn rule, a small watercolour drawing per fact, italic serif (owner, 2026-11-18) | Kept as plain numbers | The owner asked for it to feel more artistic, like the sketch |
| Q11 The third fact | "1 real kitchen" / "1 gian bếp thật" with a pot drawing (2026-11-19) | "1 light well" of `main` | The real plan has no light well |
| Q8 Vietnamese | Same drawing with Vietnamese labels on `/vi/` | — | One drawing for both languages |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html` (Artifact https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j), group "Site · walk through the house (2D drawing)", first approved on 2026-11-18, then redrawn to the owner's 6 × 18 m plan and approved again with "Prototype ổn" on 2026-11-19 (02:44 UTC):

- `#house-facts`, `#house-facts-phone`: the facts row, drawn.

- `#plan`: desktop, no room open.
- `#plan-room`: desktop, Kitchen open.
- `#plan-room-empty`: desktop, Bathroom open, no photo.
- `#plan-phone`: phone, the upright plan, gate at the top.
- `#plan-phone-sheet`: phone, Bedroom 1 in the bottom sheet.
- `#vi-plan`, `#vi-plan-phone-sheet`: the same on `/vi/`.

## Open questions
