---
name: oci-ppt-design-director
description: Direct the visual system, slide archetypes, spacing, and PowerPoint-native review standards for OCI decks and architecture slides. Use when the user wants a more polished look, stronger slide rhythm, cleaner spacing, better hierarchy, a theme refresh, or a reusable PPT design system before rendering.
---

# OCI PPT Design Director

## Overview

Use this skill when the user wants PowerPoint output that looks more deliberate, more consistent, and more customer-ready than a default generated deck.

This skill is a design director, not a renderer:

- it sets the visual thesis before slides are drafted
- it defines the slide system and layout contracts
- it controls density, spacing, and hierarchy
- it runs the final design review and PowerPoint-native quality gate

This skill should usually work with one or both sibling skills:

- use [../oci-sales-decks/SKILL.md](../oci-sales-decks/SKILL.md) for storyline, presales messaging, and slide-by-slide content
- use [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) for OCI-native architecture slides and final architecture rendering
- use [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) when the deck needs reusable conceptual diagram motifs such as layered system boxes, control-plane views, comparison frames, annotated screenshots, or footprint visuals

Treat this skill as a required review gate for every customer-facing PowerPoint deck or PowerPoint architecture slide before final sign-off.

## Use Cases

Use this skill for:

- executive decks that need stronger visual craft
- deck redesigns, theme refreshes, or cleaner clean-room presentation systems
- customer-facing PPTs where spacing, hierarchy, and slide rhythm matter as much as the copy
- architecture-heavy decks that need architecture slides to feel like part of the same presentation
- repeatable deck systems for Sales Engineering, presales, workshops, or POV proposals
- review-and-fix passes where the deck feels crowded, inconsistent, sparse, or obviously machine-generated

Do not use this skill as the only skill when the user mainly needs:

- a narrative outline with no visual deliverable
- a draw.io diagram
- a single raw architecture topology without broader PowerPoint styling concerns

## What This Skill Owns

This skill owns the visual contract for the deck:

- visual thesis
- slide archetypes
- content-density rules
- layout-safe zones
- spacing and alignment standards
- review gates before sign-off

It does not own:

- OCI product fact validation
- architecture topology correctness
- detailed presales storyline by itself
- icon rendering or PowerPoint package generation
- the low-level definition of reusable conceptual diagram motifs by itself

## Workflow

1. Identify the artifact:
   - executive briefing
   - customer solution recommendation
   - workshop readout
   - POV or POC deck
   - architecture-heavy customer deck
2. Create a short `Visual Direction Summary`:
   - audience sophistication
   - meeting outcome
   - tone such as assertive, consultative, technical, or board-ready
   - density target such as sparse, balanced, or proof-heavy
   - whether the deck should adapt a source presentation or stay clean-room
3. Build a `Visual Thesis` before slide drafting:
   - headline style
   - subtitle behavior
   - card style
   - hero-visual pattern
   - spacing model
   - palette direction
   - what to avoid
4. Choose the slide system using [references/slide-archetypes.md](references/slide-archetypes.md):
   - cover
   - why now or pressure
   - recommendation
   - proof or value
   - architecture
   - roadmap
   - next step
5. Define a layout contract for each slide type:
   - title zone
   - subtitle or context zone
   - hero zone
   - support zone
   - CTA or summary zone
   - maximum card count
   - maximum visible text load
   - whether the slide's interpretation lives on-canvas or in presenter notes
6. Set density and spacing rules using [references/design-principles.md](references/design-principles.md):
   - slide margins and gutters
   - card padding
   - title length expectations
   - maximum lines per box
   - when to split a slide instead of shrinking copy
7. Create a `Design Handoff Brief` for the sibling skills:
   - visual thesis
   - chosen archetypes
   - layout contract by slide
   - repeated diagram motifs or conceptual pattern choices when applicable
   - architecture-slide constraints when applicable
   - review gates that must pass before delivery
8. Route to the sibling skill:
   - use [../oci-sales-decks/SKILL.md](../oci-sales-decks/SKILL.md) to build or revise the story and visible copy
   - use [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) to render OCI-native architecture slides
   - use [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) when the deck needs a repeatable editable diagram pattern instead of ad hoc boxes and arrows
9. Review the rendered output using [references/review-gates.md](references/review-gates.md):
   - slide rhythm and consistency
   - overlap, clipping, alignment, and text containment inside the intended cards and containers
   - note leakage or visible author prompts
   - PowerPoint-native open and export behavior
10. Iterate until the deck feels deliberate, customer-safe, and presentation-ready rather than merely complete.

Do not treat this review as optional polish for customer-facing PowerPoint output. A clean design-director pass is part of the delivery contract.

## Director Guardrails

- Do not let design polish hide a weak recommendation or vague storyline.
- Do not copy visible content from internal Oracle decks unless that content is separately approved for reuse.
- Keep presenter notes, speaker coaching, and author prompts out of the visible canvas.
- Treat presenter-led decks as the default. If a slide only needs a spoken implication, guardrail, or workshop output, put it in PowerPoint notes instead of forcing a bottom summary strip onto the slide.
- Prefer editable PowerPoint elements over flattening content into images.
- Keep one clear message per slide.
- Prefer one hero device per slide instead of many competing visual centers.
- Reduce copy before reducing legibility.
- Treat text that escapes a card, container, chip, or summary strip as a blocker that fails sign-off.
- If a slide still feels sparse or awkward after spacing cleanup, rebalance the layout before adding decorative filler.
- Architecture slides must stay honest to OCI iconography and topology. This skill can direct the framing and whitespace, but not distort the technical meaning.
- Do not let architecture callouts, captions, or text cards sit on top of connector lanes.
- Keep architecture slides visually integrated with the deck without forcing the OCI renderer to break icon integrity or connector clarity.

## Design Questions

Ask only the questions that materially change the visual system, usually `1-4`:

- Should the deck feel executive-minimal or proof-rich?
- Should the deck inherit a source theme or use a clean-room system?
- Is the architecture slide a hero proof slide or a supporting technical slide?
- Does the customer expect conservative enterprise styling or a stronger point-of-view presentation?

Lead with the recommended option first and avoid a hardcoded checklist.

## Deliverables

Default to producing:

1. `Visual Direction Summary`
2. `Visual Thesis`
3. `Slide System`
4. `Design Handoff Brief`
5. `Design Review Findings`
6. `Final Sign-off Notes`

## Resources

- Read [references/design-principles.md](references/design-principles.md) after you know the audience and the meeting goal.
- Read [references/slide-archetypes.md](references/slide-archetypes.md) when selecting the deck’s repeatable slide system.
- Read [references/review-gates.md](references/review-gates.md) before sign-off or when the user asks for review-and-fix iteration.
- Read [../oci-sales-decks/SKILL.md](../oci-sales-decks/SKILL.md) when the deck storyline or presales messaging needs work.
- Read [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) when the deck needs OCI-native architecture slides or PowerPoint rendering.
- Read [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) when the deck needs reusable conceptual diagram motifs or editable technical diagram modules.
