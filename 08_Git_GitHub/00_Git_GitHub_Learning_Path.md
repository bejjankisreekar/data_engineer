# Git & GitHub — Learning Path

This folder teaches **Git and GitHub from zero to production-ready** — every command explained with a runnable example, building from "what is version control" to the branching strategies, hooks, and CI/CD habits a real engineering team uses daily.

## Why this folder exists

Git isn't optional — it's the one tool every engineer touches regardless of language, cloud, or role. This series treats it with the same rigor as the [PySpark series](../06_PySpark/00_PySpark_Learning_Path.md): runnable commands, a Level 1/2/3 depth structure, and a Checkpoint at the end of every file so you can confirm you actually absorbed it before moving on.

## Git vs GitHub — the one-sentence distinction, up front

**Git** is the version control *tool* — it runs entirely on your machine and has nothing to do with the internet. **GitHub** is a *website/service* that hosts Git repositories online and adds collaboration features (Pull Requests, Issues, Actions) on top. You can use Git your whole career without ever touching GitHub; you cannot use GitHub without Git underneath it. File [01](01_Introduction_to_Version_Control.md) covers this distinction in full before you type a single command.

## Reading order

| # | File | You'll learn |
|---|---|---|
| 01 | [Introduction to Version Control](01_Introduction_to_Version_Control.md) | Why Git exists, installation, first-time config, `git init`, core terminology |
| 02 | [Core Workflow: Add, Commit, Status, Log](02_Core_Workflow_Add_Commit_Status_Log.md) | The daily loop — staging, committing, inspecting history, `.gitignore` |
| 03 | [Branching & Merging](03_Branching_and_Merging.md) | Branches, `checkout`/`switch`, `merge`, and a full hands-on merge conflict |
| 04 | [Remotes: Push, Pull, Fetch, Clone](04_Remotes_Push_Pull_Fetch_Clone.md) | Working with GitHub from the command line, tracking branches, authentication |
| 05 | [GitHub Essentials](05_GitHub_Essentials.md) | Repos, README, Issues, Pull Requests, Forks — the GitHub-specific layer |
| 06 | [Rebase, Cherry-Pick, Reset & Revert](06_Rebase_Cherry_Pick_Reset_Revert.md) | Rewriting history safely (and knowing when not to) |
| 07 | [Stash, Tags & Other Commands](07_Stash_Tags_and_Other_Commands.md) | `stash`, `tag`, `blame`, `bisect` — the supporting cast |
| 08 | [Branching Strategies & Collaboration](08_Branching_Strategies_and_Collaboration.md) | Git Flow vs GitHub Flow vs trunk-based, code review, protected branches |
| 09 | [Production Best Practices & CI/CD](09_Production_Best_Practices_and_CICD.md) | Commit conventions, hooks, GitHub Actions, secrets, Git LFS, signed commits |
| 10 | [Troubleshooting & Real-World Scenarios](10_Troubleshooting_and_Real_World_Scenarios.md) | "I broke it — how do I undo this?" for every common disaster |

## How each file is structured

Same shape as the PySpark series:

- **Level 1** — the basics, with a command and its real terminal output.
- **Level 2** — the patterns you'll actually use day to day.
- **Level 3 — Pro corner** — internals, gotchas, and the judgment calls a senior engineer makes.
- **Checkpoint** — a few questions to confirm you're ready for the next file.

## Prerequisites

None — this folder assumes zero prior Git knowledge. Basic command-line comfort (navigating folders, running a command) is all you need; every Git command itself is taught from scratch.

## The example project used throughout

Most files build on one running example: a small project called `bakery-orders` that you'll `git init` in file 01 and carry forward — creating files, committing, branching, breaking things, and fixing them — so each command is demonstrated in a continuous, realistic context rather than a disconnected snippet.

Start here: **[01 — Introduction to Version Control](01_Introduction_to_Version_Control.md)**

---

## Further Learning — Docs & Videos

**Documentation**
- Official Git documentation: https://git-scm.com/doc
- Pro Git book (free): https://git-scm.com/book/en/v2
- GitHub docs: https://docs.github.com/en/get-started

**Videos**
- Git & GitHub full course: https://www.youtube.com/results?search_query=git+and+github+full+course+for+beginners
- Git tutorial for data engineers: https://www.youtube.com/results?search_query=git+tutorial+for+data+engineers
