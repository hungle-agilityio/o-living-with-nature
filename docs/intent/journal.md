# Intent: the journal

## Problem

The site is one page that says what the house is. A visitor deciding on a long stay in Hòa Xuân also wants to know what living there is like: what is near, what the owner takes care of, what a month there looks like. Today the owner (Bún) has no place to write that, and every text change needs an issue.

## Goal

A journal of short notes written by the owner in `/owner/` and published when ready: a list at `/journal/` and one page per note at `/journal/<address>/`, in English, with an optional Vietnamese version shown under `/vi/journal/`. Each note ends with the contact buttons and a link to the enquiry form, so a reader who likes it can get in touch. The Journal link appears in the menu and the footer once the first note is published. Two first notes are drafted from facts the owner already gave, for the owner to read and publish.

## Users

- **Visitor:** reads the notes in English (or Vietnamese when the note has a Vietnamese version), then calls, writes or leaves a message.
- **Owner (Bún):** writes, edits, publishes and deletes notes in `/owner/` under "Journal posts", with no issue needed.

## Out of scope

- Uploading photos or files (Render's free disk is wiped; no Cloudinary). A note's cover is one of the site's own illustrative photos, or none.
- Rich text, Markdown, comments, tags, search, an RSS feed, sharing buttons.
- Journal pages in `sitemap.xml` and search engines: the site stays noindex until real photos exist (Phase 2 adds them).
- A teaser of notes on the home page.
