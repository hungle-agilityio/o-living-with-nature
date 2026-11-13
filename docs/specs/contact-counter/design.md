# Design: the contact counter

Design card: https://claude.ai/artifact/G1rPFDgVdxm6V41gSbDyiY (demo data only).

- Board 1: the report at 1440 wide: three summary columns (This month, Last month, All time), the tables "By channel" and "By place", the table "By month", and the privacy line.
- Board 2: empty: only "Nothing counted yet. Counts start when someone opens the site." and the privacy line.
- Board 3: phone at 390 wide: the columns stack, wide tables scroll inside their own box.
- Board 4: errors and permissions: no error state of its own; not logged in → the admin login; no Add, Change or Delete.

The report uses Django's own admin look (`admin/base_site.html`), no new colours or fonts. Visitors see no change on the site.

| Label in the report | Data |
|---|---|
| Call, WhatsApp, Zalo | channel `call`, `whatsapp`, `zalo` |
| Phone bar, Rent chapter, Contact chapter | place `bar`, `rent`, `contact` |
| clicks per 100 views | clicks ÷ views × 100, one decimal; "–" with no views |
| Month | "Nov 2026" (Đà Nẵng months) |
