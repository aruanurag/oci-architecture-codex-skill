# Integration Contract

Use this file when another skill needs a reusable pattern handoff.

## Required Output

Return a compact `Pattern Brief` with:

- `pattern_name`
- `objective`
- `audience`
- `canvas_role`
- `boundaries`
- `modules`
- `actors`
- `flows`
- `label_strategy`
- `presenter_note_guidance`

## Recommended Fields

```yaml
pattern_name: layered-host-and-control-boundary
objective: Explain how the control computer, virtual host NIC, and accelerator sit inside the compute host.
audience: architects
canvas_role: hero diagram
boundaries:
  - id: host
    label: Compute Host
    treatment: light neutral outer container
  - id: control_zone
    label: Control boundary
    treatment: inner bordered zone
modules:
  - id: virtio
    label: VirtIO
    shape: ellipse
    semantic_class: adapter
  - id: hostnic
    label: Virtual HostNIC
    shape: rounded-rectangle
    semantic_class: network
actors:
  - id: cloud_network
    label: Cloud Provider Network
    shape: cloud
flows:
  - from: virtio
    to: hostnic
    style: solid orthogonal
label_strategy: Short visible labels, deeper explanation in notes.
presenter_note_guidance: Explain the boundary hierarchy first, then the packet and control relationships.
```

## Optional JSON Fragment

When the sibling skill can use the PowerPoint renderer primitives directly, also provide a JSON fragment using:

- `shape`
- `text`
- `edge`

Prefer a fragment, not a whole slide, unless the sibling explicitly asks for a full slide spec.

## Example Fragment

```json
{
  "elements": [
    {
      "id": "host-bg",
      "type": "shape",
      "shape": "rounded-rectangle",
      "x": 60,
      "y": 40,
      "w": 760,
      "h": 800,
      "style": "fillColor=#D9D9D9;strokeColor=none;"
    },
    {
      "id": "control-zone",
      "type": "shape",
      "shape": "rounded-rectangle",
      "x": 140,
      "y": 330,
      "w": 560,
      "h": 430,
      "style": "fillColor=#F7EFD9;strokeColor=#3E7B80;strokeWidth=3;"
    },
    {
      "id": "virtio",
      "type": "shape",
      "shape": "ellipse",
      "x": 185,
      "y": 425,
      "w": 120,
      "h": 120,
      "label": "VirtIO",
      "style": "fillColor=#8DB7B5;strokeColor=none;fontStyle=1;"
    },
    {
      "id": "cloud-network",
      "type": "shape",
      "shape": "cloud",
      "x": 730,
      "y": 650,
      "w": 140,
      "h": 90,
      "label": "Cloud Provider\nNetwork",
      "style": "fillColor=#FFFFFF;strokeColor=#666666;fontSize=11;"
    },
    {
      "type": "edge",
      "source": "virtio",
      "target": "cloud-network",
      "source_anchor": "right",
      "target_anchor": "left"
    }
  ]
}
```

## Handoff Notes

Also return:

- what the sibling skill should keep visible
- what should move into presenter notes
- what spacing, symmetry, or connector rules must survive implementation
