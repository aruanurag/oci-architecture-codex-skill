# Technical Storytelling

Use this file when the deck risks becoming a pile of features instead of a teachable technical narrative.

## Core Flow

Prefer this sequence:

1. the technical question
2. the old constraint or common failure mode
3. the OCI mechanism
4. the operational consequence
5. when to use it
6. the tradeoffs or caveats
7. the summary

## Slide-Level Pattern

Each technical slide should try to answer one of these:

- What is it?
- Why does it exist?
- How does it work?
- Where does it sit?
- When should I use it?
- What should I watch out for?

If a slide answers more than one of those questions, split it or move some explanation into notes.

## Mechanism Before Marketing

- explain the system behavior first
- then explain why that behavior matters
- then explain what decision the audience should make

Avoid jumping straight from feature name to business claim.

## Comparison Slides

For comparisons:

- compare on the dimensions that change architecture or operations
- keep the table small enough to scan in the room
- say the tradeoff clearly
- use notes for nuance, exceptions, and audience-specific guidance

## Presenter Notes Pattern

Every slide should include notes that answer:

- what is the one point to land verbally
- what common confusion to preempt
- what transition leads to the next slide

Short note pattern:

- `Say:` the main explanation
- `Emphasize:` the key distinction or takeaway
- `Transition:` the next logical step

## Audience Handling

- For architects, bias toward mechanisms, placement, and tradeoffs.
- For operators, bias toward workflows, observability, and consequences.
- For mixed technical audiences, keep the visible slide simple and use notes to tune the depth live.
