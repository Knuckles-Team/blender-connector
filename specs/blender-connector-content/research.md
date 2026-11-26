# Research

Unknowns settled while building this spec.

- Skills must be valid Agent Skills: lowercase names with hyphens that match their folder, so the functionality `build_scene` renders the skill `blender-build-scene` while its prompt keeps the task name `blender-build_scene`.
- The tool-use contract (ordered tools with arguments) is authored once per functionality as numbered steps, each with one objective and a check, and rendered into the skill, the prompt and the ontology.
- Role prompts follow the agent-definition shape (kind, tools, skills, data, guardrails, outputs) so the gateway can build agents from them.
