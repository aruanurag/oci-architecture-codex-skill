---
name: oci-architecture-generator
description: Generate finalized OCI physical architecture `.drawio` diagrams that follow the bundled Oracle OCI style guide and icon toolkit, default to physical diagrams, and iteratively review both architectural correctness and connector routing until the result looks clean, honest, and machine-generated.
---

# OCI Architecture Generator

## Overview

Use this skill to keep OCI architecture work disciplined and honest:

- Use Oracle-provided draw.io assets first.
- Prefer the closest bundled Oracle reference architecture before inventing a layout from scratch.
- Default to physical diagrams only. Add a logical view only when the user explicitly asks for one.
- Run a mandatory clarification gate before authoring any new diagram: do a short planning pass first, then ask only the unresolved targeted questions unless the user explicitly says not to ask questions or the current thread already answered them, and record the questions, recommendations, and selected answers in the top-level `clarification_gate`.
- Resolve every component to an official icon, an official logical generic, or a clearly labeled similar placeholder shape.
- Never claim a direct official mapping when the result is really a placeholder or a non-direct fallback.
- Run an explicit architectural review before final delivery so public or private placement, HA or DR posture, ingress security, and tier isolation are correct instead of only visually tidy.
- Run a dedicated spacing and overlap review on the rendered export before sign-off.
- Do not stop after the first render. Render, review, reroute, and rerender until the geometry review passes cleanly twice in a row.
- Treat broken-looking traffic-flow arrows, overlapping line segments, and labels sitting on top of arrows as blockers, not polish items.
- Treat stretched icons, inconsistent default icon sizing, diagonal edge segments, and shared connector lanes as blockers too.
- Treat avoidable connector elbows as blockers too. If a connector truly must bend, keep the bends orthogonal, intentional, and aligned.
- Treat shared or nearly collinear lanes between different semantic flows, such as publish, consume, and database-write paths, as overlap even when the automated checker passes.
- Treat missing direct icons, unofficial fallbacks, and placeholders as review findings that must be surfaced explicitly before sign-off.
- Preserve symmetry when the topology is staged, mirrored, or fanout-based by aligning repeated blocks and balancing whitespace before optimizing for the shortest route.

## Workflow

1. Read [references/style-guide.md](references/style-guide.md) before producing diagram guidance.
2. Read [references/output-format.md](references/output-format.md) to shape the final package.
3. Read [references/diagram-spec.md](references/diagram-spec.md) before authoring a renderable JSON spec.
4. Start with a short planning pass and share it before generating the diagram. Summarize the inferred topology, network shape, DR or HA posture, likely reference baseline, and any assumptions that would materially affect layout quality.
5. Run `python3 scripts/select_reference_architecture.py --query "user request" --bundle --top 5` and inspect the strongest bundled reference in `assets/reference-architectures/oracle/`, plus any supporting references suggested for DR, security, or workload-specific details.
6. Compare the user request against the likely reference baseline and identify the few uncertainties that would change topology, HA or DR posture, database choice, subnet framing, region layout, service selection, or icon mapping.
7. After the planning pass, derive the clarification questions from the unresolved gaps you just identified. Ask the smallest useful set, usually 1 to 4 questions, before authoring the spec unless the user explicitly says not to ask questions or the current thread already answered them. Do not ask the `clarification_gate` schema topics verbatim just to fill the contract. Prioritize questions whose answers would visibly change topology, HA or DR posture, database choice, subnet framing including regional vs AD-specific scope, region layout, service selection, icon mapping, or symmetry and stage alignment.
8. Treat a request that is only a short service list, such as "Functions, Queue, Object Storage, NoSQL", as materially ambiguous by default unless ingress, region posture, HA or DR expectations, database meaning, and managed-service placement are already obvious from context. In that case, ask at least two targeted follow-up questions before drafting.
9. If icon resolution returns `closest` or `placeholder`, or if you do not fully understand the requested component, pause before drafting when possible. Present one to three recommended icon choices or placeholder shapes, explain the tradeoff briefly, and identify the most honest recommendation first.
10. If answers are already present in the current thread, or if the user explicitly says not to ask questions, say that the clarification gate is satisfied and name the layout-affecting choices you are carrying forward before rendering.
11. If a strong reference exists, preserve the primary reference's page geometry, subnet framing, icon scale, whitespace, and routing lanes as the starting baseline. Borrow only the specific DR, security, or traffic-flow ideas that the supporting references cover better.
12. Use `python3 scripts/resolve_oci_icon.py --page physical --query "OKE"` or `--page logical` when you need explicit icon resolution, browsing, or fallback evidence.
13. Author a physical page spec by default. Add a logical page only when the user explicitly requests it, and record the final questions, recommended options, and selected answers in the top-level `clarification_gate`. Required `clarification_gate` topics are recording buckets, not a mandatory user-facing question script. Use `thread_context`, `recommendation_accepted`, `assumed`, or `not_applicable` when the planning pass already resolved a topic honestly.
14. Render with `python3 scripts/render_oci_drawio.py --spec ... --output ... --report-out ... --quality-out ... --fail-on-quality`. The renderer now refuses to render when the required `clarification_gate` is missing or incomplete.
15. For any physical flow that crosses a VCN, subnet, tier, or other container boundary, add tiny hidden `*-anchor` shapes on the relevant border and route the line through those anchors before it enters the next container.
16. Use `style: "endArrow=none;"` on intermediate boundary-to-boundary or icon-to-boundary segments. Keep the visible arrowhead only on the final segment that enters the destination workload or endpoint icon.
17. If the renderer exits non-zero because the quality review found issues, update anchors, waypoints, spacing, sizes, or canvas dimensions and rerender. Do not share the output yet.
18. Export the rendered physical page to PNG and inspect it visually before sign-off.
19. Run a dedicated spacing and overlap review against the export before sign-off:
   - verify every requested service resolved to an official OCI icon and treat `closest` and `placeholder` outcomes as blockers until they are disclosed and intentionally accepted
   - check spacing between external location groups, ingress services, and the first OCI boundary so `Internet`, `Clients`, `WAF`, and similar entry elements do not crowd each other
   - check spacing between icons and their labels so native snippet text, external labels, and connector routes do not collide
   - check spacing between subnet labels, AD background lanes, cluster containers, and service icons so the background structure stays visually behind the foreground content
   - treat any overlap between unrelated icons, labels, grouping boxes, connectors, arrowheads, or location boundaries as a blocker even if the automated quality checker passes
20. Run an architectural review against the request before sign-off:
   - only ingress services belong in public subnets for internet-facing patterns unless the user explicitly wants public compute
   - web, app, and data tiers should be isolated honestly when a 3-tier pattern is requested
   - regional subnets are the default OCI assumption when subnet scope is unspecified; do not duplicate one subnet per AD unless the user explicitly asked for AD-specific subnets or the architecture requires them
   - HA or DR claims must be explicit in the diagram through ADs, FDs, instance pools, standby regions, or similarly honest constructs
   - ingress protection, egress pattern, and management path should be present when they materially affect whether the design reads as production-ready
21. If the spacing and overlap review finds a gap, fix the spec and rerender before architectural sign-off.
22. If the architectural review finds a gap, fix the spec and rerender before visual polish sign-off.
23. Run at least three repair passes after the first render, even if the first quality review is already clean.
24. After the first passing quality review, do one more rerender and require a second clean quality review before delivering the diagram.
25. Treat a connector that stops just outside a subnet wall, VCN wall, or workload icon as broken even if the automated quality review does not flag it yet.
26. Use the bundled draw.io assets in `assets/drawio/` and `assets/reference-architectures/oracle/` instead of relying on external copies.

## Clarification Priorities

Ask only the questions that are most likely to improve the actual diagram. Prioritize:

1. Topology-defining gaps, such as single-region vs multi-region, HA vs DR, active-active vs active-standby, public vs private exposure, and hub-spoke vs flat VCN structure.
2. Network completeness gaps, such as whether to show separate app, data, management, or observability subnets, whether subnet scope should be regional or AD-specific, gateway types, CIDRs, and on-premises connectivity.
3. Service-resolution gaps, such as whether a workload should be shown with OKE, Compute, API Gateway, Functions, Autonomous Database, Base Database, Exadata, or a placeholder, plus what to do when a direct icon does not exist.
4. Visual-baseline gaps, such as whether the user wants the output to follow a specific Oracle reference or sample diagram.
5. Layout-discipline gaps, such as whether repeated stages should align symmetrically, whether fanout branches should use one block or many, and whether paired tiers should read as rows or columns.

Do not ask questions whose answers are unlikely to change geometry, routing lanes, subnet structure, region layout, or icon choice.
The required `clarification_gate` topics are there to record decisions, not to force a fixed list of user-facing questions every time.

## Mapping Rules

Apply this order strictly:

1. Use a direct official OCI icon when the service is present in the bundled catalog.
2. Use a common OCI alias that resolves to an official icon, such as `OKE`, `ADW`, `ATP`, `DRG`, or `WAF`.
3. Use an approved closest official fallback icon on physical diagrams when the local skill explicitly documents that fallback for a known catalog gap, and disclose it as a fallback in the mapping table.
4. Use an official generic logical component on logical diagrams when the workload element is clearly OCI, Oracle on-premises, or third-party but not directly represented.
5. On physical diagrams, when no official OCI icon exists and there is no approved closest official fallback, use the closest similar placeholder shape for the workload type instead of pretending an OCI icon exists.
6. Mention the closest official OCI icon considered only in notes when it helps explain the fallback. Do not silently substitute it as the rendered icon unless step 3 explicitly allows it.

When you use step 3, 4, 5, or 6, say so explicitly in the icon mapping table.
If you are not confident that the requested component and the resolved icon mean the same thing, confirm with the user when possible and offer recommendations in descending honesty.

## Diagram Rules

- Use `assets/drawio/oci-architecture-toolkit-v24.2.drawio` as the primary Oracle-provided visual source.
- Use `assets/drawio/oci-library.xml` as the machine-readable icon source and shape library.
- Remember that the toolkit is newer than the standalone library. The bundled catalog merges library titles with curated toolkit-only additions.
- Never use pink or Courier New in final diagrams. Those appear only as instructional annotations inside Oracle's source files.
- Treat Oracle example pages as layout guidance, not as technically verified solutions.
- On physical diagrams for networked workloads, show OCI Region, VCN, and clearly labeled public and private subnets with CIDRs unless the user explicitly wants a looser view.
- Default OCI subnet boundaries to regional scope unless the user explicitly asks for AD-specific subnets or the architecture genuinely depends on AD-specific framing.
- Place public-facing resources inside public subnets and application or data resources inside private subnets. Add more private subnets when the design needs a separate data, cache, or observability tier.
- For single-region multi-AD HA, let a regional subnet span the ADs by default and show AD placement with the official Oracle `Availability Domain` grouping shapes as tall vertical background containers inside the VCN but outside the subnet boundaries, while the regional subnets span horizontally across them. Match the Oracle sample treatment used for HA layouts in the OCI icon deck, with repeated workloads, AD or FD grouping cues, or database role markers instead of duplicating one subnet per AD.
- Increase canvas size, spread resources out, and use explicit waypoints so connectors do not stack on top of one another or overcrowd the page.
- Reserve separate routing lanes for major north-south and east-west traffic flows when that reduces broken-looking or stacked arrows.
- Do not let different semantic connector families share the same visible lane for convenience. If publish, consume, or database-write paths look stacked or ambiguous, reroute them onto distinct lanes or a dedicated bus.
- When adapting a bundled reference architecture, preserve its lane structure and icon scale unless the new workload forces a different layout.
- When the topology repeats paired stages such as queues and consumers, preserve symmetry by aligning the repeated rows or columns when that keeps the diagram honest and easier to scan.
- Use explicit anchors and waypoints for physical traffic arrows instead of relying on default routing for anything more complex than a straight single-lane connection.
- Prefer a single physical connector with orthogonal waypoints when it can cross boundaries cleanly and still look attached, straight, and machine-generated.
- Prefer straight connectors first. If a route can be drawn straight, do not accept an elbowed alternative.
- If a connector truly must use elbows, keep them orthogonal, intentional, aligned, and easy to justify in review.
- Use tiny invisible shape elements with ids ending in `-anchor` as routing primitives on subnet, VCN, tier, or region boundaries only when a single connector cannot stay clean, straight, and unambiguous without them.
- Keep arrowheads off intermediate routing segments by using `endArrow=none;` until the final segment into the destination workload.
- Treat "almost touching" a container wall or service icon as a blocker. A connector should visibly meet the boundary or destination, not merely approach it.
- Let the renderer normalize service icon sizes when `w` and `h` are omitted. Only override icon sizes deliberately.
- When OKE spans multiple ADs, represent it as a cluster-level container in the application subnet and place worker-node groupings inside that container with one worker grouping per AD.
- Keep worker-node and similar compute icons at an honest, unstretched aspect ratio. If the icon starts looking wider or flatter than the Oracle original, reduce width before increasing height.
- Export and visually inspect the physical page until there are no overlapping lines, floating segments, connectors that look misattached, stretched service icons, or crowded top-level ingress elements.

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
- Default those OCI subnet boundaries to regional scope unless the user explicitly asks for AD-specific subnets.
- For HA layouts across multiple ADs, keep the Oracle-style composition explicit: `Availability Domain` groupings should read as tall vertical background containers inside the VCN but outside the subnet boundaries, and the regional subnets should read as horizontal bands crossing those AD containers.
- Keep traffic-flow arrows simple and intentional. Prefer a clear dedicated lane and fewer bends over a compact but broken-looking route.
- Treat avoidable elbows as blockers. If the same relationship can be drawn as a straight connector, reroute before delivery.
- Keep service labels visually snug to their icons. Default external labels to a minimal vertical gap and only add extra spacing when a multi-line label or nearby connector would otherwise collide.
- For flows that cross subnet or VCN boundaries, prefer one clean orthogonal connector first. Use hidden `*-anchor` shapes only when the direct connector would otherwise look broken, crowded, diagonal, or ambiguous.
- Treat one semantic relationship as one visible connector. Do not stitch a single flow out of multiple edge objects just to cross VCN, subnet, or OSN boundaries when one waypointed connector with optional hidden endpoint anchors can stay clean.
- When a direct connector into a service icon makes the last arrow segment look tilted, stepped, or detached, terminate the single visible connector at a tiny invisible attach anchor placed exactly on the target icon boundary instead of letting draw.io pick a broken-looking perimeter point.
- Never route a traffic connector along the same visible lane as a VCN, subnet, or dashed workload-container border. If a connector would visually sit on top of a container edge, move it to a dedicated lane even when the automated quality check passes.
- Place boundary-attached gateways such as `Internet Gateway`, `NAT Gateway`, and `Service Gateway` directly on the VCN border by default. Let the VCN border line pass through the gateway icon's center, and parent the gateway to the region or other enclosing canvas when needed so the icon can straddle the VCN boundary cleanly. Do not move gateways down to subnet borders unless the user explicitly asks for that style, and do not add a short decorative connector line from the gateway into the boundary.
- Do not add standalone `Route Table` or `Security List` icons when the chosen subnet grouping already renders those controls on the subnet boundary. Treat duplicate `RT` or `SL` markers as blockers.
- Keep child containers and icons visually contained within their intended parent boundaries. Treat any child whose center point or bounds drift outside its parent as a blocker.
- When a dashed or grouped container represents an OKE cluster, use the official `Container Engine for Kubernetes` icon as the cluster container's emblem or header marker. Do not leave the OKE icon floating as if it were a separate workload inside the cluster.
- When using the OKE icon as a cluster badge or header marker, set `hide_internal_label: true` unless the built-in icon text is explicitly needed.
- When OKE spans multiple ADs, represent the cluster as one container within the application subnet and place worker-node groups inside it with one grouping per AD instead of stretching one worker icon across the whole cluster.
- Keep worker-node icons close to the Oracle aspect ratio. If they start looking stretched, resize the surrounding layout instead of flattening the worker icon.

## Deliverables

Default to producing:

1. A short planning summary.
2. Clarifying questions and answers, or a note that the answers were already provided earlier in the thread, plus the recorded `clarification_gate` decisions when a renderable spec is included.
3. A short assumption list.
4. A brief architecture summary.
5. Spacing and overlap review findings and applied fixes.
6. Architectural review findings and applied fixes.
7. A renderable JSON page spec when the user wants the intermediate source.
8. A finalized `.drawio` file with a physical page by default. Add a logical page only when the user explicitly asks for one.
9. An icon mapping table with `Requested Component`, `Resolved Icon`, `Resolution Type`, and `Notes`.
10. A placeholder list when any geometry fallback is required.

## Resources

- Read [references/style-guide.md](references/style-guide.md) for the Oracle-specific guardrails.
- Read [references/output-format.md](references/output-format.md) for the default architecture package shape.
- Read [references/diagram-spec.md](references/diagram-spec.md) for the renderer input contract.
- Read [references/reference-architectures.md](references/reference-architectures.md) for the imported Oracle reference corpus and the best-fit use of each bundled `.drawio`.
- Read [references/icon-catalog.md](references/icon-catalog.md) only when you need manual browsing or `rg` searches.
- Run `python3 scripts/build_icon_catalog.py` after updating the bundled draw.io assets.
- Run `python3 scripts/select_reference_architecture.py --query "request text" --bundle --top 5` to find the closest imported Oracle reference architecture and any supporting references before laying out a new design.
- Run `python3 scripts/resolve_oci_icon.py --query "service name"` to resolve icon mappings.
- Run `python3 scripts/render_oci_drawio.py --spec ... --output ... --report-out ... --quality-out ... --fail-on-quality` to generate the finished `.drawio` and fail fast on bad geometry.
- Run `python3 scripts/test_icon_resolver.py` before trusting resolver changes.
- Run `python3 scripts/test_reference_selector.py` before trusting reference-selection changes.
- Run `python3 scripts/test_render_oci_drawio.py` before trusting renderer changes.
- Reuse the bundled example specs in `assets/examples/specs/` when you want a known-good starting point.
- Reuse the imported Oracle `.drawio` references in `assets/reference-architectures/oracle/` when you want the closest visual baseline for a new architecture family.
