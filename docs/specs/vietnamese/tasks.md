# Tasks: vietnamese

An epic of three tasks. T1 lays the ground (addresses, the texts modules, the switch, the shell and the search tags); then T2 (chapters 01–02 and photo alt texts) and T3 (chapters 03–05 and the owner's Vietnamese reply time) run in parallel: each writes its own texts modules and templates and they share no file. Until T2 and T3 are merged into the epic branch, `/vi/` shows those chapters in English; the epic reaches `main` only whole.

## Query budget

| Page | Queries on main | After T1 | After T2 | After T3 |
|---|---|---|---|---|
| `/` | 1 | 1 | 1 | 1 |
| `/vi/` | (404) | 1 | 1 | 1 |
| `/sitemap.xml`, `/robots.txt`, the old addresses (301), a 404 | 0 | 0 | 0 | 0 |

T1 adds the one-query test of `/vi/` (M18 in `src/pages/tests/test_vietnamese_shell.py`); T2 and T3 keep it and every one-query test of `/` on `main` (for example `src/pages/tests/test_one_page.py::test_home_page_makes_one_query`) unchanged.

## T1: The Vietnamese page at /vi/, the switch and the search tags

- **ACs:** AC1–AC14, AC23
- **Matrix rows:** M1–M18, M33
- **Files likely touched:** `src/config/settings.py`, `src/config/urls.py`, `src/pages/urls.py`, `src/pages/views.py`, `src/pages/seo.py`, `src/pages/language.py` (NEW: the language of a request, the texts of a part), `src/pages/texts/__init__.py` (NEW), `src/pages/texts/shell.py` (NEW), `src/pages/context_processors.py`, `src/pages/photos.py` (the optional `alt_vi` field only, empty for now), `src/templates/base.html`, `src/templates/404.html`, `src/templates/includes/header.html`, `src/templates/includes/nav_links.html`, `src/templates/includes/footer.html`, `src/templates/includes/hero.html`, `src/templates/includes/media.html`, `src/pages/templates/pages/home.html`, `src/static/js/daypart.js`, `src/static/js/lang-switch.js` (NEW), `src/static/css/site.css`, `src/pages/tests/test_vietnamese_shell.py` (NEW), `docs/specs/vietnamese/decisions/T1.md` (NEW)
- **Depends on:** none
- **Risk:** medium
- **needs-ui:** yes
- **Screens to capture:** `/` → `.site-header` (`intro-day`); `/vi/` → `.site-header` (`vi-intro-day`); `/vi/` at 390px → `.site-header` (`vi-intro-phone`); `/vi/not-here/` → `main` (`vi-not-found`)
- **Label:** `agent:ready`

## T2: Chapters 01 and 02 and the photos in Vietnamese

- **ACs:** AC15–AC17, AC23
- **Matrix rows:** M19–M25, M33
- **Files likely touched:** `src/pages/texts/house.py` (NEW), `src/pages/texts/hoa_xuan.py` (NEW), `src/pages/templates/pages/chapters/house.html`, `src/pages/templates/pages/chapters/hoa_xuan.html`, `src/templates/includes/floor_plan.html`, `src/pages/floor_plan.py`, `src/pages/photos.py`, `src/pages/tests/test_vietnamese_chapters_house_area.py` (NEW), `docs/specs/vietnamese/decisions/T2.md` (NEW)
- **Depends on:** T1
- **Risk:** low
- **needs-ui:** yes
- **Screens to capture:** `/vi/` → `#house` (`vi-house`); `/vi/` → `#hoa-xuan` (`vi-hoa-xuan`); `/vi/` at 390px → `#house` (`vi-house-phone`)
- **Label:** `agent:ready`

## T3: Chapters 03 to 05 and the Vietnamese reply time

- **ACs:** AC18–AC23
- **Matrix rows:** M26–M33
- **Files likely touched:** `src/owner_content/models.py`, `src/owner_content/migrations/0003_sitesettings_reply_time_vi.py` (NEW; the number follows the last migration on `main`), `src/owner_content/admin.py`, `src/owner_content/services.py`, `src/pages/views.py` (the owner's settings in the page's language), `src/pages/texts/rent.py` (NEW), `src/pages/texts/faq.py` (NEW), `src/pages/texts/contact.py` (NEW), `src/pages/templates/pages/chapters/rent.html`, `src/pages/templates/pages/chapters/faq.html`, `src/pages/templates/pages/chapters/contact.html`, `src/pages/templatetags/price.py`, `src/owner_content/tests/test_reply_time_vi.py` (NEW), `src/pages/tests/test_vietnamese_rent_faq_contact.py` (NEW), `docs/specs/vietnamese/decisions/T3.md` (NEW)
- **Depends on:** T1
- **Risk:** medium (migration)
- **needs-ui:** yes
- **Screens to capture:** `/vi/` → `#rent` (`vi-rent`); `/vi/` → `#faq` (`vi-faq`); `/vi/` → `#contact` (`vi-contact`); `/vi/` at 390px → `#faq` (`vi-faq-phone`); `/owner/owner_content/sitesettings/1/change/` → `#sitesettings_form` (`owner-settings`)
- **Label:** `agent:ready`

The exact "Existing tests that change" of each task are settled when its issue is written (`pinned_tests.py --unlisted`), on the `main` of that day.
