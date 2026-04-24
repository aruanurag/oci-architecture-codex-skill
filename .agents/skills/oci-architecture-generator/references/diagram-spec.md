# OCI Draw.io Diagram Spec

Use this JSON contract when you want the skill to render a finished `.drawio` file with `scripts/render_oci_drawio.py`.

## Top-Level Shape

```json
{
  "title": "Architecture name",
  "clarification_gate": {
    "status": "satisfied",
    "notes": "Thread answers and recommendations were captured before rendering.",
    "decisions": [
      {
        "topic": "availability",
        "question": "Should this be HA, DR, or both?",
        "recommended_option": "Single-region HA unless cross-region recovery is explicitly required.",
        "selected_option": "Single-region multi-AD HA.",
        "resolution_source": "user_answer",
        "rationale": "The layout changes materially depending on whether DR is in scope."
      },
      {
        "topic": "database",
        "question": "Which database type should appear?",
        "recommended_option": "Use Autonomous Database when the request names ADB or a managed OCI database.",
        "selected_option": "Autonomous Database.",
        "resolution_source": "user_answer",
        "rationale": "The service icon and subnet placement depend on the database choice."
      },
      {
        "topic": "subnet_scope",
        "question": "Should the subnets be regional or AD-specific?",
        "recommended_option": "Regional subnets unless AD-specific subnet framing is explicitly requested.",
        "selected_option": "Regional subnets.",
        "resolution_source": "recommendation_accepted",
        "rationale": "This choice changes whether the diagram clones subnet boxes per AD."
      },
      {
        "topic": "icon_resolution",
        "question": "If a direct icon does not exist, what should be used?",
        "recommended_option": "Use a direct official OCI icon first, then the closest honest official fallback, then a clearly labeled placeholder.",
        "selected_option": "All requested services resolved directly, so no fallback was needed.",
        "resolution_source": "recommendation_accepted",
        "rationale": "The diagram must disclose and intentionally accept any fallback icon choice."
      }
    ]
  },
  "pages": [
    {
      "name": "Logical - Example",
      "page_type": "logical",
      "width": 1800,
      "height": 1100,
      "elements": []
    }
  ]
}
```

## Clarification Gate

The renderer now requires a top-level `clarification_gate` object before it will produce a `.drawio`.

Use `status: "satisfied"` when the questions and recommendations were answered or intentionally accepted in the thread. Use `status: "waived"` only when the user explicitly chose to skip follow-up questions; in that case provide `waiver_reason`.

When `status` is `satisfied`, `decisions` must include these topics:

- `availability`
- `database`
- `subnet_scope`
- `icon_resolution`

Each decision must include:

- `topic`
- `question`
- `recommended_option`
- `selected_option`
- `resolution_source`
- `rationale`

Allowed `resolution_source` values:

- `user_answer`
- `thread_context`
- `recommendation_accepted`
- `assumed`
- `not_applicable`

The intent is to make HA or DR posture, database choice, subnet framing, and missing-icon behavior explicit before rendering instead of burying those decisions in later notes.

## Page Fields

- `name`: draw.io page name.
- `page_type`: `logical` or `physical`. This controls icon resolution and default connector style.
- `width`: optional page width. Default is `1600`.
- `height`: optional page height. Default is `900`.
- `elements`: ordered page content. Put background grouping shapes first, then service icons, then edges.

## Element Types

### Library Elements

Use for OCI groupings, service icons, and special connectors.

```json
{
  "id": "oke",
  "query": "OKE",
  "x": 250,
  "y": 500,
  "w": 150,
  "h": 115,
  "external_label": "Regional OKE"
}
```

Supported fields:

- `id`: optional stable reference for later edges or relative positioning.
- `query`: preferred input. The renderer resolves this through `scripts/resolve_oci_icon.py`.
- `icon_title`: use when you already know the exact Oracle icon title.
- `x`, `y`, `w`, `h`: placement and size.
- `size_policy`: optional. Use `native` only when you intentionally want the raw OCI toolkit size. When omitted, service icons normalize to a common max dimension while grouping shapes and special connectors keep their native sizing.
- `parent`: optional coordinate reference to a previously placed element. This offsets `x` and `y` relative to that element's top-left corner. It does not create XML nesting.
- `label`: plain-text internal label override when the Oracle snippet has exactly one text cell.
- `value`: raw HTML label override for the first Oracle text cell. Use this for VCNs, subnets, and formatted group labels.
- `text_values`: ordered raw HTML overrides for snippets that have multiple text cells.
- `external_label`: renders a separate Oracle Sans text box below the icon.
- `hide_internal_label`: optional boolean. When `true`, blanks the snippet's built-in text cells.
- `preserve_internal_label`: optional boolean. When `true`, keeps the built-in snippet text even if `external_label` is present.

Fallback behavior is automatic:

1. direct official icon
2. trusted alias
3. logical generic icon when the page is logical
4. placeholder shape when no honest official mapping exists for a physical component

On physical diagrams, prefer explicit VCN and subnet groupings with CIDR labels, and place public and private resources inside the appropriate subnet boxes.
For multi-AD HA inside one region, keep regional subnets as horizontal bands and place the official `Availability Domain` grouping shapes as tall vertical background containers inside the VCN but outside the subnet boundaries.

Sizing notes:

- If you omit both `w` and `h` for a service icon, the renderer normalizes it to the skill's default icon box.
- If you provide only one of `w` or `h`, the renderer preserves the icon's aspect ratio automatically.
- Grouping shapes and special connectors keep their native dimensions unless you override them.

### Text Elements

```json
{
  "type": "text",
  "x": 420,
  "y": 70,
  "w": 300,
  "h": 24,
  "text": "Primary Region"
}
```

Supported fields:

- `text`: plain text by default.
- `html`: set to `true` if the text value already contains draw.io HTML.
- `style`: optional draw.io style suffix to append.

### Placeholder Shapes

```json
{
  "type": "shape",
  "shape": "ellipse",
  "x": 90,
  "y": 175,
  "w": 140,
  "h": 70,
  "label": "Analyst Users"
}
```

Supported placeholder shapes:

- `rounded-rectangle`
- `cylinder`
- `hexagon`
- `cloud`
- `ellipse`

Additional supported fields:

- `style`: optional draw.io style suffix to append. Use this when a placeholder needs a more specific Oracle-like stroke, fill, or rounding treatment.

Use an explicit `type: "shape"` entry when you already know the bundled OCI assets do not contain an honest direct icon for that component. This avoids pretending that a `query` resolves to an official icon when the correct result should really be a placeholder.

Hidden routing anchors also use `type: "shape"`, usually with a tiny `rounded-rectangle` and a fully transparent style:

```json
{
  "id": "app-subnet-egress-anchor",
  "type": "shape",
  "shape": "rounded-rectangle",
  "x": 359,
  "y": 169,
  "w": 2,
  "h": 2,
  "label": "",
  "style": "rounded=0;arcSize=0;fillColor=none;strokeColor=none;dashed=0;"
}
```

Use hidden anchors as routing primitives on subnet, VCN, tier, or region boundaries. Name them with an `-anchor` suffix and place them directly on the boundary you want the connector to visibly meet. The renderer treats these as anchors rather than placeholder shapes.

For boundary-attached OCI network controls such as `Internet Gateway`, `NAT Gateway`, and `Service Gateway`, prefer placing the icon directly on the relevant subnet or VCN border instead of drawing a short connector line into that same boundary. Use an explicit edge only when the gateway participates in a larger traffic lane that must be shown.

When a container stands for an OKE cluster, place the official `Container Engine for Kubernetes` icon in the container header area or as a container badge. Treat it as the cluster's identifying icon, not as a separate floating service node disconnected from the container. When the icon is being used purely as a badge, set `hide_internal_label: true` so the snippet text does not render as a second pseudo-node label.
When OKE spans multiple ADs, represent it as one cluster container inside the application subnet and place worker-node groupings inside it with one grouping per AD. Keep worker-node icons at an honest aspect ratio instead of stretching them to fill the container.

### Edges

```json
{
  "type": "edge",
  "source": "waf",
  "target": "oke",
  "connector": "logical-dataflow",
  "label": "HTTPS",
  "source_anchor": "bottom",
  "target_anchor": "top"
}
```

Supported edge fields:

- `source`: required element `id`.
- `target`: required element `id`.
- `connector`: `physical`, `logical-dataflow`, or `logical-user`.
- `label`: optional connector label.
- `style`: optional draw.io style suffix to append for manual routing or display tweaks.
- `source_anchor`: `left`, `right`, `top`, or `bottom`.
- `target_anchor`: `left`, `right`, `top`, or `bottom`.
- `waypoints`: optional list of `[x, y]` pairs or `{"x": ..., "y": ...}` objects.

For traffic-flow arrows on physical diagrams, use anchors and waypoints deliberately to reserve clean lanes. Do not accept a route that looks detached, overlaps another major arrow, forces the label through a boundary or icon, or relies on an uncontrolled diagonal segment.
When a physical topology repeats paired stages such as queues and consumers, align those rows or columns symmetrically before fine-tuning connectors.

Do not accept a child container or icon whose center point falls outside its intended parent boundary, or whose rendered bounds spill outside that parent. Parent-relative placement should remain visually contained.

When a physical edge crosses a container boundary:

- route the connector to a hidden boundary anchor first
- bridge across lanes with anchor-to-anchor segments when needed
- use `style: "endArrow=none;"` on intermediate segments
- keep the visible arrowhead only on the final segment into the destination workload
- treat a connector that only almost reaches a boundary or icon as incorrect

## Recommended Workflow

1. Resolve icon uncertainty with `scripts/resolve_oci_icon.py`.
2. Author the JSON spec only after the clarification gate is complete, and record the follow-up questions, recommended options, and selected answers in `clarification_gate`.
3. Render the final diagram and quality-check it:

```bash
python3 scripts/render_oci_drawio.py \
  --spec assets/examples/specs/multi-region-oke-saas.json \
  --output /tmp/multi-region-oke-saas.drawio \
  --report-out /tmp/multi-region-oke-saas.report.json \
  --quality-out /tmp/multi-region-oke-saas.quality.json \
  --fail-on-quality
```

4. Validate with `scripts/test_render_oci_drawio.py` or `validate_drawio_file(...)`.
5. If the quality review fails, fix the spec and rerender until it passes.
6. Export the physical page to PNG and run a dedicated spacing and overlap review focused on ingress spacing, labels, AD background lanes, cluster containers, and unrelated overlaps.
7. Run an architectural review focused on public versus private placement, regional versus AD-specific subnet truth, HA or DR honesty, and any material ingress or security omissions.
8. After the first passing quality review, do one more rerender and require a second passing quality review before delivery.
9. Do at least one final visual confirmatory pass focused on arrowheads, traffic-flow routing, boundary attachment, icon sizing, child containment within parent boundaries, and label collisions.

## Bundled Examples

- `assets/examples/specs/multi-region-oke-saas.json`
- `assets/examples/specs/oke-genai-rag.json`
- `assets/examples/specs/mushop-oke-ecommerce.json`
- `assets/examples/specs/oke-multidatabase-modern-app.json`
