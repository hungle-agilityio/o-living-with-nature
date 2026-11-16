# Spec: faq-contact-count

## Summary

The contact counter learns a fourth place, `faq` ("FAQ chapter"), so that a press on a contact button in the FAQ chapter is stored instead of refused. `DailyCount.Place` gets the value between `rent` and `contact` (the order of the chapters on the page), with a migration that only changes the field's choices (no table change). The owner's report at `/owner/counter/dailycount/` gains the row "FAQ chapter" in its "By place" table. A new test checks that every `data-place` the home page sends is accepted by `/count/`. Visitors see nothing new.

## User story

As the owner, I want presses on the contact buttons in the FAQ chapter to be counted and shown on their own row, so that my report shows every contact the site brings.

## Acceptance criteria

- **AC1.** `DailyCount.Place` in `src/counter/models.py` has exactly four values, in this order: `bar` "Phone bar", `rent` "Rent chapter", `faq` "FAQ chapter", `contact` "Contact chapter". The field `place` keeps `max_length=7`.
- **AC2.** A new migration `src/counter/migrations/0002_daily_count_faq_place.py`, depending on `0001_initial`, holds only an `AlterField` of `place` with the new choices. `makemigrations counter --check --dry-run` finds nothing to do. `0001_initial.py` is unchanged.
- **AC3.** Given no counts yet, when `POST /count/` is sent with `kind=click&channel=<channel>&place=faq` for each channel `call`, `whatsapp` and `zalo`, then each answers `204` with an empty body and the row of today, `click`, that channel and `faq` has a count of 1; sending the same request again gives a count of 2.
- **AC4.** `POST /count/` with `kind=click&channel=call&place=<value>` still answers `400` and stores nothing for a place that is not one of the four, for example `hero`, `FAQ` (capitals) or an empty place.
- **AC5.** Given the owner's settings have a Call, a WhatsApp and a Zalo number, when `/` is opened, then every `a[data-channel]` link has a `data-place` that is one of the four values of AC1, the FAQ chapter's links have `data-place="faq"`, and a `POST /count/` of `kind=click` with each link's `data-channel` and `data-place` answers `204`.
- **AC6.** Given the demo counts of this month (Nov 2026): 5 Call presses in the phone bar on 2 Nov, 4 Zalo presses in the contact chapter on 3 Nov and 3 WhatsApp presses in the FAQ chapter on 4 Nov, when the owner opens the contact counts report, then the "By place" table has the rows, in this order, "Phone bar" 5, "Rent chapter" 0, "FAQ chapter" 3, "Contact chapter" 4 in the column This month, and the summary's clicks this month count the 3 FAQ presses (12 clicks).
- **AC7.** Given no FAQ press has been counted (only the demo counts of `src/counter/tests/test_report.py`), when the owner opens the report, then the "By place" table still has the row "FAQ chapter" with 0 in This month, Last month and All time.
- **AC8.** Given no counts at all, when the owner opens the report, then the page shows only the empty line "Nothing counted yet. Counts start when someone opens the site.", as on `main`.
- **AC9.** `build_report()` still makes exactly 2 database queries, whatever the number of rows.
- **AC10.** `bash scripts/check.sh` passes. Every test on `main` passes unchanged, except `src/counter/tests/test_report.py::test_by_channel_and_by_place_rows_in_order_with_zeros`, whose expected "By place" list gains `("FAQ chapter", 0, 0, 0)` between `("Rent chapter", 0, 2, 3)` and `("Contact chapter", 4, 0, 4)`.

## Edge cases

- **Empty:** no FAQ press yet: the row "FAQ chapter" shows 0 (AC7). No counts at all: only the empty line (AC8).
- **Large data:** one row per day, kind, channel and place: at most 13 rows a day (1 view + 3 channels × 4 places), about 4 750 a year. The report still sums in the database in 2 queries (AC9).
- **Permissions:** unchanged: `/count/` is open to visitors with the same-origin check; the report is for the owner (staff with the view permission) only.
- **Lost presses:** presses in the FAQ before this change were answered `400` and stored nothing; they cannot be counted back.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Lane | Full lane | Fast lane as an exception | The project rule puts every migration in the full lane, even one that only changes choices |
| Q2 Where the "FAQ chapter" row goes in the report | In page order: Phone bar, Rent chapter, FAQ chapter, Contact chapter | Added at the end | The owner reads the rows in the order the visitor meets the chapters |
| Fix in the counter or in the page | Add `faq` to the counter | Send `place=contact` from the FAQ | The FAQ buttons were designed as their own place (#83); merging them into "Contact chapter" would hide where contacts come from |
| Row label | "FAQ chapter" | "FAQ" | Same pattern as "Rent chapter" and "Contact chapter" |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

`docs/design/prototype.html`, state `#counter-report` (and `#counter-report-phone`): the "By place" table has the row "FAQ chapter" between "Rent chapter" and "Contact chapter". Approved with "Prototype ổn" on 2026-11-16. No page a visitor sees changes.

## Open questions
