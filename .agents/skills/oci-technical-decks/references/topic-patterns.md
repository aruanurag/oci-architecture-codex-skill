# Topic Patterns

Use this file after you know the OCI topic.

## OCI Networking

Typical teaching goals:

- explain why OCI networking is different
- show how the data path, edge, and control model fit together
- compare OCI networking choices honestly

Recommended sequence:

1. networking problem or design goal
2. OCI network foundation
3. edge and ingress services
4. connectivity and hybrid patterns
5. security and isolation model
6. performance or scale characteristics
7. workload fit and tradeoffs
8. summary

Useful visuals:

- region or edge placement diagram
- VCN and traffic-flow architecture
- comparison table
- hybrid connectivity diagram

Clarify early:

- architecture-heavy vs service-overview deck
- customer-safe vs internal technical posture
- whether the deck should compare OCI to another platform or just explain OCI

## OCI Compute Shapes

Typical teaching goals:

- explain shape families and how to choose them
- compare VM, bare metal, GPU, and Flex options
- connect shape choice to workload behavior

Recommended sequence:

1. shape-selection problem
2. compute portfolio at a glance
3. family-by-family breakdown
4. Flex and customization model
5. GPU, local NVMe, or networking considerations
6. workload-fit examples
7. selection guide or tradeoff table
8. summary

Useful visuals:

- family matrix
- comparison table
- decision tree
- workload-to-shape mapping

Clarify early:

- overview vs deep dive
- current-generation shapes only vs broad portfolio
- whether price-performance discussion is required

## OCI Observability

Typical teaching goals:

- explain how OCI observability services work together
- show the telemetry path from workload to operator action
- differentiate logging, monitoring, tracing, APM, and analytics roles

Recommended sequence:

1. operator problem or visibility gap
2. observability service map
3. telemetry ingestion and storage flow
4. logging, monitoring, APM, analytics roles
5. alerting and troubleshooting workflow
6. integration with OCI services and apps
7. use cases and guardrails
8. summary

Useful visuals:

- telemetry pipeline diagram
- service taxonomy slide
- troubleshooting workflow
- responsibility matrix

Clarify early:

- platform-operator audience vs application-owner audience
- service overview vs troubleshooting workflow focus
- whether the deck should include logging analytics, APM, or OpenTelemetry angles

## Reusable Topic Rule

For any technical topic, make sure the deck answers:

- what problem this solves
- what the OCI mechanism actually is
- where it fits in an architecture or operator workflow
- what tradeoffs matter
- what the audience should do with the information
