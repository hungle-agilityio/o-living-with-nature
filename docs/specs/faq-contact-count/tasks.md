# Tasks: faq-contact-count

One task, no epic: the model, its migration, the report test and the new tests belong together and stay well under 400 lines.

## Query budget

| Page | Queries on main | After T1 |
|---|---|---|
| `/owner/counter/dailycount/` (`build_report()`) | 2 | 2 |
| `/` | 1 | 1 |
| `POST /count/` | unchanged | unchanged |

T1 keeps `src/counter/tests/test_report.py::test_report_query_count_does_not_grow` and `test_page_query_count_does_not_grow` unchanged.

## T1: Count the contact presses in the FAQ chapter

- **ACs:** AC1–AC10
- **Matrix rows:** M1–M11
- **Files likely touched:** `src/counter/models.py`, `src/counter/migrations/0002_daily_count_faq_place.py` (NEW), `src/counter/tests/test_faq_place.py` (NEW), `src/counter/tests/test_report.py`, `docs/specs/faq-contact-count/decisions/T1.md` (NEW)
- **Existing tests that change:** `src/counter/tests/test_report.py::test_by_channel_and_by_place_rows_in_order_with_zeros` (the "By place" list gains `("FAQ chapter", 0, 0, 0)` between "Rent chapter" and "Contact chapter")
- **Depends on:** none
- **Risk:** low
- **needs-ui:** yes (the owner's report)
- **Screens to capture:** `/owner/counter/dailycount/` → the "By place" table, design state `counter-report`
- **Label:** `agent:ready`
