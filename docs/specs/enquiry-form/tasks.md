# Tasks: the rental enquiry form (epic)

Epic: one epic issue and five task issues on the epic branch (ADR-021, ADR-022), plus one task built by hand (T6). T1 comes first. T2, T3 and T5 need T1 and share no file, so they run in parallel after it. T4 needs T3 (both change `src/enquiries/services.py`).

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 | After T4 | After T5 |
|---|---|---|---|---|---|---|
| `GET /`, `GET /vi/` (also with `?enquiry=sent`) | 1 | 1 | 1 | 1 | 1 | 1 |
| `POST /enquiry/` stored | – | ≤ 3 | ≤ 3 | ≤ 3 | ≤ 5 | ≤ 5 |
| `POST /enquiry/` refused (errors) | – | ≤ 1 | ≤ 1 | ≤ 1 | ≤ 1 | ≤ 1 |
| `POST /enquiry/` daily limit | – | ≤ 2 | ≤ 2 | ≤ 2 | ≤ 2 | ≤ 2 |
| `POST /count/` (visitor) | ≤ 2 | ≤ 2 | ≤ 2 | ≤ 2 | ≤ 2 | ≤ 2 |
| "Contact counts" report in `/owner/` | same with 1 or 400 rows | same | same | same | same | same |
| "Enquiries" list in `/owner/` | – | – | – | – | – | same with 1 or 300 rows |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`, `src/pages/tests/test_home_hero.py::test_home_page_asks_the_database_one_query` and `src/pages/tests/test_hero_intro.py::test_home_page_still_makes_one_query` unchanged. T2 to T5 keep the query tests of `POST /enquiry/` that T1 adds in `src/enquiries/tests/test_enquiry_endpoint.py`; T4 raises the stored-post cap from 3 to 5 in that file (AC21, ADR-022).

## T1: Store a visitor's enquiry at /enquiry/

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC29
- **Matrix rows:** M1–M14, M47, M48
- **Files likely touched:**
  - `src/enquiries/__init__.py` (NEW)
  - `src/enquiries/apps.py` (NEW)
  - `src/enquiries/models.py` (NEW)
  - `src/enquiries/forms.py` (NEW)
  - `src/enquiries/months.py` (NEW: the move-in months and the stay choices, with their EN and VI labels)
  - `src/enquiries/services.py` (NEW)
  - `src/enquiries/views.py` (NEW)
  - `src/enquiries/urls.py` (NEW)
  - `src/enquiries/migrations/__init__.py` (NEW)
  - `src/enquiries/migrations/0001_initial.py` (NEW)
  - `src/enquiries/tests/__init__.py` (NEW)
  - `src/enquiries/tests/test_enquiry_endpoint.py` (NEW)
  - `src/config/settings.py` (`INSTALLED_APPS` only)
  - `src/config/urls.py` (`/enquiry/` inside `i18n_patterns`, so `/vi/enquiry/` exists)
  - `src/pages/views.py` (the home context takes an optional bound form and a state, so the enquiry view can answer with the home page; `GET /` unchanged)
  - `docs/specs/enquiry-form/decisions/T1.md` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** no (the error and paused blocks are drawn by T2; T1 passes `enquiry_form` and `enquiry_state` in the context and tests the status codes, storage and context)
- **Label:** `agent:ready`

## T2: Show the enquiry form in chapter 05

- **ACs:** AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC29
- **Matrix rows:** M15–M26, M49, M50, M51
- **Files likely touched:**
  - `src/pages/templates/pages/chapters/contact.html`
  - `src/templates/includes/enquiry_form.html` (NEW)
  - `src/static/css/chapters/contact.css`
  - `src/pages/texts/enquiry.py` (NEW: EN and VI texts of the form)
  - `src/pages/tests/test_enquiry_form.py` (NEW)
  - `docs/specs/enquiry-form/decisions/T2.md` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` at 1440×900 → `#enquiry` (design `enquiry`); 390×844 → `#enquiry` (design `enquiry-phone`); `/vi/` → `#enquiry` (design `vi-enquiry`); `/?enquiry=sent` → `#enquiry` (design `enquiry-sent`); a refused post → `#enquiry` (design `enquiry-errors`)
- **Label:** `agent:ready`

## T3: Push "New enquiry on Ở" to the owner's phone

- **ACs:** AC19, AC20, AC29
- **Matrix rows:** M27–M31
- **Files likely touched:**
  - `src/enquiries/notify.py` (NEW)
  - `src/enquiries/services.py` (call the push after an enquiry is stored)
  - `src/config/settings.py` (`NTFY_TOPIC_URL` only)
  - `render.yaml` (`NTFY_TOPIC_URL`, `sync: false`)
  - `src/enquiries/tests/test_notify.py` (NEW)
  - `docs/specs/enquiry-form/decisions/T3.md` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** no
- **Label:** `agent:ready`

## T4: Count messages in "Contact counts"

- **ACs:** AC21, AC22, AC23, AC29
- **Matrix rows:** M32–M37
- **Files likely touched:**
  - `src/counter/models.py`
  - `src/counter/migrations/0003_daily_count_message_kind.py` (NEW)
  - `src/counter/forms.py` (keep `kind=message` out of `/count/`)
  - `src/counter/report.py`
  - `src/counter/templates/admin/counter/report.html`
  - `src/enquiries/services.py` (count a stored enquiry)
  - `src/enquiries/tests/test_enquiry_endpoint.py` (stored-post query cap 3 → 5, added by T1 in this epic)
  - `src/counter/tests/test_message_count.py` (NEW)
  - `docs/specs/enquiry-form/decisions/T4.md` (NEW)
- **Depends on:** T3
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/owner/counter/dailycount/` at 1440×900 with demo counts → `#content` (design `counter-report`)
- **Label:** `agent:ready`

## T5: The Enquiries inbox in the admin

- **ACs:** AC24, AC25, AC26, AC27, AC28, AC29
- **Matrix rows:** M38–M45, M52
- **Files likely touched:**
  - `src/enquiries/admin.py` (NEW)
  - `src/enquiries/inbox.py` (NEW: labels for received time, move in, stay, deleted-on date)
  - `src/enquiries/templates/admin/enquiries/enquiry/change_list.html` (NEW)
  - `src/enquiries/templates/admin/enquiries/enquiry/change_form.html` (NEW)
  - `src/enquiries/tests/test_inbox.py` (NEW)
  - `docs/specs/enquiry-form/decisions/T5.md` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/owner/enquiries/enquiry/` at 1440×900 → `#content` (design `owner-enquiries`), 390×844 → `#content` (design `owner-enquiries-phone`), with no enquiry → `#content` (design `owner-enquiries-empty`), one enquiry → `#content` (design `owner-enquiry`)
- **Label:** `agent:ready`

## T6: Update the domain rule on contact (by hand)

- **ACs:** AC29
- **Matrix rows:** M46
- **Change:** in `.claude/rules/domain.md`, "Business rules", "Contact": add "An enquiry form in the contact chapter keeps a visitor's name, reply address, move-in month, stay and message for the owner, who reads them in `/owner/`; they are deleted after 12 months (`docs/specs/enquiry-form/spec.md`). The site still sends nothing to the visitor." In "Counting", add "and messages sent through the enquiry form".
- **Files likely touched:** `.claude/rules/domain.md`
- **Depends on:** none
- **Risk:** low
- **needs-ui:** no
- **Label:** none (a `.claude/` file: built by hand through the Mac mini, ADR-023 "Exception: .claude/")
