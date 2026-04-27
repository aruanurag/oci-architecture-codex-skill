# OCI Architecture and PowerPoint Skills Workspace

This repository is a Codex skill workspace for OCI-focused architecture generation and PowerPoint creation.

It bundles a coordinated set of local skills for:

- OCI physical architecture diagrams in `.drawio`
- OCI architecture slides in `.pptx`
- OCI presales and executive slide decks
- OCI instructor-led technical decks
- reusable PowerPoint-native diagram patterns
- visual direction and review gates for customer-ready PPT output

The repo is intentionally simple at the top level. Most of the logic, assets, references, and scripts live in `.agents/skills/`, and generated artifacts land in `output/`.

## Repository Layout

```text
.
|-- .agents/
|   `-- skills/
|       |-- oci-architecture-generator/
|       |-- oci-architecture-powerpoint-generator/
|       |-- oci-diagram-patterns/
|       |-- oci-ppt-design-director/
|       |-- oci-sales-decks/
|       |-- oci-technical-decks/
|       `-- shared/
|-- output/
`-- README.md
```

## Skills At A Glance

| Skill | Primary Job | Main Output | Best Used When |
| --- | --- | --- | --- |
| `oci-architecture-generator` | OCI architecture generation for draw.io | `.drawio`, `.json`, review reports, previews | You want an editable OCI architecture diagram |
| `oci-architecture-powerpoint-generator` | OCI architecture generation for PowerPoint | `.pptx`, `.json`, review reports, previews | You want an OCI architecture slide in PowerPoint |
| `oci-sales-decks` | OCI presales and executive storytelling | slide outline, notes, `.pptx` | You want a customer-facing sales or briefing deck |
| `oci-technical-decks` | OCI instructor-led technical presentations | slide outline, presenter notes, `.pptx` | You want a technical deck with notes on every slide |
| `oci-ppt-design-director` | visual system and design review | design brief, review findings, direction | You want cleaner, more polished PowerPoint output |
| `oci-diagram-patterns` | reusable conceptual diagram motifs | pattern brief, optional PPT JSON fragment | You need editable conceptual visuals, not full topology |
| `shared` | helper utilities for preview review | Python helpers | The OCI skills need shared audit logic |

## Skill Details

### `oci-architecture-generator`

What it does:

- Creates OCI physical architecture diagrams as finalized `.drawio` files.
- Starts with a planning pass and a clarification gate instead of jumping straight to drawing.
- Prefers bundled Oracle references before inventing a layout from scratch.
- Resolves OCI services to official icons first and surfaces honest fallbacks when a direct icon does not exist.
- Runs architecture review, spacing review, and connector cleanup until the diagram looks production-ready.

How to use it:

- Use it when the final deliverable should be an editable draw.io architecture.
- Use it for reference replication, OCI network layouts, multi-AD or multi-region designs, and clean physical diagrams.
- It defaults to physical diagrams, regional subnets unless the request says otherwise, and iterative review for overlaps, elbows, detached lines, missing icons, and container-boundary issues.

Example prompt:

```text
Use the oci-architecture-generator skill to create a physical OCI architecture for a highly available 3-tier web application with regional subnets and multi-AD deployment.
```

### `oci-architecture-powerpoint-generator`

What it does:

- Creates OCI architecture slides as PowerPoint-native `.pptx` output.
- Uses the bundled Oracle OCI PowerPoint toolkit as the visual source of truth.
- Applies the same planning, clarification, icon-resolution, and architecture-review discipline as the draw.io skill.
- Adds PowerPoint-specific review for overlap, spacing, connector routing, slide containment, and package-integrity issues.

How to use it:

- Use it when the architecture itself needs to be delivered as a PowerPoint slide instead of draw.io.
- Use it for executive or customer decks that need OCI-native icons and architecture framing.
- It stores presenter-only guidance in notes instead of visible slide furniture, and it treats repair prompts, broken previews, note leakage, and text overflow as blockers.

Example prompt:

```text
Use the oci-architecture-powerpoint-generator skill to create a physical OCI architecture slide for an OKE-based application with WAF, load balancer, and Autonomous Database.
```

### `oci-sales-decks`

What it does:

- Creates or adapts OCI customer-facing PowerPoint decks for presales, executive briefings, workshops, POCs, migrations, and recommendation narratives.
- Starts from an approved `Why OCI` deck or existing customer deck when available, otherwise builds clean-room.
- Keeps the story anchored in customer outcomes, recommendation logic, proof, and next steps rather than a service catalog.
- Uses OCI architecture as supporting evidence, not the whole story.

How to use it:

- Use it when the ask is a customer-facing OCI presentation, not just a single diagram.
- Use it for slide outlines, slide-by-slide messaging, speaker notes, or a full `.pptx`.
- It should normally pair with `oci-ppt-design-director` for visual system and review, and with `oci-architecture-powerpoint-generator` when the deck needs OCI architecture slides.

Example prompt:

```text
Use the oci-sales-decks skill to create an OCI executive recommendation deck for a customer CTO, including speaker notes and one supporting architecture slide.
```

### `oci-technical-decks`

What it does:

- Creates OCI technical decks for workshops, product overviews, architecture explainers, service deep dives, and field enablement.
- Treats every deck as instructor-led by default.
- Requires presenter notes on every slide and keeps visible copy concise enough for live delivery.
- Organizes material around how a service works, where it fits, tradeoffs, and operational implications.

How to use it:

- Use it when the audience needs a technical explanation rather than a sales story.
- Use it for networking, compute, observability, containers, storage, security, or architecture internals.
- It should normally pair with `oci-ppt-design-director` for review and with `oci-diagram-patterns` or `oci-architecture-powerpoint-generator` when the deck needs diagrams.

Example prompt:

```text
Use the oci-technical-decks skill to create an instructor-led OCI containers deck with presenter notes on every slide and one architecture explainer slide.
```

### `oci-ppt-design-director`

What it does:

- Acts as the visual direction and review layer for OCI PowerPoint work.
- Defines the visual thesis, slide archetypes, layout contracts, spacing rules, and density limits before rendering.
- Reviews PowerPoint output for rhythm, alignment, hierarchy, note leakage, clipping, crowding, and customer-readiness.

How to use it:

- Use it whenever the deck or architecture slide needs to feel deliberate, polished, and presentation-ready.
- Use it with `oci-sales-decks`, `oci-technical-decks`, and `oci-architecture-powerpoint-generator`.
- Treat it as a required review gate for customer-facing PowerPoint output, not optional polish.

Example prompt:

```text
Use the oci-ppt-design-director skill to improve the visual system, spacing, and review quality of this OCI customer deck before final delivery.
```

### `oci-diagram-patterns`

What it does:

- Creates reusable, editable PowerPoint-native conceptual diagram patterns.
- Covers motifs such as control-plane versus data-plane views, layered system diagrams, comparison frames, annotated screenshot layouts, packet flows, and subsystem maps.
- Produces a `Pattern Brief`, geometry guidance, connector guidance, and optional JSON fragments for sibling skills.

How to use it:

- Use it when a slide needs an explanatory diagram pattern rather than a literal OCI service topology.
- Use it as a helper for `oci-sales-decks`, `oci-technical-decks`, `oci-ppt-design-director`, or `oci-architecture-powerpoint-generator`.
- Prefer it over ad hoc boxes and arrows when a diagram motif might recur across slides or decks.

Example prompt:

```text
Use the oci-diagram-patterns skill to create a reusable control-plane and data-plane comparison motif for an OCI technical deck.
```

### `shared`

What it does:

- Holds shared helper code used by the OCI skills.
- The current shared helper is used by the preview-review wrappers in the architecture skills.

How to use it:

- You normally do not invoke `shared` directly.
- Keep it alongside the OCI skills when copying or installing the suite, because the review scripts import it by relative path.

## How The Skills Work Together

Use the skills as a small OCI content system rather than isolated tools:

- `oci-architecture-generator` for editable `.drawio` architecture source.
- `oci-architecture-powerpoint-generator` for OCI-native PowerPoint architecture slides.
- `oci-sales-decks` for presales and executive stories.
- `oci-technical-decks` for instructor-led product and architecture teaching decks.
- `oci-ppt-design-director` as the visual contract and final PPT review gate.
- `oci-diagram-patterns` when a slide needs conceptual diagrams that are not full OCI topologies.

Typical combinations:

- Customer deck: `oci-sales-decks` + `oci-ppt-design-director` + optional `oci-architecture-powerpoint-generator`
- Technical deck: `oci-technical-decks` + `oci-ppt-design-director` + optional `oci-diagram-patterns`
- Architecture-only slide: `oci-architecture-powerpoint-generator` + `oci-ppt-design-director`
- Editable source diagram: `oci-architecture-generator`

## Local Vs Global Installation

### Local Install In This Repo

This repository already uses the local-skill layout Codex expects:

- local skills live in `.agents/skills/`
- they are available only inside this workspace
- this is the best mode when the skills are under active development

Nothing extra is required for local use in this repo.

### Local Install In Another Repo

To use the same skill suite inside a different repository, copy the local skills folder into that repo:

```bash
REPO_ROOT=/path/to/OCiArchitecture-CodexSkill
mkdir -p /path/to/other-repo/.agents
cp -R "$REPO_ROOT/.agents/skills" /path/to/other-repo/.agents/
```

That installs the OCI skills only for that repository.

### Global Install For All Repos

To make the OCI skills available across repositories, copy the skill suite into the Codex global skills directory:

```bash
REPO_ROOT=/path/to/OCiArchitecture-CodexSkill
mkdir -p ~/.codex/skills
cp -R "$REPO_ROOT/.agents/skills/." ~/.codex/skills/
```

Global notes:

- The typical global location is `~/.codex/skills/`.
- Keep the directory names exactly the same.
- Copy `shared/` along with the OCI skills, because the review scripts expect it to exist as a sibling folder under the skills root.
- Installing the whole OCI suite together is recommended, because the skills cross-reference one another.
- If the skills do not appear immediately, start a new Codex session in the target workspace.

### Copy Vs Symlink

If you want the global install to track this repo while you continue editing the skills, you can symlink instead of copying:

```bash
REPO_ROOT=/path/to/OCiArchitecture-CodexSkill
mkdir -p ~/.codex/skills
ln -s "$REPO_ROOT/.agents/skills/oci-architecture-generator" ~/.codex/skills/oci-architecture-generator
ln -s "$REPO_ROOT/.agents/skills/oci-architecture-powerpoint-generator" ~/.codex/skills/oci-architecture-powerpoint-generator
ln -s "$REPO_ROOT/.agents/skills/oci-diagram-patterns" ~/.codex/skills/oci-diagram-patterns
ln -s "$REPO_ROOT/.agents/skills/oci-ppt-design-director" ~/.codex/skills/oci-ppt-design-director
ln -s "$REPO_ROOT/.agents/skills/oci-sales-decks" ~/.codex/skills/oci-sales-decks
ln -s "$REPO_ROOT/.agents/skills/oci-technical-decks" ~/.codex/skills/oci-technical-decks
ln -s "$REPO_ROOT/.agents/skills/shared" ~/.codex/skills/shared
```

## How To Invoke The Skills

In Codex, name the skill directly in the prompt:

```text
Use the oci-architecture-generator skill to create a multi-AD OCI web application diagram.
```

```text
Use the oci-sales-decks skill to create an OCI presales deck for a customer executive team.
```

```text
Use the oci-technical-decks skill to create a technical deck on OCI observability services with presenter notes on every slide.
```

## Output Artifacts

Generated files land in `output/`. Depending on the workflow, a run may produce:

- `.drawio` diagrams
- `.pptx` presentations
- `.json` render specs
- `.report.json` execution summaries
- `.quality.json` review outputs
- preview images for visual QA

Example artifacts already present in this workspace include:

- `lytx-oci-cto-deck-recreated.pptx`
- `oci-container-offerings-tech-deck.pptx`

## Quality Expectations

These skills are built for iterative, review-driven output rather than one-pass drafts. The shared expectations across the suite are:

- ask targeted clarification questions when the answer changes the architecture or the deck
- prefer official OCI icons and honest fallbacks
- keep connector routing simple and avoid unnecessary elbows
- prevent overlaps, clipped text, and elements crossing container boundaries
- keep presenter guidance in notes instead of leaking it onto slides
- rerender until the artifact is presentation-ready
