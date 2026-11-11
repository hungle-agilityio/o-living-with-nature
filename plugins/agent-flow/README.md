# agent-flow

The issue-to-pull-request flow of Ở — Living with Nature as a Claude Code plugin: the guard hooks, the flow skills, the slash commands and the sub-agents of a loop that builds labelled issues. It is listed by the marketplace `o-living` at the root of this repository (`.claude-plugin/marketplace.json`). Why it is a plugin: `.claude/knowledge/decisions/ADR-020-flow-as-a-plugin.md`.

| Folder | What |
|---|---|
| `hooks/` | The guard hooks, registered in `hooks/hooks.json` (see `hooks/README.md`) |
| `skills/` | The flow skills (`agent-flow:<skill>`) |
| `commands/` | The slash commands (`/agent-flow:<command>`) |
| `agents/` | The sub-agents (`agent-flow:<agent>`) |
| `tests/` | Tests of the plugin as a whole (no project words, versions, texts) |

The repository turns the plugin on in `.claude/settings.json` (`extraKnownMarketplaces` and `enabledPlugins`), and the hooks read the project's `ops/flow.toml` through `$CLAUDE_PROJECT_DIR`. The installed plugin only changes when its version does, so every change here raises the version in `.claude-plugin/plugin.json` (CI checks it with `ops/check_plugin_version.py`).

## Install (Mac mini)

```
claude plugin marketplace add hungle-agilityio/o-living-with-nature
claude plugin install agent-flow@o-living --scope project     # inside the repository
claude plugin install agent-flow@o-living --scope user        # used by the build worktrees
claude plugin disable agent-flow@o-living --scope user        # never enabled at user scope
```

Check it with `claude plugin validate plugins/agent-flow` (the plugin) and `claude plugin validate .` (the marketplace), both at the repository root.

## Tests

```
uv run pytest plugins/agent-flow .claude/skills -q --no-cov -p no:cacheprovider
```

Run them from the repository root: the hook tests need `ops/flow.toml` there (`hooks/tests/conftest.py`).

## What is known about plugins in `claude -p`

Found when the flow was moved into a plugin (Claude Code 2.1.318):

- Plugin hooks run in interactive and `claude -p` sessions, and `FLOW_LOOP` reaches them.
- Plugin skills resolve as `agent-flow:<skill>`; their scripts live at `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, a path that **changes with every version**. The old version's folder stays on disk.
- No Bash allow rule both survives a version change and allows only the plugin's own script: a `*` for the version also matches `..`. So no rule names the plugin's scripts; the hook `before-skill-script-allow` allows exactly the plugin's own skill scripts after resolving their real path (ADR-020, point 5).
