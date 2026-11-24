# Engine ontology seam contract

Provider: medulla MEDULLA-TYPED-PACKS-R105
Consumer: blender-connector CONN-BLENDER-CONNECTOR-CONTENT-R003

Counterpart: medulla `specs/typed-packs-and-catalog/requirements.md`, rows `MEDULLA-TYPED-PACKS-R071.2` and `MEDULLA-TYPED-PACKS-R102.3`.

## Wire shape

The pack carries the single ontology file `blender.ttl` as a Turtle entry under the app namespace `http://knuckles.team/kg/blender#`. The file declares no `owl:imports` at all, so it never imports the core ontology and never needs a sibling pack. Every class has an `rdfs:subClassOf` path to a core class: `app:BlenderApp` to `:Application`, `app:BlenderTool` to `:Tool`, `app:BlenderUseCase` to `:Task`. The domain classes extend `:Document`, `:Artifact` or `:CreativeWork`.

The parent catalog a serving engine composes depends on the engine generation. PyPI medulla 3.3.3 composes it under the retired `http://knuckles.team/kg#` namespace; current-source medulla composes it under the single organization base with the core module at `https://knuckles-team.github.io/ontology/core` (MEDULLA-TYPED-PACKS-R105.1, R071.2). The orphan check is refuse-only (R105), so one namespace would orphan the pack on the other generation. Each class therefore names its core parent under both namespaces: one `rdfs:subClassOf` edge to the `http://knuckles.team/kg#` class and one to the same local name under `https://knuckles-team.github.io/ontology/core#`. Both edges point at core classes as objects, never subjects, so the redeclaration check (MEDULLA-TYPED-PACKS-R102.3) is not triggered.

## Refusal codes

The engine refuses an import with `ONTOLOGY_PACK_IMPORTS_CORE`, `ONTOLOGY_ORPHAN` or `ONTOLOGY_CORE_CONFLICT`. The connector adds `CONTENT_PARENT_UNKNOWN` at generation time so it never ships a file that the engine would refuse.
