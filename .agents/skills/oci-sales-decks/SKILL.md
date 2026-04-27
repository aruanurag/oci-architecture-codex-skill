---
name: oci-sales-decks
description: Create or adapt OCI customer-facing PowerPoint slide decks for presales, executive briefings, solution recommendations, workshop readouts, POV or POC proposals, migration narratives, and competitive positioning. Use when the user wants a new OCI deck, an adapted "Why OCI" starter deck, slide outline, slide-by-slide content, speaker notes, or a polished PowerPoint that connects business outcomes, OCI architecture, and next steps.
---

# OCI Sales Decks

## Overview

Use this skill when the user wants a new OCI PowerPoint deck or a major rewrite of an OCI customer deck.

This skill is Sales Engineering and presales focused:

- lead with customer outcomes, not a service catalog
- frame recommendations and tradeoffs clearly
- tailor the story to executives, technical buyers, or mixed audiences
- keep the deck concise and action-oriented
- use OCI architecture as supporting proof, not as the whole story

This skill is not the right starting point when the user only wants a single OCI architecture diagram or a single architecture slide. In that case, use the sibling architecture skills directly.

## Use Cases

Use this skill for:

- executive briefings
- customer solution recommendation decks
- workload modernization or migration decks
- workshop agendas and workshop readouts
- POV or POC proposal decks
- competitive positioning or takeout decks
- customer follow-up decks after discovery or architecture sessions
- deck outlines, slide-by-slide messaging, speaker notes, or full `.pptx` creation

## Quick Routing

- If the user provides an approved internal `Why OCI` deck or an existing customer deck, audit it first and use it as the design and storytelling starting point.
- If the user needs a new deck quickly, pick the closest blueprint from [references/deck-blueprints.md](references/deck-blueprints.md) and adapt it.
- If the user needs a sharper storyline for an existing deck, preserve the strongest slides, remove repetition, and rebuild the opener, recommendation, and next-step slides first.
- For any customer-facing PowerPoint deck or architecture slide that will ship in PowerPoint form, read [../oci-ppt-design-director/SKILL.md](../oci-ppt-design-director/SKILL.md) and let it define the visual contract and review gate before final PPT authoring.
- If the deck needs conceptual proof diagrams, capability stacks, comparison frames, or other reusable non-topology visuals, read [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) instead of improvising boxes and arrows slide by slide.
- If the deck needs OCI architecture slides or Oracle visual assets, read [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) and use that workflow for the architecture slide instead of improvising it.
- If the deck needs a draw.io source diagram before slide creation, read [../oci-architecture-generator/SKILL.md](../oci-architecture-generator/SKILL.md).

## Starter Deck Preference

Prefer this order of starting inputs:

1. A user-provided, approved internal `Why OCI` starter deck.
2. A user-provided existing customer deck that needs to be sharpened or repurposed.
3. A clean-room deck built from scratch.

When a starter deck exists:

- use it as a pattern library for narrative arc, layout rhythm, typography hierarchy, proof-slide types, and theme
- do not copy or lightly paraphrase its visible copy, charts, proof points, customer examples, or sourced claims unless the user separately provides those facts for reuse
- remove or rewrite inherited internal-only material before it reaches the customer deck

If no starter deck is provided, proceed from scratch using [references/why-oci-north-star.md](references/why-oci-north-star.md).

## Workflow

1. Choose the starting artifact:
   - first look for an attached or referenced `Why OCI` starter deck or an existing customer deck
   - if none exists, ask once for an approved starter deck if it would materially help; otherwise proceed from scratch
   - if a starter deck exists, audit it for slide archetypes, section pacing, visual hierarchy, proof patterns, and anything that is internal-only or must be removed
2. Start with a short plan:
   - engagement type
   - audience
   - desired outcome
   - whether to adapt a starter deck or build clean-room
   - missing information that would materially change the deck
3. Identify the deck mode:
   - executive briefing
   - technical solution recommendation
   - workshop readout
   - POV or POC proposal
   - competitive positioning
   - internal account strategy
4. Extract the customer facts that shape the story:
   - industry and workload
   - business goals and pain points
   - timeline and urgency
   - stakeholders and decision criteria
   - constraints such as region, security, compliance, or migration posture
   - competitors or incumbent platforms
   - success metrics
5. Ask only the smallest useful set of follow-up questions, usually `1-4`, after the plan and any starter-deck audit. Questions must be driven by real decision gaps, not by a hardcoded checklist. Lead with the recommended assumption or option first.
6. Choose the closest deck blueprint from [references/deck-blueprints.md](references/deck-blueprints.md).
7. Tune the tone and detail level using [references/presales-storytelling.md](references/presales-storytelling.md) and the design/content guidance in [references/why-oci-north-star.md](references/why-oci-north-star.md).
8. For every customer-facing `.pptx` deck, read [../oci-ppt-design-director/SKILL.md](../oci-ppt-design-director/SKILL.md) and capture a visual thesis, slide system, and review gates before final slide authoring. Treat the design-director review as mandatory, not optional polish.
9. Build the storyline before drafting slides:
   - why now
   - current-state friction
   - desired future state
   - what OCI does differently that matters for this customer
   - recommended OCI approach
   - why OCI for this customer
   - proof themes such as economics, workload fit, distributed cloud, AI, or operations only when they support the ask
   - delivery or adoption path
   - risks, dependencies, and open questions
   - next steps
10. Draft the deck slide by slide. For each slide, include:
   - `title`
   - `core message`
   - `supporting points`
   - `recommended visual`
   - `speaker notes` when useful, but keep them separate from visible slide copy
   - `call to action` when the slide should drive a decision
   - for presenter-led decks, move implication, guardrail, output, and talk-track interpretation into `speaker notes` or `presenter_notes` instead of adding visible bottom bars unless the user explicitly wants a leave-behind summary on the canvas
   - when the slide needs a reusable conceptual diagram motif, route through [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) and record the selected pattern
11. If the user wants an actual `.pptx`:
   - if a starter deck is approved for adaptation, preserve the layout rhythm, visual hierarchy, and theme where useful, but rewrite or replace inherited content slide by slide
   - if working from scratch, use the abstract north-star principles in [references/why-oci-north-star.md](references/why-oci-north-star.md) rather than imitating any one internal deck too literally
   - always use [../oci-ppt-design-director/SKILL.md](../oci-ppt-design-director/SKILL.md) to set the design contract and run the final review before rendering a customer-facing PowerPoint deck
   - use [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) for editable conceptual proof diagrams and comparison motifs when the slide needs more than simple cards
   - reuse approved Oracle visual language when appropriate
   - use [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) for OCI architecture slides
   - reuse [../oci-architecture-powerpoint-generator/assets/powerpoint/oracle-oci-architecture-toolkit-v24.1.pptx](../oci-architecture-powerpoint-generator/assets/powerpoint/oracle-oci-architecture-toolkit-v24.1.pptx) when OCI-native architecture visuals are needed
   - keep the deck concise instead of expanding into documentation
12. If you produce or update a `.pptx`, export a preview with [../oci-architecture-powerpoint-generator/scripts/export_powerpoint_preview.py](../oci-architecture-powerpoint-generator/scripts/export_powerpoint_preview.py) when available and review for crowded slides, weak headlines, alignment issues, leaked notes, internal-only remnants, and visual overlap.
13. Before sign-off, explicitly record that the design-director review passed or list the findings that were fixed.
14. Always finish with a concrete next step, owner, or decision request.

## Default Deck Sizes

- Executive briefing: `6-8` slides
- Customer solution recommendation: `8-12` slides
- Workshop readout: `5-7` slides
- POV or POC proposal: `6-9` slides
- Competitive positioning: `5-7` slides

Increase slide count only when the audience or artifact really needs appendix material.

## Sales Engineering Guardrails

- Lead with the customer problem and business outcome first.
- When a starter deck is available, borrow structure and visual system before borrowing words. Rewrite copy from scratch unless the user explicitly provides approved text to retain.
- Translate OCI services into buyer-relevant language such as speed, risk reduction, security posture, operational simplicity, or platform fit.
- Do not invent pricing, discounts, SLAs, benchmarks, contractual language, roadmap commitments, or region availability.
- Do not carry over statistics, charts, customer logos, case studies, or proof points from a starter deck unless they are separately validated for the target deck.
- When precise OCI product facts matter, verify them against official Oracle sources instead of guessing.
- Separate what is `known`, `assumed`, and `recommended`.
- Keep the core story executive-friendly even when the room includes architects. Push dense technical detail into backup slides when possible.
- Keep presenter coaching, writing prompts, and authoring instructions out of the visible slide canvas. Phrases such as `the pitch should`, `keep the deck anchored`, `narrative for the CTO`, or similar belong in notes or should be removed before rendering.
- Treat customer-facing decks as presenter-led by default. Use visible takeaway or guardrail strips only when the user explicitly wants a leave-behind artifact; otherwise move that material into PowerPoint notes.
- Keep internal-only marks, confidentiality labels, and legal text only when they are appropriate for the target audience and approved source deck.
- Prefer `1-2` architecture slides in a presales deck unless the user explicitly wants a deep technical workshop.
- For OCI architecture slides inside a presales deck, prefer native OCI icon labels and put customer-specific wording in surrounding narrative text before rewriting multiple grouped icon labels directly.
- Avoid laundry-list slides that just enumerate OCI services without a customer decision point.
- Keep one clear message per slide. The title should state the answer or takeaway, not just the topic.
- Favor a `statement -> proof -> implication` rhythm. A slide should normally have one headline, one hero visual or proof device, and a short interpretation.
- Keep visible subtitles audience-facing and concise. Prefer one takeaway sentence rather than a presenter instruction.
- Keep visible text boxes compact. As a default guardrail, target `3-5` lines per card or content box and shorten the copy before shrinking it into overlap.
- Use the customer name, industry terms, and workload language when provided.
- Keep competitive positioning tied to the customer's priorities instead of generic vendor claims.

## Review Checklist

Before sharing the deck or outline, check:

- Is the recommendation explicit?
- Does the deck tell a story instead of listing features?
- Would an executive understand the ask from the title slide and final slide alone?
- Is there a clear `why OCI` thread tied to the customer problem?
- If a starter deck was used, did all inherited copy, customer examples, and proof points get rewritten, removed, or separately validated?
- Does the slide sequence have a deliberate rhythm such as customer pressure, OCI thesis, proof, recommendation, and next step?
- Did the deck pass an explicit design-director review for spacing, hierarchy, rhythm, and PowerPoint-native behavior before delivery?
- Did any presenter notes, speaker coaching, or authoring instructions leak into visible slide text?
- If the deck is presenter-led, did implication bars, guardrails, workshop outputs, or CTA interpretation move into notes instead of remaining as visible footer bands?
- Did any internal-only label, speaker prompt, or confidential footer remain that should not ship to the customer?
- Does any visible text clip, overlap another text box, or touch a container border?
- Are assumptions and open questions visible where they matter?
- Are the next steps concrete?
- Did every generated `.pptx` open cleanly through a PowerPoint-native export path, without falling back to `quicklook-pptx`, timing out, or showing a repair prompt?

## Deliverables

Default to producing:

1. A short planning summary.
2. A starter-deck audit summary when a source deck is provided, including what to preserve structurally, what to replace, and what to remove.
3. The recommended deck type and why it fits.
4. The slide-by-slide outline.
5. Speaker notes when they add value.
6. Architecture-slide handoff notes when OCI diagrams are needed.
7. A final `.pptx` when the user asks for an actual deck.
8. Assumptions, risks, and next steps.

## Resources

- Read [references/deck-blueprints.md](references/deck-blueprints.md) after you know the deck type.
- Read [references/presales-storytelling.md](references/presales-storytelling.md) after you know the audience and need to sharpen the narrative.
- Read [references/why-oci-north-star.md](references/why-oci-north-star.md) when the deck should feel like a polished OCI field deck, or when no approved starter deck is available and you need clean-room guidance for design and content strategy.
- Read [../oci-ppt-design-director/SKILL.md](../oci-ppt-design-director/SKILL.md) for every customer-facing PowerPoint deck before final rendering and sign-off.
- Read [../oci-diagram-patterns/SKILL.md](../oci-diagram-patterns/SKILL.md) when the deck needs conceptual diagrams, capability stacks, side-by-side comparison motifs, or other reusable editable visuals that are not full OCI architectures.
- Read [../oci-architecture-powerpoint-generator/SKILL.md](../oci-architecture-powerpoint-generator/SKILL.md) when the deck needs OCI architecture slides or Oracle toolkit visuals.
- Read [../oci-architecture-generator/SKILL.md](../oci-architecture-generator/SKILL.md) when the deck needs a source diagram before slide authoring.
- Use [../oci-architecture-powerpoint-generator/scripts/export_powerpoint_preview.py](../oci-architecture-powerpoint-generator/scripts/export_powerpoint_preview.py) to preview a generated deck when visual QA matters.
