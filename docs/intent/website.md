# Intent: the Ở website

Written 2026-11-11 from the grill-me rounds in the Project thread "Grill the Ở website and SEO plan" (Q1–Q15), updated 2026-11-12 after epic 1 (photos stay static files, no Cloudinary). Every fact about the house below comes from the owner. Anything still missing is listed under "Content the owner still provides" and must not be invented.

## Vision

Ở — Living with Nature is one small garden house in Hòa Xuân, Đà Nẵng, rented whole, by the month, for long stays. It is slow, close to nature, and made to feel good in daily life rather than to look good in photos. The website is where someone who might live there meets the house and the owner, and gets in touch.

## Problem

The house is still being designed. Without a website, the owner cannot find out who wants to live in it, has no link to share in expat groups, and starts from zero on Google the day the house opens.

## Goal and success

- **Main goal for the next 6 months (Q6):** collect people who are really interested. Every page leads to contacting the owner. Search engines are a channel, not the goal.
- **Success at 6 months (Q7):** at least 10 real contacts (calls, messages or emails about Ở). The site counts clicks on each contact button so the number is known.

## Users

- **Visitor:** a foreigner, a couple or a remote worker looking for a whole house to live in for a month or more in Đà Nẵng. Reads English.
- **Owner:** answers contacts and updates the price range, contact details, first name and reply time in the Django admin.

## Phase 1 scope (MVP)

The site is written **as if the house is finished (Q15)**, in **English only (Q5)**, and stays **out of search engines until real photos replace the stand-ins**.

- **Five pages (domain rule):** Home, The house, Hòa Xuân, FAQ, Contact. English at the root: `/`, `/house/`, `/hoa-xuan/`, `/faq/`, `/contact/` (Q1). Vietnamese will be added later under `/vi/`, and English addresses never change.
- **Voice (Q9):** the owner speaking in the first person, introduced by first name only (Q14). For example: "Hi, I'm <first name>. I built a small garden house in Hoa Xuan…"
- **Price (Q2):** an expected range, for example "from <X> million VND / month", set by the owner in the admin.
- **Photos (Q15):** licensed stock photos (Unsplash or Pexels) stand in for the house until real ones exist. Each has a visible "Illustrative photo" label, and its source and licence are recorded in the repository (`docs/specs/*/media-credits.md` and the photo list in the code). Photos and videos are static files in the repository; changing them is an issue. Never use images taken from search results.
- **Contact (domain rule):** phone, WhatsApp, Zalo and email, shown as buttons. The site does not send messages for the visitor.
- **Counting (Q10):** a small cookieless counter in Django records page views and clicks on each contact channel. The owner reads it in the admin. No Google Analytics, no cookie banner.
- **Owner-editable in the admin (Q11, narrowed 2026-11-12):** price range, contact values, owner first name and reply time. Page texts and photos stay in the repository and change through issues.
- **SEO groundwork:** a title and description per page aimed at niche local keywords (Q12), such as "house for rent Hoa Xuan", "garden house Da Nang" and "monthly house rental Da Nang". Also a canonical URL from `SITE_BASE_URL`, `sitemap.xml`, Open Graph tags, and one switch (`INDEXING_ENABLED`) that keeps `robots.txt` and the meta robots tag on "noindex" until the owner turns it on.

### What each page holds

| Page | Sections |
|---|---|
| Home | Hero photo and one line in the owner's voice; three short points (private garden and veranda, light and air, live like at home); a short hello from the owner; price range and "monthly, minimum one month"; contact buttons |
| The house | Photo gallery; the layout (2 bedrooms, 1 bathroom, living room and kitchen, mezzanine, light well, front and back gardens, covered veranda, laundry, drying and storage area); what is included; price range and rental terms |
| Hòa Xuân | The area in the owner's words; travel times to the beach, market, supermarket and airport; a link to Google Maps (a link, not an embedded map) |
| FAQ | Minimum stay; whole house or room; price; deposit; electricity and water; pets; temporary residence registration for foreigners; how to visit |
| Contact | The four channels with click counting, the owner's first name, and the usual reply time |

## Out of scope for phase 1

- Vietnamese pages (a later phase).
- Booking, availability calendar, online payment, enquiry form.
- Blog or journal, and a CMS for page texts.
- Being indexed by search engines before real photos exist.
- Own domain and paid hosting (kept on the free plans for now).
- The house's construction progress or milestones (Q3 is set aside while the site is written as finished).

## Stack and hosting

- **App (Q8):** Django 5, Python 3.11, server-rendered HTML, no JavaScript framework, no front-end build step.
- **Hosting:** Render, free plan, service `o-living-web`, deploys from the `deploy` branch. The free plan sleeps when idle, so the first visit after a quiet spell is slow. That is acceptable while the site is noindex. Revisit before turning indexing on.
- **Data (Q13, updated 2026-11-12):** Neon (free Postgres) holds the admin data and the counters, because Render's free disk is wiped on every deploy and when the free service sleeps. Photos and videos are static files served by WhiteNoise; no Cloudinary. SQLite stays for development and tests. The owner creates the Neon account and puts `DATABASE_URL` in Render's environment.
- **Site address:** `https://o-living-web.onrender.com` for now, set only in `SITE_BASE_URL`. Moving to an own domain later means changing that value and adding 301 redirects.

## Rules that must change first

These conflict with the decisions above. They are changes under `.claude/`, so they are built by hand on the Mac mini and not by the loop (ADR-023).

- `.claude/rules/domain.md`: phase 1 is English only (Vietnamese later under `/vi/`). The house is presented as finished, with labelled illustrative photos and noindex until real photos exist. The owner edits the price range, contacts, first name and reply time in the admin.
- `.claude/rules/architecture.md`: phase 1 now stores data (site settings, photos, counters). Postgres on Neon in production, SQLite locally, photos and videos as static files, and the new dependencies (a Postgres driver and `dj-database-url`).
- `src/config/settings.py`: `LANGUAGE_CODE = "en"`, with `LANGUAGES` reduced to English for now. This part is an app change the loop can build.

## First epics (phase 1)

1. **Site shell and look.** `base.html` with header, navigation for the five pages, and footer. The Natural Editorial style, with L'OISEAU DÉ (https://loiseau.framer.website/) as the main visual reference: large refined typography, wide white space, calm photo-led layout. Cabana Mountain adds the nature feel, and BetheWind the practical structure (amenities, FAQ, contact). Adapt, never copy, and drop its shop and product structure. A reusable "Illustrative photo" label. The English 404 page. SEO basics: per-page title and description, canonical, Open Graph, `sitemap.xml`, and `robots.txt` with the noindex switch.
2. **Owner-editable content and storage.** Neon Postgres in production through `DATABASE_URL`, the admin at `/owner/` with the owner's account from environment variables, site settings (price range, Call, WhatsApp and Zalo, owner first name, reply time), and a list of the illustrative photos as static files with their credits (spec: `docs/specs/owner-content/`).
3. **The five pages.** Home, The house, Hòa Xuân, FAQ and Contact, filled with the owner's real text and the admin values. They use the illustrative photos listed in epic 2, with their labels, and the walk-through floor plan on The house (schematic until the architect's plan).
4. **Contact counting.** A cookieless counter for page views and contact-button clicks per channel: the buttons keep their real links (`tel:`, `wa.me`, `zalo.me`) and a small script reports views and clicks; daily totals, no IP address, no cookie. A simple admin view (totals per channel, per page, per month).

Order: 1 → 2 → 3, then 4. Epic 4 depends only on 1 and 2, so it can run beside 3.

## Later phases

- **Phase 2: real photos and going public.** Replace the stand-ins with real photos and remove their labels. Turn on `INDEXING_ENABLED`, submit the sitemap to Google Search Console, and add `LodgingBusiness` structured data with real details. Decide whether to leave Render's free plan (cold starts), then run a speed check.
- **Phase 3: Vietnamese.** Add `/vi/` pages with the same content, a language switch and hreflang. Vietnamese keywords, for example "thuê nhà nguyên căn Hòa Xuân" and "nhà vườn cho thuê Đà Nẵng".
- **Phase 4 (optional, by need).** Own domain with 301 redirects from onrender.com, an enquiry form, a journal.

## Content from the owner (2026-11-11)

| Item | Owner's answer | English for the site (owner to approve) |
|---|---|---|
| Price range | 13–14 million VND / month | "From 13–14 million VND a month" |
| Contact | Phone 0945384500, WhatsApp and Zalo on the same number; no email | Buttons: Call, WhatsApp, Zalo |
| Owner name, reply time | Bún; replies within 1 hour | "Hi, I'm Bún." / "I usually reply within an hour." |
| Travel times | Supermarket right across the road; market 10 minutes; beach 10 minutes | "A supermarket across the road, the market and the beach about 10 minutes away" (by motorbike: to confirm) |
| Utilities | Electricity and water included up to a monthly allowance; usage above it is charged | "Electricity and water are included up to a monthly allowance; anything above is charged at cost" (allowance amount: to confirm) |
| Included in rent | Basic furniture; cleaning by arrangement; garden care once a week at a set time | "Basic furniture. Garden care once a week. Cleaning can be arranged." |
| Why Ở | Owner asked Claude to write it | DRAFT for approval: "I wanted a house that feels good to live in every day, not just in photos: a little garden, morning light, a veranda to sit on. Ở is that house, and I'd love for someone to make it home for a while." |
| Logo | None yet; use a text wordmark for now | Wordmark "Ở" set in the display face, replaced when a designed logo exists |
| Neon | Use the free plan; pay only after completion | Free plan. The owner signs up (Claude cannot create accounts) and adds `DATABASE_URL` in Render. Cloudinary dropped on 2026-11-12 |

### Answers added later the same day

| Item | Owner's answer | English for the site |
|---|---|---|
| WhatsApp, Zalo, email | WhatsApp and Zalo on 0945384500; no email given | Call, WhatsApp, Zalo buttons on 0945384500; no email button |
| Airport | 15 minutes | "The airport about 15 minutes away" |
| Deposit | 2 months | "Two months' deposit" |
| Pets | Negotiable | "Pets: let's talk" |
| Minimum contract | Not changed: one month (earlier decision) | "Minimum stay one month" |
| Residence registration | Owner registers foreign tenants | "I take care of temporary residence registration for you" |
| Utility allowance | Owner asked Claude to set it | "Included each month: up to 300 kWh of electricity and 10 m³ of water. Anything above is charged at the official rate." |

**Why 300 kWh and 10 m³ (Claude's estimate, owner can change it):** two people living full time with air-conditioning in the bedrooms, a fridge, cooking and laundry typically use about 200–350 kWh a month in Đà Nẵng, more in the hot months. 300 kWh covers normal use for a couple without frequent extra charges, and costs the owner very roughly 0.8–0.9 million VND a month at EVN's tiered household rates (check against a real bill). Water at 4–5 m³ per person a month means 10 m³ covers two people, at roughly 0.1 million VND. Together that is about 7% of a 13–14 million rent, so the price range still holds.

### Still missing

- Nothing blocks building phase 1. The owner creates the free Neon account and sets `DATABASE_URL`, `OWNER_USERNAME` and `OWNER_PASSWORD` in Render before epic 2 is released.

## Decisions (grill-me, 2026-11-11)

| # | Question | Chosen | Rejected |
|---|---|---|---|
| Q1 | Language URLs | English at root, `/vi/` later | `/en/` prefix from the start |
| Q2 | Price on the site | Expected range | Announce near completion; no price |
| Q3 | Construction progress | Milestones without dates (set aside by Q15) | Quarter date; one status line |
| Q4 | Launch images | Owner's land and area photos (set aside by Q15) | Studio renders; no photos |
| Q5 | "English first" scope | Whole phase-1 site | 404 page only |
| Q6 | Main goal | Collect interested people | SEO first; a link to share |
| Q7 | Success measure | At least 10 real contacts in 6 months | Google page 1; no number |
| Q8 | Stack | Keep Django; Render free for now | Astro static; Next.js |
| Q9 | Voice | Owner, first person | Brand third person; listing style |
| Q10 | Counting contacts | Own cookieless counter in Django | Google Analytics 4; none |
| Q11 | Admin editing | Price, contacts, photos (texts in templates) | Full CMS; nothing |
| Q12 | Keywords | Niche local English | Broad Đà Nẵng; research first |
| Q13 | Storage on free Render | Neon Postgres for data; photos as static files in the repository (changed 2026-11-12) | Cloudinary; SQLite on Render (wiped); paid Render disk |
| Q14 | Owner on the site | First name only | Name and portrait; anonymous |
| Q15 | As-if-finished site | Labelled illustrative photos, noindex until real photos | Index now; keep "under construction" |
