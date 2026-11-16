# Test matrix: vietnamese

The tests planned per AC of [spec.md](spec.md). Test files: T1 `src/pages/tests/test_vietnamese_shell.py`, T2 `src/pages/tests/test_vietnamese_chapters_house_area.py`, T3 `src/pages/tests/test_vietnamese_rent_faq_contact.py` and `src/owner_content/tests/test_reply_time_vi.py` (all NEW).

| Row | AC | Case | Check | Level | Test file | Task |
|---|---|---|---|---|---|---|
| M1 | AC1 | normal | `settings.LANGUAGES == [("en", "English"), ("vi", "Tiếng Việt")]` and `LANGUAGE_CODE == "en"`. | unit | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M2 | AC2 | normal | Given `Accept-Language: vi`, when `/` is opened, then 200, no redirect, `<html lang="en">`; when `/vi/` is opened, then 200 and `<html lang="vi">`. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M3 | AC2 | edge | Given a `django_language` cookie set to `vi`, when `/` is opened, then `<html lang="en">`. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M4 | AC3 | normal | `/vi` → 301 `/vi/`; the four old addresses → 301 `/#…`; `/sitemap.xml`, `/robots.txt`, `/healthz/` → 200 and `/vi/sitemap.xml`, `/vi/owner/` → 404. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M5 | AC4 | normal | Given `/vi/not-here/`, then 404, `lang="vi"`, the heading, line and two buttons of texts.md with links `/vi/` and `/vi/#contact`, `noindex, nofollow`. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M6 | AC4 | empty | n/a: the 404 page has no data to be empty; `/not-here/` keeps its English texts (asserted). | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M7 | AC5 | normal | For every module in `src/pages/texts/`, `EN.keys() == VI.keys()` and no value is empty. | unit | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M8 | AC5 | error | A made-up module with a key missing in `VI` makes the key check fail (the check function returns the missing key). | unit | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M9 | AC6 | normal | Given `/`, then one `.lang-switch` with `aria-label="Language"`, "EN" a `<span class="lang-switch__current">`, not a link, and no `aria-current` in the page, "VI" an `<a href="/vi/" hreflang="vi" lang="vi">`; on `/vi/` the mirror, `aria-label="Ngôn ngữ"`. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M10 | AC6, AC7 | narrow screen | Given `/vi/` at 390px, the switch is visible, on one line, and its box overlaps neither the clock line nor the Menu button; at 1440px it is right of the menu links. | browser | `src/pages/tests/test_vietnamese_shell.py` (Screens to capture) | T1 |
| M11 | AC8 | normal | Given `/` scrolled to `#faq`, when "VI" is pressed, then the address is `/vi/#faq`; at the top of the page it is `/vi/`. | browser | Screens to capture of T1 | T1 |
| M12 | AC8 | empty | n/a: without JavaScript the link is the plain `/vi/` (asserted in the HTML: `href="/vi/"`). | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M13 | AC9 | normal | Given 14:52 (day) on `/vi/`, the line reads "14:52 ở Hòa Xuân · Ban ngày"; at 18:00 "18:00 ở Hòa Xuân · Hoàng hôn"; `/` keeps "It's 14:52 in Hòa Xuân · Day". `daypart.js` takes its labels from the page (asserted in the HTML: `data-labels`). | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M14 | AC10 | normal | Given `/vi/`, the five menu links read and link as AC10 (both menus), the wordmark links to `/vi/`, hero, footer, chips and credits read as texts.md "Shell". | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M15 | AC11 | normal | Given `/vi/`, title, description, canonical, `og:url`, `og:site_name` and the JSON-LD `name`, `description`, `url` are the Vietnamese values; `/` unchanged. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M16 | AC12 | normal | `/` and `/vi/` hold the three alternates right after the canonical; `/not-here/` and `/vi/not-here/` hold none. | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M17 | AC13 | normal | The sitemap lists exactly the two addresses with the three `xhtml:link` each; both pages noindex with indexing off, index with it on. | unit | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M18 | AC14 | normal | `/vi/` makes exactly one query (`django_assert_num_queries(1)`). | integration | `src/pages/tests/test_vietnamese_shell.py` | T1 |
| M19 | AC15 | normal | Given owner "Bún", `/vi/#house` shows every text of texts.md "Chapter 01" and no English text of the chapter. | integration | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M20 | AC15 | empty | n/a: the chapter has no data that can be empty; the walk through's empty room blocks keep their Vietnamese names (asserted). | integration | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M21 | AC16 | normal | `/vi/#hoa-xuan` shows every text of texts.md "Chapter 02". | integration | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M22 | AC16 | empty | n/a: the chapter has no data that can be empty. | integration | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M23 | AC17 | normal | Every photo of `photos.py` has the Vietnamese alt text of texts.md; on `/vi/` every `<img alt>` and `data-alt` is Vietnamese and every credit starts "Ảnh: "; on `/` all English. | integration | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M24 | AC17 | empty | A made-up photo with no Vietnamese alt text shows its English alt text on `/vi/`. | unit | `src/pages/tests/test_vietnamese_chapters_house_area.py` | T2 |
| M25 | AC15–AC17 | narrow screen | `/vi/#house` at 390px matches `#vi-house-phone`: labels and the facts row fit without overflow. | browser | Screens to capture of T2 | T2 |
| M26 | AC18 | normal | The field's name, label, length, default and help texts are as AC18; the migration gives the existing record "trong vòng một giờ"; the admin change page lists it right under "Usual reply time". | integration | `src/owner_content/tests/test_reply_time_vi.py` | T3 |
| M27 | AC18 | empty | Saving the admin form with an empty Vietnamese reply time is refused with "This field is required." | integration | `src/owner_content/tests/test_reply_time_vi.py` | T3 |
| M28 | AC19 | normal | Given the settings of AC19, `/vi/` shows the rent line with its accents, the three buttons, terms, quote, greeting, reply line, eight Q&A and "Bạn sẽ ở lại chứ?"; the JSON-LD `priceRange` of `/vi/` is "Từ 13–14 triệu đồng mỗi tháng" and of `/` unchanged. | integration | `src/pages/tests/test_vietnamese_rent_faq_contact.py` | T3 |
| M29 | AC20 | edge | One price → "Từ 13 triệu đồng mỗi tháng"; no price → "Hỏi mình về giá thuê nhé" and "Hỏi mình về giá thuê nhé.". | integration | `src/pages/tests/test_vietnamese_rent_faq_contact.py` | T3 |
| M30 | AC21 | empty | No channel → no buttons, no bar, greeting and reply line kept, "Thông tin liên hệ sẽ sớm có.". | integration | `src/pages/tests/test_vietnamese_rent_faq_contact.py` | T3 |
| M31 | AC22 | normal | On `/vi/` the buttons keep their `href`, `data-channel` and `data-place` values, the same as on `/`. | integration | `src/pages/tests/test_vietnamese_rent_faq_contact.py` | T3 |
| M32 | AC19, AC21 | narrow screen | `/vi/#rent` and `/vi/#faq` at 390px match `#vi-rent-phone` and `#vi-faq-phone`; "Gọi điện" fits its pill in the contact bar. | browser | Screens to capture of T3 | T3 |
| M33 | AC23 | normal | `bash scripts/check.sh` passes; only the tests listed under "Existing tests that change" of each task differ from `main`. | integration | all | T1, T2, T3 |
