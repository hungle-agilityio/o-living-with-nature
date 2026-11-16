# Test matrix: the rental enquiry form

The tests planned per AC of `spec.md`, for QA and the build: one row per check. Test files: T1 `src/enquiries/tests/test_enquiry_endpoint.py`, T2 `src/pages/tests/test_enquiry_form.py`, T3 `src/enquiries/tests/test_notify.py`, T4 `src/counter/tests/test_message_count.py`, T5 `src/enquiries/tests/test_inbox.py`.

| Row | AC | Case | Check | Level | Test file | Task |
|---|---|---|---|---|---|---|
| M1 | AC1 | normal | `Enquiry` has the fields, lengths and defaults of AC1; the migration applies; `status` defaults to `new`. | unit | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M2 | AC1 | edge | The model has no field for an IP address, user agent, referrer, cookie or visitor id. | unit | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M3 | AC2 | normal | `EnquiryForm` accepts `anna.k@example.com`, `+84 905 000 111` and `0905-000-111`; `move_in=2027-01` on 16 Nov 2026; `stay=6-12`. | unit | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M4 | AC2 | error | It refuses an empty or spaces-only name or message, `0905 12` (6 digits), a 16-digit number, `anna@`, `move_in=2026-10` and `2027-11` on 16 Nov 2026, `stay=2-4`, a name of 81 characters, a message of 1001. | unit | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M5 | AC3 | normal | Given the English page, when Anna K. posts a valid enquiry to `/enquiry/`, then one row with `language=en`, `status=new` is stored and the answer is `303` to `/?enquiry=sent#enquiry`. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M6 | AC3 | normal | The same post to `/vi/enquiry/` stores `language=vi` and redirects to `/vi/?enquiry=sent#enquiry`. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M7 | AC4 | edge | Given `website=http://spam.example`, when posted, then 0 rows, `303` to the sent page. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M8 | AC5 | error | Given an empty name and `reply_to=0905 12`, when posted, then 0 rows, `400`, the context has a bound form with the errors and `enquiry_state` "errors", and the trap value is not in the response. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M9 | AC6 | edge | Given 20 rows created today in Đà Nẵng, when a 21st valid post arrives, then still 20 rows and `429` with `enquiry_state` "paused"; given 20 rows from yesterday (23:59 Đà Nẵng), a post at 00:01 is stored. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M10 | AC7 | permission | A post with `Origin: https://evil.example` answers `403`, stores nothing; without `Origin` it is accepted; no `Set-Cookie`; `GET /enquiry/` answers `405`. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M11 | AC8 | edge | Given a row created 366 days ago and one 364 days ago, when a valid post is stored, then the 366-day row is gone and the 364-day row stays. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M12 | AC9 | normal | A stored post makes ≤ 3 queries; a refused post ≤ 1; `GET /` still 1. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M13 | AC10 | edge | With `caplog` at DEBUG, a stored and a refused post log no name, reply-to or message. | integration | `src/enquiries/tests/test_enquiry_endpoint.py` | T1 |
| M14 | AC29 | normal | `bash scripts/check.sh` passes. | manual | n/a: the build runs it and pastes the output | T1 |
| M15 | AC11 | normal | Given Call, WhatsApp and Zalo set, when `/` opens, then `#contact` holds `#enquiry` after `.contact__row`, with the English labels, placeholders, 12 months "November 2026" … "October 2027" (clock fixed at 16 Nov 2026), 4 stay choices, the privacy line, "Send message", `method="post"` and `action="/enquiry/"`. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M16 | AC11 | narrow screen | At 390×844 the fields are one column, the button full width, no sideways scroll (prototype `enquiry-phone`). | browser | `src/pages/tests/test_enquiry_form.py` | T2 |
| M17 | AC12 | normal | Given `/vi/`, the form shows the Vietnamese texts, "Tháng 11/2026" … "Tháng 10/2027" and `action="/vi/enquiry/"`. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M18 | AC13 | error | Given a refused post with an empty name, `reply_to=0905 12` and an empty message, then "3 things need a look before I can read your message.", the three field lines, `aria-invalid="true"` and `aria-describedby` on each; with one error the singular sentence; on `/vi/enquiry/` the Vietnamese lines. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M19 | AC13 | edge | An empty reply-to shows "Please leave an email or a phone number so I can reply."; a 1001-character message shows "Please keep this under 1000 characters."; `stay=2-4` shows "Please pick from the list.". | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M20 | AC14 | normal | Given `/?enquiry=sent`, then `#enquiry` shows "Message sent", "Thank you, your message is with me." and "I usually reply within an hour." in the accent, `role="status"`, and no form; `/vi/?enquiry=sent` shows the Vietnamese lines. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M21 | AC14 | empty | Given no reply time set, `/?enquiry=sent` shows only "Thank you, your message is with me.". | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M22 | AC15 | edge | Given the limit reached, the `429` page shows "Messages paused for today" and the sentence with "Please use Call, WhatsApp or Zalo above"; with no channel, the sentence ends "Please try again tomorrow."; on `/vi/` the Vietnamese lines. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M23 | AC16 | empty | Given no contact channel, `/` shows "Contact details are on their way." and the form under it. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M24 | AC17 | edge | Echoed name, reply-to and message carry `data-sensitive`; the trap has `aria-hidden="true"`, `tabindex="-1"`, `autocomplete="off"`; the home page links no new script. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M25 | AC18 | normal | `GET /`, `GET /vi/` and `GET /?enquiry=sent` each make one query. | integration | `src/pages/tests/test_enquiry_form.py` | T2 |
| M26 | AC29 | normal | `bash scripts/check.sh` passes. | manual | n/a: the build runs it and pastes the output | T2 |
| M27 | AC19 | normal | Given `NTFY_TOPIC_URL=https://ntfy.sh/o-living-test`, when an enquiry is stored, then one POST (mocked `urllib.request.urlopen`) goes there with the body "New enquiry on Ở", `Title: New enquiry` and `Click: <SITE_BASE_URL>/owner/enquiries/enquiry/`. | unit | `src/enquiries/tests/test_notify.py` | T3 |
| M28 | AC19 | edge | The request body and headers contain none of the posted name, reply-to, move-in, stay or message; the trap, a refused post and the limit send nothing. | integration | `src/enquiries/tests/test_notify.py` | T3 |
| M29 | AC20 | empty | Given `NTFY_TOPIC_URL` empty, nothing is sent and the enquiry is stored. | unit | `src/enquiries/tests/test_notify.py` | T3 |
| M30 | AC20 | error | Given `urlopen` raises a timeout, the enquiry is stored, the answer is still `303`, and the log has "ntfy push failed: TimeoutError" and nothing personal; the call passes `timeout=3`. | integration | `src/enquiries/tests/test_notify.py` | T3 |
| M31 | AC19 | normal | `render.yaml` lists `NTFY_TOPIC_URL` with `sync: false`. | unit | `src/enquiries/tests/test_notify.py` | T3 |
| M32 | AC21 | normal | Given a stored enquiry on 16 Nov 2026 (Đà Nẵng), the `message` row of that day with place `contact` is 1; a second makes 2; a stored post makes ≤ 5 queries. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M33 | AC21 | permission | The trap, a refused post, the limit and a logged-in staff user add nothing to the message row. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M34 | AC22 | error | `POST /count/` with `kind=message` answers `400` and stores nothing. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M35 | AC23 | normal | Given 2 messages this month, 1 last month, the report shows "Messages sent" 2, 1, 3, the row "Form (messages sent)" 2, 1, 3 and the "Messages" column; "Contact clicks" and the rate are unchanged. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M36 | AC23 | empty | Given no count at all, the report shows only "Nothing counted yet. Counts start when someone opens the site."; given views and clicks but no message, the new row and column show 0. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M37 | AC23 | edge | The report's query count is the same with 1 and 400 rows, messages included. | integration | `src/counter/tests/test_message_count.py` | T4 |
| M38 | AC24 | normal | Given 3 enquiries (Anna K. 16 Nov new, Minh T. 14 Nov new, Lukas & Mai 28 Oct replied), the list shows them newest first with the columns, badges, filter, the two actions and the note line; `/owner/` lists "Enquiries". | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M39 | AC24 | edge | "Mark as replied" on Anna K. and Minh T. sets both to `replied`; the filter New then lists none. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M40 | AC25 | empty | Given no enquiry, the list shows "No enquiries yet. They appear here when someone sends the form on the site." and the 12-month line. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M41 | AC26 | normal | The page of Anna K. shows "Enquiry from Anna K.", "16 Nov 2026, 09:12 (English page)", a `mailto:` link, "January 2027", "6–12 months", the message with line breaks, "Deleted on" "16 Nov 2027"; saving Status Replied changes only the status; there is no Add. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M42 | AC27 | permission | Not logged in, `/owner/enquiries/enquiry/` redirects to the admin login; name, reply-to and message cells carry `data-sensitive`. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M43 | AC27 | edge | Given a row 366 days old, opening the list deletes it. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M44 | AC28 | narrow screen | At 390×844 the list has no sideways page scroll; the table scrolls in its box (prototype `owner-enquiries-phone`). | browser | `src/enquiries/tests/test_inbox.py` | T5 |
| M45 | AC28 | edge | The list's query count is the same with 1 and 300 enquiries. | integration | `src/enquiries/tests/test_inbox.py` | T5 |
| M46 | AC29 | normal | T6: `.claude/rules/domain.md` has the two new sentences; `bash scripts/check.sh` passes. | manual | n/a: built by hand; the owner reads the diff | T6 |
| M47 | AC3 | empty | n/a: a post with no fields is the error case of AC5 (M8). | – | – | T1 |
| M48 | AC4, AC5, AC6 | normal, empty | n/a: these ACs are the trap, error and limit cases of AC3; their normal case is M5 and an empty post is M8. | – | – | T1 |
| M49 | AC11, AC12 | empty | n/a: the form is the same with or without data; the no-channel page is M23. | – | – | T2 |
| M50 | AC13, AC15 | normal, empty | n/a: AC13 and AC15 are the error and limit states of the form; its normal state is M15 and its empty (no channel) state is M23. | – | – | T2 |
| M51 | AC16 | normal | n/a: AC16 is the no-channel case; with channels it is M15. | – | – | T2 |
| M52 | AC26 | empty | n/a: the page exists only for a stored enquiry; an unknown id gives Django's admin "doesn't exist" message. | – | – | T5 |

## Allowed values

- "Case" is one of "normal", "empty", "edge", "error", "permission", "narrow screen".
- "Level" is one of "unit", "integration", "browser", "manual".
