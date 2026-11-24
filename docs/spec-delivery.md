# Spec delivery

Specs for this connector live under [`specs/`](../specs/README.md) and
follow the shared pipelines spec standard:

- [`CONN-BLENDER-CONNECTOR`](blender-connector/spec.md) — the upstream
  declaration, the native tool, deployment modes and the phase gates.
- [`CONN-BLENDER-CONNECTOR-CONTENT`](blender-connector-content/spec.md) —
  the generated skill, ontology and prompts and their gates.

Requirement rows carry their delivery state in `status.json`, which the
lifecycle generator owns; run the pipelines `spec-status` hook after
reviewed source changes enter Git history. A passing source test does not
establish publication or deployment.
