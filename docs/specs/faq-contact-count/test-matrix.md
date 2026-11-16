# Test matrix: faq-contact-count

All new tests are in `src/counter/tests/test_faq_place.py` (NEW), task T1.

| Row | AC | Case | Check | Level | Test file | Task |
|---|---|---|---|---|---|---|
| M1 | AC1 | normal | `[(v, str(l)) for v, l in DailyCount.Place.choices]` equals `[("bar", "Phone bar"), ("rent", "Rent chapter"), ("faq", "FAQ chapter"), ("contact", "Contact chapter")]`, and the `place` field has `max_length == 7`. | unit | `src/counter/tests/test_faq_place.py` | T1 |
| M2 | AC2 | normal | The file `src/counter/migrations/0002_daily_count_faq_place.py` exists, depends on `("counter", "0001_initial")` and has one operation, an `AlterField` of `place`; `call_command("makemigrations", "counter", check=True, dry_run=True)` raises nothing. | unit | `src/counter/tests/test_faq_place.py` | T1 |
| M3 | AC3 | normal | Given no counts, when `kind=click&channel=<c>&place=faq` is posted twice for each of `call`, `whatsapp`, `zalo`, then each answers `204` with an empty body and the row of today, `click`, `<c>`, `faq` has a count of 2. | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M4 | AC4 | error | Posting `kind=click&channel=call&place=<p>` for `p` in `hero`, `FAQ`, `""` answers `400` and `DailyCount.objects.count() == 0`. | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M5 | AC5 | normal | Given owner settings with Call, WhatsApp and Zalo numbers, when `/` is opened, then every `a[data-channel]` has a `data-place` in the four values, the links inside `<section id="faq">` have `data-place="faq"`, and posting each link's channel and place as a click answers `204`. | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M6 | AC5 | empty | Given owner settings with no channel at all, when `/` is opened, then the page has no `a[data-channel]` link and the test of M5 finds nothing to reject (n/a for posting: there is no button). | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M7 | AC6 | normal | Given 5 Call/bar on 2 Nov, 4 Zalo/contact on 3 Nov and 3 WhatsApp/faq on 4 Nov 2026 (today 13 Nov 2026), when `build_report()` runs and the owner opens `/owner/counter/dailycount/`, then `by_place` labels are `["Phone bar", "Rent chapter", "FAQ chapter", "Contact chapter"]` with This month `[5, 0, 3, 4]`, the summary has 12 clicks this month, and the page shows "FAQ chapter". | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M8 | AC7 | empty | Given the demo counts with no `faq` row, when `build_report()` runs, then the "FAQ chapter" row is `(0, 0, 0)`. | unit | `src/counter/tests/test_faq_place.py` | T1 |
| M9 | AC8 | empty | Given no counts, when the owner opens the report, then the page has "Nothing counted yet. Counts start when someone opens the site." and no "FAQ chapter" text. | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M10 | AC9 | edge | With one view row and then with 40 rows across the four places, `build_report()` makes exactly 2 queries each time. | integration | `src/counter/tests/test_faq_place.py` | T1 |
| M11 | AC10 | normal | `bash scripts/check.sh` passes; `test_report.py::test_by_channel_and_by_place_rows_in_order_with_zeros` expects `("FAQ chapter", 0, 0, 0)` third. | manual | run `bash scripts/check.sh` from the repository root | T1 |
