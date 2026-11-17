# Tasks: the journal (epic)

Epic: one epic issue and three task issues on the epic branch (ADR-021, ADR-022), plus one task built by hand (T4). They run one after another: T2 needs T1 (the model and the flags), T3 needs T2 (the journal views and URLs). T4 changes only `.claude/rules/` and is built by hand on the Mac mini once the tick has made the epic branch.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `GET /`, `GET /vi/` | 1 | 1 | 1 | 1 |
| Page not found (`GET /this-page-does-not-exist/`) | 0 | 0 | 0 | 0 |
| `GET /sitemap.xml`, `GET /robots.txt` | 0 | 0 | 0 | 0 |
| `GET /journal/`, `GET /vi/journal/` | – | – | ≤ 3 | ≤ 3 |
| `GET /journal/<slug>/`, `GET /vi/journal/<slug>/` | – | – | ≤ 3 | ≤ 3 |
| "Journal posts" list in `/owner/` | – | same with 1 or 50 notes | same | same |

Every task keeps `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`, `src/owner_content/tests/test_database_and_owner.py::test_public_address_sends_no_cookie_and_asks_the_database_nothing` and `src/owner_content/tests/test_database_and_owner.py::test_not_found_page_sends_no_cookie_and_asks_the_database_nothing` unchanged. T3 keeps the query tests of the journal pages that T2 adds in `src/journal/tests/test_journal_pages.py` (ADR-022).

## T1: Store journal notes and write them in the admin

- **ACs:** AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9
- **Matrix rows:** M1–M18
- **Files likely touched:**
  - `src/journal/__init__.py` (NEW)
  - `src/journal/apps.py` (NEW: connects the save and delete signals)
  - `src/journal/models.py` (NEW)
  - `src/journal/admin.py` (NEW)
  - `src/journal/services.py` (NEW: keeps `journal_en` and `journal_vi` of `SiteSettings` in step)
  - `src/journal/text.py` (NEW: `to_html`)
  - `src/journal/templates/admin/journal/journalpost/change_list.html` (NEW: the empty line of AC6)
  - `src/journal/migrations/__init__.py` (NEW)
  - `src/journal/migrations/0001_initial.py` (NEW)
  - `src/journal/migrations/0002_first_drafts.py` (NEW)
  - `src/journal/tests/__init__.py` (NEW)
  - `src/journal/tests/test_journal_store.py` (NEW)
  - `src/config/settings.py` (`INSTALLED_APPS` only)
  - `src/owner_content/models.py` (`journal_en`, `journal_vi`, `editable=False`)
  - `src/owner_content/migrations/0004_sitesettings_journal_flags.py` (NEW)
  - `src/owner_content/services.py` (`SiteSettingsValue` gains `journal_en` and `journal_vi`, default `False`)
  - `docs/specs/journal/decisions/T1.md` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/owner/journal/journalpost/` → `#content` (design `owner-journal`); `/owner/journal/journalpost/<pk of ten-minutes-from-everything>/change/` → `#content` (design `owner-journal-edit`)
- **Label:** `agent:ready`

## T2: Show the journal at /journal/ and /vi/journal/

- **ACs:** AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21
- **Matrix rows:** M19–M33
- **Files likely touched:**
  - `src/journal/views.py` (NEW)
  - `src/journal/urls.py` (NEW)
  - `src/journal/reading.py` (NEW: the published notes of a language, a page of 12, the other note)
  - `src/journal/templates/journal/list.html` (NEW)
  - `src/journal/templates/journal/note.html` (NEW)
  - `src/pages/texts/journal.py` (NEW: EN and VI texts of the journal pages)
  - `src/static/css/journal.css` (NEW)
  - `src/config/urls.py` (the journal addresses inside `i18n_patterns`)
  - `src/pages/seo.py` (the head of a journal page; `sitemap_xml` unchanged)
  - `src/pages/language.py` (the language switch of a journal page)
  - `src/counter/models.py` (`Place.JOURNAL`)
  - `src/counter/migrations/0004_daily_count_journal_place.py` (NEW)
  - `src/journal/tests/test_journal_pages.py` (NEW)
  - `docs/specs/journal/decisions/T2.md` (NEW)
- **Depends on:** T1
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/journal/` at 1440×900 → `main` (design `journal`); 390×844 → `main` (design `journal-phone`); `/journal/ten-minutes-from-everything/` → `main` (design `journal-note`); 390×844 (design `journal-note-phone`); `/journal/staying-a-month-or-longer/` → `main` (design `journal-note-plain`); `/vi/journal/` → `main` (design `vi-journal`); `/vi/journal/ten-minutes-from-everything/` → `main` (design `vi-journal-note`). The check publishes the two first drafts first.
- **Label:** `agent:ready`

## T3: Add Journal to the menu and footer

- **ACs:** AC22, AC23, AC24
- **Matrix rows:** M34–M37
- **Files likely touched:**
  - `src/templates/includes/nav_links.html`
  - `src/templates/includes/footer.html`
  - `src/pages/texts/shell.py` (`menu_journal`, `footer_journal`: "Journal" / "Nhật ký")
  - `src/pages/views.py` (the home context passes the Journal link from the owner's settings)
  - `src/journal/views.py` (the journal pages pass the link and mark it current)
  - `src/pages/tests/test_journal_link.py` (NEW)
  - `docs/specs/journal/decisions/T3.md` (NEW)
- **Depends on:** T2
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/` at 1440×900 → `.site-header` (design `journal-menu`); `/` → `.site-footer` (design `journal-menu`); `/` with no published note → `.site-header` (design `journal-none`)
- **Label:** `agent:ready`

## T4: Write the journal into the rules (by hand)

- **ACs:** AC25
- **Matrix rows:** M38, M39
- **Files likely touched:** `.claude/rules/domain.md`, `.claude/rules/architecture.md`
- **Depends on:** none (goes into the epic branch once the tick has created it)
- **Risk:** low
- **needs-ui:** no
- **Label:** none (ADR-023, "Exception: .claude/"): built by hand through the Mac mini; the owner clicks Merge.
