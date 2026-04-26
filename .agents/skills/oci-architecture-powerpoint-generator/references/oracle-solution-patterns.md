# Oracle Solution Patterns

Use this pack when the user provides a specific Oracle solution link, asks to recreate a known Oracle diagram, or wants the closest possible match to an Oracle reference architecture in PowerPoint form.

Treat the linked Oracle solution as the source of truth for:

- architecture goal and workload intent
- component inventory
- major topology and tiering
- primary traffic flows
- HA or DR posture
- constraints and best practices that the slide should make visible

Do not add extra services just because they are common. Add only the services the reference clearly shows, plus the minimum routing, gateway, or security constructs needed to represent the reference honestly.

## Reference Replication Loop

When working from a reference link, follow this sequence:

1. Build a short planning pass from the link and the current request.
2. Extract a structured `Reference Summary`:
   - goal or use case
   - key OCI and non-OCI components
   - topology and tiering
   - data flow and interactions
   - constraints, recommendations, and layout cues
3. Ask only the smallest useful set of follow-up questions that remain unresolved after that plan.
4. Write a `Recreation Prompt` that could regenerate the reference with high fidelity.
5. Choose one primary PowerPoint baseline slide and only the smallest useful set of supporting slides.
6. Draft the initial slide.
7. Run a `Reference Alignment Review`:
   - similarity score from `0` to `100`
   - missing or extra components
   - structural or layout differences
   - flow mismatches
   - icon or grouping mismatches
8. Apply the most meaningful fixes and rerender.
9. Stop when similarity is `>= 95`, or when no meaningful improvement remains, or after `10` iterations.

## Oracle Solutions

### OCI Generative AI and LLM Platforms

- Oracle link: `https://docs.oracle.com/en/solutions/oci-generative-ai-llm-platforms/`
- Goal:
  Build a secure self-service OCI platform for LLM experimentation, model promotion, inference, RAG, and enterprise integration.
- Key components:
  OCI Data Science, model deployment VMs, GPU playground, OCI Load Balancer, Oracle APEX, OCI Monitoring, OCI Generative AI Agents, Oracle Digital Assistant, OCI Speech, OCI Functions, OCI DevOps, OCI API Gateway, OKE, bare metal GPU/RDMA infrastructure, Oracle AI Database 23ai or 26ai, OCI Object Storage, Oracle Integration, OCI Events, OCI Streaming, OCI Connector Hub, IAM or IDCS, logging, and DRG or FastConnect connectivity to on-premises or other clouds.
- Topology:
  One OCI region with a centralized compartment and VCN. Inside it, separate sandbox and production environments, plus an Oracle services network. The production environment is layered into application, processing, and data domains. The sandbox includes development, playground, and validation workloads. The reference also shows internet, on-premises, and multicloud touchpoints.
- Core flows:
  Integration flow from customer apps and Oracle Integration into Object Storage, Events, Streaming, Connector Hub, Functions, GPU-backed processing, and the AI data layer.
  User flow from APEX or conversational interfaces through OCI GenAI services into the processing and data layers.
  Sandbox flow from external model sources through security validation, Data Science, and GPU playground resources before promotion into production.
- Constraints and best practices:
  Keep sandbox and production visibly separated.
  Show event-driven orchestration for RAG ingestion rather than a simple point-to-point line.
  Keep the AI database and Object Storage as the retrieval or knowledge layer, not as generic side databases.
  Prefer private integration paths for multicloud or on-premises connectivity and show governance or observability when the slide claims enterprise readiness.
- Recommended follow-up questions:
  Ask whether the user wants the full sandbox plus production layout or only the production serving path.
  Ask whether multicloud and on-premises integrations should remain visible.
  Ask whether OCI Generative AI, third-party models, or both should appear.
  Ask whether the slide should emphasize RAG, conversational interfaces, or model-training infrastructure.
- Recreation prompt:
  Create a physical OCI architecture slide for a secure self-service generative AI platform with separate sandbox and production environments inside one OCI region. Show Data Science and GPU playground resources for experimentation, OKE and OCI Generative AI for production inference, Oracle AI Database plus Object Storage as the knowledge layer, and OCI Events, Streaming, Connector Hub, Functions, API Gateway, and DevOps for orchestration and promotion. Preserve hybrid or multicloud touchpoints only when requested and keep enterprise governance and observability visible.
- Best local starting points:
  Primary baseline slide: `32`
  Supporting baseline slide: `31`

### Cloud-Native DICOM Store on OCI

- Oracle link: `https://docs.oracle.com/en/solutions/cloud-native-dicom-on-oci/`
- Goal:
  Move medical imaging storage and analysis from on-premises PACS or VNA systems into a secure OCI-native DICOM store with AI-ready services.
- Key components:
  On-premises clinicians and imaging devices, PACS or VNA, OCI Roving Edge Device, OCI FastConnect, OCI API Gateway with DICOMweb, OCI Object Storage, Orthanc, OCI Database with PostgreSQL, one OKE environment for inference, another OKE environment for training or fine-tuning, OCI Data Science, IAM, Cloud Guard, Monitoring, and Logging.
- Topology:
  Hybrid pattern with an on-premises medical facility on the left and one OCI region on the right. The OCI side contains a DICOM store block and separate AI execution blocks for inference and training. The DICOM store itself combines Object Storage, Orthanc, and PostgreSQL.
- Core flows:
  Imaging devices send studies to PACS or VNA.
  PACS or VNA sends DICOM data through Roving Edge Device over FastConnect to OCI API Gateway using DICOMweb.
  The API tier writes image payloads and metadata into the DICOM store.
  Training and inference environments read from the DICOM store.
- Constraints and best practices:
  Preserve the hybrid on-premises to OCI transfer path.
  Keep the DICOM store as a composed block, not as unrelated standalone services.
  Treat Orthanc as the DICOM service tier sitting with Object Storage and PostgreSQL.
  Default to regional subnets and strong security posture, especially Cloud Guard, security zones, and NSGs when the user wants production posture.
- Recommended follow-up questions:
  Ask whether the user wants to show both training and inference clusters or only one.
  Ask whether Roving Edge Device must remain visible or can be simplified to FastConnect.
  Ask how honest to be about Orthanc if a direct icon is unavailable.
  Ask whether compliance or security services should be foregrounded or kept secondary.
- Recreation prompt:
  Create a physical OCI architecture slide for a cloud-native DICOM store with an on-premises medical imaging facility feeding OCI through Roving Edge Device, FastConnect, and API Gateway. In OCI, show a DICOM store composed of Object Storage, Orthanc, and OCI Database with PostgreSQL, plus separate OKE-backed inference and training environments that read from the store. Keep the design hybrid, secure, and AI-ready without adding unrelated services.
- Best local starting points:
  Primary baseline slide: `32`
  Supporting baseline slide: `31`

### WebLogic Server for OKE via Marketplace

- Oracle link: `https://docs.oracle.com/en/solutions/wls-on-oke-marketplace/`
- Goal:
  Show a Marketplace-provisioned WebLogic domain running on OKE with Jenkins, ingress, shared storage, bastion access, and public and private load balancers.
- Key components:
  OCI region, one availability domain in the reference, regional public and private subnets, bastion tier, administrative host tier, OKE cluster in a private subnet, two node pools, Jenkins controller and agent, Nginx ingress controller, WebLogic Kubernetes Operator, WebLogic administration server, managed servers, introspector, private load balancer for admin and Jenkins access, public load balancer for cluster access, OCI Registry, File Storage, Service Gateway, Internet Gateway.
- Topology:
  One region with regional subnets grouped by function: bastion tier, administrative host tier, WebLogic for OKE tier, public load balancing tier, and storage tier. The OKE tier contains the domain workloads and the private load balancer, while the public load balancer is in a public subnet.
- Core flows:
  Internet traffic enters the public load balancer and reaches the WebLogic cluster.
  Bastion reaches the administrative host, which manages the OKE cluster and shared storage.
  Jenkins and the operator run inside OKE and interact with the registry and domain workloads.
  File Storage is shared across pods for Jenkins home, logs, and helper scripts.
- Constraints and best practices:
  Prefer regional subnets even when adapting the pattern to multi-AD.
  Keep the private and public load balancers distinct.
  Keep the administrative host and bastion separate from the OKE application tier.
  Do not collapse File Storage into a generic database or storage icon without labeling it as shared storage.
- Recommended follow-up questions:
  Ask whether to preserve the single-AD reference layout or adapt it to multi-AD while keeping regional subnets.
  Ask whether the user wants the Marketplace and Resource Manager context visible or only the deployed runtime.
  Ask whether the WebLogic admin path and Jenkins path should be shown separately.
  Ask how to represent WebLogic-specific pods if the icon catalog is limited.
- Recreation prompt:
  Create a physical OCI architecture slide for Oracle WebLogic Server on OKE using a Marketplace-style deployment. Show regional public and private subnets, a bastion tier, an administrative host tier, a private OKE tier with WebLogic and Jenkins workloads, a public load balancer for the WebLogic cluster, a private load balancer for Jenkins and admin access, OCI Registry, and a private File Storage tier shared across pods. Keep the separation between runtime, administration, and storage explicit.
- Best local starting points:
  Primary baseline slide: `32`
  Supporting baseline slides: `29`, `31`

### GitOps with Argo CD on OKE

- Oracle link: `https://docs.oracle.com/en/solutions/deploy-gitops-argocd-oke/`
- Goal:
  Show an OKE-based GitOps control plane where Argo CD synchronizes Kubernetes configuration from Git repositories and exposes the Argo UI through a load balancer.
- Key components:
  Git repository or GitHub, OCI region, one availability domain in the reference, fault domains, VCN, one public subnet, one private subnet, Internet Gateway, NAT Gateway, Service Gateway, Container Registry, load balancer, OKE, Argo CD server service, Argo namespace, worker nodes, and application namespaces.
- Topology:
  Simple one-region OKE pattern with a public ingress subnet and a private application subnet. Argo CD runs inside the OKE cluster, and the cluster communicates outward to Git and OCI services through NAT and Service Gateway paths.
- Core flows:
  Git repository traffic enters through the load balancer to the Argo CD server.
  Argo CD pulls desired state from Git.
  Argo workloads reach external dependencies through NAT and OCI services through Service Gateway.
  OKE worker nodes consume images from Container Registry.
- Constraints and best practices:
  Use regional subnets.
  Keep the public surface area limited to the load balancer.
  Treat Git as the source of truth and show Argo CD as the reconciliation layer, not just another application pod.
  Keep OKE and the Argo namespace in the private subnet.
- Recommended follow-up questions:
  Ask whether the Git repository is external or OCI DevOps hosted.
  Ask whether the user wants only the Argo control plane or also the managed application namespaces.
  Ask whether the registry path should be explicit.
  Ask whether the slide should emphasize one public and one private subnet or a richer enterprise landing zone around them.
- Recreation prompt:
  Create a physical OCI architecture slide for GitOps with Argo CD on OKE. Show a simple OCI region with a VCN, one public ingress subnet with a load balancer, one private subnet with an OKE cluster, Argo CD in its own namespace, application namespaces, NAT and Service Gateway egress, and a container registry path. Keep Git as the external source of truth and keep the control plane private behind the load balancer.
- Best local starting points:
  Primary baseline slide: `32`
  Supporting baseline slide: `27`

### Exadata DR on Oracle Database@Azure

- Oracle link: `https://docs.oracle.com/en/solutions/exadb-dr-on-db-azure/`
- Goal:
  Replicate a cross-region disaster recovery topology for Oracle Exadata Database Service on Oracle AI Database@Azure, fronted by an AKS application tier and protected with Oracle Data Guard.
- Key components:
  Primary and standby Azure regions, AKS subnet, client subnet, Azure load balancer, Azure Container Registry, OCI child site per Azure region, primary and standby OCI regions, primary VCN and standby VCN, hub VCN per region, DRGs, LPGs, Exadata VM clusters, Vault, Oracle Data Guard or Active Data Guard, Oracle Database Autonomous Recovery Service or Object Storage backups.
- Topology:
  Cross-cloud, cross-region pattern with mirrored primary and standby sites. Each Azure site hosts AKS and an OCI child site. Each OCI site uses two VCNs: a primary application or client VCN plus a small hub VCN for transit. DRGs and LPGs provide connectivity, and Oracle Data Guard replicates between Exadata VM clusters.
- Core flows:
  End users reach the AKS application through an Azure public load balancer.
  AKS talks to the Exadata client subnet in OCI.
  Data Guard replicates from primary Exadata to standby Exadata across regions.
  Vault keys and backup services are replicated or available in both sites.
- Constraints and best practices:
  Preserve the mirrored primary and standby posture.
  Show Azure and OCI boundaries distinctly.
  Keep the hub VCNs separate from the primary or standby client VCNs because they exist to satisfy the DRG and transit-routing requirement.
  Keep Data Guard explicit. Do not label the design as DR if the standby database path is not shown.
- Recommended follow-up questions:
  Ask whether the user wants a detailed network-transit view or a simplified DR story.
  Ask whether the slide should highlight Active Data Guard versus basic Data Guard.
  Ask whether backups should point to Autonomous Recovery Service, Object Storage, or both.
  Ask whether AKS should be drawn in both sites or only as a workload context.
- Recreation prompt:
  Create a physical cross-cloud disaster recovery architecture slide with mirrored primary and standby sites across Azure and OCI. In each Azure region, show AKS behind a public load balancer and an Azure client subnet connected to an OCI child site. In each OCI region, show a primary or standby VCN containing Exadata VM clusters plus a separate hub VCN with DRG and LPG transit routing. Make Oracle Data Guard, Vault, and the backup path explicit, and preserve the symmetry between primary and standby.
- Best local starting points:
  Primary baseline slide: `31`
  Supporting baseline slides: `29`, `27`

### Modern App on OKE with PostgreSQL, Redis or Valkey, and OpenSearch

- Oracle link: `https://docs.oracle.com/en/solutions/modernize-app-dev-oci-postgresql-redis-opensearch/`
- Goal:
  Show a modern OCI application platform with OKE for the application tier, OCI Database with PostgreSQL for transactional data, OCI Cache with Redis or Valkey for caching, and OCI Search with OpenSearch for search and observability.
- Key components:
  On-premises connectivity or customer premises equipment, internet clients, WAF, Internet Gateway, DRG, Service Gateway, Bastion, OKE application subnet, OCI Cache with Valkey or Redis subnet, OCI Database with PostgreSQL subnet, OCI Search with OpenSearch subnet, IAM, Object Storage, API Gateway, Cloud Guard, Key Vault, and Monitoring. The HA view also uses multi-node clusters across fault domains.
- Topology:
  One OCI region with multiple private service subnets around an OKE application tier plus ingress and hybrid connectivity. The HA pattern uses dedicated cache, PostgreSQL, and OpenSearch cluster subnets with nodes distributed across fault domains and storage or replicas where appropriate.
- Core flows:
  Internet traffic reaches the application through WAF and Internet Gateway.
  Bastion reaches private resources for administration.
  OKE reads and writes to PostgreSQL, cache, and OpenSearch.
  FastConnect and DRG provide private access from on-premises or enterprise systems.
  Service Gateway provides access to OCI-native services.
- Constraints and best practices:
  Treat PostgreSQL, cache, and OpenSearch as distinct data services with separate roles.
  When HA is in scope, show at least three nodes for managed clusters where the reference calls for one primary and two replicas or equivalent leader or replica roles.
  Keep regional subnets unless the user explicitly wants AD-specific subnet framing.
  Preserve the security story with WAF, Bastion, Cloud Guard, and gateway placement when the user wants production posture.
- Recommended follow-up questions:
  Ask whether the user wants the single-region deployment view, the HA fault-domain view, the cross-region DR view, or a simplified combination.
  Ask whether Redis should be labeled as Redis, Valkey, or a generic cache cluster.
  Ask whether observability should appear as OpenSearch only or as a richer logging stack around it.
  Ask whether the on-premises and FastConnect path must remain visible.
- Recreation prompt:
  Create a physical OCI architecture slide for a modern application on OKE with separate private service tiers for OCI Database with PostgreSQL, OCI Cache with Redis or Valkey, and OCI Search with OpenSearch. Show internet ingress through WAF, optional hybrid access through DRG and FastConnect, Bastion for administration, and OCI service access through a Service Gateway. If HA is requested, show the managed data services with replica or leader roles spread across fault domains while keeping the application platform clear and uncluttered.
- Best local starting points:
  Primary baseline slide: `32`
  Supporting baseline slides: `31`, `29`
