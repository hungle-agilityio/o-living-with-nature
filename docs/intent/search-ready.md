# Intent: search-ready

## Problem

Phase 2 (`docs/intent/website.md`, "Later phases") turns indexing on, submits the sitemap to Google Search Console and adds `LodgingBusiness` structured data. The house is not built yet, so there are no real photos, and the site must stay out of search results until there are (`.claude/rules/domain.md`, "Search engines"). Today the owner cannot even verify the site in Search Console, and the home page tells search engines nothing structured about the house. When real photos arrive, every Phase 2 step would still be ahead.

## Goal

The owner can verify `https://o-living-web.onrender.com/` in Google Search Console by pasting one value into Render, and the home page describes the house as a `LodgingBusiness` that the Rich Results Test can read. The site stays noindex. When real photos exist, going public is: replace the photos, set `INDEXING_ENABLED=1`, submit the sitemap.

## Users

- The owner, who verifies the site in Search Console and sets one value on Render.
- Search engines, which read the structured data once indexing is on.
- Visitors see nothing new.

## Out of scope

- Turning indexing on, real photos, removing the "Illustrative" labels (wait for real photos).
- Submitting the sitemap (the owner does it in Search Console once indexing is on).
- A street address, map coordinates or photos in the structured data (none are real yet).
- Render's paid plan and the speed check (decided before indexing is turned on).
- Vietnamese pages (phase 3).
