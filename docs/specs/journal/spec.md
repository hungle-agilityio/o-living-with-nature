# Spec: the journal (epic)

## Summary

A new feature `src/journal/` lets the owner write short notes ("journal posts") in `/owner/` and publish them. Published notes are listed at `/journal/` and each has its own page at `/journal/<address>/`, in English. A note may also have a Vietnamese version; only notes with one are listed at `/vi/journal/` and shown at `/vi/journal/<address>/`. A note can have one cover photo chosen from the site's own illustrative photos (no upload). Every note ends with a contact block: the price and reply time, the Call, WhatsApp and Zalo buttons (counted with the new place "journal") and a link to the enquiry form. "Journal" appears in the menu and the footer of the home page and the journal pages once a note is published in that language. Two first notes are stored as drafts for the owner to read and publish.

The site stays noindex; `sitemap.xml`, `robots.txt` and the page-not-found page do not change. `GET /` still makes one database query. Prototype states: see "Design". Every test on `main` passes unchanged, except the ones a task lists under "Existing tests that change".

## User story

As a visitor weighing a long stay in Hòa Xuân, I want to read short notes from the owner about the house and the neighbourhood, so that I know what living there is like before I get in touch.

As the owner (Bún), I want to write, publish and edit those notes myself in `/owner/`, so that I can add one whenever I like without asking for a change to the site.

Names used below:

- **Note:** one `JournalPost` record. **Published:** `status = "published"`. **Draft:** `status = "draft"`.
- **Has Vietnamese:** `title_vi`, `summary_vi` and `body_vi` are all filled.
- **Owner's settings:** the `SiteSettingsValue` of `owner_content.services.site_settings(lang)`: `price_line`, `reply_line`, `channels`.
- **Photo keys:** the `key` values of the photo list in `src/pages/photos.py` (`beach-sunset`, `bedroom`, `corner`, `first-light`, `garden-evening`, `kitchen`, `leaves`, `lightwell`, `lit-window`, `market`, `mezzanine`, `street`, `tea`, `veranda` on 2026-11-17).
- **Dates:** English "16 November 2026", Vietnamese "16/11/2026".

## Acceptance criteria

### Notes, the owner's admin and the first drafts (T1)

- **AC1.** A new Django app `journal` (in `INSTALLED_APPS`) has one model `JournalPost` (admin names "Journal post" / "Journal posts") with: `title` (up to 120 characters, required), `slug` (Django `SlugField`, up to 80, unique, required, label "Address"), `summary` (up to 240, required), `body` (text up to 8000 characters, required, label "Text"), `title_vi` (up to 120), `summary_vi` (up to 240), `body_vi` (up to 8000) (the three Vietnamese fields optional, labels "Title (Vietnamese)", "Summary (Vietnamese)", "Text (Vietnamese)"), `cover` (empty or one photo key, label "Cover photo"), `date` (a date, default today in Đà Nẵng `Asia/Ho_Chi_Minh`), `status` (`draft` or `published`, shown "Draft" / "Published", default `draft`), `created_at` and `updated_at` (set on save). The migration `src/journal/migrations/0001_initial.py` creates it.
- **AC2.** Given a note whose Vietnamese fields are filled only in part (for example `title_vi` filled and `body_vi` empty), when the owner saves it, then it is refused with "Fill the Vietnamese title, summary and text, or leave all three empty." and nothing is saved. A note with all three or none saves.
- **AC3.** The data migration `src/journal/migrations/0002_first_drafts.py` adds the two notes of "First notes" below as drafts, unless a note with the same `slug` exists. Reversing it deletes exactly those two slugs while they are still drafts.
- **AC4.** `SiteSettings` gains two fields not shown in its admin form, `journal_en` and `journal_vi` (booleans, default false; migration in `src/owner_content/migrations/`). After every save and every delete of a note (one at a time or the admin's bulk delete), `journal_en` is true exactly when at least one published note exists, and `journal_vi` exactly when at least one published note has Vietnamese; the first `SiteSettings` record by `pk` is updated, and created when there is none. `site_settings(lang)` returns them as `journal_en` and `journal_vi` in the same one query as today.
- **AC5.** Given the owner is signed in to `/owner/`, when they open the admin index, then it has a section "Journal" with "Journal posts" and an "Add" link. The list `/owner/journal/journalpost/` shows the columns "Title", "Date", "Status", "Vietnamese" ("Yes" / "No") and "Cover photo" (`photos/<key>.jpg` or "—"), newest date first, a filter "By status" and a search on the title. It matches the prototype state `#owner-journal`.
- **AC6.** Given no note exists, when the owner opens `/owner/journal/journalpost/`, then the list shows "No journal posts yet. The Journal link stays hidden on the site until you publish the first one." and the button "Add journal post" (prototype `#owner-journal-empty`).
- **AC7.** Given the owner opens a note to change it, then the form has three groups: "English (required)" with Title, Address (filled from the title while typing on a new note; help "The page is /journal/<address>/. Made from the title; change it only before you publish."), Summary (help "One or two sentences, shown in the list.") and Text; "Tiếng Việt (optional)" with the three Vietnamese fields (help on the title "Leave the Vietnamese empty and the note shows only on the English pages."); "Publishing" with Cover photo (a select of "— No cover —" and `photos/<key>.jpg` for every photo key; help "One of the site's photos (they show the Illustrative label), or none. Uploading is not possible."), Date (help "Shown on the note; the list is newest first.") and Status (help "Only published notes are on the site."). Both Text fields carry the help "A blank line starts a new paragraph. A line that starts with ## is a subheading. Web addresses become links by themselves." The page has "View on site" to `/journal/<slug>/`. It matches the prototype state `#owner-journal-edit`.
- **AC8.** `journal.text.to_html(text)` turns a note's text into safe HTML: lines are split on blank lines into blocks; a block that starts with `## ` becomes `<h2>` with the rest of its first line, any further lines of that block a `<p>`; every other block becomes one `<p>`, single line breaks kept as `<br>`; every `<`, `>`, `&`, `"` and `'` is escaped; each `http://` or `https://` address becomes `<a href="…" rel="noopener" target="_blank">…</a>` (a trailing `.`, `,`, `;`, `:`, `!`, `?` or `)` stays outside the link). Nothing else is markup: `<script>alert(1)</script>` shows as text and `javascript:` is never a link.
- **AC9.** The admin list makes the same number of queries with 1 or 50 notes.

### The journal pages (T2)

- **AC10.** Given two published notes "Ten minutes from everything" (16 November 2026, cover `market`) and "Staying a month or longer" (12 November 2026, no cover), when a visitor opens `/journal/`, then the page shows the label "Journal", the heading "Notes from Hòa Xuân", the line "I write here now and then about the house, the neighbourhood and what staying a while is like. — Bún" (with the owner's first name from the settings), and the two notes newest first: each with its date, its title linked to `/journal/<slug>/`, its summary and "Read →"; the first with its cover photo, the label "Illustrative photo" and the credit of that photo in `src/pages/photos.py`. It matches `#journal` (desktop) and `#journal-phone` (390×844, one column).
- **AC11.** Notes are ordered by `date` newest first, then newest `pk`. With more than 12 notes in the language, a page shows 12 and links "Older notes →" (`?page=2`) and "← Newer notes"; VI "Ghi chép cũ hơn →" and "← Ghi chép mới hơn". A page number that has no notes or is not a whole number answers 404.
- **AC12.** Given the same two notes where only "Ten minutes from everything" has Vietnamese, when a visitor opens `/vi/journal/`, then it shows "Nhật ký", "Ghi chép từ Hòa Xuân", "Thỉnh thoảng mình viết ở đây về căn nhà, khu xung quanh và chuyện ở lâu. — Bún", only "Mười phút là tới mọi thứ" with "16/11/2026", its Vietnamese summary, "Đọc →", the cover with "Ảnh minh hoạ" and the credit "Ảnh: Pexels" (prototype `#vi-journal`).
- **AC13.** Given no published note (drafts only, or none), when a visitor opens `/journal/`, then the answer is the site's page-not-found page with status 404 (prototype `#journal-none-404`). Given published notes but none with Vietnamese, `/vi/journal/` answers the Vietnamese 404.
- **AC14.** Given the published note "Ten minutes from everything", when a visitor opens `/journal/ten-minutes-from-everything/`, then they see "← All notes" (to `/journal/`), the date, the title as the page heading, the cover with its label and credit, the text made by AC8 (paragraphs and the subheadings "Every day", "The sea", "Arriving and leaving"), and at the end the contact block: "Like the sound of it?", the line "<price line>. <reply line>" ("From 13–14 million VND a month. I usually reply within an hour."), the Call, WhatsApp and Zalo buttons of the owner's settings each with `data-place="journal"`, and "Or leave me a message →" to `/#enquiry`. Under it, "Another note: Staying a month or longer" links to that note. It matches `#journal-note` and `#journal-note-phone`.
- **AC15.** The Vietnamese note page `/vi/journal/<slug>/` shows the same parts in Vietnamese: "← Tất cả ghi chép", "Bạn thấy hợp chứ?", the Vietnamese price and reply line, "Gọi", "WhatsApp", "Zalo", "Hoặc để lại lời nhắn cho mình →" to `/vi/#enquiry`, "Ghi chép khác: …" (prototype `#vi-journal-note`). A note without a cover has no figure (`#journal-note-plain`).
- **AC16.** "Another note" links the next older published note in the same language; for the oldest, the newest other one; with only one note in that language it is absent. Given the owner has set no price, the line shows only the reply line; given no channel, the buttons are absent and the form link stays.
- **AC17.** Given a draft note, an unknown address, or a note without Vietnamese opened under `/vi/journal/<slug>/`, when a visitor opens it, then the answer is the page-not-found page of that language with status 404.
- **AC18.** Each journal page has the site's head: title "Journal · Ở" / "Nhật ký · Ở" on the list and "<title> · Ở" on a note; description the lead line on the list and the summary on a note; canonical address; robots as today (`noindex, nofollow` while `INDEXING_ENABLED` is off); `og:type` `website` on the list and `article` on a note; `hreflang` alternates only when the page exists in both languages. The language switch goes to the same page in the other language when it exists, else to that language's journal list when it has notes, else to that language's home page.
- **AC19.** The counter has a new place `journal` labelled "Journal notes" (migration in `src/counter/migrations/`). Journal pages load `js/count.js`, so a page load counts one view and a press on a journal button counts a click with `place=journal`; the "Contact counts" report shows the row "Journal notes".
- **AC20.** Queries: `GET /journal/` and `GET /vi/journal/` make at most 3, a note page at most 3, the same with 1 or 30 notes. `GET /` and `GET /vi/` still make one; the page-not-found page, `/sitemap.xml` and `/robots.txt` still make none, and `sitemap.xml` still lists only the home pages.
- **AC21.** The journal pages work without JavaScript, set no cookie, and load no other script than the site's own. Their CSS is a new file `src/static/css/journal.css`. Given a heading of two or more lines with Vietnamese marks (for example "NOTES FROM HÒA XUÂN" or "GHI CHÉP TỪ HÒA XUÂN" at 390 px and 1440 px wide), then no mark touches the line above: the list heading has `line-height` of at least 0.9 and the note title at least 1.05.

### The Journal link in the menu and footer (T3)

- **AC22.** Given at least one published note, when a visitor opens `/`, then the menu (the desktop row and the phone "Menu") shows "Journal" between "FAQ" and "Contact", linking `/journal/`, and the footer shows "Journal" above its first line (prototype `#journal-menu`). On `/vi/` the link reads "Nhật ký" and goes to `/vi/journal/`, shown only when a published note has Vietnamese.
- **AC23.** Given no published note, when a visitor opens `/` or `/vi/`, then neither the menu nor the footer has a Journal link (prototype `#journal-none`). Given published notes without Vietnamese, `/vi/` has none and `/` has it.
- **AC24.** On the journal pages the menu and footer show the link of their language, and the menu link carries `aria-current="page"`. The page-not-found page never shows the link and still makes no query.

### The rules (T4, by hand)

- **AC25.** `.claude/rules/domain.md` drops "No blog." and says: "**Journal:** the owner writes notes in `/owner/` (English, Vietnamese optional) and publishes them at `/journal/` (`docs/specs/journal/spec.md`). A note's cover is one of the photos in `src/pages/photos.py`, never an upload." The Content rule adds journal notes to what the owner edits in `/owner/`. `.claude/rules/architecture.md` adds journal notes to the stored data under "Models".

## First notes

Stored as drafts by AC3, from facts the owner gave in `docs/intent/website.md` (2026-11-11). Blank lines separate paragraphs.

**1.** `slug` `ten-minutes-from-everything`, `date` 2026-11-16, `cover` `market`.

- `title`: Ten minutes from everything
- `summary`: A supermarket across the road, the market and the beach about ten minutes away, the airport about fifteen.
- `body`:

  ```text
  People often ask me what is near the house. Here is the short version.

  ## Every day

  There is a supermarket right across the road, so water, fruit and the small things are a few steps away. The market is about ten minutes away.

  ## The sea

  The beach is about ten minutes away.

  ## Arriving and leaving

  The airport is about fifteen minutes away.

  If you would like to see exactly where the house is, ask me and I will send you the location.
  ```

- `title_vi`: Mười phút là tới mọi thứ
- `summary_vi`: Siêu thị ngay bên kia đường, chợ và biển khoảng mười phút, sân bay khoảng mười lăm phút.
- `body_vi`:

  ```text
  Nhiều bạn hỏi mình quanh nhà có gì. Đây là bản ngắn gọn.

  ## Hằng ngày

  Siêu thị ở ngay bên kia đường, nước, trái cây và đồ lặt vặt chỉ cách vài bước. Chợ cách khoảng mười phút.

  ## Biển

  Biển cách khoảng mười phút.

  ## Đi và về

  Sân bay cách khoảng mười lăm phút.

  Nếu bạn muốn biết chính xác nhà ở đâu, cứ hỏi, mình gửi vị trí cho bạn.
  ```

**2.** `slug` `staying-a-month-or-longer`, `date` 2026-11-12, no cover, no Vietnamese.

- `title`: Staying a month or longer
- `summary`: What the rent includes, and what I take care of for you.
- `body`:

  ```text
  The house is rented whole, by the month. The minimum stay is one month, with two months' deposit.

  ## Included

  Basic furniture. Up to 300 kWh of electricity and 10 m³ of water each month; anything above is charged at the official rate. Garden care once a week. Cleaning can be arranged.

  ## Paperwork

  I take care of temporary residence registration for you.

  ## Pets

  Let's talk.
  ```

## Edge cases

- Empty: no published note: no Journal link anywhere, `/journal/` and `/vi/journal/` answer 404; the admin list shows the AC6 line.
- Large data: 12 notes per list page; list and note pages keep their query caps with 30 notes; the admin list the same with 1 or 50.
- Permissions: only a signed-in staff user (the owner) sees or changes notes in `/owner/`; visitors see published notes only; drafts answer 404.
- A cover key no longer in `src/pages/photos.py` shows no figure (never a broken image).
- A changed address after publishing: the old address answers 404 (no redirect).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Who writes the notes | The owner in `/owner/`, Draft and Published | Notes as files in the repository, one issue each | The owner can write whenever they like, no issue needed |
| Q2 Photos in a note | One cover from the site's photo list, or none; no upload | Uploads with a storage service | Render's free disk is wiped; Cloudinary was dropped on 2026-11-12 |
| Q3 Text format | Plain paragraphs, `## ` subheadings, addresses become links | Full Markdown | No new dependency, nothing to sanitise beyond escaping |
| Q4 Languages | English required, Vietnamese optional; `/vi/journal/` lists only notes with Vietnamese | Both required; English only | The owner writes English first and translates when there is time |
| Q5 Where on the site | `/journal/` and `/journal/<address>/`, menu and footer link; home unchanged | A strip of the latest 3 notes on the home page | Keeps the one page as it is and its one query |
| Q6 Before the first note | No link; `/journal/` answers 404 | A page saying the first note is coming | No empty page to find |
| Q7 End of each note | Price and reply line, Call/WhatsApp/Zalo, link to the enquiry form | Only a link to the contact chapter | A reader who likes a note can get in touch at once |
| Q8 Counting | Views count as page views; buttons count with place `journal` | No counting | The goal is at least 10 real contacts; the owner sees where they come from |
| Q9 First notes | Two drafts written only from facts the owner gave, published by the owner | The owner writes the first note | A start without inventing facts; the owner reads before publishing |
| (self) How the menu knows a note is published | Two flags on `SiteSettings`, kept by the journal on every save and delete | One more query on every page | `GET /` keeps one query and the page-not-found page none |
| (self) Journal in `sitemap.xml` | Not now; Phase 2 adds it with indexing | Add now | The site is noindex; the sitemap stays without queries |
| (self) Page-not-found page | No Journal link | Link from a query | That page asks the database nothing |
| (self) Notes per list page | 12 | 10; all on one page | Fits a 3-column rhythm and keeps a short page |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html` (artifact https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j), approved with "Prototype ổn" on 2026-11-17. States: `#journal`, `#journal-note`, `#journal-note-plain`, `#journal-menu`, `#journal-none`, `#journal-none-404`, `#journal-phone`, `#journal-note-phone`, `#vi-journal`, `#vi-journal-note`, `#vi-journal-note-phone`, `#owner-journal`, `#owner-journal-empty`, `#owner-journal-edit`, `#owner-journal-phone`.

## Open questions
