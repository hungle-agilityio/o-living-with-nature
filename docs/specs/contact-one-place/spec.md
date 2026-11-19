# Spec: contact-one-place

## Summary

Two changes to the home page `/` and `/vi/`:

1. **Contact in one place (T1).** The Call / WhatsApp / Zalo buttons leave chapter 03 (the rent) and chapter 04 (FAQ). On a computer (more than 760 px wide) the only set is in chapter 05. On a phone (760 px or less) chapter 05 shows no buttons; the phone bar is the only place. The bar stays under the screen through the hero and chapter 01, slides in once chapter 02 (Hòa Xuân) reaches the screen, stays pinned down to the footer, and steps away while a field of the enquiry form has focus.
2. **The form stands out (T2).** The enquiry form of chapter 05 sits on its own Paper panel inside the Ink band, with Ink text, and its button reads "Send message →": 56 px high, as wide as the form, in Ink fill. The three contact buttons of chapter 05 become outlines, so "Send message →" is the one filled button of the chapter.

The journal note page, the owner pages and the 404 page do not change. No database query is added; the counter's places stay as they are (no migration).

## User story

As a visitor on a phone, I want one always-at-hand way to call or message the owner and a form that clearly invites me to write, so that I can get in touch without meeting the same buttons again and again.

As the owner (Bún), I want the contact buttons and the form to be easy to find, so that more visitors call or write to me.

## Acceptance criteria

Phone means a viewport 390 px wide and 844 px high; desktop means 1280 px wide. The demo data is the seed of `docs/design/prototype.html`: owner Bún, greeting "Hi, I'm Bún." with the line "I usually reply within an hour.", Call `tel:+84945384500`, WhatsApp `https://wa.me/84945384500`, Zalo `https://zalo.me/0945384500`. "A set of contact buttons" is a `div.contact-buttons` (from `includes/contact_buttons.html`).

### Contact in one place (T1)

- **AC1.** Given the owner settings above, when a visitor opens `/` (and `/vi/`) on desktop, then the page has exactly one set of contact buttons outside the phone bar, inside `#contact .contact__row`, with `data-place="contact"`; chapter 03 (`#rent`) has no `.rent__buttons` and no `data-place="rent"` link; chapter 04's `.faq-side__invite` holds only the owner's line ("Hi, I'm Bún. I usually reply within an hour.") and no `.contact-buttons`.
- **AC2.** Given a phone and `/`, when the page opens on the hero and the visitor scrolls through chapter 01 (the house), then the phone bar stays out of view (`contact-bar--away`); when the top of chapter 02 (`#hoa-xuan`) reaches the bottom of the screen, the bar slides in (`transform` 0.3 s, as on `main`) and stays shown through chapters 02, 03, 04, 05 and the footer; when the visitor scrolls back up until `#hoa-xuan` is wholly below the screen, the bar steps away again.
- **AC3.** Given a phone and `/`, when the visitor reaches chapter 05, then it shows the label, "ở lại?", the heading, the owner's line and the enquiry form, and no contact buttons (`.chapter--contact .contact__row .contact-buttons` is `display: none` at 760 px or less); the bar is shown at the bottom. The buttons stay in the markup of chapter 05 for desktop (AC1).
- **AC4.** Given a phone with the bar shown, when the visitor taps into any field of the enquiry form (name, how can I reply, move-in month, stay, message), then the bar moves out of view; when focus leaves the form, the bar comes back (if `#hoa-xuan` is not wholly below the screen).
- **AC5.** Given a phone without JavaScript, when `/` opens, then the bar always shows, as on `main` (the noscript style of `pages/home.html`). Given a browser without IntersectionObserver, the bar shows at once.
- **AC6.** `src/static/js/contact-bar.js` uses one IntersectionObserver on `document.getElementById("hoa-xuan")` (no longer the hero, the contact chapter or the sets of buttons). It toggles `contact-bar--away` on the bar while `#hoa-xuan` is not on screen and its top is below the screen, or while a field of `form.enquiry-form` has focus (`focusin` / `focusout` on the form). It adds `contact-bar-ready` to `<html>` after its first callback, at once when IntersectionObserver is missing, and at once (bar shown) when there is no `#hoa-xuan`. It stays under 4,000 bytes. The bar's markup `<nav class="contact-bar" aria-label="…">`, its look and `chapters/contact.css`'s `html:not(.contact-bar-ready) .contact-bar` rule stay as on `main`.
- **AC7.** Given an owner settings record with no channel, when `/` opens, then there is no bar, no bar script and no noscript style, and chapter 05 shows "the details are on their way" line, as on `main`.
- **AC8.** The counter's places (`DailyCount.Place`) keep their choices, so no migration is made; clicks are counted with `data-place` `contact` (chapter 05) and `bar` (phone bar) on the home page, `journal` on a journal note.

### The form stands out (T2)

- **AC9.** Given desktop and `/`, when the visitor reaches the form of chapter 05, then the form (`div#enquiry`) is a panel with background Paper `#f4f0e8` (`var(--paper)`), text Ink `#1f2a22` (`var(--ink)`), padding 48 px (32 px top and bottom, 24 px at the sides on a phone), radius 4 px and no top border, inside the Ink band. The lead "Or leave me a message", the labels and the privacy line are Ink; the line under each field is Ink at 35% and Ink when the field has focus; placeholders are Ink at 45%. The same panel holds the "sent" and "paused" states.
- **AC10.** Given `/`, the form's button is `<button class="button button--send" type="submit">Send message <span class="button--send__arrow" aria-hidden="true">→</span></button>` (on `/vi/` "Gửi lời nhắn"); its accessible name stays "Send message" / "Gửi lời nhắn". It is at least 56 px high and as wide as the form on desktop and phone, Ink fill with Paper text and capitals of 15 px (letter spacing 0.16 em); on hover or keyboard focus its fill is `#2f3d33` and the arrow moves 5 px to the right (no movement when the visitor asked for less motion). The privacy line sits above it.
- **AC11.** Given desktop and `/`, when the visitor looks at chapter 05, then Call, WhatsApp and Zalo are all outlines (Paper border and text, no fill), so "Send message →" is the one filled button of the chapter. The phone bar's Call keeps its Paper fill, as on `main`.
- **AC12.** Given the form sent back with errors, when it shows, then the summary box and each field's error line are `#a4502a` (border and text) on the Paper panel, and the line under a field with an error is `#a4502a`.

### Both tasks

- **AC13.** `/` and `/vi/` still make exactly one database query each; the journal pages, the owner pages and the 404 page are unchanged.
- **AC14.** Every test on `main` passes unchanged, except the ones each task lists under "Existing tests that change" in its issue, changed only as listed there. `bash scripts/check.sh` passes.

## Edge cases

- Empty: with no channel there are no buttons anywhere and no bar (AC7); the FAQ keeps the owner's line; the form's panel shows as usual (its "paused, no channel" state too).
- Large data: nothing grows with data; always one set of buttons.
- Narrow screens: at 320 px the bar keeps three equal pills (as on `main`) and the Send button stays full width.
- Reduced motion: the bar has no transition (as on `main`) and the arrow does not move.
- Keyboard on a phone: the bar never covers a field or the Send button while typing (AC4).

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Q1 Where does the one set of buttons live on desktop? | Chapter 05, above the form | The FAQ's sticky column | A visitor ready to get in touch goes to chapter 05; it sits next to the form. |
| Q2 When does the phone bar show? | From chapter 02 (Hòa Xuân) to the footer (owner, 05:28 UTC: "scroll past the hero and one more section") | Always from the first screen; after the hero only | The owner asked for it after the hero and chapter 01, then always. |
| Q3 The bar while typing in the form? | Steps away while a form field has focus | Always shown | It would cover the field and Send message above the phone keyboard. |
| Q4 How does Send message stand out? | 56 px, full width, arrow, the one filled button; the form on its own Paper panel (owner, 05:29 UTC) | Warm sand fill `#e4be97` | The brand has no bright accent colour; contrast of panel and button does the work. |
| Rent and FAQ after the buttons go? | Nothing in their place; the FAQ keeps the owner's line | A text link to chapter 05 | "Only one place"; the menu already links to Contact. |
| Journal note page? | Keeps its own block | Remove it | A separate page with no bar; not part of the repeat. |
| Counter places rent and faq? | Keep the choices, no migration | Remove them | Old rows stay readable in the report. |

## Decisions during build

See [decisions/](decisions/): one file per task, written by its build.

## Design

Prototype `docs/design/prototype.html` (Artifact https://claude.ai/artifact/2NC89mzeQcgb5aWe6hPg5j), group "Site · contact in one place (new)", approved with "Prototype ổn" on 2026-11-19:

- T1: `#one-rent`, `#one-faq`, `#one-contact` (desktop); `#one-phone-hero`, `#one-phone-house` (no bar), `#one-phone-hoa-xuan` (bar slides in), `#one-phone-rent`, `#one-phone-faq`, `#one-phone-contact`, `#one-phone-typing`, `#vi-one-phone-contact`, `#vi-one-phone-typing`.
- T2: `#one-send`, `#one-send-errors`, `#one-send-sent`, `#one-phone-send`, `#vi-one-send`.

The state `#rent-phone-no-bar` of the earlier contact-bar rule is removed; `#hoa-xuan-phone-bar` and `#rent-phone` now show the bar pinned.

## Open questions
