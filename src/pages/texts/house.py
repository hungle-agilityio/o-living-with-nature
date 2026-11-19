"""The texts of chapter 01, the house, and of the walk through the house
(docs/specs/vietnamese/texts.md, section "Chapter 01").

Accent words are their own keys (`heading_accent`, `owner_line_accent`) so the markup stays in the
template. The owner's greeting comes from the owner's settings, not from here. The `block_*` keys
are the names of the rooms of the hand-drawn plan and the `about_*` keys their texts (same
suffixes; `pages.floor_plan`); the other plan keys (`sketch_*`, `plan_*`, `room_of`, `room_empty`,
`room_previous`, `room_next`, `section_word`, `gate`, `hall`) are the words of the drawing.
"""

EN: dict[str, str] = {
    "marker": "01 · at home",
    "heading": "The",
    "heading_accent": "house",
    "owner_line": "I built a small garden house in Hòa Xuân, and I'd love for someone to make it",
    "owner_line_accent": "home for a while.",
    "why": (
        "I wanted a house that feels good to live in every day, not just in photos: a little "
        "garden, morning light, a veranda to sit on. Ở is that house."
    ),
    "room_bedroom": "Bedrooms · two",
    "room_lightwell": "Light well",
    "room_veranda": "Veranda",
    "room_kitchen": "Living & kitchen",
    "room_garden_evening": "Back garden",
    "fact_bedrooms": "bedrooms",
    "fact_gardens": "gardens",
    "fact_light_well": "light well",
    "fact_household": "household at a time",
    "included": "Included",
    "included_line": "Basic furniture. Garden care once a week. Cleaning can be arranged.",
    "walk_heading": "Walk through the house",
    "close": "Close",
    "block_front_garden": "Front garden",
    "block_kitchen": "Kitchen",
    "block_bedroom_1": "Bedroom 1",
    "block_bedroom_2": "Bedroom 2",
    "block_bathroom": "Bathroom",
    "block_back_garden": "Back garden",
    "block_laundry": "Laundry and drying",
    "about_front_garden": (
        "The way in from the gate: a garden 3.5 m wide and 9 m deep, beside the kitchen."
    ),
    "about_kitchen": (
        "A long kitchen, 2.5 m wide and 9 m deep, along the garden: a real kitchen for everyday "
        "cooking and a table to eat together."
    ),
    "about_bathroom": "The bathroom, off the corridor that leads to the two bedrooms.",
    "about_laundry": "A corner to wash and dry clothes, across the corridor from the bathroom.",
    "about_bedroom_1": "A calm bedroom at the back of the house, away from the gate.",
    "about_bedroom_2": "The second bedroom, next to the first, opening onto the back garden.",
    "about_back_garden": (
        "A small triangle of garden at the back corner, easy to look after. Garden care once a "
        "week is included."
    ),
    "sketch_chip": "Sketch · not to scale",
    "sketch_note": "A hand sketch of the 6 × 18 m plan, not the architect's drawing.",
    "plan_hint": "Tap a room on the plan to look inside.",
    "plan_label": "Plan of the house: tap a room",
    "section_word": "Section",
    "gate": "gate",
    "hall": "hall",
    "room_of": "of",
    "room_empty": "No photo of this room yet",
    "room_previous": "Previous room",
    "room_next": "Next room",
}

VI: dict[str, str] = {
    "marker": "01 · căn nhà",
    "heading": "Căn",
    "heading_accent": "nhà",
    "owner_line": (
        "Mình đã xây một căn nhà vườn nhỏ ở Hòa Xuân, và rất mong có người đến biến nó thành"
    ),
    "owner_line_accent": "nhà của mình một thời gian.",
    "why": (
        "Mình muốn một căn nhà sống dễ chịu mỗi ngày, chứ không chỉ đẹp trong ảnh: một khoảnh "
        "vườn nhỏ, nắng sớm, một hiên nhà để ngồi. Ở chính là căn nhà ấy."
    ),
    "room_bedroom": "Phòng ngủ · hai",
    "room_lightwell": "Giếng trời",
    "room_veranda": "Hiên nhà",
    "room_kitchen": "Phòng khách & bếp",
    "room_garden_evening": "Vườn sau",
    "fact_bedrooms": "phòng ngủ",
    "fact_gardens": "khoảng vườn",
    "fact_light_well": "giếng trời",
    "fact_household": "hộ thuê một lúc",
    "included": "Đã bao gồm",
    "included_line": "Nội thất cơ bản. Chăm vườn mỗi tuần một lần. Có thể sắp xếp người dọn dẹp.",
    "walk_heading": "Đi một vòng quanh nhà",
    "close": "Đóng",
    "block_front_garden": "Vườn trước",
    "block_kitchen": "Bếp",
    "block_bedroom_1": "Phòng ngủ 1",
    "block_bedroom_2": "Phòng ngủ 2",
    "block_bathroom": "Phòng vệ sinh",
    "block_back_garden": "Vườn sau",
    "block_laundry": "Giặt và phơi",
    "about_front_garden": "Lối vào từ cổng: khu vườn rộng 3,5 m, sâu 9 m, nằm cạnh gian bếp.",
    "about_kitchen": (
        "Gian bếp dài, rộng 2,5 m, sâu 9 m, chạy dọc khu vườn: bếp thật để nấu mỗi ngày và bàn "
        "để cùng ăn."
    ),
    "about_bathroom": "Phòng vệ sinh, mở ra hành lang dẫn vào hai phòng ngủ.",
    "about_laundry": "Góc giặt và phơi đồ, đối diện phòng vệ sinh qua hành lang.",
    "about_bedroom_1": "Phòng ngủ yên tĩnh ở phía sau nhà, xa cổng.",
    "about_bedroom_2": "Phòng ngủ thứ hai, cạnh phòng thứ nhất, nhìn ra vườn sau.",
    "about_back_garden": (
        "Mảnh vườn tam giác nhỏ ở góc sau nhà, dễ chăm. Đã bao gồm chăm vườn mỗi tuần một lần."
    ),
    "sketch_chip": "Phác thảo · không theo tỉ lệ",
    "sketch_note": "Phác tay mặt bằng 6 × 18 m, chưa phải bản vẽ của kiến trúc sư.",
    "plan_hint": "Chạm vào một phòng trên bản vẽ để xem bên trong.",
    "plan_label": "Mặt bằng căn nhà: chạm vào một phòng",
    "section_word": "Mặt cắt",
    "gate": "cổng",
    "hall": "hành lang",
    "room_of": "/",
    "room_empty": "Chưa có ảnh phòng này",
    "room_previous": "Phòng trước",
    "room_next": "Phòng sau",
}
