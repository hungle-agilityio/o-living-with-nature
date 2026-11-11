# ADR-020: The flow is a Claude Code plugin, agent-flow

- Status: Accepted
- Superseded in part by ADR-023 (no agent:manual)
- Date: 2026-11-05
- Adopted here: 2026-11-11, when this repository was set up with the flow. The incidents in Context happened in the project the flow was first built in; their issue numbers are left out because they are not this repository's.

## Context

The flow's hooks, skills, slash commands and sub-agents used to live in each project's `.claude/`, so every fix had to be made in each copy, and a loop build on a pull request branch ran that branch's own copy of the hooks, so a branch could weaken its own guards. This repository carries its own copy of the plugin, so it depends on no other repository.

## Decision

1. **One plugin in this repository.** `plugins/agent-flow/` holds the guard hooks (`hooks/hooks.json`), the flow skills, the commands and the sub-agents, with their tests. The marketplace `o-living` (`.claude-plugin/marketplace.json` at the repository root) lists it. `.claude/settings.json` turns it on: `extraKnownMarketplaces` has only `o-living` (source: this repository on GitHub) and `enabledPlugins` has only `agent-flow@o-living`. `ops/flow.toml` names the same plugin (`[plugin] id`, `marketplace`).
2. **Generic.** The hooks read the project through `$CLAUDE_PROJECT_DIR` (`ops/flow.toml`, `ops/flow_config.py`; the allowed repository is `project.repo`). The skills, commands and sub-agents name no project and point to the project's `.claude/rules/`, `.claude/knowledge/` and `ops/flow.toml`. A test (`plugins/agent-flow/tests/test_generic_words.py`) greps them for this project's words. The app skills (`check-in-browser`) stay in `.claude/skills/`.
3. **Names.** Skills resolve as `agent-flow:<skill>`, commands as `/agent-flow:<command>`, sub-agents as `agent-flow:<agent>`.
4. **A pull request branch runs the installed plugin from `main`**, never its own copy. Which plugin files a loop build may edit is set by ADR-023.
5. **Skill scripts without a prompt.** The plugin's path holds its version, and a permission rule with `*` for the version also matches `..`, so it could run a script outside the plugin. No rule names the plugin's scripts. The hook `before-skill-script-allow` answers `allow` for exactly one plain `python3 [-I]` or `uv run python` call of a `.py` file at `skills/<skill>/` of the plugin, after resolving its real path; anything else is left to the permission rules.
6. **Versions.** The installed plugin changes only when its version does, so every change under `plugins/agent-flow/` raises the version in `plugin.json` (CI: `ops/check_plugin_version.py`). The version starts at `1.0.0` in this repository. The tick runs `claude plugin marketplace update` and `claude plugin update` once per tick.
7. **Install on the Mac mini.** From this repository only: `claude plugin marketplace add hungle-agilityio/o-living-with-nature`, then in the repository `claude plugin install agent-flow@o-living --scope project`; the build worktrees use a user-scope install that stays disabled (`claude plugin install agent-flow@o-living --scope user`, then `claude plugin disable agent-flow@o-living --scope user`).
8. **The coverage gate is a project setting.** The report reads it from `FLOW_COVERAGE_INCLUDE` and `FLOW_COVERAGE_FAIL_UNDER` in `.claude/settings.json` `env`; `ops/flow.toml` has no key for it yet.

## Decisions

| Question | Chosen | Rejected | Why |
|---|---|---|---|
| Where the plugin lives | This repository: `plugins/agent-flow/` + root marketplace `o-living` | A shared plugin from another repository | The project must not depend on another repository; one place to review |
| What goes in | Hooks, flow skills, commands, sub-agents, made generic | Hooks and skills only | One package |
| New versions on the Mac mini | Marketplace install; the tick runs `plugin update` each tick | `--plugin-dir` from `main`; update by hand | Same route for loop and interactive sessions |
| Skill scripts in `claude -p` | A plugin hook allows only the plugin's own skill scripts, after resolving the real path | An allow rule with the exact version; `ask` (refused in `claude -p`) | A `*` rule escapes with `..`; an exact rule breaks at each update; `ask` would stop the verify report |

## Consequences

- A change to the flow is a change to this repository, reviewed like app code, with a new plugin version.
- The plugin's own tests run in CI (`Plugin and skill tests`).
