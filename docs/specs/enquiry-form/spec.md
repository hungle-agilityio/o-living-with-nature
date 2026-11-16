# Spec: the rental enquiry form (epic)

## Summary

A new feature `src/enquiries/` keeps the messages visitors leave in a form at the end of chapter 05 ("ở lại?", `#contact`) of the home page, in English at `/` and in Vietnamese at `/vi/`. The form sits under the Call, WhatsApp and Zalo buttons, also when the owner has no channel yet. A message sent is stored, counted in "Contact counts", and announced to the owner's phone by an ntfy push that carries no personal data. The owner reads the messages in `/owner/` under "Enquiries", marks them New or Replied, and answers outside the site. A message is deleted 12 months after it arrived. The page keeps working without JavaScript, sets no cookie, and `GET /` still makes one database query.

Prototype states: see "Design". Every test on `main` passes unchanged, except the ones a task lists under "Existing tests that change".

## User story

As a visitor who would rather not call a stranger, I want to leave my name, how to reach me, when I would move in and a short message, so that the owner can answer me when it suits us both.

As the owner (Bún), I want to be told on my phone when a message arrives and to read and mark the messages in `/owner/`, so that no interested person is missed and I can count real contacts.

Names used below:

- **The form:** the block `#enquiry` inside `section#contact`, after `.contact__row`.
- **Reply to:** the field `reply_to`, an email address or a phone number (WhatsApp or Zalo).
- **Move-in months:** the 12 months that start with the current month in Đà Nẵng (`Asia/Ho_Chi_Minh`); on 16 Nov 2026 they are November 2026 to October 2027.
- **Stay choices:** `1-3`, `3-6`, `6-12`, `12+`, shown as "1–3 months", "3–6 months", "6–12 months", "A year or more" (VI: "1–3 tháng", "3–6 tháng", "6–12 tháng", "Từ một năm trở lên").
- **Daily limit:** 20 enquiries stored per Đà Nẵng day for the whole site.

## Acceptance criteria

### Storage and the address that takes a message (T1)

- **AC1.** A new Django app `enquiries` (in `INSTALLED_APPS`) has one model `Enquiry` (admin name "Enquiry", plural "Enquiries") with: `created_at` (set on save), `name` (up to 80 characters), `reply_to` (up to 120), `move_in` (`YYYY-MM` or empty), `stay` (one of the stay choices or empty), `message` (up to 1000), `language` (`en` or `vi`) and `status` (`new` or `replied`, default `new`). The migration `src/enquiries/migrations/0001_initial.py` creates it. Nothing else about the visitor is stored: no IP address, user agent, referrer, cookie or visitor id.
- **AC2.** A Django form `EnquiryForm` checks the fields: `name`, `reply_to` and `message` are required after trimming spaces; `reply_to` is an email address (Django's email validator) or a phone number with 8 to 15 digits once spaces, `+`, `-`, `.`, `(` and `)` are removed; `move_in` is empty or one of the move-in months; `stay` is empty or a stay choice; the lengths are those of AC1. A hidden field `website` (the trap) must stay empty.
- **AC3.** Given the English page, when a visitor posts `name=Anna K.`, `reply_to=anna.k@example.com`, `move_in=2027-01`, `stay=6-12` and a message to `POST /enquiry/`, then one `Enquiry` with `language=en` and `status=new` is stored and the answer is a `303` redirect to `/?enquiry=sent#enquiry`. The same post to `POST /vi/enquiry/` stores `language=vi` and redirects to `/vi/?enquiry=sent#enquiry`.
- **AC4.** Given a post with the trap field `website` filled, when it is sent, then nothing is stored, nothing is counted, no push is sent, and the answer is the same `303` redirect as AC3 (the sender sees a thank-you).
- **AC5.** Given a post that fails AC2 (for example an empty name and `reply_to=0905 12`), when it is sent, then nothing is stored and the answer is `400` with the home page of that language, the form showing the errors of AC13 and the values the visitor typed (the trap field is never echoed).
- **AC6.** Given 20 enquiries already stored since midnight in Đà Nẵng, when a 21st valid post arrives, then nothing is stored and the answer is `429` with the home page of that language showing the paused block of AC15 in place of the form. At 00:00 Đà Nẵng time the limit starts again.
- **AC7.** A post whose `Origin` header is present and is not the site's own origin answers `403` and stores nothing. A post without `Origin` is accepted. The address needs no CSRF token and no response of `/enquiry/` sets a cookie for a visitor without a session. `GET /enquiry/` answers `405`.
- **AC8.** When an enquiry is stored, every enquiry whose `created_at` is more than 365 days old is deleted first, in one query.
- **AC9.** A stored valid post makes at most 3 database queries (limit count, old-row delete, insert) before the redirect. A refused post (AC5) makes at most 1. `GET /` still makes one query.
- **AC10.** No name, reply-to value or message is ever written to a log.

### The form on the page (T2)

- **AC11.** Given the owner has set Call, WhatsApp and Zalo, when a visitor opens `/` and scrolls to `#contact`, then under the buttons they see the label "Or leave me a message" and a form with the fields "Your name", "How can I reply?" (placeholder "Email, or a WhatsApp / Zalo number"), "When would you move in? (optional)" with "Not sure yet" and the 12 move-in months written "November 2026" … "October 2027", "For how long? (optional)" with "Not sure yet" and the 4 stay choices, "Your message" (placeholder "Who will live here, what matters to you…"), the line "I keep your message only to reply to you, and delete it after 12 months. No cookies." and the button "Send message". The form posts to `/enquiry/` with `method="post"`. It matches the prototype state `#enquiry` (desktop) and `#enquiry-phone` (390×844, one column, full-width button).
- **AC12.** Given the Vietnamese page `/vi/`, when the visitor scrolls to `#contact`, then the same form shows "Hoặc để lại lời nhắn cho mình", "Tên của bạn", "Mình liên lạc lại bằng cách nào?" (placeholder "Email, hoặc số WhatsApp / Zalo"), "Bạn định vào ở tháng nào? (không bắt buộc)" with "Chưa chắc" and the months "Tháng 11/2026" … "Tháng 10/2027", "Ở trong bao lâu? (không bắt buộc)", "Lời nhắn" (placeholder "Ai sẽ ở, điều gì quan trọng với bạn…"), the line "Mình chỉ giữ lời nhắn để trả lời bạn, và xóa sau 12 tháng. Không dùng cookie." and the button "Gửi lời nhắn", posting to `/vi/enquiry/` (prototype `#vi-enquiry`, `#vi-enquiry-phone`).
- **AC13.** Given a refused post (AC5) with an empty name, `reply_to=0905 12` and an empty message, when the page comes back, then above the fields it shows "3 things need a look before I can read your message." (one error: "1 thing needs a look before I can read your message."; VI: "Còn 3 chỗ cần xem lại trước khi gửi."), and under each field its line: empty name "Please tell me your name." (VI "Bạn cho mình biết tên nhé."), empty reply-to "Please leave an email or a phone number so I can reply." (VI "Bạn để lại email hoặc số điện thoại để mình trả lời nhé."), wrong reply-to "That doesn’t look like an email or a phone number." (VI "Email hoặc số điện thoại này có vẻ chưa đúng."), empty message "Please write a few words." (VI "Bạn viết vài dòng nhé."), too long "Please keep this under {n} characters." (VI "Bạn viết ngắn hơn {n} ký tự nhé."), a value not in a list "Please pick from the list." (VI "Bạn chọn trong danh sách nhé."). Each field in error has `aria-invalid="true"` and `aria-describedby` pointing to its line. Prototype `#enquiry-errors`, `#enquiry-errors-phone`, `#vi-enquiry-errors`.
- **AC14.** Given `/?enquiry=sent`, when the page opens at `#enquiry`, then in place of the form it shows the label "Message sent" and the line "Thank you, your message is with me." followed by the owner's reply line in the accent ("I usually reply within an hour."); on `/vi/?enquiry=sent`: "Đã gửi" and "Cảm ơn bạn, mình đã nhận được lời nhắn." followed by "Mình thường trả lời trong vòng một giờ.". The block has `role="status"`. With no reply time set, only the thank-you sentence shows. Prototype `#enquiry-sent`, `#enquiry-sent-phone`, `#vi-enquiry-sent`.
- **AC15.** Given the daily limit is reached (AC6), when the page comes back, then in place of the form it shows the label "Messages paused for today" and "Many messages came in today, so the form rests until tomorrow. Please use Call, WhatsApp or Zalo above, or try again tomorrow."; when the owner has no channel the last sentence is "Please try again tomorrow." VI: "Hôm nay tạm dừng nhận lời nhắn", "Hôm nay có nhiều lời nhắn nên form nghỉ đến mai. Bạn gọi hoặc nhắn WhatsApp, Zalo ở trên, hoặc thử lại ngày mai nhé." / "… Bạn thử lại ngày mai nhé.". Prototype `#enquiry-paused`, `#enquiry-no-channel-paused`, `#vi-enquiry-paused`, `#vi-enquiry-no-channel-paused`.
- **AC16.** Given the owner has no contact channel, when a visitor opens `/`, then "Contact details are on their way." shows as on `main` and the form shows under it (prototype `#enquiry-no-channel`).
- **AC17.** The name, reply-to and message values echoed in an error page carry `data-sensitive`. The trap field sits off screen, has `aria-hidden="true"`, `tabindex="-1"` and `autocomplete="off"`. The form works without JavaScript and adds no script file. At 390×844 the page has no sideways scroll.
- **AC18.** `GET /` and `GET /vi/` make one database query, with or without `?enquiry=sent`.

### The push to the owner's phone (T3)

- **AC19.** A setting `NTFY_TOPIC_URL` is read from the environment (empty by default) and listed in `render.yaml` with `sync: false`. When it is set and an enquiry is stored (not for the trap, a refused post or the limit), the site sends one HTTPS `POST` to that address with the body "New enquiry on Ở" (UTF-8), the header `Title: New enquiry` (ASCII only) and the header `Click: <SITE_BASE_URL>/owner/enquiries/enquiry/`. The push carries no name, reply-to, move-in, stay or message.
- **AC20.** The push uses only the Python standard library, with a timeout of 3 seconds. When `NTFY_TOPIC_URL` is empty nothing is sent. When the push fails (timeout, error, non-2xx), the enquiry is still stored, the visitor still gets the redirect of AC3, and the log line names only the failure ("ntfy push failed: <error class>"). Tests never call the network.

### Counting messages (T4)

- **AC21.** `DailyCount` gets the kind `message` ("Message") with an empty channel and the place `contact`; the migration `src/counter/migrations/0003_daily_count_message_kind.py` changes the choices. Each stored enquiry adds 1 to the message row of its Đà Nẵng day (at most 2 more queries, so a stored post makes at most 5). The trap, a refused post, the limit and a logged-in staff user (as in contact-counter AC6) add nothing.
- **AC22.** `POST /count/` still refuses `kind=message` with `400`: messages are counted only by the server.
- **AC23.** Given 2 messages this month, 1 last month and 3 in all, when the owner opens "Contact counts", then each summary column adds "Messages sent" under "Contact clicks" (2, 1, 3), "By channel" adds the row "Form (messages sent)" (2, 1, 3), and "By month" adds the column "Messages" after "Total clicks". "Contact clicks" and "clicks per 100 views" are unchanged. Prototype `#counter-report`. With nothing counted the report still shows only the line of contact-counter AC17. The report's query count stays the same with 1 or 400 rows.

### The inbox in the admin (T5)

- **AC24.** Given a logged-in owner, when they open `/owner/`, then "Enquiries" is listed under "Enquiries" with a View link (prototype `#owner-home`). The list at `/owner/enquiries/enquiry/` shows, newest first, the columns Received ("16 Nov 2026, 09:12", Đà Nẵng time), Name, Reply to, Move in ("Jan 2027" or "Not sure yet"), Stay ("6–12 months" or "Not sure yet") and Status (a "New" or "Replied" badge); a filter "By status" with All, New, Replied; the actions "Mark as replied" and "Mark as new"; under the table the line "Newest first. Each enquiry is deleted 12 months after it arrived. The site never sends a reply for you: answer by email, WhatsApp or Zalo, then mark it as replied." Prototype `#owner-enquiries`, `#owner-enquiries-phone`.
- **AC25.** Given no enquiry, when the owner opens the list, then it shows "No enquiries yet. They appear here when someone sends the form on the site." and "Each enquiry is deleted 12 months after it arrived." (prototype `#owner-enquiries-empty`).
- **AC26.** Given the enquiry of Anna K., when the owner opens it, then the page "Enquiry from Anna K." shows Received with the page language ("16 Nov 2026, 09:12 (English page)" or "(Vietnamese page)"), Name, Reply to (a `mailto:` link when it is an email, plain text otherwise), Move in ("January 2027"), Stay, Message (line breaks kept), "Deleted on" (created date + 365 days, "16 Nov 2027") and a Status choice New or Replied with Save and Delete (prototype `#owner-enquiry`). Only Status can change. There is no Add.
- **AC27.** Name, reply-to and message cells in the list and the detail carry `data-sensitive`. A visitor who is not logged in is sent to the admin login. Opening the list deletes enquiries older than 365 days first (AC8 rule).
- **AC28.** At 390×844 the list has no sideways page scroll; the table scrolls in its own box. The list's query count is the same with 1 and with 300 enquiries.

### Every task

- **AC29.** `bash scripts/check.sh` passes. Every test on `main` passes unchanged, except the ones the task lists under "Existing tests that change".

## Edge cases

- **Empty:** no enquiry: the admin list shows AC25; "Contact counts" with no message shows 0 in the new row and column. The page always shows the empty form on `GET`.
- **Large data:** at most 20 enquiries a day and 365 days kept: at most 7 300 rows; in practice a few a month. The admin list is paginated by Django (100 a page).
- **Permissions:** anyone may post the form (spam is limited by the trap, the origin check and the daily limit). Only a logged-in staff user reads the enquiries.
- **No JavaScript:** the form posts and the page reloads at `#enquiry`; nothing depends on a script.
- **Owner with no channel:** the form is the only way to reach the owner (AC16); the paused text drops the buttons (AC15).
- **Push not set or down:** the enquiry is kept and readable in `/owner/` (AC20).
- **Month change:** a form opened on 31 October and sent on 1 November with `move_in` of the old first month is refused with "Please pick from the list." (AC13).
- **Owner testing the form while logged in:** the enquiry is stored and pushed, but not counted (AC21).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1: fields | Name, reply-to (email or phone), move-in month, stay, message | Name, reply-to, message only; or adding people and pets | Enough to judge a serious enquiry, still short |
| Q2: place | In chapter 05 under the buttons, "Or leave me a message" | A chapter of its own | Keeps the one page; the buttons stay first |
| Q3: tell the owner | ntfy push with no personal data | Email through an email API; no alert | The owner already uses ntfy; nothing personal leaves the site; Render's free plan does not send SMTP mail |
| Q4: spam | Hidden trap field, origin check, 20 a day | Cloudflare Turnstile or reCAPTCHA | No third-party script and no cookie (domain rule) |
| Q5: keeping data | Delete after 12 months, said under the form | Keep until the owner deletes; 6 months | Long enough for a long-term rental cycle, honest to the visitor |
| Q6: counting | Each stored message counted in "Contact counts" | Not counted | The 10-contact goal counts messages too |
| Q7: after sending | Thank-you in place, works without JavaScript | JavaScript only | Same rule as the rest of the site |
| Q8: inbox | List with New / Replied and actions | Read only | The owner needs to see what is still open |
| (build) daily limit | 20 a day for the whole site | Per IP | No IP is stored |
| (build) old rows | Deleted when a message is stored and when the list opens | A scheduled job | Render's free plan has no cron |
| (build) state after sending | Redirect to `?enquiry=sent` | A session message | A session would set a cookie |
| (build) month list | The next 12 months from the current Đà Nẵng month, plus "Not sure yet" | A free date field | Monthly rental, simple to read |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html`, approved with "Prototype ổn" on 2026-11-16 (https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j). States added: `#enquiry`, `#enquiry-errors`, `#enquiry-sent`, `#enquiry-paused`, `#enquiry-no-channel`, `#enquiry-no-channel-paused`, `#enquiry-phone`, `#enquiry-errors-phone`, `#enquiry-sent-phone`, `#vi-enquiry`, `#vi-enquiry-errors`, `#vi-enquiry-sent`, `#vi-enquiry-paused`, `#vi-enquiry-no-channel-paused`, `#vi-enquiry-phone`, `#owner-enquiries`, `#owner-enquiries-empty`, `#owner-enquiry`, `#owner-enquiries-phone`. States changed: `#owner-home` (Enquiries module), `#counter-report` (messages), and every home state (the form under the buttons). The demo names (Anna K., Minh T., Lukas & Mai) and the `example.com` addresses are demo data only.

## Open questions
