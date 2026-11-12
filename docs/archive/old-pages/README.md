# Archived: the four page templates of epic 1

`house.html`, `hoa_xuan.html`, `faq.html` and `contact.html` were the inner pages of epic 1 (`/house/`, `/hoa-xuan/`, `/faq/`, `/contact/`). Issue #37 (one-page T1, 2026-11-12) made `/` the whole site: those addresses now redirect (301) to their chapter, and each chapter has its own template in `src/pages/templates/pages/chapters/`. The old templates are kept here instead of deleted ("Archive, do not delete", `.claude/rules/workflow.md`). Django does not load templates from this folder.
