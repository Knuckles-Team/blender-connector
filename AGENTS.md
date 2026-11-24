# Blender connector engineering contract

<!-- agent-contract:start -->
## Agent contract

Tool-neutral rules for any AI agent or human working in this repository. This
block is maintained by the fleet standard; edit outside the markers.

- **Owner boundary:** this repository owns one external system's calls,
  mappings and MCP tools (spec prefix `CONN-BLENDER-CONNECTOR-`); it depends
  on the connector SDK only. The external system is the popular third-party
  `mcp-for-blender` upstream (formerly `blender-mcp`). Feature routing across
  repositories: [ecosystem boundaries](https://github.com/Knuckles-Team/pipelines/blob/main/reference/ecosystem-boundaries.md).
- **Setup:** run `scripts/bootstrap.sh`. It is idempotent and
  non-interactive: it pins uv and Python, syncs the locked environment,
  installs the git hooks and prints the gate command.
- **Gates:** `uvx pre-commit run --all-files` must pass before you push. Do
  not bypass hooks to get green.
- **Commits:** one logical change per commit with a `Spec: <ID>` trailer
  (or `Spec: none (<reason>)`), plus a `Co-Authored-By:` trailer naming the
  assisting agent. Stage explicit paths only; never `git add -A` or
  `git add .`. Use your own configured Git identity, never a tool or bot
  name.
- **Org rules:** [organization AGENTS.md](https://github.com/Knuckles-Team/.github/blob/main/AGENTS.md).
<!-- agent-contract:end -->

## Architecture

`blender_connector/upstreams.py` owns the one upstream declaration; the
connector SDK owns the registry, the pool, the health, the namespacing and
the activation. `blender_connector/mcp/` owns the connector-native tools
(`handshake`); `blender_connector/content_gen/` renders the packaged skill,
ontology and prompts from the authored source and the committed tool
snapshot. The SDK owns server policy, content publication and fleet
registration. The graph engine owns durable storage and semantics.

All Blender interaction stays in the upstream: the connector never opens a
second socket to Blender and never executes code in it.

## Setup and commands

Use the repository's locked environment. Install its declared test
dependencies and pre-commit before running `pre-commit run --all-files` and
`pytest -q`. The shared pipelines hooks own scanner versions and gate
policy; provision those tools through the approved development
environment, never a hook-time installer.

## Development rules

Keep configuration as operator-provided references. Do not generate
credentials, commit resolved secrets, bypass failing gates, or infer
publication/deployment permission from a scaffolding request. Test real
contract behavior with the fixture upstream at the outbound boundary. A
tool fingerprint is not release certification. The tool names in
`content/snapshots/blender.tools.json` are upstream names; the renderers
add the namespace prefix. Refresh the snapshot with
`scripts/generate_blender_content.py --refresh` after every upstream
update, then `--check` and `--live` before landing.

## Documentation and delivery

[README.md](README.md) contains install/start instructions; [docs/](docs/index.md)
contains usage and constraints. Keep both synchronized with code and
examples. Follow the current shared pipelines spec standard for
requirement bundles and its generators for status and the delivery
dashboard; do not hand-maintain status.

## Branching and isolation

Use a distinct topic branch and real Git worktree. Stage reviewed paths
only; never stash another session's work or disable verification. Commit,
push, open a PR, merge, publish and deploy each require the applicable
user authorization and checks. Do not automatically merge or remove
worktrees after scaffolding.
