# Kubernetes / AKS — Interview Questions

## Overview
Kubernetes (AKS = Azure Kubernetes Service) orchestrates containers at scale — scheduling, scaling, self-healing. For DE it's relevant when running containerized pipelines, Airflow, or Spark-on-K8s. Interviews stay conceptual: pods, deployments, services, scaling.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Kubernetes? Why use it? | 🟢 | ★★★★☆ |
| 2 | Pod vs Deployment vs Service? | 🟡 | ★★★★★ |
| 3 | What is a node / cluster? | 🟢 | ★★★☆☆ |
| 4 | How does scaling work (HPA)? | 🟡 | ★★★☆☆ |
| 5 | Self-healing / ReplicaSet? | 🟡 | ★★★☆☆ |
| 6 | ConfigMaps vs Secrets? | 🟡 | ★★★★☆ |
| 7 | AKS specifics? | 🟡 | ★★★☆☆ |
| 8 | Where does K8s fit in DE? | 🟡 | ★★★★☆ |

## Key Answers
- **Q1:** Automated container orchestration — scheduling, scaling, self-healing, rolling updates across a cluster. Use it to run many containers reliably at scale.
- **Q2 (key):** **Pod** = smallest unit, one or more containers sharing network/storage. **Deployment** = manages pods (desired replicas, rolling updates, self-healing via ReplicaSet). **Service** = stable network endpoint/load balancer for a set of pods.
- **Q6:** **ConfigMaps** = non-secret config; **Secrets** = sensitive data (base64, integrate with Key Vault via CSI driver for real security).
- **Q8:** Run containerized pipelines, **Airflow on K8s**, or **Spark-on-Kubernetes**; AKS gives managed control plane, autoscaling, and Azure integration.

## Scenario Questions
- **"A pipeline pod keeps crashing."** Deployment/ReplicaSet **self-heals** (restarts); check logs (`kubectl logs`), resources, liveness probes.
- **"Handle variable load."** **Horizontal Pod Autoscaler** scales pods on CPU/metrics; cluster autoscaler adds nodes.
- **"Secure secrets in AKS."** Key Vault + CSI Secrets Store driver, workload identity.

## Quick Revision
- ✔ K8s = container orchestration (schedule/scale/self-heal)
- ✔ **Pod** (containers) → **Deployment** (manages replicas) → **Service** (stable endpoint)
- ✔ **HPA** scales pods; cluster autoscaler scales nodes
- ✔ **ConfigMaps** (config) vs **Secrets** (sensitive)
- ✔ AKS = managed K8s on Azure; runs Airflow/Spark-on-K8s

## Common Mistakes
- Confusing pod vs deployment vs service.
- Plaintext secrets instead of Key Vault CSI.
- Treating pods as durable (they're ephemeral).

## Senior-Level
Seniors run containerized/Airflow/Spark workloads on AKS with autoscaling, workload identity + Key Vault CSI for secrets, resource requests/limits and probes for reliability — choosing K8s when they need portable orchestration beyond managed Databricks/ADF.

## Related Topics
Docker, CI-CD, Azure DevOps, Kafka
