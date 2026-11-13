# Intent: the contact counter

## Problem

The goal for the next six months is at least 10 real contacts about Ở (`docs/intent/website.md`, Q6 and Q7). Today the owner cannot tell how many people opened the site or pressed Call, WhatsApp or Zalo, so there is no way to know whether the site works or which button people use.

## Goal

The site counts page views and presses on each contact button, as daily totals, with no IP address, no cookie and no third-party script (Q10). The owner reads the totals in the admin at `/owner/`: per channel, per place on the page and per month.

## Users

- **Visitor:** sees nothing new. The buttons keep their real links (`tel:`, `wa.me`, `zalo.me`) and the page works without JavaScript.
- **Owner (Bún):** opens "Contact counts" in `/owner/` to read the numbers.

## Out of scope

- Google Analytics or any other tracker, a cookie banner, an IP address, a visitor id, a user agent or a referrer.
- Unique visitors, sessions, sources of traffic, time on page.
- A notice to the owner when someone presses a button (email, push).
- Counting what happens after the press (whether the visitor really called or wrote).
- Exporting the numbers, charts.
