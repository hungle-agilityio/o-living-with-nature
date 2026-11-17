"""The texts of the shell: header, menu, switch, footer, hero, labels, the 404 page and the
search tags of the home page (docs/specs/vietnamese/texts.md, section "Shell").

Texts that surround inline markup are split in parts (before, accent, after) so the markup stays
in the template. `{clock}` is a placeholder filled by `{% text %}`.
"""

EN: dict[str, str] = {
    "site_name": "Ở — Living with Nature",
    "seo_title": "Ở — Living with Nature · Garden house for rent in Hòa Xuân, Đà Nẵng",
    "seo_description": (
        "A whole garden house with two bedrooms, rented by the month in Hòa Xuân, Đà Nẵng. "
        "From 13–14 million VND a month, minimum stay one month."
    ),
    "clock_line": "It's {clock} in Hòa Xuân",
    "daypart_dawn": "Dawn",
    "daypart_day": "Day",
    "daypart_dusk": "Dusk",
    "daypart_night": "Night",
    "preview_dawn": "dawn",
    "preview_day": "day",
    "preview_dusk": "dusk",
    "preview_night": "night",
    "footer_preview": "See Ở at",
    "footer_name": "a word for staying · Hòa Xuân, Đà Nẵng",
    "footer_note": (
        'Photos and videos marked "Illustrative" are stand-ins until the house is finished.'
    ),
    "nav_label": "Main",
    "menu_button": "Menu",
    "menu_nav_label": "Menu",
    "switch_label": "Language",
    "menu_house": "The house",
    "menu_hoa_xuan": "Hòa Xuân",
    "menu_rent": "Rent",
    "menu_faq": "FAQ",
    "menu_journal": "Journal",
    "menu_contact": "Contact",
    "footer_journal": "Journal",
    "chip_video": "Illustrative video",
    "chip_photo": "Illustrative photo",
    "credit_photo": "Photo: ",
    "credit_video": "Video: ",
    "hero_gloss_kind": ' · verb · Vietnamese · say "uh?"',
    "hero_gloss_senses": "1. to stay. 2. to live somewhere. 3. ",
    "hero_gloss_accent": "to be at home.",
    "hero_cue": "Scroll, and come in ↓",
    "hero_title_before": "Living ",
    "hero_title_accent": "with",
    "hero_title_after": " nature",
    "hero_line": "A garden house in Hòa Xuân, Đà Nẵng. Two bedrooms, two gardens, ",
    "hero_line_accent": "rented whole, by the month.",
    "contact_bar_label": "Contact",
    "not_found_heading": "This path leads nowhere — the garden is this way.",
    "not_found_line": (
        "The page you were looking for isn't here. It may have moved, or the link has a typo."
    ),
    "not_found_home": "Back to the home page",
    "not_found_contact": "Contact Bún",
}

VI: dict[str, str] = {
    "site_name": "Ở — Sống cùng thiên nhiên",
    "seo_title": "Ở — Nhà vườn cho thuê nguyên căn ở Hòa Xuân, Đà Nẵng",
    "seo_description": (
        "Thuê nhà nguyên căn ở Hòa Xuân, Đà Nẵng: nhà vườn hai phòng ngủ cho thuê theo tháng. "
        "Từ 13–14 triệu đồng mỗi tháng, thuê tối thiểu một tháng."
    ),
    "clock_line": "{clock} ở Hòa Xuân",
    "daypart_dawn": "Bình minh",
    "daypart_day": "Ban ngày",
    "daypart_dusk": "Hoàng hôn",
    "daypart_night": "Ban đêm",
    "preview_dawn": "bình minh",
    "preview_day": "ban ngày",
    "preview_dusk": "hoàng hôn",
    "preview_night": "ban đêm",
    "footer_preview": "Xem Ở lúc",
    "footer_name": "một chữ để ở lại · Hòa Xuân, Đà Nẵng",
    "footer_note": 'Ảnh và video có nhãn "Minh hoạ" là ảnh tạm cho đến khi nhà xây xong.',
    "nav_label": "Chính",
    "menu_button": "Menu",
    "menu_nav_label": "Menu",
    "switch_label": "Ngôn ngữ",
    "menu_house": "Căn nhà",
    "menu_hoa_xuan": "Hòa Xuân",
    "menu_rent": "Giá thuê",
    "menu_faq": "Hỏi đáp",
    "menu_journal": "Nhật ký",
    "menu_contact": "Liên hệ",
    "footer_journal": "Nhật ký",
    "chip_video": "Video minh hoạ",
    "chip_photo": "Ảnh minh hoạ",
    "credit_photo": "Ảnh: ",
    "credit_video": "Video: ",
    "hero_gloss_kind": " · động từ · tiếng Việt · thanh hỏi",
    "hero_gloss_senses": "1. lưu lại. 2. sống ở một nơi. 3. ",
    "hero_gloss_accent": "có mặt ở nhà.",
    "hero_cue": "Cuộn xuống, mời bạn vào nhà ↓",
    "hero_title_before": "Sống ",
    "hero_title_accent": "cùng",
    "hero_title_after": " thiên nhiên",
    "hero_line": "Một căn nhà vườn ở Hòa Xuân, Đà Nẵng. Hai phòng ngủ, hai khoảng vườn, ",
    "hero_line_accent": "cho thuê nguyên căn, theo tháng.",
    "contact_bar_label": "Liên hệ",
    "not_found_heading": "Lối này không dẫn đến đâu cả — vườn ở phía này.",
    "not_found_line": (
        "Trang bạn tìm không có ở đây. Có thể trang đã chuyển chỗ, hoặc đường dẫn bị gõ sai."
    ),
    "not_found_home": "Về trang chủ",
    "not_found_contact": "Liên hệ Bún",
}
