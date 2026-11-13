# Intent: the time of day, live

## Problem

The site already picks a colour theme and a hero loop for the time of day in Hòa Xuân (dawn, day, dusk, night; epic 1, `src/pages/daypart.py`). Three things spoil it for a visitor:

- At night the top of the letter Ở is almost black on the night ground, so half of the letter disappears.
- The theme is chosen only when the page loads. A visitor who opens the page at 16:58 still sees "day" at 17:05.
- The "Ở" intro feels rushed and jerky: the letter barely moves for two seconds, then grows about 15 times in its last second.

## Goal

The page always shows the time of day in Hòa Xuân (Đà Nẵng time), also while it stays open: the colours, the loop in the letter and the header clock follow the clock. The letter is easy to see at night. The "Ở" intro is slower (about 7 seconds) and grows at an even pace.

## Users

Visitors to the site (foreigners looking for a long stay), on desktop and phones, in any time zone.

## Out of scope

- The visitor's own clock or time zone: the site keeps Đà Nẵng time (epic 1, Q2; confirmed 2026-11-13, Q1).
- New hours, new themes, new colours, new media.
- A theme switch in the header: the footer preview links stay as they are.
- The other chapters and their motion.
