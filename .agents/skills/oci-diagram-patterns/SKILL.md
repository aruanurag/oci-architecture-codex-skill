---
name: oci-diagram-patterns
description: Create reusable editable PowerPoint-native diagram patterns and visual motifs for OCI decks, such as layered system diagrams, control-plane and data-plane views, comparison frames, annotated screenshot layouts, packet-flow diagrams, and footprint visuals. Use when another deck or design skill needs a conceptual diagram pattern rather than a full OCI architecture topology.
---

# OCI Diagram Patterns

## Overview

Use this skill when a slide needs a reusable diagram pattern like:

- layered host and control-boundary diagrams
- control-plane versus data-plane diagrams
- side-by-side technical comparison frames
- annotated screenshot or terminal layouts
- lifecycle, packet, or processing flows
- coverage, footprint, or region-presence visuals
- component stacks, trust boundaries, or subsystem maps

This skill is a pattern-builder, not a full deck skill and not a full OCI topology generator.

It should usually work with one or more sibling skills:

- use [../oci-technical-decks/SKILL.md](../oci-technical-decks/SKILL.md) for instructor-led technical decks
- use [../oci-sales-decks/SKILL.md](../oci-sales-decks/SKILL.md) when a customer-facing deck needs a conceptual proof diagram
- use [../oci-ppt-design-director/SKILL.md](../oci-ppt-design-director/SKILL.md) when the visual system or slide rhythm must stay consistent
- use [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) when the slide needs a real OCI architecture plus a conceptual sidecar pattern

## What This Skill Owns

This skill owns:

- pattern selection
- diagram motif structure
- editable PowerPoint shape language
- boundary, lane, and module relationships
- geometry recommendations for reusable conceptual diagrams
- optional JSON fragments that reuse the PowerPoint renderer primitives when appropriate

It does not own:

- full deck storyline
- OCI product fact validation
- full OCI architecture topology
- final deck sign-off by itself

## Workflow

1. Start with a short plan:
   - what the slide needs to explain
   - whether the diagram is conceptual, comparative, architectural, or operational
   - who will read it
   - whether it must be customer-safe or can remain internal
2. Extract the semantic parts of the diagram:
   - boundaries
   - modules
   - actors
   - flows
   - labels
   - annotations
3. Choose the closest pattern from [references/pattern-catalog.md](references/pattern-catalog.md).
4. Read [references/shape-language.md](references/shape-language.md) to map the pattern to editable PowerPoint primitives.
5. Produce a `Pattern Brief` using [references/integration-contract.md](references/integration-contract.md):
   - pattern name
   - diagram objective
   - element inventory
   - geometry plan
   - connector plan
   - label strategy
6. When the sibling skill is PowerPoint-native, prefer editable shapes over pasted images:
   - `shape`
   - `text`
   - `edge`
   - OCI icon groups only when the diagram truly needs native OCI services or logos
7. If the pattern can be expressed through the PowerPoint renderer’s existing shape and edge primitives, provide an optional JSON fragment the sibling skill can drop into its slide spec.
8. If the desired look depends on decoration the renderer does not support well, such as gradients, soft shadows, or bespoke vector art, first approximate it with editable shapes. Use flattened or external art only when the editable approximation would be misleading or visibly poor.
9. Hand back integration notes to the sibling skill:
   - what stays visible on the canvas
   - what belongs in presenter notes
   - what spacing or symmetry rules are non-negotiable

## Pattern Guardrails

- Prefer editable PowerPoint shapes over screenshots or flattened illustrations.
- Use one dominant diagram idea per slide.
- Keep boundary hierarchy obvious.
- Keep connectors orthogonal unless a different route is materially clearer.
- Keep labels short and audience-facing.
- Put explanation, caveats, and transitions into presenter notes before adding extra on-canvas text.
- Use restrained color coding: one meaning per color family.
- Do not let decoration overpower the logic of the diagram.
- Avoid overlapping modules, crossing arrows, or labels sitting directly on connector lanes.
- When a sibling skill can already render OCI-native architecture honestly, do not replace it with a conceptual pattern.

## Deliverables

Default to producing:

1. `Pattern Selection`
2. `Pattern Brief`
3. `Element Inventory`
4. `Geometry Plan`
5. `Connector Plan`
6. Optional `PowerPoint JSON Fragment`
7. `Integration Notes` for the sibling skill

## Resources

- Read [references/pattern-catalog.md](references/pattern-catalog.md) after you understand the diagram objective.
- Read [references/shape-language.md](references/shape-language.md) before choosing colors, boxes, arrows, and callout treatment.
- Read [references/integration-contract.md](references/integration-contract.md) when handing a pattern back to another skill or when you want a reusable JSON fragment.
