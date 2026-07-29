# Docker — Interview Questions

## Overview
Docker packages code + dependencies into portable **containers** for consistent runs across environments. In DE it's used for packaging jobs, custom Spark/Airflow images, and reproducible pipelines. Interviews stay practical: images vs containers, Dockerfile, volumes, and why containers.

## Top Interview Questions

| # | Question | Difficulty | Confidence |
|---|---|---|---|
| 1 | What is Docker? Why containers? | 🟢 | ★★★★★ |
| 2 | Image vs container? | 🟢 | ★★★★★ |
| 3 | Container vs VM? | 🟡 | ★★★★☆ |
| 4 | What is a Dockerfile? Key instructions? | 🟡 | ★★★★☆ |
| 5 | Volumes / persisting data? | 🟡 | ★★★☆☆ |
| 6 | Layers & caching? | 🟡 | ★★★☆☆ |
| 7 | Docker Compose? | 🟢 | ★★★☆☆ |
| 8 | How is Docker used in data pipelines? | 🟡 | ★★★★☆ |
| 9 | Registry (ACR)? | 🟢 | ★★★☆☆ |

## Key Answers
- **Q1:** Containers bundle app + dependencies so it runs identically everywhere — solving "works on my machine." Lightweight, fast, portable.
- **Q2:** An **image** is the immutable blueprint (built from a Dockerfile); a **container** is a running instance of an image. One image → many containers.
- **Q3:** Containers share the host OS kernel (lightweight, fast, seconds to start); VMs virtualize full OS (heavier, minutes). Containers = process isolation, not full OS.
- **Q8:** Package pipeline/job code + libs into an image, run in ACI/AKS/Airflow workers; ensures reproducible dependencies (matches the venv/requirements idea at scale).

## Scenario Questions
- **"A job runs on my laptop but fails in prod."** Containerize it (same image everywhere) → identical runtime.
- **"Ship a custom Airflow/Spark image."** Dockerfile from a base image + your deps, push to **ACR**, run on AKS.

## Quick Revision
- ✔ Container = app + deps, portable, consistent
- ✔ **Image** (blueprint) → **container** (running instance)
- ✔ Container shares host kernel (light) vs VM (full OS)
- ✔ **Dockerfile** (FROM/RUN/COPY/CMD) builds images; layers cached
- ✔ **Volumes** persist data outside the container
- ✔ Store images in a **registry (ACR)**

## Common Mistakes
- Confusing image vs container.
- Storing state inside a container (use volumes).
- Bloated images (no layer optimization).

## Senior-Level
Seniors containerize pipeline code for reproducibility, optimize layers/caching, store images in ACR with scanning, and run on AKS/ACI — treating containers as the deployment unit in CI/CD.

## Related Topics
Kubernetes, CI-CD, Python, Azure DevOps
