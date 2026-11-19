# Tasks: contact-one-place

One epic of two tasks. Both change `src/static/css/chapters/contact.css`, so T2 waits for T1. Each task's issue lists its existing tests that change (found with `pinned_tests.py`) before it gets `agent:ready`.

## Query budget

| Page | Queries on main | After T1 | After T2 |
|---|---|---|---|
| `/` | 1 | 1 | 1 |
| `/vi/` | 1 | 1 | 1 |

No task adds a query-cap test that a later task must list: each new test file checks one query on `/` and `/vi/`, as the existing ones do.

## T1: Show the contact buttons in one place, and the phone bar from chapter 02

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC13, AC14
- **Matrix rows:** M1–M12, M21, M22
- **Files likely touched:** `src/pages/templates/pages/chapters/rent.html`, `src/pages/templates/pages/chapters/faq.html`, `src/static/css/chapters/rent.css`, `src/static/css/chapters/faq.css`, `src/static/css/chapters/contact.css`, `src/static/js/contact-bar.js`, `src/pages/tests/test_contact_one_place.py` (NEW), `docs/specs/contact-one-place/decisions/T1.md` (NEW); plus the existing tests it changes (rent and FAQ buttons, the bar's watch list: `test_rent_and_contact.py`, `test_rent_quote_and_contact_row.py`, `test_faq_two_columns.py`, `test_contact_bar_once.py`, `test_vietnamese_rent_faq_contact.py`, `src/counter/tests/test_faq_place.py`, `src/owner_content/tests/test_site_settings.py`, as `pinned_tests.py` finds them)
- **Depends on:** none
- **Risk:** medium (many existing tests change)
- **needs-ui:** yes
- **Screens to capture:** `/#rent` desktop → `#rent` (design `one-rent`); `/#faq` desktop → `.faq-side` (design `one-faq`); `/#house` at 390x844 → viewport bottom (design `one-phone-house`); `/#hoa-xuan` at 390x844 → `.contact-bar` (design `one-phone-hoa-xuan`); `/#contact` at 390x844 → `#contact` (design `one-phone-contact`)
- **Label:** `agent:ready`

## T2: Put the enquiry form on its own panel and make Send message the one filled button

- **ACs:** AC9, AC10, AC11, AC12, AC13, AC14
- **Matrix rows:** M13–M22
- **Files likely touched:** `src/templates/includes/enquiry_form.html`, `src/static/css/chapters/contact.css`, `src/pages/tests/test_enquiry_panel.py` (NEW), `docs/specs/contact-one-place/decisions/T2.md` (NEW); plus the existing tests it changes (the submit button markup in `src/pages/tests/test_enquiry_form.py`, as `pinned_tests.py` finds them)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/#enquiry` desktop → `#enquiry` (design `one-send`); `/#contact` desktop → `.contact__row` (design `one-contact`); `/#enquiry` at 390x844 → `#enquiry` (design `one-phone-send`)
- **Label:** `agent:ready`
