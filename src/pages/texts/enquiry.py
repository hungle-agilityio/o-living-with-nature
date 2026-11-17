"""The texts of the enquiry form in chapter 05 (docs/specs/enquiry-form/spec.md).

`{n}` is replaced by a number (the count of fields to look at, or a maximum length).
"""

EN: dict[str, str] = {
    "lead": "Or leave me a message",
    "name": "Your name",
    "reply_to": "How can I reply?",
    "reply_to_placeholder": "Email, or a WhatsApp / Zalo number",
    "move_in": "When would you move in?",
    "stay": "For how long?",
    "optional": "(optional)",
    "message": "Your message",
    "message_placeholder": "Who will live here, what matters to you…",
    "trap": "Leave this empty",
    "privacy": (
        "I keep your message only to reply to you, and delete it after 12 months. No cookies."
    ),
    "send": "Send message",
    "summary_one": "1 thing needs a look before I can read your message.",
    "summary_many": "{n} things need a look before I can read your message.",
    "error_name": "Please tell me your name.",
    "error_reply_empty": "Please leave an email or a phone number so I can reply.",
    "error_reply_invalid": "That doesn’t look like an email or a phone number.",
    "error_message": "Please write a few words.",
    "error_too_long": "Please keep this under {n} characters.",
    "error_choice": "Please pick from the list.",
    "sent_label": "Message sent",
    "thanks": "Thank you, your message is with me.",
    "paused_label": "Messages paused for today",
    "paused": (
        "Many messages came in today, so the form rests until tomorrow. "
        "Please use Call, WhatsApp or Zalo above, or try again tomorrow."
    ),
    "paused_no_channel": (
        "Many messages came in today, so the form rests until tomorrow. Please try again tomorrow."
    ),
}

VI: dict[str, str] = {
    "lead": "Hoặc để lại lời nhắn cho mình",
    "name": "Tên của bạn",
    "reply_to": "Mình liên lạc lại bằng cách nào?",
    "reply_to_placeholder": "Email, hoặc số WhatsApp / Zalo",
    "move_in": "Bạn định vào ở tháng nào?",
    "stay": "Ở trong bao lâu?",
    "optional": "(không bắt buộc)",
    "message": "Lời nhắn",
    "message_placeholder": "Ai sẽ ở, điều gì quan trọng với bạn…",
    "trap": "Để trống ô này",
    "privacy": "Mình chỉ giữ lời nhắn để trả lời bạn, và xóa sau 12 tháng. Không dùng cookie.",
    "send": "Gửi lời nhắn",
    "summary_one": "Còn 1 chỗ cần xem lại trước khi gửi.",
    "summary_many": "Còn {n} chỗ cần xem lại trước khi gửi.",
    "error_name": "Bạn cho mình biết tên nhé.",
    "error_reply_empty": "Bạn để lại email hoặc số điện thoại để mình trả lời nhé.",
    "error_reply_invalid": "Email hoặc số điện thoại này có vẻ chưa đúng.",
    "error_message": "Bạn viết vài dòng nhé.",
    "error_too_long": "Bạn viết ngắn hơn {n} ký tự nhé.",
    "error_choice": "Bạn chọn trong danh sách nhé.",
    "sent_label": "Đã gửi",
    "thanks": "Cảm ơn bạn, mình đã nhận được lời nhắn.",
    "paused_label": "Hôm nay tạm dừng nhận lời nhắn",
    "paused": (
        "Hôm nay có nhiều lời nhắn nên form nghỉ đến mai. "
        "Bạn gọi hoặc nhắn WhatsApp, Zalo ở trên, hoặc thử lại ngày mai nhé."
    ),
    "paused_no_channel": (
        "Hôm nay có nhiều lời nhắn nên form nghỉ đến mai. Bạn thử lại ngày mai nhé."
    ),
}
