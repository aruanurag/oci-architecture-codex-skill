# OCI Draw.io Style Guide

This reference distills the Oracle-provided files bundled in `assets/drawio/`.

## Source Files

- `assets/drawio/oci-style-guide-readme.drawio`
- `assets/drawio/oci-architecture-toolkit-v24.2.drawio`
- `assets/drawio/oci-library.xml`

## Non-Negotiables

- Use Oracle-provided OCI icons and grouping shapes first.
- Do not use pink or Courier New in final diagrams. Oracle uses those only for instructional callouts inside the source files.
- Default to physical diagrams only. Add a logical view only when the user explicitly asks for one.
- Treat example pages as layout guidance. The toolkit explicitly says the examples are not always complete or technically correct.
- Keep iterating until connectors look attached, readable, and non-overlapping in a visual export.
- Treat broken-looking traffic arrows, arrowheads that seem detached, and labels colliding with arrows as blockers.

## Oracle Asset Usage

- Use `oci-architecture-toolkit-v24.2.drawio` as the primary visual source.
- Use `oci-library.xml` as the machine-readable library for scripted icon lookup.
- Remember that the toolkit is newer than the standalone library. The local catalog merges the library titles with a curated supplement for newer toolkit-only icons.

## Logical Diagram Guidance

Use logical pages only when the user explicitly requests them.

Use logical pages for conceptual system flow and responsibility boundaries.

- Use location canvases for Oracle Cloud, On-Premises, Internet, and 3rd Party Cloud.
- Use logical components for OCI, Oracle on-premises, and third-party systems.
- Use atomic or composite component shapes when the system needs drill-down views.
- Use the logical connector styles for user interaction and data flow.
- Prefer official generic logical components over plain geometry when the element is conceptual and no direct service icon exists.

## Physical Diagram Guidance

Use physical pages for deployable infrastructure layout.

- Use grouping shapes for Tenancy, Compartment, OCI Region, Availability Domain, Fault Domain, VCN, Subnet, Tier, and User Group.
- Use special connector shapes for FastConnect, Site-to-site VPN, and Remote Peering.
- Use service icons for OCI products and managed services.
- Use public and private subnet boundaries with CIDR labels on networked workloads.
- Keep public-facing resources inside public subnets and application or data tiers inside private subnets.
- Add extra private subnets for data, cache, or observability tiers when that reduces crowding and makes the network clearer.
- Increase the canvas and route connectors with waypoints before letting lines pile up on top of each other.
- Reserve dedicated traffic lanes when multiple arrows traverse the same area of the page.
- Export the physical page and inspect it visually. If any route looks detached, ambiguous, broken by labels, or unnecessarily overlapped, reroute and rerender.
- Prefer more whitespace and clearer attachment points over compactness.
- Use geometry placeholders only when there is no direct OCI icon.

## Fallback Policy

Apply this order:

1. Direct official icon.
2. Official icon reached through a trusted alias, such as `OKE`, `ADW`, or `DRG`.
3. Official generic logical component when the page is logical and the element is clearly OCI, Oracle on-premises, or third-party.
4. Closest similar placeholder shape with a clear label when the page is physical and no OCI icon exists.
5. Mention the closest official OCI icon considered only in notes when it would otherwise be ambiguous.

## Placeholder Shapes

Use the simplest honest placeholder:

- `rounded-rectangle` for generic applications, compute nodes, services, and middleware.
- `cylinder` for databases, warehouses, data lakes, and storage-like data services.
- `hexagon` for network and security controls.
- `cloud` for external SaaS or generic cloud services.
- `ellipse` for people or user actors.

Choose the shape that is closest to the missing component's role, not just the first generic shape that fits.
Prefix the label with `PLACEHOLDER:` when the diagram itself needs to signal the fallback directly.
