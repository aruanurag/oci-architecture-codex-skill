---
name: oci-architecture-generator
description: Generate finalized OCI physical architecture `.drawio` diagrams that follow the bundled Oracle OCI style guide and icon toolkit. Default to physical diagrams only unless a logical view is explicitly requested, and iteratively review connector routing until traffic-flow arrows are attached, readable, and free of overlaps.
---

# OCI Architecture Generator

## Overview

Use this skill to keep OCI architecture work disciplined and honest:

- Use Oracle-provided draw.io assets first.
- Default to physical diagrams only. Add a logical view only when the user explicitly asks for one.
- Resolve every component to an official icon, an official logical generic, or a clearly labeled similar placeholder shape.
- Never claim a direct official mapping when the result is really a placeholder or a non-direct fallback.
- Do not stop after the first render. Export, inspect, and reroute until connectors are clean, attached, and readable.
- Treat broken-looking traffic-flow arrows, overlapping line segments, and labels sitting on top of arrows as blockers, not polish items.

## Workflow

1. Read [references/style-guide.md](references/style-guide.md) before producing diagram guidance.
2. Read [references/output-format.md](references/output-format.md) to shape the final package.
3. Read [references/diagram-spec.md](references/diagram-spec.md) before authoring a renderable JSON spec.
4. Use `python3 scripts/resolve_oci_icon.py --page physical --query "OKE"` or `--page logical` when you need explicit icon resolution, browsing, or fallback evidence.
5. Author a physical page spec by default. Add a logical page only when the user explicitly requests it.
6. Render the final `.drawio` with `python3 scripts/render_oci_drawio.py --spec ... --output ... --report-out ...`.
7. Export the rendered physical page to PNG and inspect it visually before considering the work done.
8. Inspect traffic-flow arrows first. If any arrow overlaps another line or label, appears detached from an icon, clips a subnet boundary awkwardly, doubles back unnecessarily, or crowds the page, adjust anchors, waypoints, spacing, or canvas size and rerender.
9. Perform at least two cleanup passes and one confirmatory visual review after the first clean pass to catch subtle routing and attachment issues.
10. Use the bundled draw.io assets in `assets/drawio/` instead of relying on external copies.

## Mapping Rules

Apply this order strictly:

1. Use a direct official OCI icon when the service is present in the bundled catalog.
2. Use a common OCI alias that resolves to an official icon, such as `OKE`, `ADW`, `ATP`, `DRG`, or `WAF`.
3. Use an official generic logical component on logical diagrams when the workload element is clearly OCI, Oracle on-premises, or third-party but not directly represented.
4. On physical diagrams, when no official OCI icon exists, use the closest similar placeholder shape for the workload type instead of pretending an OCI icon exists.
5. Mention the closest official OCI icon considered only in notes when it helps explain the fallback. Do not silently substitute it as the rendered icon.

When you use step 3, 4, or 5, say so explicitly in the icon mapping table.

## Diagram Rules

- Use `assets/drawio/oci-architecture-toolkit-v24.2.drawio` as the primary Oracle-provided visual source.
- Use `assets/drawio/oci-library.xml` as the machine-readable icon source and shape library.
- Remember that the toolkit is newer than the standalone library. The bundled catalog merges library titles with curated toolkit-only additions.
- Never use pink or Courier New in final diagrams. Those appear only as instructional annotations inside Oracle's source files.
- Treat Oracle example pages as layout guidance, not as technically verified solutions.
- On physical diagrams for networked workloads, show OCI Region, VCN, and clearly labeled public and private subnets with CIDRs unless the user explicitly wants a looser view.
- Place public-facing resources inside public subnets and application or data resources inside private subnets. Add more private subnets when the design needs a separate data, cache, or observability tier.
- Increase canvas size, spread resources out, and use explicit waypoints so connectors do not stack on top of one another or overcrowd the page.
- Reserve separate routing lanes for major north-south and east-west traffic flows when that reduces broken-looking or stacked arrows.
- Export and visually inspect the physical page until there are no overlapping lines, floating segments, or connectors that look misattached.

## Logical Diagrams

Only produce a logical page when the user explicitly asks for one.

- Use logical grouping canvases such as Oracle Cloud, On-Premises, Internet, and 3rd Party Cloud.
- Use logical components such as `OCI Component`, `Oracle On-Premises Component`, `3rd Party Non- OCI`, `Atomic`, `Collapsed Composite`, and `Expanded Composite`.
- Use logical connectors and connector labels for user interaction and data flow.
- Prefer generic logical components over simple geometry when the element is conceptual and no exact service icon exists.

## Physical Diagrams

- Use physical grouping shapes such as Tenancy, Compartment, OCI Region, Availability Domain, Fault Domain, VCN, Subnet, Tier, and User Group.
- Use special physical connectors for FastConnect, Site-to-site VPN, and Remote Peering when those links are part of the design.
- Use service icons for OCI infrastructure and managed services.
- Use clearly labeled similar placeholder shapes when no direct OCI icon exists.
- Default to public and private subnet structure with CIDR labels on bundled examples and final physical diagrams unless the user asks for a different level of detail.
- Keep traffic-flow arrows simple and intentional. Prefer a clear dedicated lane and fewer bends over a compact but broken-looking route.

## Deliverables

Default to producing:

1. A short assumption list.
2. A brief architecture summary.
3. A renderable JSON page spec when the user wants the intermediate source.
4. A finalized `.drawio` file with a physical page by default. Add a logical page only when the user explicitly asks for one.
5. An icon mapping table with `Requested Component`, `Resolved Icon`, `Resolution Type`, and `Notes`.
6. A placeholder list when any geometry fallback is required.

## Resources

- Read [references/style-guide.md](references/style-guide.md) for the Oracle-specific guardrails.
- Read [references/output-format.md](references/output-format.md) for the default architecture package shape.
- Read [references/diagram-spec.md](references/diagram-spec.md) for the renderer input contract.
- Read [references/icon-catalog.md](references/icon-catalog.md) only when you need manual browsing or `rg` searches.
- Run `python3 scripts/build_icon_catalog.py` after updating the bundled draw.io assets.
- Run `python3 scripts/resolve_oci_icon.py --query "service name"` to resolve icon mappings.
- Run `python3 scripts/render_oci_drawio.py --spec ... --output ... --report-out ...` to generate the finished `.drawio`.
- Run `python3 scripts/test_icon_resolver.py` before trusting resolver changes.
- Run `python3 scripts/test_render_oci_drawio.py` before trusting renderer changes.
- Reuse the bundled example specs in `assets/examples/specs/` when you want a known-good starting point.
