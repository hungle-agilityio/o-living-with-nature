# Intent: faq-contact-count

## Problem

The FAQ chapter (issue #83) has its own Call, WhatsApp and Zalo buttons. They send `place=faq` to the contact counter (epic #86), but the counter only knows the places `bar`, `rent` and `contact`, so `POST /count/` answers `400` and every press in the FAQ is lost. The two were built in parallel and nothing checked them together. The owner's report at `/owner/` therefore misses part of the contacts the site brings, which is the number the project's goal is measured by (at least 10 real contacts in 6 months, `docs/intent/website.md`).

## Goal

A press on a contact button in the FAQ chapter is counted like a press anywhere else, and the owner's report shows it on its own row, "FAQ chapter", in the "By place" table. A test makes sure that every place a page sends is a place the counter accepts, so the same gap cannot open again.

## Users

- The owner, who reads the contact counts report in the admin.
- Visitors see nothing new: the buttons and links stay as they are.

## Out of scope

- Getting back the presses lost so far: nothing about them was stored.
- New places, channels or kinds, and any change to the page, the buttons or `count.js`.
- The Vietnamese pages (phase 3).
