# 10 — Practice Questions by Domain

> Prev: [Monitoring & Management Tools](09_Monitoring_and_Management_Tools.md) · Next: [Most Asked & Tricky Questions](11_Most_Asked_and_Tricky_Exam_Questions.md)

Work through each domain after finishing its notes files. Cover the options with your hand/a piece of paper, answer first, **then** check — don't read the explanation before committing to an answer, or you're not actually testing recall. Each answer explains not just what's right, but why the distractors are wrong, since that reasoning is what the real exam requires.

---

## Domain 1: Cloud Concepts

*(notes: [01_Cloud_Concepts.md](01_Cloud_Concepts.md))*

#### Q1. A company wants its e-commerce site to automatically add more server capacity during a flash sale and automatically remove that capacity once the sale ends, without any manual intervention. Which cloud characteristic does this describe?
A. Scalability B. Elasticity C. Fault tolerance D. Agility

**Correct Answer: B — Elasticity.** Elasticity specifically means automatic scaling in *both directions* in response to real-time demand. Scalability (A) is the broader capability to scale but doesn't imply automation or scaling back down. Fault tolerance (C) is about surviving failures, not demand. Agility (D) is about speed of deploying/iterating, not runtime scaling.

#### Q2. Which statement correctly describes the cloud consumption-based model?
A. You pay a fixed annual fee regardless of usage B. You pay upfront for hardware before using it C. You pay only for the resources you actually use, when you use them D. You must sign a 3-year contract to use any cloud service

**Correct Answer: C.** This is the defining feature of cloud computing's OpEx model. A and D describe fixed/contractual models (more like traditional licensing); B describes CapEx, the opposite of cloud economics.

#### Q3. A retail company currently spends millions purchasing and depreciating servers every 3–5 years. After moving to Azure, they instead pay a variable monthly bill based on usage. What shift does this represent?
A. PaaS to SaaS B. CapEx to OpEx C. Public to hybrid cloud D. IaaS to PaaS

**Correct Answer: B.** Buying and depreciating physical hardware is Capital Expenditure; paying an ongoing, usage-based bill is Operating Expenditure. Nothing in the scenario describes a service-model or deployment-model change, ruling out A, C, and D.

#### Q4. Which of the following is an example of Infrastructure as a Service (IaaS)?
A. Microsoft 365 B. Azure Virtual Machines C. Azure App Service D. Azure Functions

**Correct Answer: B.** A VM gives you the raw infrastructure (compute) and you manage the OS upward — the definition of IaaS. Microsoft 365 (A) is SaaS. App Service (C) and Functions (D) are both PaaS.

#### Q5. A development team wants to deploy their web application code without provisioning or managing any virtual machines, operating systems, or runtime patching. Which service model best fits this requirement?
A. IaaS B. PaaS C. On-premises D. Colocation

**Correct Answer: B.** PaaS (e.g. Azure App Service) is exactly "bring your code, we manage everything below it." IaaS (A) would still require them to manage the OS. C and D are not cloud service models at all.

#### Q6. Which cloud deployment model combines a private cloud with a public cloud, connected to allow data and applications to move between them?
A. Multi-cloud B. Community cloud C. Hybrid cloud D. Public cloud

**Correct Answer: C.** Hybrid cloud = private + public, connected. Multi-cloud (A) refers to using two or more *public* cloud providers, not a public+private combination.

#### Q7. A financial services company uses both Azure and AWS simultaneously to avoid depending on a single cloud vendor. Which deployment model does this describe?
A. Hybrid cloud B. Multi-cloud C. Private cloud D. Community cloud

**Correct Answer: B.** Two or more *public* cloud providers used together = multi-cloud, regardless of whether any on-premises infrastructure is involved.

#### Q8. Which of the following is NOT typically considered a core benefit of cloud computing?
A. High availability B. Reduced need for any internet connectivity C. Elasticity D. Disaster recovery

**Correct Answer: B.** Cloud computing inherently *requires* internet/network connectivity to reach services — it doesn't reduce the need for it. The other three are textbook cloud benefits.

#### Q9. Which term describes increasing a single virtual machine's size from 4 vCPUs to 16 vCPUs to handle more load?
A. Scaling out B. Scaling up C. Elastic scaling D. Load balancing

**Correct Answer: B.** Changing the size of a single instance is vertical scaling ("scale up/down"). Scaling out (A) means adding more instances, not resizing one.

#### Q10. What is "serverless computing" best described as?
A. Computing that runs entirely without any physical servers anywhere B. A model where you write code and the cloud provider automatically manages the underlying infrastructure and scaling, billing you per execution C. A deprecated term no longer used in Azure D. A type of on-premises virtualization

**Correct Answer: B.** Serverless doesn't mean no servers exist — it means the provider fully abstracts and manages them, typically with automatic scale-to-zero and consumption-based billing (e.g. Azure Functions).

#### Q11. A hospital must keep all patient records on infrastructure it fully owns and controls, for regulatory reasons, but wants that infrastructure to behave like a modern, self-service cloud environment. Which deployment model fits?
A. Public cloud B. Private cloud C. Multi-cloud D. Community cloud

**Correct Answer: B.** Private cloud gives cloud-style self-service and automation while remaining dedicated to a single organization — either on-premises or hosted privately — which satisfies a strict regulatory requirement for full control that public cloud's shared/multi-tenant model cannot.

#### Q12. Which of the following is the best example of a Software as a Service (SaaS) product, as distinguished from the underlying platform it might run on?
A. Azure App Service B. Azure Virtual Machines C. The Power BI service (accessed via a web browser) D. Azure Kubernetes Service

**Correct Answer: C.** The Power BI *service* is a finished, ready-to-use application accessed over the web with nothing to install or manage — the definition of SaaS. The other three are IaaS/PaaS building blocks a SaaS product might be built on top of, not SaaS themselves.

#### Q13. A company adds more identical web server instances behind a load balancer to handle increased traffic, rather than resizing any single server. What is this called?
A. Scaling up B. Scaling out C. Vertical scaling D. Elastic pricing

**Correct Answer: B.** Adding more instances of the same size is horizontal scaling ("scaling out"). Scaling up (A) and vertical scaling (C) both refer to resizing a single instance, which is not what's described.

#### Q14. Which cloud benefit specifically refers to a business's ability to quickly build, test, and release new features, shortening the time between an idea and a working product?
A. Reliability B. Agility C. Fault tolerance D. Economies of scale

**Correct Answer: B.** Agility is defined as the speed of developing, testing, and deploying solutions — cloud resources being available on-demand in minutes (instead of weeks for physical procurement) is what enables it.

#### Q15. A global streaming company designs its platform so that if an entire Azure region became unavailable due to a natural disaster, the service could be restored in a paired region with minimal data loss. Which capability does this describe?
A. Elasticity B. Disaster recovery C. Vertical scaling D. Multi-cloud

**Correct Answer: B.** Restoring business function after a major regional outage is the definition of disaster recovery — distinct from high availability, which is about avoiding downtime from smaller, routine failures rather than recovering from a catastrophic one.

#### Q16. Which statement correctly distinguishes high availability from disaster recovery?
A. They are identical concepts with different names B. High availability keeps a system running through routine, smaller-scale failures; disaster recovery restores the system after a major, catastrophic outage C. Disaster recovery only applies to on-premises systems D. High availability guarantees zero downtime under all circumstances

**Correct Answer: B.** High availability addresses everyday resilience (a disk fails, a node reboots) so users rarely notice; disaster recovery is the plan and mechanism for recovering after a large-scale event a region or datacenter can't absorb on its own.

#### Q17. Which of the following is an example of Platform as a Service (PaaS)?
A. Azure Virtual Network B. Azure SQL Database C. Outlook on the web D. A virtual machine running SQL Server that you installed and patch yourself

**Correct Answer: B.** Azure SQL Database is a fully managed database platform — you manage schema/data/queries, Microsoft manages the OS, patching, and underlying engine. Option D describes the same database engine deployed as IaaS instead, which is the classic distractor pairing for this question.

#### Q18. In the shared responsibility model, which layer remains the customer's responsibility in EVERY service model — IaaS, PaaS, and SaaS alike?
A. Physical datacenter security B. The operating system C. Data and identity/access management D. The virtualization layer

**Correct Answer: C.** No matter how much of the stack the provider manages, the customer always retains responsibility for their own data and for controlling who has access to it. Physical security (A) and virtualization (D) are always the provider's responsibility; the OS (B) shifts to the provider starting at PaaS.

#### Q19. Which of the following is NOT one of the cloud deployment models covered on the AZ-900 exam?
A. Public cloud B. Private cloud C. Federated cloud D. Hybrid cloud

**Correct Answer: C.** "Federated cloud" is not one of the AZ-900 deployment models. The exam covers public, private, hybrid, and multi-cloud.

#### Q20. A startup signs up for a SaaS project-management tool, paying a monthly per-user subscription fee with no infrastructure to manage. This billing approach is an example of:
A. CapEx B. OpEx C. A perpetual license D. Amortized hardware cost

**Correct Answer: B.** An ongoing, usage/subscription-based fee with no upfront infrastructure purchase is Operating Expenditure — true of SaaS billing just as much as IaaS/PaaS consumption billing.

#### Q21. Why can a large cloud provider typically offer lower per-unit compute costs than an individual company running its own datacenter?
A. Cloud providers are not subject to hardware costs B. Economies of scale — operating at massive scale spreads fixed costs across far more customers, lowering the cost per unit C. Cloud providers use entirely different, cheaper hardware than any company could buy D. Government subsidies cover all cloud infrastructure costs

**Correct Answer: B.** This is the definition of economies of scale as tested on AZ-900 — massive operational scale lowers the provider's per-unit cost, and some of that saving passes through to customers via lower prices than most companies could achieve self-hosting.

#### Q22. A manufacturing company keeps its proprietary CAD design workloads in a private cloud but bursts overflow rendering jobs into Azure public cloud during peak production periods. What is this specific hybrid pattern commonly called?
A. Cloud bursting B. Vertical scaling C. Multi-cloud failover D. Community clustering

**Correct Answer: A.** "Cloud bursting" is the standard term for a hybrid pattern where normal load stays on private/on-prem infrastructure and temporary overflow demand is offloaded to the public cloud.

---

## Domain 2: Azure Architecture and Services

*(notes: [02](02_Azure_Architecture_Fundamentals.md) – [06](06_Identity_Access_Security.md))*

#### Q23. What is the correct order of the Azure management hierarchy, from broadest to narrowest scope?
A. Subscription → Management Group → Resource Group → Resource B. Management Group → Subscription → Resource Group → Resource C. Resource Group → Subscription → Management Group → Resource D. Management Group → Resource Group → Subscription → Resource

**Correct Answer: B.** Management groups sit above subscriptions to allow governance across many subscriptions at once; subscriptions contain resource groups; resource groups contain resources.

#### Q24. What happens to the resources inside a resource group when that resource group is deleted?
A. Nothing — resources must be deleted individually first B. They are moved automatically to the default resource group C. They are all deleted along with the resource group D. They are archived for 30 days before deletion

**Correct Answer: C.** Deleting a resource group deletes every resource inside it. This is the single most tested fact about resource groups — treat it as an irreversible, cascading action.

#### Q25. A region supports Availability Zones. What is the minimum number of physically separate zones such a region must have?
A. 1 B. 2 C. 3 D. 5

**Correct Answer: C.** A region enabled for Availability Zones has at least 3 separate zones, each with independent power, cooling, and networking.

#### Q26. Why does Microsoft pair most Azure regions with another region at least 300 miles away?
A. To reduce latency for all customers globally B. To allow disaster recovery, sequential platform updates, and data residency within the same geography C. To offer a discount on storage in paired regions D. It is only for regions outside the United States

**Correct Answer: B.** Region pairs exist specifically for staged rollout of updates (never both regions updated simultaneously), disaster recovery prioritization, and staying within the same legal/data-residency geography.

#### Q27. Which Azure networking service provides a private, dedicated connection between an on-premises network and Azure that does not travel over the public internet?
A. VPN Gateway B. ExpressRoute C. Azure Front Door D. Network Security Group

**Correct Answer: B.** ExpressRoute is a private, dedicated circuit via a connectivity provider. VPN Gateway (A) is encrypted but still traverses the public internet.

#### Q28. A company needs to load balance HTTP traffic across web servers, routing requests based on URL path, and also wants Web Application Firewall protection. Which service should they use?
A. Azure Load Balancer B. Application Gateway C. Azure Traffic Manager D. Network Security Group

**Correct Answer: B.** Application Gateway is Layer 7 (HTTP-aware), supports URL-path-based routing, and includes a built-in WAF. Load Balancer (A) is Layer 4 and has no WAF or path-based routing. Traffic Manager (C) is DNS-based global routing, not in-region load balancing.

#### Q29. Which Azure storage service is best suited for hosting a fully managed, mountable SMB file share to support a lift-and-shift of an application expecting a traditional network drive?
A. Blob Storage B. Azure Files C. Table Storage D. Queue Storage

**Correct Answer: B.** Azure Files provides SMB/NFS-mountable file shares. Blob Storage (A) is object storage, not a mountable share.

#### Q30. Which storage redundancy option replicates data synchronously across three Availability Zones within a single region?
A. LRS B. ZRS C. GRS D. RA-GRS

**Correct Answer: B.** Zone-Redundant Storage (ZRS) replicates across zones within one region. LRS (A) stays within a single datacenter. GRS (C) and RA-GRS (D) replicate to a separate paired region.

#### Q31. Which Blob Storage access tier is appropriate for data that must be retained for compliance for 7 years and is expected to be accessed less than once a year, tolerating retrieval delays of several hours?
A. Hot B. Cool C. Archive D. Premium

**Correct Answer: C.** Archive is the lowest storage-cost tier, designed for rarely accessed data, with rehydration (retrieval) taking hours — exactly matching this scenario's tolerance for delay.

#### Q32. Which Azure compute service is the fastest option for running a single, short-lived container without setting up any orchestration?
A. Azure Kubernetes Service (AKS) B. Azure Container Instances (ACI) C. Azure Virtual Machines D. Azure App Service

**Correct Answer: B.** ACI is purpose-built for quickly running a single container with no orchestration overhead — the "fastest to start" is the key phrase.

#### Q33. Which compute service should a team choose if they need to orchestrate dozens of interdependent containers with self-healing and rolling updates?
A. Azure Container Instances B. Azure Functions C. Azure Kubernetes Service (AKS) D. Virtual Machine Scale Sets

**Correct Answer: C.** AKS provides full container orchestration (scheduling, self-healing, rolling updates) at scale — ACI (A) is for a single container, not a coordinated fleet.

#### Q34. What is the primary difference between authentication and authorization?
A. They are two names for the same process B. Authentication proves who you are; authorization determines what you're allowed to do C. Authentication happens after authorization D. Authorization requires a password; authentication does not

**Correct Answer: B.** Authentication = identity verification ("who are you"). Authorization = permission checking ("what can you do"), and it always happens *after* successful authentication.

#### Q35. Which built-in Azure RBAC role allows a user to manage all resources in a resource group but NOT grant access to other users?
A. Owner B. Contributor C. Reader D. User Access Administrator

**Correct Answer: B.** Contributor can manage (create/modify/delete) resources but cannot assign roles to others. Owner (A) can do both manage resources and grant access. Reader (C) is view-only. User Access Administrator (D) manages access but not the resources themselves.

#### Q36. Which security principle is summarized by the phrase "never trust, always verify"?
A. Defense in depth B. Zero Trust C. Least privilege alone D. Shared responsibility model

**Correct Answer: B.** This is Microsoft's own summary phrase for the Zero Trust model, which also incorporates least-privilege access and assuming breach as supporting principles — but the exact "never trust, always verify" phrase maps directly to Zero Trust as a whole.

#### Q37. Which Azure service provides a Secure Score and continuous recommendations to improve your cloud security posture?
A. Microsoft Sentinel B. Microsoft Defender for Cloud C. Azure Policy D. Azure Advisor

**Correct Answer: B.** Defender for Cloud is specifically the Cloud Security Posture Management (CSPM) tool that issues a Secure Score. Sentinel (A) is for active threat detection/response (SIEM), not posture scoring. Advisor (D) covers broader recommendations (cost, performance, etc.) but the *Secure Score* specifically belongs to Defender for Cloud.

#### Q38. A company wants users to sign in once and then access multiple applications (email, HR system, expense system) without re-entering credentials for each one. Which feature enables this?
A. Multi-Factor Authentication B. Conditional Access C. Single Sign-On (SSO) D. Role-Based Access Control

**Correct Answer: C.** SSO is defined exactly as signing in once to access multiple applications without repeated authentication prompts.

#### Q39. Which layer of the "defense in depth" model is positioned as the innermost, final layer of protection?
A. Perimeter B. Network C. Data D. Physical security

**Correct Answer: C.** The defense-in-depth layers, from outside in, are: physical security → identity & access → perimeter → network → compute → application → data. Data sits at the core as the asset ultimately being protected.

#### Q40. A company creates two subscriptions, one named "Production" and one named "Development," each with its own budget and access rules. What is the main reason for this separation?
A. Subscriptions provide a billing boundary and an access-control boundary, letting each environment be managed and charged independently B. Azure requires a separate subscription for every resource group C. Resources in different subscriptions automatically replicate to each other D. Subscriptions are only used for identity, not billing

**Correct Answer: A.** This is exactly why organizations commonly split subscriptions by environment or department — each subscription is both a distinct billing unit and a distinct access-control scope.

#### Q41. Can resources within the same resource group be located in different Azure regions?
A. No, all resources in a resource group must be in the same region as the resource group B. Yes, a resource group is a logical container and its resources can span multiple regions C. Only if the resource group has Availability Zones enabled D. Only for storage accounts

**Correct Answer: B.** A resource group is a logical grouping, not a physical/regional boundary — resources inside it can be deployed to different regions from each other and from the resource group's own metadata location.

#### Q42. Two Azure Virtual Networks in the same region need to communicate with each other as though they were a single network, without traffic going over the public internet. What should be configured?
A. ExpressRoute B. VNet Peering C. A Network Security Group D. Azure Front Door

**Correct Answer: B.** VNet Peering connects two VNets over Microsoft's private backbone network so resources in each can communicate directly, without touching the public internet or requiring a gateway.

#### Q43. Which Azure networking resource is used to define basic allow/deny rules controlling inbound and outbound traffic to a subnet or network interface based on IP, port, and protocol?
A. Azure Firewall B. Network Security Group (NSG) C. Load Balancer D. VNet Peering

**Correct Answer: B.** An NSG is Azure's fundamental network-level firewall — a set of security rules filtering traffic by source/destination IP, port, and protocol. (Azure Firewall (A) is a more advanced, fully managed firewall service, but the *basic* allow/deny rule concept described here is the NSG.)

#### Q44. A media company wants users worldwide to experience low latency when loading images and videos from their website, by caching that static content at locations physically closer to each user. Which Azure service should they use?
A. Azure Traffic Manager B. Content Delivery Network (CDN) C. Azure Load Balancer D. Azure Files

**Correct Answer: B.** A CDN caches static content at edge locations ("points of presence") around the world, close to end users, reducing latency versus always fetching from the origin server.

#### Q45. Which Azure Storage service is best suited for storing large volumes of simple, schema-less key-value data at very low cost and massive scale?
A. Blob Storage B. Table Storage C. Queue Storage D. Disk Storage

**Correct Answer: B.** Table Storage is Azure's NoSQL key-value store, purpose-built for large amounts of structured but non-relational data at low cost.

#### Q46. An application's components need to communicate asynchronously, with one component placing work items into a store and another retrieving and processing them independently. Which storage service fits this pattern?
A. Queue Storage B. Table Storage C. Blob Storage D. Azure Files

**Correct Answer: A.** Queue Storage is designed exactly for this — decoupling application components via asynchronous message passing, typically processed in a first-in-first-out order.

#### Q47. If an entire Azure region hosting GRS-replicated data experiences a disaster, what is true about accessing the data in the secondary region immediately afterward?
A. The secondary copy is instantly readable at all times, even before any failover B. With plain GRS (not RA-GRS), the secondary copy is not accessible for reads until Microsoft initiates a failover to that region C. GRS does not replicate to a second region at all D. GRS guarantees zero data loss in every scenario

**Correct Answer: B.** Plain GRS replicates asynchronously to the secondary region, but that secondary copy is not available for read access until a failover occurs — RA-GRS is the option that adds standing read access to the secondary at all times, even before failover.

#### Q48. A company is running a set of identical web server VMs and wants the number of running instances to automatically increase during high traffic and decrease during low traffic, all while being distributed behind a load balancer. What should they deploy?
A. A single large Virtual Machine B. Virtual Machine Scale Sets C. Azure Container Instances D. A Resource Lock

**Correct Answer: B.** VM Scale Sets manage a group of identical, load-balanced VMs that can automatically scale out and in based on demand or a schedule — the mechanism behind horizontal autoscaling for VM-based workloads.

#### Q49. A team has deployed a new version of their web app to a "staging" deployment slot in Azure App Service and verified it works correctly. What should they do to release it to production with minimal downtime?
A. Delete the production app and redeploy from scratch B. Swap the staging slot into the production slot C. Manually copy files from staging to production using FTP D. Create an entirely new App Service plan

**Correct Answer: B.** Deployment slots are designed to be swapped — the staging version becomes production near-instantly, and if something goes wrong, swapping back provides an equally fast rollback.

#### Q50. How does Microsoft Entra ID differ from traditional on-premises Active Directory Domain Services (AD DS)?
A. They are the exact same product with different names B. Entra ID is a cloud-based identity service accessed over HTTP/REST for users, groups, and app registrations; AD DS is designed around on-premises domains, organizational units, and domain controllers for networked devices C. AD DS is only for cloud resources D. Entra ID cannot be used with any Azure subscription

**Correct Answer: B.** This distinction is explicitly tested — Entra ID does not replace AD DS's domain/OU/Group-Policy model for on-prem devices, though the two can be synchronized in hybrid environments (e.g. via Entra Connect).

#### Q51. A company wants to require a one-time code from an authenticator app in addition to a password whenever a user signs in, to reduce the risk from a stolen password alone. What should they enable?
A. Single Sign-On B. Multi-Factor Authentication (MFA) C. Role-Based Access Control D. A resource lock

**Correct Answer: B.** MFA specifically requires two or more independent verification factors (something you know + something you have/are), directly reducing the risk of a compromised password on its own.

#### Q52. A company wants to automatically require MFA whenever a user signs in from outside the corporate office network, but not when signing in from inside it. Which Microsoft Entra feature enables this kind of if-this-then-that access rule?
A. Conditional Access B. Azure Policy C. Resource Locks D. Azure Advisor

**Correct Answer: A.** Conditional Access evaluates signals (like network location, device compliance, or risk level) and applies access rules accordingly — exactly the "if this condition, then require this" logic described.

#### Q53. Where should an application store a database connection string or API key so it is never hardcoded into source code?
A. Azure Key Vault B. A Network Security Group C. A Resource Lock D. Azure Advisor

**Correct Answer: A.** Azure Key Vault is purpose-built to securely store and manage secrets, keys, and certificates, which applications then retrieve at runtime instead of embedding sensitive values directly in code.

---

## Domain 3: Azure Management and Governance

*(notes: [07](07_Cost_Management.md) – [09](09_Monitoring_and_Management_Tools.md))*

#### Q54. Which tool would a company use to estimate the monthly cost of a new Azure deployment before creating any resources?
A. TCO Calculator B. Pricing Calculator C. Cost Management + Billing D. Azure Advisor

**Correct Answer: B.** The Pricing Calculator estimates costs for a planned configuration of specific Azure services. TCO Calculator (A) instead compares existing on-premises costs against running the same workload in Azure.

#### Q55. Which pricing model offers the deepest discount but can have the underlying virtual machine reclaimed by Azure with little notice?
A. Pay-as-you-go B. Reserved Instances C. Spot Instances D. Azure Hybrid Benefit

**Correct Answer: C.** Spot VMs use Azure's spare capacity at steep discounts (up to ~90%) but can be evicted when Azure needs that capacity back — unsuitable for critical, always-on workloads.

#### Q56. A company wants to prevent a specific production database resource from ever being accidentally deleted, even by users with Owner-level access. What should they configure?
A. An Azure Policy with a Deny effect B. RBAC with only Reader access for everyone C. A CanNotDelete resource lock D. A budget alert in Cost Management

**Correct Answer: C.** A CanNotDelete lock blocks deletion regardless of the user's RBAC role — even an Owner cannot delete a locked resource without first removing the lock.

#### Q57. Which of the following correctly distinguishes Azure Policy from RBAC?
A. RBAC controls resource configuration; Policy controls user permissions B. Policy controls what configurations resources are allowed to have; RBAC controls what actions users are allowed to perform C. They are the exact same feature under two different names D. Policy only applies to storage accounts; RBAC applies to all resources

**Correct Answer: B.** RBAC governs identity/permissions ("can this user act on this resource"); Azure Policy governs resource configuration/compliance ("is this resource's configuration allowed to exist"). They operate independently and simultaneously.

#### Q58. Which Azure feature packages ARM templates, RBAC assignments, and Policy assignments together so an entire compliant environment can be deployed repeatably?
A. Azure Advisor B. Azure Blueprints C. Resource Locks D. Microsoft Purview

**Correct Answer: B.** Azure Blueprints bundle governance artifacts (templates, RBAC, Policy, resource groups) into one repeatable deployable package.

#### Q59. Which service is designed specifically to discover, classify, and track the lineage of data across an organization's entire data estate for governance purposes?
A. Azure Monitor B. Microsoft Purview C. Azure Policy D. Log Analytics

**Correct Answer: B.** Microsoft Purview is Azure's unified data governance service for discovery, classification, and lineage tracking.

#### Q60. A company wants a real-time dashboard that shows whether any of THEIR specific deployed Azure resources are currently affected by an ongoing service incident. Which tool should they use?
A. Azure Status B. Azure Service Health C. Azure Advisor D. Microsoft Trust Center

**Correct Answer: B.** Service Health is the personalized view scoped to your own subscription/resources. Azure Status (A) is a public, non-personalized global dashboard.

#### Q61. Which tool provides free, personalized recommendations across Cost, Reliability, Security, Operational Excellence, and Performance categories?
A. Azure Monitor B. Azure Advisor C. Log Analytics D. Azure Policy

**Correct Answer: B.** Azure Advisor is exactly this — a free recommendation engine spanning those five specific categories.

#### Q62. What best describes the relationship between Bicep and ARM templates?
A. Bicep replaces ARM entirely and ARM templates are deprecated B. Bicep is a more concise language that compiles down to an ARM template (JSON) before deployment C. ARM templates compile down to Bicep D. They are unrelated deployment technologies

**Correct Answer: B.** Bicep is a domain-specific language designed to be more readable than raw JSON; it compiles to an ARM template under the hood, and ARM ultimately deploys that JSON.

#### Q63. Which characteristic do both ARM templates and Bicep share that makes redeploying the same template safe and repeatable?
A. They are imperative B. They are declarative C. They require manual approval at each step D. They only work with virtual machines

**Correct Answer: B.** Both describe the *desired end state* declaratively rather than a sequence of imperative steps, which is what makes repeated deployment of the same template idempotent and safe.

#### Q64. A company wants to allocate and report on Azure spend by department, even though each department's resources are spread across multiple resource groups. What should they use?
A. Resource locks B. Tags C. Management groups D. Availability zones

**Correct Answer: B.** Tags (key-value metadata like `Department: Finance`) let you filter and report cost regardless of which resource group a resource physically sits in.

#### Q65. Which tool would you use to browse and manage Blob Storage contents through a graphical interface, without writing any scripts?
A. AzCopy B. Azure Storage Explorer C. Azure Data Box D. Azure Migrate

**Correct Answer: B.** Storage Explorer is the free GUI application for browsing/managing Azure Storage data. AzCopy (A) is the command-line equivalent.

#### Q66. A company has 300 TB of archival data to move to Azure and has very limited internet bandwidth. What is the recommended approach?
A. Use AzCopy over their existing internet connection B. Use Azure Data Box to physically ship the data C. Upload via the Azure Portal one file at a time D. Wait until their internet bandwidth improves

**Correct Answer: B.** Azure Data Box is designed exactly for this: large one-time data volumes where network transfer would be impractically slow — data is copied to a physical appliance and shipped.

#### Q67. A finance manager wants to be automatically notified by email once monthly Azure spending crosses 80% of an agreed limit. Which capability should they configure?
A. A resource lock B. A budget and alert in Cost Management + Billing C. Azure Advisor recommendations D. A management group

**Correct Answer: B.** Cost Management + Billing lets you set a budget and configure alerts that fire when spending reaches a defined threshold — the direct fit for proactive spend monitoring.

#### Q68. What is the key distinction between using tags and using resource groups to organize resources?
A. They are identical and interchangeable B. A resource can belong to only one resource group but can have multiple tags, and tags can cut across resource groups for flexible reporting (e.g. by department) regardless of physical placement C. Tags can only be applied to virtual machines D. Resource groups are used only for cost tracking, never tags

**Correct Answer: B.** Resource group membership is a single, structural placement; tags are flexible metadata that can group resources for reporting purposes (cost, ownership) independently of, and across, resource group boundaries.

#### Q69. Before migrating on-premises servers to Azure, a company wants to assess their current server inventory, performance data, and dependencies to plan the migration. Which tool should they use?
A. Azure Migrate B. Azure Data Box C. AzCopy D. Azure Advisor

**Correct Answer: A.** Azure Migrate is the hub of tools specifically for assessing and migrating on-premises servers, databases, and applications to Azure — including discovery and dependency mapping before the move.

#### Q70. Under a ReadOnly resource lock, which of the following actions is still permitted?
A. Deleting the resource B. Modifying the resource's configuration C. Viewing/reading the resource's current configuration D. Adding a new setting to the resource

**Correct Answer: C.** A ReadOnly lock blocks both modification and deletion, but reading/viewing the resource's existing state remains permitted — that's the entire point of the "ReadOnly" name.

#### Q71. An Azure Policy is assigned with the "Audit" effect rather than "Deny." What happens when a non-compliant resource is created?
A. The resource creation is blocked entirely B. The resource is created, but it is flagged as non-compliant in the policy compliance dashboard, without preventing the action C. The resource is automatically deleted after 24 hours D. The user's account is suspended

**Correct Answer: B.** "Audit" is a monitor-only effect — it lets the action proceed but records and reports the non-compliance, unlike "Deny," which actively blocks the action.

#### Q72. What is the relationship between a policy definition and a policy initiative in Azure Policy?
A. They are the same thing B. A policy initiative is a single, narrowly scoped rule; a policy definition is a group of initiatives C. A policy initiative groups multiple related policy definitions together so they can be assigned as a single unit D. Policy initiatives can only be used with resource locks

**Correct Answer: C.** A policy definition is one rule; an initiative (or "policy set") bundles several related definitions — commonly used to represent a whole regulatory or organizational standard as one assignable package.

#### Q73. Which of these is a key difference between Azure Cloud Shell and Azure CLI installed locally?
A. Cloud Shell only supports PowerShell, never Bash B. Cloud Shell runs in the browser, requires no local installation, and comes pre-authenticated, while Azure CLI is installed on your own machine C. Azure CLI cannot be used to manage Azure resources D. Cloud Shell cannot be accessed from a mobile browser

**Correct Answer: B.** Cloud Shell is a browser-based, pre-authenticated shell (choice of Bash or PowerShell) needing no local setup — ideal for quick access from anywhere, including a browser on a different machine, whereas Azure CLI/PowerShell are locally installed tools.

#### Q74. Which Azure Monitor component is used to write and run queries (using the Kusto Query Language, KQL) against collected log data?
A. Azure Advisor B. Log Analytics C. Azure Policy D. Azure Blueprints

**Correct Answer: B.** Log Analytics is the query and analysis workspace within Azure Monitor, and KQL is the language used to explore the log data it collects.

#### Q75. Where would an organization go to find Microsoft's official compliance certifications, audit reports, and trust documentation (e.g. for ISO or GDPR-related requirements)?
A. Azure Advisor B. Service Trust Portal C. Resource locks D. Azure Blueprints

**Correct Answer: B.** The Service Trust Portal (linked from the broader Microsoft Trust Center) is where customers access Microsoft's compliance audit reports and trust documentation.

#### Q76. A company applies an Azure Policy denying the creation of storage accounts without HTTPS-only traffic enabled, at the Management Group level covering five subscriptions. What is the effect?
A. The policy only applies to the management group itself, not any subscription within it B. The policy cascades down and is enforced across all five subscriptions and everything within them, unless overridden at a lower scope C. Each subscription must separately re-enable the policy for it to take effect D. The policy only affects resource groups named "Production"

**Correct Answer: B.** Governance applied at a management group scope inherits downward through every subscription, resource group, and resource beneath it by default — a core reason management groups exist.

#### Q77. Which statement correctly compares Azure Advisor and Azure Service Health?
A. Both report active incidents currently affecting your resources B. Advisor gives proactive best-practice recommendations (cost, security, performance, etc.); Service Health reports actual ongoing or planned service issues affecting your specific resources C. They are the same tool under two names D. Service Health only covers cost-related issues

**Correct Answer: B.** Advisor is forward-looking guidance on how to improve your environment; Service Health is about real incidents/maintenance events that are actually happening or scheduled, scoped to your resources.

#### Q78. A team wants to check via a mobile device whether any of their Azure resources have triggered an alert while they are away from their desk. Which option supports this?
A. Azure Mobile App B. Azure Data Box C. Azure Migrate D. Resource locks

**Correct Answer: A.** The Azure Mobile App (iOS/Android) is built for exactly this — monitoring resource status and receiving alerts on the go.

---

Total: 78 practice questions across the three domains.

---

## Further Learning — Docs & Videos

**Official practice resources**
- Microsoft Learn free practice assessment (official): https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/practice/assessment
- AZ-900 study guide (skills measured): https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-900
- Microsoft Q&A (ask exam/topic questions): https://learn.microsoft.com/en-us/answers/tags/133/azure

**Videos**
- Microsoft Azure official YouTube channel: https://www.youtube.com/@MicrosoftAzure
- AZ-900 practice questions walkthrough: https://www.youtube.com/results?search_query=az-900+practice+questions+with+answers
- AZ-900 exam questions explained: https://www.youtube.com/results?search_query=az-900+exam+questions+explained+2024

---

Next, work through the specific comparisons that trip people up most often: **[11 — Most Asked & Tricky Exam Questions](11_Most_Asked_and_Tricky_Exam_Questions.md)**.
