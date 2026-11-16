"""The texts of chapter 01, the house, and of the walk through the house
(docs/specs/vietnamese/texts.md, section "Chapter 01").

Accent words are their own keys (`heading_accent`, `owner_line_accent`) so the markup stays in the
template. The owner's greeting comes from the owner's settings, not from here. The `block_*` keys
are the names of the blocks of the floor plan (`pages.floor_plan`).
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
    "layout": "The layout",
    "layout_bedrooms": "Two bedrooms",
    "layout_bathroom": "One bathroom",
    "layout_living": "Living room and kitchen",
    "layout_mezzanine": "Mezzanine",
    "layout_light_well": "Light well",
    "layout_gardens": "Front and back gardens",
    "layout_veranda": "Covered veranda",
    "layout_laundry": "Laundry, drying and storage area",
    "included": "Included",
    "included_line": "Basic furniture. Garden care once a week. Cleaning can be arranged.",
    "walk_heading": "Walk through the house",
    "schematic": "Schematic",
    "schematic_note": (
        "Schematic until the architect's plan: the rooms of the house, not their real layout."
    ),
    "dialog_label": "Photo",
    "close": "Close",
    "block_front_garden": "Front garden",
    "block_living_kitchen": "Living room and kitchen",
    "block_light_well": "Light well",
    "block_bedroom_1": "Bedroom 1",
    "block_bedroom_2": "Bedroom 2",
    "block_bathroom": "Bathroom",
    "block_mezzanine": "Mezzanine",
    "block_veranda": "Covered veranda",
    "block_back_garden": "Back garden",
    "block_laundry": "Laundry, drying and storage",
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
    "layout": "Bố cục",
    "layout_bedrooms": "Hai phòng ngủ",
    "layout_bathroom": "Một phòng tắm",
    "layout_living": "Phòng khách và bếp",
    "layout_mezzanine": "Gác lửng",
    "layout_light_well": "Giếng trời",
    "layout_gardens": "Vườn trước và vườn sau",
    "layout_veranda": "Hiên có mái che",
    "layout_laundry": "Khu giặt, phơi và kho",
    "included": "Đã bao gồm",
    "included_line": "Nội thất cơ bản. Chăm vườn mỗi tuần một lần. Có thể sắp xếp người dọn dẹp.",
    "walk_heading": "Đi một vòng quanh nhà",
    "schematic": "Sơ đồ",
    "schematic_note": (
        "Sơ đồ tạm cho đến khi có bản vẽ của kiến trúc sư: đây là các phòng của căn nhà, "
        "chưa phải cách bố trí thật."
    ),
    "dialog_label": "Ảnh",
    "close": "Đóng",
    "block_front_garden": "Vườn trước",
    "block_living_kitchen": "Phòng khách và bếp",
    "block_light_well": "Giếng trời",
    "block_bedroom_1": "Phòng ngủ 1",
    "block_bedroom_2": "Phòng ngủ 2",
    "block_bathroom": "Phòng tắm",
    "block_mezzanine": "Gác lửng",
    "block_veranda": "Hiên có mái che",
    "block_back_garden": "Vườn sau",
    "block_laundry": "Giặt, phơi và kho",
}
