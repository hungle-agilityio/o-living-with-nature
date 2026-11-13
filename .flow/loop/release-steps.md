# Release steps

The Project's release thread follows this file on `main`, in the main checkout on the Mac mini. The Project instructions point here so they stay under the 16,000-character limit of Project settings (ADR-017, ADR-031, ADR-032).

## Release ("phát hành")

1. When the owner asks for a release, a thread on the Mac mini runs `uv run python .flow/loop/release.py --dry-run` in the main checkout.
2. When the dry-run is refused by `security check failed: ...`, the card shows the security lines and offers only "Huỷ".
3. Otherwise the thread runs, in the main checkout, a security review of `git diff <the range printed after "Security review diff:">` with the method of Claude Code's `/security-review` (only findings of high or medium severity with high confidence), and shows the dry-run output on a choice card with `Security review: no findings.` or one line per finding, `<HIGH|MEDIUM> <file>:<line> <one-line reason>`.
4. With no finding the card is A "Phát hành (đề xuất)", B "Huỷ"; with a finding it is A "Huỷ (đề xuất)", B "Phát hành vẫn", and the owner decides (ADR-031).
5. After "Phát hành" it runs `uv run python .flow/loop/release.py --notes-url https://claude.ai/artifact/9YeTDzCKwuvkYq2jDphaye` and reports the branch, the tag and the pull request list, or the reason it refused. It also reports the `Release page:` line (the GitHub Release page of the tag), or the `warning: GitHub Release not created` line with its command.
6. When the output has the `Project settings:` line, after the release report the thread posts the whole `.claude/project-instructions.md` from `main` in one code block, saying "Paste this into Project settings (replace all)".
7. Only this command pushes `release/sprint-N`, the `v*` tags and `deploy` (ADR-017). Render then deploys `deploy` by itself after Checks pass.
8. After `release.py` succeeds, the thread updates the living release notes page https://claude.ai/artifact/9YeTDzCKwuvkYq2jDphaye (republished at the same link, newest release on top, in English): one section per release, `Release of <d Month yyyy>` with the tag, and one entry per pull request under `Client-facing pull requests:` of the output, written from its issue's user story and ACs (what users can do now, and where). Internal pull requests are not listed. With no client-facing pull request the section says `No changes on your screens in this release.` The page stays private and the owner shares it (ADR-029).
9. Then the thread runs `uv run python .flow/loop/live_check.py` in the main checkout and reports its lines.
10. On `result: fail` it runs `uv run python .flow/loop/rollback.py --dry-run` and shows the output on a choice card: A "Rollback (đề xuất)", B "Giữ bản này". After A it runs `uv run python .flow/loop/rollback.py`, then `uv run python .flow/loop/live_check.py --commit <target sha>`, and reports both. The rollback never moves `deploy` or a tag and leaves Render's Auto-Deploy on; the fix goes to `main` and out with the next release (ADR-032).
11. After `.flow/loop/live_check.py` prints `result: pass`, the thread checks the released ACs on the live site: it lists the epic pull requests in the release (titles starting `[EPIC]` in the `release.py` output), reads each epic's `docs/specs/<feature>/spec.md` on `main`, and checks every AC written Given/When/Then on the live site (`[live] url` of `.flow/flow.toml`), signed in as `demo` (`[live] username`, with `LIVE_CHECK_PASSWORD`) in a headless browser, keeping no screenshot and no page text beyond the AC's own expected text. It reports one table per epic: AC, `pass`, `fail: <what it saw>` or `n/a: <why>`.
12. For each `fail` it drafts a fast-lane issue (Summary with the user story, the failed AC as AC1, the steps it took, labels `risk:low` plus `needs-ui` when users see it) and shows it on a choice card: A "Đăng issue (đề xuất)", B "Bỏ qua"; it posts only after A. On `result: fail` of the live check, steps 11 and 12 do not run. A release with no epic: `No epic in this release; no live AC check.`

## Rollback

When the owner asks for "rollback": run `uv run python .flow/loop/rollback.py --dry-run` in the main checkout and show its output on a choice card, A "Rollback (đề xuất)", B "Giữ bản này"; after A run `uv run python .flow/loop/rollback.py`, then `uv run python .flow/loop/live_check.py --commit <target sha>`, and report both (ADR-032).

## One-time setup for the live check

The owner adds `LIVE_CHECK_PASSWORD` (the demo password set on Render), `RENDER_API_KEY` (Render, Account settings, API keys) and `RENDER_SERVICE_ID` (`srv-...`, from the service's page) to the loop's settings file on the Mac mini (`.flow/loop/agent.env` in the main checkout when that file exists, else `~/.o-living/agent.env`); sets `SENTRY_DSN` on Render (Environment); and the loop is restarted once ("dừng loop", then "bật loop") so the uptime ping starts.
