# Spec: owner-editable content and storage (epic 2)

## Summary

Nothing visible to visitors. Production gets a lasting database (Postgres on Neon, through `DATABASE_URL`). Development and tests keep SQLite. The Django admin opens at `/owner/` with the owner's account taken from Render's environment. In the admin the owner edits one "Site settings" record: price range, Call, WhatsApp and Zalo numbers, first name and reply time. A service turns it into the lines and links epic 3 will show. The fourteen illustrative photos and the Hòa Xuân loop become static files in the site, with a typed list of their sizes, alt texts and credits that epic 3 will place on the pages. No page changes, no page makes a database query, and no visitor gets a cookie.

Every test on `main` passes unchanged, and `bash scripts/check.sh` passes, for every task.

## Acceptance criteria

### Database and the owner's sign-in (T1)

- **AC1.** With `DATABASE_URL` set, the app uses that database. Connections are kept for 600 seconds, and a `postgres://` or `postgresql://` address requires SSL. Without `DATABASE_URL`, the app uses SQLite as today: `DJANGO_DB_NAME` when set, otherwise `db.sqlite3`. The address is parsed by `dj-database-url`, and Postgres is reached through `psycopg` (binary). Both are added to `pyproject.toml` and `uv.lock`. Tests check the parsed settings with a fake address and never connect to Postgres.
- **AC2.** With `DJANGO_DEBUG=0` and neither `DATABASE_URL` nor `DJANGO_DB_NAME` set, `python manage.py check` shows the warning `config.W001`: "DATABASE_URL is not set: on Render the SQLite file is wiped on every deploy and the owner's settings are lost." The app still starts. With debug on, or either value set, there is no warning.
- **AC3.** The Django admin answers at `/owner/`. Signed out, it shows the sign-in page. `/admin/` answers 404. The admin's header reads "Ở admin", its site title "Ở admin", and its index title "Site administration".
- **AC4.** `python manage.py ensure_owner` reads `OWNER_USERNAME` and `OWNER_PASSWORD`:
  - When the user does not exist, it creates a superuser with that name and password, and prints `owner ready: created`.
  - When the user exists, it sets that password (so the owner resets it by changing the value on Render) and prints `owner ready: password updated`.
  - When either value is empty or missing, it prints `owner skipped: OWNER_USERNAME and OWNER_PASSWORD are not set` and exits 0.
  - When the password is shorter than 12 characters, it prints `owner not ready: OWNER_PASSWORD needs at least 12 characters`, changes nothing, and exits 1.
  - It never prints the password.
- **AC5.** `render.yaml`'s start command runs `migrate --noinput`, then `ensure_owner`, then gunicorn, and stops if either of the first two fails. Its `envVars` add `DATABASE_URL`, `OWNER_USERNAME` and `OWNER_PASSWORD` with `sync: false`. `.env.example` documents the three, with empty values.
- **AC6.** The five pages, `/sitemap.xml`, `/robots.txt` and the 404 page send no `Set-Cookie` header to a visitor who is not signed in. Their query counts stay 0, and the query-cap tests on `main` pass unchanged.

### Site settings (T2)

- **AC7.** A model `SiteSettings` in the new app `src/owner_content/` holds one record:

  | Field | Label in the admin | Rule | Help text |
  |---|---|---|---|
  | `price_from_million` | Price from (million VND a month) | whole number 1–999, optional | "The lower end of the monthly rent, in million VND." |
  | `price_to_million` | Price to (million VND a month) | whole number 1–999, optional, not below "Price from" | "The upper end. Leave empty for one price." |
  | `phone` | Phone (Call button) | optional | "A Vietnamese number like 0945 384 500 or +84 945 384 500. Empty hides the button." |
  | `whatsapp` | WhatsApp | optional | same as Phone |
  | `zalo` | Zalo | optional | same as Phone |
  | `owner_first_name` | Your first name | required, at most 40 characters | "Shown as \"Hi, I'm …\"." |
  | `reply_time` | Usual reply time | required, at most 60 characters | "Shown as \"I usually reply …\", for example \"within an hour\"." |

  A number is valid when it has 9 to 11 digits after an optional leading `+84` or `0`, separated only by spaces, dots or dashes. Otherwise the admin refuses it with "Enter a Vietnamese number like 0945 384 500 or +84 945 384 500." A "Price to" below "Price from" is refused with "Price to cannot be lower than Price from."
- **AC8.** At `/owner/` the owner sees "Site settings" under "Owner content". When the record exists, there is no "Add" button and no delete action. The list links straight to the one record.
- **AC9.** A data migration creates the record with the owner's values from `docs/intent/website.md`: price from 13 to 14, phone, WhatsApp and Zalo `0945 384 500`, first name `Bún`, reply time `within an hour`. If a record already exists, the migration leaves it as it is.
- **AC10.** The service `owner_content.services.site_settings()` returns a frozen value with:
  - `price_line`:
    - "From 13–14 million VND a month" for 13 and 14 (an en dash);
    - "From 13 million VND a month" when only "Price from" is set, or both are equal;
    - `None` when "Price from" is empty. Epic 3 then shows "Ask me about the rent".
  - `channels`: one entry per filled channel, in the order Call, WhatsApp, Zalo. Each entry has a key (`call`, `whatsapp`, `zalo`), a label ("Call", "WhatsApp", "Zalo") and a link. For `0945 384 500` the links are `tel:+84945384500`, `https://wa.me/84945384500` and `https://zalo.me/0945384500`. A number given as `+84 945 384 500` gives the same three links.
  - `greeting`: "Hi, I'm Bún."
  - `reply_line`: "I usually reply within an hour."
- **AC11.** `site_settings()` makes exactly one query. With no record, it returns an empty value (no price line, no channels, the greeting and reply line from the model defaults "Bún" and "within an hour") and raises no error.
- **AC12.** No page shows these values yet, and no page's query count changes.

### Illustrative photos (T3)

- **AC13.** `src/pages/photos.py` lists the fourteen photos and the one loop of `docs/specs/owner-content/media-credits.md`, with the keys, sizes, alt texts or labels, credits and sources of that file. Every entry is marked illustrative, with the licence "Pexels License".
- **AC14.** `photo(key)` returns the entry with its static path (`media/photos/<key>.jpg`). It returns `None` when the key is unknown or the file is not found by the static files finders. In that case the media slot of epic 1 shows its empty state. `area_loop()` returns the loop's mp4, WebM and poster paths, or `None` when any of the three files is missing.
- **AC15.** A test checks that every listed file exists in `src/static/media/`, that every entry has a non-empty alt text or label and credit, and that every source starts with `https://www.pexels.com/`.
- **AC16.** No page shows the photos yet.

## Edge cases

- **Empty:**
  - With no settings record, the service gives no price line and no channels, and epic 3 shows "Ask me about the rent" with no buttons.
  - A missing photo file gives `None` and the media slot's empty state, never a broken image.
- **Large data:** one settings record and fifteen media entries; nothing grows.
- **Permissions:**
  - Only the owner's superuser signs in at `/owner/`.
  - Visitors cannot reach the admin pages and get no cookie.
  - The owner's password lives only in Render's environment, never in the repository or a log.
- **Production without Neon yet:** the release waits until the owner has set `DATABASE_URL`, `OWNER_USERNAME` and `OWNER_PASSWORD` on Render. If it is released without them, the site still runs on a wiped SQLite file, and `config.W001` warns about it.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Neon and Cloudinary accounts not created yet | Build epic 2 now, release only when the keys are on Render | Wait for the accounts; build epic 3 first with values in the templates | Tests need no key; only the deploy does |
| Owner account on Render free (no shell) | `ensure_owner` from `OWNER_USERNAME` and `OWNER_PASSWORD` at every start, admin at `/owner/` | `createsuperuser` from the Mac mini against Neon; the default `/admin/` | Nothing to run by hand; a less obvious address draws fewer password-guessing bots |
| Where the photos live | Static files in the repository, listed in `src/pages/photos.py` (owner, 2026-11-12) | Cloudinary uploads through the admin; an import command | The owner wants them local for now; one account fewer; photos change through issues |
| Where the settings and counters live in production | Neon free Postgres; SQLite only for development and tests | SQLite on Render (wiped on deploy and sleep); SQLite on a paid Render disk | The values and the counts of epic 4 must survive; Neon is free |
| Counting views and clicks (epic 4) | The buttons keep their real links, a small script reports the view or click, daily totals, no IP, no cookie | Count through `/go/<channel>/` redirects | Buttons always work; bots rarely run scripts |
| Floor plan (epic 3) | Last task of epic 3, schematic and labelled until the architect's plan | Phase 2 | As decided in epic 1 |
| First values of the settings | A data migration with the owner's values | Owner types them after the release | The site is right from its first deploy; the number is public on the site anyway |

## Design

Nothing visible to visitors. The admin is Django's own, with the header "Ở admin".

## Open questions
