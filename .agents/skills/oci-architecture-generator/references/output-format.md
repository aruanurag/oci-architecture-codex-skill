# OCI Architecture Output Format

Use this contract unless the user asks for a different deliverable.

## Default Package

1. Assumptions
2. Architecture Summary
3. Final `.drawio` Diagram
4. JSON Diagram Spec
5. Icon Mapping Table
6. Placeholder and Gap Notes

## Assumptions

Keep this short. Include only items that materially affect the design, such as:

- regions or multi-region posture
- HA or DR targets
- security or compliance constraints
- user traffic pattern
- integration boundaries

## Architecture Summary

Summarize the workload in plain language:

- what is being deployed
- which OCI services carry the design
- why the topology was chosen

## Final `.drawio` Diagram

Default to delivering a finished `.drawio` file, not just prose.

Unless the user says otherwise:

- include a physical page by default
- include a logical page only when the user explicitly requests one
- include VCN and public/private subnet structure with CIDR labels on physical pages for networked workloads
- keep public resources visually inside public subnets and private resources inside private subnets
- enlarge the page or reroute edges before accepting overlapping or crowded connector paths
- export the physical page to PNG and perform at least two cleanup passes plus one confirmatory visual QA pass before finalizing
- treat overlapping lines, broken-looking traffic arrows, disconnected-looking attachments, and crowded labels as blockers, not polish items
- note the output path clearly

## JSON Diagram Spec

Include this when the user wants the renderable source, when the diagram may be iterated later, or when repeatability matters.

Use [diagram-spec.md](diagram-spec.md) for the JSON contract.

For each page, define:

- page name and page type
- canvas size
- ordered elements
- edges and connector labels
- network boundaries such as VCNs and public/private subnets when the page is physical

Default to physical page specs only. Add logical page specs only when the user explicitly requests a logical view.

## Icon Mapping Table

Use this table for every architecture package:

| Requested Component | Resolved Icon | Resolution Type | Notes |
| --- | --- | --- | --- |

Use these resolution types:

- `direct`
- `alias`
- `closest`
- `generic`
- `placeholder`

## Placeholder and Gap Notes

List every placeholder explicitly.

Include:

- the requested component
- the placeholder shape
- why no direct official icon was used
- the closest official icon considered, if one existed but would have been misleading
- why the chosen shape is the closest similar fallback for that workload role

## If You Need to Create or Update `.drawio`

- Prefer rendering with `python3 scripts/render_oci_drawio.py`.
- Default to a physical page only. Add a logical page only on explicit request.
- Keep labels concise and service-specific.
- Keep physical examples network-complete with VCNs and labeled subnets when the workload is deployed in a VCN.
- Use more whitespace, extra tiers, and waypointed connectors instead of allowing overlapping lines or crowded clusters.
- Export the rendered page and visually inspect it. If a connector appears detached, partially attached, stacked on another route, broken by labels, or forced through labels or boundaries, reroute and rerender.
- Prioritize traffic-flow arrows during visual QA and assign dedicated routing lanes when they would otherwise overlap.
- Do one more confirmatory review after the first clean render before delivering the diagram.
- Preserve the exact official icon name in your mapping notes, especially for toolkit-only additions.
- Keep the JSON spec beside the final diagram when repeatability matters.
