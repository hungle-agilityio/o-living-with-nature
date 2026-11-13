# Spec: search-ready

## Summary

Two additions to the `<head>` of the home page `/`, nothing a visitor sees:

1. A Google Search Console verification tag, `<meta name="google-site-verification" content="…">`, whose value comes from a new environment variable `GOOGLE_SITE_VERIFICATION`. The owner pastes the value Google gives into Render; no code change is needed to set or change it.
2. Structured data in a `<script type="application/ld+json">` block that describes the house as a schema.org `LodgingBusiness`, built from values the site already has: the site name, the home page description and address, the area (Hòa Xuân, Đà Nẵng, Vietnam), the owner's price range and the Call number from the admin.

The site stays noindex (`INDEXING_ENABLED` off). The home page still makes one database query.

## User story

As the owner, I want to verify my site in Google Search Console and have the home page describe the house to search engines, so that going public is only a matter of real photos and one switch.

## Acceptance criteria

### Search Console verification

- **AC1.** `src/config/settings.py` reads a new setting `GOOGLE_SITE_VERIFICATION` from the environment variable of the same name, with spaces around it removed; it is the empty string when the variable is unset or blank.
- **AC2.** Given `GOOGLE_SITE_VERIFICATION=abc123-XYZ_9` on the server, when someone opens `/`, then the `<head>` holds exactly one `<meta name="google-site-verification" content="abc123-XYZ_9">`.
- **AC3.** Given `GOOGLE_SITE_VERIFICATION` is unset or blank, when someone opens `/`, then the page has no `google-site-verification` tag at all (not an empty one).
- **AC4.** The value is written through Django's autoescape: given the value `a"><script>`, the page holds `content="a&quot;&gt;&lt;script&gt;"` and no new tag.
- **AC5.** The 404 page and the admin at `/owner/` carry no `google-site-verification` tag, whatever the setting.
- **AC6.** `render.yaml` lists `GOOGLE_SITE_VERIFICATION` under `envVars` with `sync: false` and a comment that the owner sets it by hand on Render.

### Structured data

- **AC7.** Given the owner's settings price 13 to 14 million and Call number `0905 123 456`, when someone opens `/`, then the `<head>` holds exactly one `<script type="application/ld+json">` placed right after the `og:site_name` tag, and parsing its text as JSON gives exactly:

  ```json
  {
    "@context": "https://schema.org",
    "@type": "LodgingBusiness",
    "name": "Ở — Living with Nature",
    "description": "<the home page description of src/pages/seo.py>",
    "url": "<SITE_BASE_URL>/",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "Hòa Xuân",
      "addressRegion": "Đà Nẵng",
      "addressCountry": "VN"
    },
    "priceRange": "From 13–14 million VND a month",
    "telephone": "+84905123456"
  }
  ```

  `description` and `url` are the same values as the page's `<meta name="description">` and canonical link. `priceRange` is the same line as the price the page shows. `telephone` is the number of the Call button (its `tel:` link without `tel:`).
- **AC8.** Given no price is set in the admin, when someone opens `/`, then the JSON has no `priceRange` key. Given no Call number is set (WhatsApp or Zalo may still be set), the JSON has no `telephone` key. Given no settings record at all, the JSON has the keys of AC7 except the ones whose value is missing; the block is never left out.
- **AC9.** The JSON has no `image`, `geo`, `streetAddress`, `postalCode`, rating or review: none are real yet (`.claude/rules/domain.md`: never invent facts).
- **AC10.** The JSON is written so that no value can close the script: every `<`, `>` and `&` in it is written as `<`, `>` and `&`. Vietnamese letters stay readable or escaped; either way the parsed JSON equals AC7.
- **AC11.** The structured data is built by a typed, unit-tested function in `src/pages/seo.py` from the owner's settings value the home view already reads; the home view passes it to the template. `/` still makes exactly one database query.
- **AC12.** The 404 page and the admin carry no `application/ld+json` block. The block is there whether indexing is on or off.

### Every task

- **AC13.** `bash scripts/check.sh` passes. Every test on `main` passes unchanged, except the one listed under "Existing tests that change": `src/pages/tests/test_layout.py::test_page_uses_no_javascript`, whose list of `<script…>` tags gains `'<script type="application/ld+json">'` as its first entry (the block sits in the `<head>`, before the scripts `base.html` links). It still asserts no `onclick` and no script in the header.

## Edge cases

- **Empty:** no verification value: no tag (AC3). No settings record or no price or Call number: the JSON leaves those keys out (AC8).
- **Large data:** none; one block and one tag on one page.
- **Permissions:** the value of `GOOGLE_SITE_VERIFICATION` is public by design (Google reads it from the page); it is not a secret. Only the owner sets it, on Render.
- **Indexing off:** Google's verification fetch still reads the tag; the robots `noindex` does not stop verification.
- **Owner's text in the JSON:** the price comes from two whole numbers and the phone from a validated Vietnamese number, but the JSON is escaped anyway (AC10).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 What to do while there are no real photos | Prepare Phase 2: verification tag and structured data, stay noindex | Phase 3 Vietnamese first; go public now with illustrative photos | Keeps the noindex rule (Q15); going public later is one switch |
| Q2 How to verify in Search Console | Meta tag from the `GOOGLE_SITE_VERIFICATION` environment variable | Google's HTML file at the site root | Set or change on Render with no code change; works on the onrender.com address |
| Q3 When the structured data shows | Always | Only when `INDEXING_ENABLED` is on | Can be checked now with the Rich Results Test; noindex keeps it out of results |
| Q4 Address and photos in the structured data | Area only (Hòa Xuân, Đà Nẵng, VN), price and Call number from the admin, no photo | The owner gives street address and coordinates now | Never invent facts; the stock photos are not the house |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Nothing visible to users. No prototype change.

## After release (owner, by hand)

1. In Google Search Console add a "URL prefix" property `https://o-living-web.onrender.com/`, choose "HTML tag" and copy only the `content` value.
2. On Render, service `o-living-web`, Environment: add `GOOGLE_SITE_VERIFICATION` with that value and save (Render redeploys).
3. Back in Search Console press Verify.
4. Optional: run `https://o-living-web.onrender.com/` through the Rich Results Test; it should find one `LodgingBusiness`.
5. Submit `sitemap.xml` only after indexing is turned on (Phase 2, with real photos).

## Open questions
