# Test matrix: search-ready

All rows are tests in `src/pages/tests/test_search_ready.py` (NEW), task T1.

| Row | AC | Case | Check | Level | Test file | Task |
|---|---|---|---|---|---|---|
| M1 | AC1 | normal | In a fresh process with `GOOGLE_SITE_VERIFICATION=" abc123 "`, `settings.GOOGLE_SITE_VERIFICATION == "abc123"`. | unit | `src/pages/tests/test_search_ready.py` | T1 |
| M2 | AC1 | empty | In a fresh process without the variable, and with it blank, the setting is `""`. | unit | `src/pages/tests/test_search_ready.py` | T1 |
| M3 | AC2 | normal | Given `GOOGLE_SITE_VERIFICATION=abc123-XYZ_9`, when `/` is opened, then the head has exactly one `<meta name="google-site-verification" content="abc123-XYZ_9">`. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M4 | AC3 | empty | Given the setting is `""`, when `/` is opened, then the page has no `google-site-verification` tag. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M5 | AC4 | error | Given the value `a"><script>`, when `/` is opened, then the tag reads `content="a&quot;&gt;&lt;script&gt;"` and the page gains no `<script>` tag. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M6 | AC5 | edge | With the setting `abc123`, a missing page (404, `DEBUG` off) and `/owner/login/` have no `google-site-verification` tag. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M7 | AC6 | normal | The text of `render.yaml` has a line `- key: GOOGLE_SITE_VERIFICATION` followed by a line `sync: false` (read as text: the project has no YAML library). | unit | `src/pages/tests/test_search_ready.py` | T1 |
| M8 | AC7 | normal | Given settings price 13–14 and Call `0905 123 456`, when `/` is opened, then one `application/ld+json` block follows the `og:site_name` tag and parses to exactly the JSON of AC7. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M9 | AC8 | empty | Given no price, the JSON has no `priceRange`; given no Call number but a Zalo number, no `telephone`; given no settings record, the block is still there with only the keys that have values. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M10 | AC9 | normal | The parsed JSON has none of the keys `image`, `geo`, `aggregateRating`, `review`, and its address has no `streetAddress` or `postalCode`. | unit | `src/pages/tests/test_search_ready.py` | T1 |
| M11 | AC10 | error | The function of AC11 given a description containing `</script><b>&` returns text with no `<`, `>` or `&`, which parses back to the same description. | unit | `src/pages/tests/test_search_ready.py` | T1 |
| M12 | AC11 | normal | `/` still makes exactly one database query with the block in the page. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M13 | AC12 | edge | A 404 page and `/owner/login/` have no `application/ld+json`; `/` has it with `INDEXING_ENABLED` on and off. | integration | `src/pages/tests/test_search_ready.py` | T1 |
| M14 | AC13 | normal | `bash scripts/check.sh` passes; `test_layout.py::test_page_uses_no_javascript` expects the JSON-LD tag first in its list. | unit | `src/pages/tests/test_search_ready.py` | T1 |
