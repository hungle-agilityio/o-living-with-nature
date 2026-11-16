# Spec: vietnamese

## Summary

The one page in Vietnamese at `/vi/` (phase 3), approved as the `#vi-*` states of `docs/design/prototype.html`:

1. **Addresses.** `/` stays English; `/vi/` is the same page in Vietnamese. A path under `/vi/` that does not exist answers the Vietnamese 404. The old addresses `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` keep their 301 to `/#…`; there are no `/vi/house/` and the like.
2. **Texts.** Every text a visitor reads on `/`, its 404 page and its search tags has a Vietnamese version, given word for word in [texts.md](texts.md). The texts live in typed Python modules, one per part of the page (`src/pages/texts/<part>.py`), each with the same keys for `en` and `vi`, so a missing translation fails a test. No gettext: no `.po` or `.mo` files and no new dependency.
3. **The switch.** "EN · VI" in the header, beside the menu, on both languages and on phones. The current language is marked; the other one is a link to the same page in that language, at the chapter on screen.
4. **Search tags.** Each language has its own `<html lang>`, title, description, canonical, `og:url`, `og:site_name` and JSON-LD description; both pages carry `hreflang` links (`en`, `vi`, `x-default`). The sitemap lists both addresses. Both stay noindex while `INDEXING_ENABLED` is off.
5. **The owner's reply time.** A new admin field "Usual reply time (Vietnamese)" (default "trong vòng một giờ"); the Vietnamese page shows "Mình thường trả lời <value>." The rent line, the greeting and the Call button come in Vietnamese from the owner's settings.

The counter is unchanged (Q6): `/vi/` counts views and presses exactly like `/`, with the same places.

## User story

As a visitor who reads Vietnamese, I want the whole page in Vietnamese at `/vi/`, so that I understand the house, the rent and how to contact the owner without translating.

As a visitor reading in either language, I want an EN · VI switch that keeps my place, so that I can change language without starting over.

As the owner, I want to write my reply time in Vietnamese in the admin, so that the Vietnamese page speaks in my own words.

## Acceptance criteria

### Addresses and language (T1)

- **AC1.** `src/config/settings.py` has `LANGUAGES = [("en", "English"), ("vi", "Tiếng Việt")]` and keeps `LANGUAGE_CODE = "en"`. The home page is served at `/` in English and at `/vi/` in Vietnamese; the language comes from the address only, never from the browser's `Accept-Language` or a cookie (Q4).
- **AC2.** Given a browser that sends `Accept-Language: vi`, when it opens `/`, then the answer is 200 with `<html lang="en">` and the English page, with no redirect; when it opens `/vi/`, the answer is 200 with `<html lang="vi">`.
- **AC3.** `/vi` (no slash) answers 301 to `/vi/`. `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` still answer 301 to `/#house`, `/#hoa-xuan`, `/#faq`, `/#contact`. `/sitemap.xml`, `/robots.txt`, `/healthz/`, `/count/` and `/owner/` keep their addresses (no `/vi/` version).
- **AC4.** Given the path `/vi/not-here/`, when someone opens it, then the answer is 404 with `<html lang="vi">`, the heading "Lối này không dẫn đến đâu cả — vườn ở phía này.", the line and buttons of [texts.md](texts.md) ("Về trang chủ" links to `/vi/`, "Liên hệ Bún" links to `/vi/#contact`), and `noindex, nofollow`. `/not-here/` keeps the English 404 unchanged.
- **AC5.** Each part of the page has a module `src/pages/texts/<part>.py` holding `EN` and `VI`, two dictionaries of text by key; a test checks for every module that `EN` and `VI` have exactly the same keys and no empty value. Templates read the texts of the request's language; no visitor-facing English text stays written in a template or a Python module outside `src/pages/texts/` (the owner's values and photo credits excepted).

### The switch and the shell (T1)

- **AC6.** Given `/` at 1440px, when the page loads, then the header shows "EN · VI" to the right of the menu links, "EN" marked current (`aria-current="true"`, not a link) and "VI" a link to `/vi/` with `hreflang="vi"` and `lang="vi"`; the switch has `aria-label="Language"` (on `/vi/`: `aria-label="Ngôn ngữ"`, "VI" current, "EN" links to `/` with `hreflang="en"`). Prototype: `#intro-day`, `#vi-intro-day`.
- **AC7.** Given `/vi/` at 390px, when the page loads, then "EN · VI" shows in the header row between the clock line and the Menu button, on one line, without covering either. Prototype: `#vi-intro-phone`.
- **AC8.** Given a visitor on `/` reading chapter 04 (the FAQ heading above the middle of the screen), when they press "VI", then `/vi/#faq` opens at the FAQ chapter. This is a small script (`src/static/js/lang-switch.js`, deferred) that sets the link's hash to the chapter whose top is above the middle of the screen; without JavaScript the link opens `/vi/` at the top. Over the hero it carries no hash.
- **AC9.** Given `/vi/` at 14:52 in Hòa Xuân (day), when the page loads, then the header line reads "14:52 ở Hòa Xuân · Ban ngày"; at 18:00 it reads "18:00 ở Hòa Xuân · Hoàng hôn", and when the theme changes while the page is open the script writes the Vietnamese label (Bình minh, Ban ngày, Hoàng hôn, Ban đêm). `/` keeps "It's 14:52 in Hòa Xuân · Day" unchanged.
- **AC10.** Given `/vi/`, when the page loads, then the menu (desktop row and phone menu) reads Căn nhà, Hòa Xuân, Giá thuê, Hỏi đáp, Liên hệ, linking to `/vi/#house`, `/vi/#hoa-xuan`, `/vi/#rent`, `/vi/#faq`, `/vi/#contact`; the wordmark Ở links to `/vi/`; the hero, the footer, the "Illustrative" chips ("Ảnh minh hoạ", "Video minh hoạ") and the credits ("Ảnh: Pexels") read as in [texts.md](texts.md), "Shell". The footer preview links stay `?t=dawn` and the like, on the same address.

### Search tags (T1)

- **AC11.** Given `/vi/`, the `<head>` holds title "Ở — Nhà vườn cho thuê nguyên căn ở Hòa Xuân, Đà Nẵng", the description of [texts.md](texts.md), canonical and `og:url` `<SITE_BASE_URL>/vi/`, `og:site_name` "Ở — Sống cùng thiên nhiên", and a JSON-LD whose `name`, `description` and `url` are those three values (`telephone` and `address` unchanged; `priceRange` becomes Vietnamese in AC19). `/` keeps all its tags unchanged.
- **AC12.** Both `/` and `/vi/` hold, right after the canonical, `<link rel="alternate" hreflang="en" href="<SITE_BASE_URL>/">`, `<link rel="alternate" hreflang="vi" href="<SITE_BASE_URL>/vi/">` and `<link rel="alternate" hreflang="x-default" href="<SITE_BASE_URL>/">`. The 404 pages hold none.
- **AC13.** `sitemap.xml` lists `<SITE_BASE_URL>/` and `<SITE_BASE_URL>/vi/`, each `<url>` with the three `xhtml:link` alternates of AC12 (`xmlns:xhtml="http://www.w3.org/1999/xhtml"` on `urlset`), and nothing else. With `INDEXING_ENABLED` off both pages say `noindex, nofollow`; with it on both say `index, follow`.
- **AC14.** `/vi/` makes one database query, as `/` (Query budget in [tasks.md](tasks.md)).

### Chapters 01 and 02 (T2)

- **AC15.** Given `/vi/`, when the visitor reads chapter 01 (`#house`), then every text reads as [texts.md](texts.md), "Chapter 01": the label "01 · căn nhà", the heading "Căn nhà" with "nhà" in the accent, "Chào bạn, mình là Bún. …" with the owner's first name from the admin, the room labels, the facts row (2 phòng ngủ, 2 khoảng vườn, 1 giếng trời, 1 hộ thuê một lúc), the layout list, "Đã bao gồm", and the walk through ("Đi một vòng quanh nhà", room names, "Sơ đồ", its note, "Đóng"). Prototype: `#vi-house`, `#vi-house-phone`.
- **AC16.** Given `/vi/`, when the visitor reads chapter 02 (`#hoa-xuan`), then every text reads as [texts.md](texts.md), "Chapter 02" ("Mọi thứ bạn cần hằng ngày đều ở gần.", Siêu thị · ngay bên kia đường, Chợ · khoảng 10 phút, Biển, Sân bay · khoảng 15 phút, "Hòa Xuân trên Google Maps ↗"). Prototype: `#vi-hoa-xuan`.
- **AC17.** Every photo of `src/pages/photos.py` has a Vietnamese alt text, word for word from [texts.md](texts.md), "Photo alt texts"; on `/vi/` every `<img>` alt, every floor plan `data-alt` and the dialog it opens use it, and every credit reads "Ảnh: …". A photo with no Vietnamese alt text shows its English one (tested with a made-up photo). `/` keeps every English alt text.

### Chapters 03 to 05 and the owner's settings (T3)

- **AC18.** `SiteSettings` gains `reply_time_vi`, "Usual reply time (Vietnamese)", at most 60 characters, required, default "trong vòng một giờ", help text `Shown on the Vietnamese page as "Mình thường trả lời …", for example "trong vòng một giờ".`; the help text of `reply_time` becomes `Shown on the English page as "I usually reply …", for example "within an hour".`. A migration adds the column with that default for the existing record. The admin shows it right under "Usual reply time". Prototype: `#owner-settings`.
- **AC19.** Given the owner's settings first name "Bún", price 13 to 14 million, Vietnamese reply time "trong vòng một giờ" and all three numbers, when someone opens `/vi/`, then chapter 03 shows "Từ 13–14 triệu đồng mỗi tháng" with "triệu" and "mỗi tháng" in the accent, buttons "Gọi điện", "WhatsApp", "Zalo", the terms and the quote of [texts.md](texts.md); the FAQ shows "Chào bạn, mình là Bún." and "Mình thường trả lời trong vòng một giờ." and the eight questions and answers of [texts.md](texts.md) (the rent answer "Từ 13–14 triệu đồng mỗi tháng."); chapter 05 shows "Bạn sẽ ở lại chứ?". The phone contact bar shows the same three buttons, and the JSON-LD `priceRange` of `/vi/` is "Từ 13–14 triệu đồng mỗi tháng" (`/` keeps "From 13–14 million VND a month"). Prototype: `#vi-rent`, `#vi-faq`, `#vi-contact`, `#vi-rent-phone`, `#vi-faq-phone`.
- **AC20.** Given only a "from" price of 13 million, then `/vi/` reads "Từ 13 triệu đồng mỗi tháng"; given no price, the rent line reads "Hỏi mình về giá thuê nhé" and the FAQ rent answer "Hỏi mình về giá thuê nhé.".
- **AC21.** Given no phone, WhatsApp or Zalo in the admin, when someone opens `/vi/`, then there are no contact buttons and no phone contact bar, the FAQ keeps the greeting and reply line, and chapter 05 reads "Thông tin liên hệ sẽ sớm có.". Prototype: `#vi-rent-no-channel`, `#vi-faq-no-channel`, `#vi-contact-no-channel`.
- **AC22.** The contact buttons on `/vi/` keep their links and their `data-channel` and `data-place` values (`call`, `whatsapp`, `zalo`; `bar`, `rent`, `faq`, `contact`), so a press on `/vi/` is counted as on `/` (Q6).
- **AC23.** `/` keeps every English text and value it shows today; every test on `main` passes unchanged, except the tests each task lists under "Existing tests that change".

## Edge cases

- Empty: no price, no contact channel (AC20, AC21); a photo without a Vietnamese alt text (AC17); the Vietnamese reply time cannot be empty (AC18).
- Large data: none: two pages, one settings record.
- Permissions: only the owner edits the reply time at `/owner/`; visitors cannot choose anything but the address.
- Unknown paths under `/vi/` give the Vietnamese 404 (AC4); a query string on `/vi/` is never echoed into the search tags, as on `/`.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Who writes the Vietnamese texts | Claude translates, the owner approves in the prototype ([texts.md](texts.md)) | The owner writes them | Fastest; the owner kept the last word ("Prototype ổn", 2026-11-16) |
| Q2 Form of address | "mình – bạn" | "tôi – anh/chị" | Warm, as the English voice |
| Q3 Where the switch is | "EN · VI" in the header, keeps the chapter | Footer only | Seen at once on every screen |
| Q4 Redirect by browser language | No, the visitor chooses | Redirect on the first visit | Search engines and shared links always reach the page asked for |
| Q5 The reply time in Vietnamese | A second admin field (migration) | A fixed list of replies | The owner keeps writing it in their own words |
| Q6 Count per language | No change to the counter | A language column (migration) | Smaller scope; the goal counts contacts, not languages |
| How texts are stored (technical) | Typed modules `src/pages/texts/<part>.py` with `EN` and `VI` | Django gettext (`.po`/`.mo`) | No gettext tools on Render or the Mac mini, no new dependency, and a test catches a missing translation; one module per part lets tasks run in parallel |
| The admin's language | English | Vietnamese | The owner's admin is outside phase 3 |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

States added to `docs/design/prototype.html` and approved with "Prototype ổn" (2026-11-16): `#vi-intro-day`, `#vi-intro-dawn`, `#vi-intro-dusk`, `#vi-intro-night`, `#vi-house`, `#vi-hoa-xuan`, `#vi-rent`, `#vi-faq`, `#vi-contact`, `#vi-rent-no-channel`, `#vi-faq-no-channel`, `#vi-contact-no-channel`, `#vi-intro-phone`, `#vi-house-phone`, `#vi-rent-phone`, `#vi-faq-phone`, `#vi-not-found`, `#vi-not-found-phone`, `#owner-settings`. Changed: every English site state gains the "EN · VI" switch (for example `#intro-day`, `#intro-phone`, `#not-found`).

## Open questions
