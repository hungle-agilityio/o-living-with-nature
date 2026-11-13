# Spec: the contact counter (epic)

## Summary

A new feature `src/counter/` counts, per day in Đà Nẵng time, the views of the home page `/` and the presses on its contact buttons (Call, WhatsApp, Zalo, in the phone bar, the rent chapter and the contact chapter). A small script on `/` reports them to a new address `POST /count/`. The owner reads the totals in a read-only report in the admin at `/owner/`. Nothing changes for visitors: the buttons keep their real links and the page works without JavaScript.

Design of the report: `docs/specs/contact-counter/design.md`. Every test on `main` passes unchanged, except the ones a task lists under "Existing tests that change".

Names used below:

- **kind:** `view` (the page was opened) or `click` (a contact button was pressed).
- **channel:** `call`, `whatsapp` or `zalo`, the `data-channel` of the button (`src/templates/includes/contact_buttons.html`).
- **place:** `bar` (the phone contact bar), `rent` (the rent chapter) or `contact` (the contact chapter), the `data-place` of the button.

## Acceptance criteria

### Storage and the count address (T1)

- **AC1.** A new Django app `counter` (in `INSTALLED_APPS`) has one model of daily totals, `DailyCount` (shown in the admin as "Contact counts"): day (a date), kind, channel, place and count, with one row per day, kind, channel and place (a unique constraint). A view has an empty channel and place. The migration `src/counter/migrations/0001_initial.py` creates it. Nothing else is stored: no IP address, user agent, referrer, cookie or visitor id.
- **AC2.** `POST /count/` with the form fields `kind=view`, or `kind=click&channel=<channel>&place=<place>`, adds 1 to the row of that day, kind, channel and place (creating it at 1 the first time), and answers `204` with an empty body. Two requests in a row give a count of 2. The fields are checked by a Django form.
- **AC3.** Every other request to `/count/` stores nothing: an unknown kind, channel or place, a click without a channel or a place, or a view with a channel or a place answers `400`; a method other than POST answers `405`.
- **AC4.** A POST whose `Origin` header is present and is not the site's own origin (scheme and host of the request) answers `403` and stores nothing. A POST without an `Origin` header is accepted. The address needs no CSRF token, because the visitor has no cookie.
- **AC5.** No response of `/count/` sets a cookie (no `Set-Cookie` header) for a visitor without a session.
- **AC6.** A POST from a logged-in staff user (the owner in `/owner/`) answers `204` and stores nothing, so the owner's own visits are not counted (Q3).
- **AC7.** The day is the date in Đà Nẵng (`Asia/Ho_Chi_Minh`): a count at 23:59 and one at 00:01 Đà Nẵng time go to two different days, also when UTC is still on the same date.
- **AC8.** A valid count from a visitor makes at most 2 database queries. The response of `/` still makes one query.

### The script on the page (T2)

- **AC9.** A new plain script `src/static/js/count.js` is linked with `defer` on `/` only, as the last script of the page, also when the owner has no channel. The 404 page and the admin do not load it.
- **AC10.** When `/` loads, the script sends one view to `/count/` with `navigator.sendBeacon` and the body `kind=view` (`application/x-www-form-urlencoded`); without `sendBeacon`, it uses `fetch` with `method: "POST"` and `keepalive: true`. Each load is one view (Q2): nothing is kept in the browser (no cookie, no `localStorage`, no `sessionStorage`).
- **AC11.** A press on any `a[data-channel]` (a `click`, or an `auxclick` with the middle button) sends one click with its `data-channel` and `data-place`, the same way. The script never stops or delays the link: the button still opens `tel:`, `wa.me` or `zalo.me` as on `main`, and the links in the HTML are unchanged.
- **AC12.** A failed or refused count shows nothing to the visitor and throws no error in the console. The script has no library, no address other than `/count/`, and is under 3 000 bytes.

### The report in the admin (T3)

- **AC13.** The admin index at `/owner/` lists "Contact counts" under "Counter". It opens a read-only report: there is no Add, Change or Delete for counts. A visitor who is not logged in is sent to the admin login.
- **AC14.** The report starts with three columns, "This month", "Last month" and "All time" (Đà Nẵng months), each with page views, contact clicks, and "clicks per 100 views" with one decimal ("–" when there are no views).
- **AC15.** A table "By channel" has the rows Call, WhatsApp and Zalo, and a table "By place" the rows "Phone bar", "Rent chapter" and "Contact chapter", each with the columns This month, Last month and All time. A row with nothing counted shows 0.
- **AC16.** A table "By month" lists, newest first, up to the last 12 months that have any count: the month ("Nov 2026"), views, Call, WhatsApp, Zalo and total clicks.
- **AC17.** With nothing counted, the report shows only the line "Nothing counted yet. Counts start when someone opens the site." and no tables.
- **AC18.** Under the report the line "Daily totals only: no IP address, no cookie. Your own visits while you are logged in are not counted." is shown.
- **AC19.** At 390×844 the page has no sideways scroll; a wide table scrolls inside its own box.
- **AC20.** The number of database queries of the report is the same with 1 count row and with 400 rows.

### Every task

- **AC21.** `bash scripts/check.sh` passes. Every test on `main` passes unchanged, except the ones the task lists under "Existing tests that change".

## Edge cases

- **Empty:** no row yet: the report shows the line of AC17. The page `/` is unchanged.
- **Large data:** one row per day, kind, channel and place: at most 10 rows a day (1 view + 3 channels × 3 places), about 3 650 a year. The report sums in the database (AC20). No row is ever deleted.
- **Permissions:** anyone may POST a count (it can be inflated on purpose; the owner reads the numbers as a guide). Only a logged-in staff user sees the report.
- **No JavaScript, or blocked script:** nothing is counted for that visit; the page and buttons work as on `main`.
- **Owner with no channel:** no buttons, so no clicks; views are still counted.
- **The `?t=` preview links:** a view like any other.
- **Bots that do not run JavaScript:** not counted (Q1).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1: how a page view is counted | The script reports it when the page opens | Count in the view on the server | Bots without JavaScript are left out; `/` keeps its one query |
| Q2: what one view is | Every load of the page | Once per browser tab (`sessionStorage`) | Nothing kept in the browser, simplest |
| Q3: the owner's own visits | Not counted while logged in to `/owner/` | Count everything | The owner checks the site often; that would swamp a small number |
| (docs) how a press is counted | Real links plus a script that reports | A redirect address on the server | Fixed in `docs/intent/website.md` (Q10, epic 4) |
| (docs) what is stored | Daily totals, no IP, no cookie | Single events | Fixed in `docs/intent/website.md` (Q10, epic 4) |

## Design

The report in the admin: `docs/specs/contact-counter/design.md`. Nothing visible changes for visitors.

## Open questions

