# Intent: mobile-smoothness

## Problem

The owner opened the site on a phone and found it rough:

- The five room photos of "ở nhà" sit in a small sideways row (240 by 320 px cards). While a visitor swipes, each card also rises 42 px and fades in, and every photo zooms slowly on its own, so the row jerks and the page feels heavy.
- The Call, WhatsApp and Zalo buttons show twice: the fixed phone bar stays on screen over the rent chapter and the FAQ, which have the same buttons, and it flashes over the hero while the page loads.
- In the header, the clock line "It's 14:52 in Hòa Xuân · Day" wraps onto three lines on a 390 px phone, which pushes the wordmark Ở against the top edge.
- Some motion costs more than it should: the hero keeps drawing a frame on every screen refresh for as long as the page is open, even after the intro and off screen; every photo keeps zooming when nobody can see it; the language switch measures five chapters on every scroll event.

(The distorted Ở on first load was fixed separately in #129, released in v2026.11.17.2.)

## Goal

On a phone, the room photos are a calm swipe carousel, one photo at a time with "2 / 5" and dots; the contact buttons are on screen once at most; the header is one line; and nothing animates or redraws where nobody can see it. Desktop looks as it does today.

## Users

- Visitors on phones (most of the people the site reaches through Zalo and WhatsApp links).
- Visitors on desktop see no change.
- The owner sees no change in /owner/.

## Out of scope

- A page-flip or 3D gallery (the owner chose the swipe carousel, Q1).
- New photos, real photos, or a photo lightbox.
- Changing the desktop collage, the intro timings, or the Hòa Xuân band.
- Removing the contact buttons from the rent chapter or the FAQ (Q2 kept them).
- Self-hosting fonts.
