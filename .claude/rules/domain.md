# Domain

## Terms

- **The house:** one garden house for rent in Hòa Xuân (Đà Nẵng), two bedrooms. It is still being built, but the site presents it as finished (see Content).
- **Rental:** the whole house, rented monthly, long term, minimum one month. Not by the room, not by the night.
- **Visitor:** someone reading the site. In phase 1 the site is English only.
- **Owner:** Bún, who rents out the house, answers contacts and edits some values in the admin. The site names the owner by first name only.

## Business rules

- **Pages of phase 1 (five):** Home `/`, The house `/house/`, Hòa Xuân `/hoa-xuan/`, FAQ `/faq/`, Contact `/contact/`. No blog.
- **Languages:** phase 1 is English only, at the site root. Vietnamese comes in phase 3 under `/vi/`; English addresses never change.
- **Voice:** the owner speaking in the first person ("Hi, I'm Bún…").
- **Contact:** phone, WhatsApp and Zalo, shown as buttons (no email in phase 1). The site does not send messages for the visitor.
- **Price:** an expected range set by the owner in the admin, for example "From 13–14 million VND a month".
- **Content:** page texts live in the templates and change through issues. The owner edits in the Django admin only the price range, the contact values, the owner's first name, the reply time and the photos (with alt text, caption, the illustrative flag and the credit).
- **Photos and video:** until real ones exist, licensed stock photos and clips (Unsplash, Pexels) stand in. Each shows the visible label "Illustrative" (photo or video), and its source and licence are recorded (for example `docs/specs/site-shell/media-credits.md`). Never use images taken from search results. A place with no file shows the empty state, never a broken image.
- **Look:** the design is fixed in `docs/specs/site-shell/design.md`: design E "Through the Ở" (a giant letter Ở filled with a time-of-day loop on the home page, a dictionary line, chapters ở nhà, ở gần, ở lâu, ở lại?), editorial type, colours that follow the time of day in Đà Nẵng (dawn, day, dusk, night).
- **Search engines:** the site stays out of search results (`INDEXING_ENABLED` off: noindex) until real photos replace the stand-ins. The base URL is set in one place (`SITE_BASE_URL`).
- **Counting:** a cookieless counter in Django for page views and contact-button clicks. No Google Analytics, no cookie banner.
- Never invent facts about the house (price, size, dates, photos, amenities): they come from the owner, in `docs/intent/website.md` or an issue.

## Audience of issues

The owner reads every issue and every pull request: write them in plain English, name the page a change touches, and give the exact text to show.
