# Pattern Catalog

Use this file after you understand what the diagram needs to explain.

## 1. Layered Host And Control Boundary

Best for:

- host, hypervisor, accelerator, or control-computer diagrams
- trust boundaries
- subsystem separation
- the example pattern the user shared

Structure:

- outer host or environment box
- one or more internal boundary zones
- small subsystem modules
- one or two external actors such as cloud network or internet
- orthogonal arrows for path or control relationships

Typical primitives:

- large neutral background container
- border-only or lightly tinted inner zones
- rounded rectangles for subsystems
- ellipse for legacy or adapter module when appropriate
- cloud shape for external network or service
- small chip labels for buses, VM labels, or resource labels

Avoid:

- too many tiny module boxes
- diagonal arrows
- labels that sit on borders

## 2. Control Plane Versus Data Plane

Best for:

- networking, security, and observability topics
- explaining where orchestration ends and packet or workload flow begins

Structure:

- left-right or top-bottom split
- one side for control plane
- one side for data plane
- shared services or handoff boundary between them

Typical primitives:

- two major zones
- repeated service modules
- clear connector families
- dashed versus solid flow semantics when useful

## 3. Capability Stack

Best for:

- service layering
- platform stacks
- infrastructure-to-runtime explanation

Structure:

- vertical stack of layers
- optional side annotations
- one or two supporting callouts

Typical primitives:

- full-width horizontal blocks
- one stack title
- optional side braces or callout chips

## 4. Side-By-Side Comparison Frame

Best for:

- compute shapes
- old versus new model
- service A versus service B

Structure:

- two or three equal columns
- shared category labels or criteria
- strong row or section alignment

Typical primitives:

- comparison table
- equal-width cards
- shared headline and short tradeoff line

## 5. Annotated Screenshot Pair

Best for:

- console views
- terminal comparisons
- before and after images

Structure:

- screenshot or terminal frame on each side
- short labels above each frame
- optional one-line bottom interpretation

Typical primitives:

- cropped image frame or screenshot panel
- title chips
- minimal annotation boxes

Avoid:

- unreadably small screenshots
- dense explanatory text on the canvas

## 6. Packet Or Processing Flow

Best for:

- observability pipelines
- packet processing
- request flows
- event paths

Structure:

- left-to-right or top-to-bottom stages
- one connector family per semantic relationship
- optional side callouts for policy or observation points

Typical primitives:

- stage boxes
- connector lanes
- thin divider lines
- small callout clouds or note cards

## 7. Footprint Or Coverage

Best for:

- region maps
- service reach
- platform presence

Structure:

- hero map or coverage visual
- restrained legend
- sparse callouts

Typical primitives:

- one large footprint frame
- small legend group
- update badge if genuinely needed

## 8. Architecture Sidecar Explainer

Best for:

- architecture slides that need one conceptual inset
- explaining a subsystem without redrawing the whole OCI topology

Structure:

- one primary architecture
- one sidecar conceptual module
- short bridge caption or arrow

Typical primitives:

- compact inset group
- contained connectors
- labels kept out of the main topology lanes
