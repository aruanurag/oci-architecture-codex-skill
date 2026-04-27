# Shape Language

Use this file before choosing colors, boxes, arrows, and callout treatment.

## Core Principle

A conceptual diagram should read as a system, not a collage.

Use a small shape vocabulary consistently:

- boundaries
- zones
- modules
- connectors
- callouts
- chips

## Primitive Mapping

Prefer these PowerPoint-native primitives first:

- `rounded-rectangle` for most modules
- `ellipse` for adapters, loops, or legacy nodes
- `cloud` for external network or external system actors
- `text` for labels and titles
- `edge` for flows

Use OCI icon groups only when the slide truly needs OCI service identity rather than a conceptual block.

## Boundary Treatment

- Outer environment: light neutral fill or dark inverse section frame.
- Inner trust or control boundaries: border-first treatment with restrained fill.
- Keep visible inset between nested boundaries.
- Use the boundary title once, not repeatedly inside the zone.

## Module Treatment

- Keep module corners rounded and readable.
- Use one color family per semantic class.
- Do not rely on color alone for meaning; labels still matter.
- Avoid more than `4-6` module colors on one slide.

## Connector Treatment

- Keep connectors orthogonal.
- Prefer straight routes before elbows.
- Differentiate semantic families with dash or color only when it clarifies meaning.
- Keep arrowheads consistent.
- Keep connector labels off the line unless absolutely needed.

## Chips And Micro-Labels

Use small chips for:

- VM
- PCIe bus
- system resources
- control tags
- role markers

Keep them:

- compact
- high-contrast
- away from arrowheads

## Color Direction

Recommended default families:

- neutral gray for outer environments
- muted teal or blue for control zones
- warm amber or coral for active subsystem modules
- green for managed or control services
- white or pale neutral for external actors

Avoid:

- gradients as the primary differentiator
- random saturated colors
- too many accent families on one slide

## Unsupported Or Fragile Styling

The current PowerPoint renderer handles:

- solid fills
- strokes
- common primitive shapes
- editable text
- orthogonal connectors

It is weaker at:

- gradients
- soft shadows
- decorative scribbles
- bespoke vector icons

If a pattern depends on those, approximate with editable shapes first and only escalate to copied vector artwork if the result otherwise becomes misleading or visibly poor.
