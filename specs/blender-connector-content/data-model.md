# CONN-BLENDER-CONNECTOR-CONTENT data model

This spec adds ontology classes and generated content files. It adds no persisted type.

- Pack classes (`blender_connector/ontology/blender.ttl`, CONN-BLENDER-CONNECTOR-CONTENT-R003): `app:BlenderApp` under `:Application`, `app:BlenderTool` under `:Tool`, `app:BlenderUseCase` under `:Task`; each parent edge declared under both parent-catalog namespaces.
- Pack properties: `app:appNamespace`, `app:appVersion` (implicit via the individual), `app:forApp`, `app:usesToolName`.
- Ontology individuals (CONN-BLENDER-CONNECTOR-CONTENT-R003): one `app:BlenderApp` with the namespace and the snapshot version, and one `app:BlenderUseCase` per functionality with its namespaced tool names.
- App source (`content/apps/blender.yml`, CONN-BLENDER-CONNECTOR-CONTENT-R002): authored summary, eight domain classes and nine functionalities.
- Tool snapshot (`content/snapshots/blender.tools.json`, CONN-BLENDER-CONNECTOR-CONTENT-R006): generated, sorted upstream tool names, descriptions and input schemas, with the app version.
