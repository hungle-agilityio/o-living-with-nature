# Release steps

The Project's release thread follows this file on `main`, in the main checkout on the Mac mini. The Project instructions point here so they stay under the 16,000-character limit of Project settings (ADR-017, ADR-031, ADR-032).

## Release ("phát hành")

1. When the owner asks for a release, a thread on the Mac mini runs `uv run python .flow/loop/release.py --dry-run` in the main checkout.
2. When the dry-run is refused by `security check failed: ...`, the card shows the security lines and offers only "Huỷ".
3. Otherwise the thread runs, in the main checkout, a security review of `git diff <the range printed after "Security review diff:">` with the method of Claude Code's `/security-review` (only findings of high or medium severity with high confidence), and shows the dry-run output on a choice card with `Security review: no findings.` or one line per finding, `<HIGH|MEDIUM> <file>:<line> <one-line reason>`.
4. With no finding the card is A "Phát hành (đề xuất)", B "Huỷ"; with a finding it is A "Huỷ (đề xuất)", B "Phát hành vẫn", and the owner decides (ADR-031).
5. After "Phát hành" it runs `uv run python .flow/loop/release.py` and reports the branch, the tag and the pull request list, or the reason it refused. It also reports the `Release page:` line (the GitHub Release page of the tag), or the `warning: GitHub Release not created` line with its command.
6. When the output has the `Project settings:` line, after the release report the thread posts the whole `.claude/project-instructions.md` from `main` in one code block, saying "Paste this into Project settings (replace all)".
7. Only this command pushes `release/sprint-N`, the `v*` tags and `deploy` (ADR-017). Render then deploys `deploy` by itself after Checks pass.

## Live check, rollback and live AC check

Live check, rollback and the live AC check are off: `.flow/flow.toml` has no `[live]` table. Turning them on is its own task (ADR-032).
