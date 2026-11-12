# Intent: owner-editable content and storage (epic 2)

## Problem

The site has its look (epic 1), but nothing on it can be changed without a code change, and nothing it stores survives: Render's free plan wipes its disk on every deploy and whenever the sleeping service wakes up. The owner, Bún, cannot set the price range or the Call, WhatsApp and Zalo numbers, and the counter of epic 4 would lose its numbers. The illustrative photos the inner pages need (epic 3) exist only in the project files, not in the site.

## Goal

The owner signs in at `/owner/` and edits the price range, the three contact channels, the first name and the reply time, and those values survive deploys because production keeps them in a free Neon Postgres database. The fourteen illustrative photos and the Hòa Xuân loop are in the site as static files, each with its alt text, credit, source and licence, ready for epic 3 to place on the pages. Visitors see nothing new yet.

## Users

- **Owner (Bún):** signs in at `/owner/` with the account set in Render's environment, and edits the site settings.
- **Visitor:** no visible change in this epic; still no cookie.

## Out of scope

- Showing the settings and photos on the pages: epic 3.
- Counting views and clicks: epic 4.
- Uploading photos in the admin, and Cloudinary: photos and videos stay static files in the repository and change through issues (owner, 2026-11-12).
- Editing page texts in the admin.
- More than one admin account, password reset by email.
