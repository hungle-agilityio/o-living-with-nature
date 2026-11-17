"""The texts of the journal pages: the list at `/journal/` and each note (journal spec, #137).

`{name}` is the owner's first name from the site settings; `{title}` is the note's title.
"""

EN: dict[str, str] = {
    "label": "Journal",
    "heading": "Notes from Hòa Xuân",
    "lead": (
        "I write here now and then about the house, the neighbourhood and what staying a "
        "while is like. — {name}"
    ),
    "read": "Read →",
    "older": "Older notes →",
    "newer": "← Newer notes",
    "back": "← All notes",
    "contact_line": "Like the sound of it?",
    "form_link": "Or leave me a message →",
    "other": "Another note:",
    "list_title": "Journal · Ở",
    "note_title": "{title} · Ở",
}

VI: dict[str, str] = {
    "label": "Nhật ký",
    "heading": "Ghi chép từ Hòa Xuân",
    "lead": ("Thỉnh thoảng mình viết ở đây về căn nhà, khu xung quanh và chuyện ở lâu. — {name}"),
    "read": "Đọc →",
    "older": "Ghi chép cũ hơn →",
    "newer": "← Ghi chép mới hơn",
    "back": "← Tất cả ghi chép",
    "contact_line": "Bạn thấy hợp chứ?",
    "form_link": "Hoặc để lại lời nhắn cho mình →",
    "other": "Ghi chép khác:",
    "list_title": "Nhật ký · Ở",
    "note_title": "{title} · Ở",
}
