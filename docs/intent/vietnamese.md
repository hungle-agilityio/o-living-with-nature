# Intent: vietnamese

## Problem

The site is English only. Phase 3 (`docs/intent/website.md`, "Later phases") adds Vietnamese, because many people who rent a whole house in Đà Nẵng for months read and search in Vietnamese ("thuê nhà nguyên căn Hòa Xuân", "nhà vườn cho thuê Đà Nẵng"). Today a Vietnamese visitor reads every word in English, and there is no Vietnamese page for search engines to find once indexing is on.

## Goal

`/vi/` is the same one page as `/`, every word a visitor reads in Vietnamese in the owner's voice ("mình – bạn"), with an EN · VI switch in the header that keeps the chapter being read, `hreflang` links between the two, both addresses in the sitemap, a Vietnamese 404 under `/vi/`, and a Vietnamese reply time the owner edits in the admin. English addresses never change.

## Users

- Visitors who read Vietnamese, and those who read English (who now see the switch).
- The owner, who sets the Vietnamese reply time at `/owner/`.
- Search engines, once indexing is on (the site stays noindex until real photos exist).

## Out of scope

- Turning indexing on, real photos (phase 2).
- Choosing the language from the browser or redirecting by it (Q4: the visitor chooses).
- A Vietnamese admin: `/owner/` stays English.
- Counting views or presses per language (Q6: the counter stays as it is).
- Owner-editable page texts: texts live in the repository and change through issues.
