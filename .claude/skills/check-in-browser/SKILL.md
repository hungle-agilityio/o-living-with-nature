---
name: check-in-browser
description: Start the app on a throw-away database, drive the pages in a headless browser, save a screenshot of each step and report console errors, failed requests and missing text. Use in /verify for any issue that changes what users see, or when the user asks to check a page in the browser.
---

# Check in a browser

Unit tests prove the parts; the browser proves the feature. This skill runs the real pages the way a user would and reports what a user cannot see: console errors and failed requests.

## Run it

```
uv run python .claude/skills/check-in-browser/browser_check.py
```

- It starts the app on a **throw-away database** (never `db.sqlite3`), runs the steps in a headless Chromium with a fixed window size (1280 by 800), and stops the app and deletes the database at the end.
- The pages are public, so every step runs as a visitor; there is no sign-in.
- Default steps: the home page and the health page.
- Screenshots, one per step, and `result.json` go to `out/browser-check/<time>/` (git-ignored). The screenshots show the public pages only.
- For another page or flow, write a spec from the issue's "Steps to check the result" and pass it with `--spec`: a list of steps, each with a `name`, a `goto` address, optional `actions` (`select`, `fill`, `click` on a selector), and optional `expect` and `absent` texts. A step may also give `status`, the HTTP status its page must answer (for example 404 for an error page). A spec written as an object (`{"steps": [...]}`) may set `"debug": false` to run the app as in production (needed to see `404.html` or `500.html`) and `"viewport": "390x844"` for a narrow screen; `--debug-off` and `--viewport` do the same on the command line and win over the spec.
- **Debug off** runs the app as in production on this machine: it collects the style files (`collectstatic`) before starting the app, lets WhiteNoise serve them as the live site does (`runserver --nostatic`), and sets `DJANGO_SECURE_SSL_REDIRECT=0` for this run only, so the plain local address is not sent to https. The live site keeps its https redirect.
- **Close-up of the changed part:** a step may give `"capture": "<css selector>"`. The step then saves the full page `NN-<name>.png` as before and the first visible match alone as `NN-<name>-element.png`; `result.json` lists them as `screenshot` and `element_screenshot`. If the selector matches nothing visible, the step fails with `capture: no visible element for <selector>` (exit code 1) and keeps no close-up. The masking scan covers the step as before, and a finding deletes both screenshots of that step. A step without `capture` is unchanged.

```
{"steps": [{"name": "house-en", "goto": "/en/house/",
            "expect": ["Garden house"], "capture": "main h1"}]}
```

## Read the result

| Exit code | Meaning | What to report |
|---|---|---|
| 0 | `result: clean`: no console error, no failed request, every expected text shown | PASS, with the screenshots of the steps |
| 1 | Something is wrong | FAIL, with each flagged line and its screenshot |
| 3 | **Masking:** personal data was found; the run stopped and kept no screenshot of that step | FAIL for masking: name the kind and the step (never the value), and do not share anything |
| 2 | The check could not run | NOT CONFIGURED and the reason; if no browser is installed run `uv sync` and `uv run playwright install chromium`, then try once more |

## Masking

Every page text, log line and address is scanned for emails, phone numbers, tokens, local paths, public IP addresses and credentials in a URL. The first finding stops the whole run, the screenshot of that step is deleted, and logs are stored with the values replaced by `[redacted]`; only the kind and the step are reported. `result.json` carries `masking: clean` or `findings`, which the report and the sharing gate read.

- Only the page is captured (never the browser window), on a throw-away database.
- Numbers shown on the site on purpose (the owner's Call, WhatsApp and Zalo number) are listed in `public_values.txt`, one per line (`#` starts a comment). The scan, the redaction and the stored logs skip a listed number in any spelling (spaces, dots, dashes, `+84` or a leading `0`, `tel:` links); any other phone number is still reported. A public email is still reported.
- Fields marked `data-sensitive` in the templates are blurred in the screenshots with `--blur`.
- `--plant` is not supported yet (the app stores no content); it stops with `NOT RUN`.

## Rules

- After **three failed actions in a row** the run stops by itself. Do not retry in a loop: tell the user what failed and ask.
- Never point it at the developer database; never publish the screenshots (sharing is a separate step with its own checks).
- The browser extension for Chrome is not needed and is not used; this check has its own browser and profile.
- Report only what the output says. Never write PASS without having run it.
