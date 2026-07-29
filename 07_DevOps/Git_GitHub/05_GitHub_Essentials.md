# 05 — GitHub Essentials

> Prev: [Remotes: Push, Pull, Fetch, Clone](04_Remotes_Push_Pull_Fetch_Clone.md) · Next: [Rebase, Cherry-Pick, Reset & Revert](06_Rebase_Cherry_Pick_Reset_Revert.md)

Everything in files 01–04 is *Git* — it works identically whether your remote is GitHub, GitLab, or a plain server. This file covers what **GitHub specifically** adds on top: the web UI, and the collaboration features (Issues, Pull Requests, Forks) that make it a platform, not just a hosting service.

---

## Level 1 — Creating a repository on GitHub

On github.com: **New repository** → name it → choose Public or Private → optionally initialize with a README, `.gitignore` template, and license → **Create repository**.

GitHub then shows you the exact commands to connect it, matching what you learned in [file 04](04_Remotes_Push_Pull_Fetch_Clone.md):

```bash
git remote add origin https://github.com/asha-verma/bakery-orders.git
git branch -M main
git push -u origin main
```

## Level 1 — The README

`README.md` is the one file every repository should have — GitHub automatically renders it on the repository's home page. At minimum: what the project is, how to install/run it, and how to contribute. This entire course you're reading is itself just a folder of README-style Markdown files rendered by a Git host.

## Level 1 — Issues: tracking work and bugs

An **Issue** is a tracked unit of work — a bug report, a feature request, a task — with a title, description, labels (`bug`, `enhancement`, `good first issue`), an assignee, and a comment thread. Issues are how teams (and open-source projects) track *what needs doing*, separately from the code itself.

```
Title: Negative order quantities are accepted
Labels: bug, priority-high
Assignee: @asha-verma

Body:
Steps to reproduce:
1. Submit an order with quantity = -5
2. Order is accepted without validation

Expected: quantity <= 0 should be rejected.
```

Referencing an issue number in a commit message (`Fixes #42`) and later merging that commit into the default branch **automatically closes the issue** — a small but genuinely useful piece of automation.

---

## Level 2 — Pull Requests: the heart of GitHub collaboration

A **Pull Request (PR)** is a formal request to merge changes from one branch (or a fork) into another, with a dedicated space for **discussion, code review, and automated checks** before anything actually merges. This is the mechanism that makes `main` safe to trust — nothing reaches it without review.

### The typical PR workflow, end to end

```bash
git switch -c fix-negative-quantity
# ...make your code changes...
git add .
git commit -m "Reject orders with quantity <= 0"
git push -u origin fix-negative-quantity
```

Then on GitHub: **Compare & pull request** → write a description of *what* changed and *why* → **Create pull request**.

From there:
1. **Reviewers** read the diff, leave inline comments on specific lines, and either **Approve**, **Request changes**, or just comment.
2. **Automated checks** (tests, linters, CI — see [file 09](09_Production_Best_Practices_and_CICD.md)) run automatically against the PR's branch.
3. The author pushes more commits to the *same branch* in response to feedback — they automatically appear in the same PR, no new PR needed.
4. Once approved and checks pass, someone **merges** the PR — usually via one of three merge strategies GitHub offers:

| Merge strategy | What happens | When to use |
|---|---|---|
| **Merge commit** | A standard three-way merge, preserving every individual commit plus a merge commit | Default; preserves full history |
| **Squash and merge** | All commits in the PR are combined into **one** commit on the target branch | Keeps `main`'s history clean — one commit per feature, regardless of how messy the PR's WIP commits were |
| **Rebase and merge** | Every commit in the PR is individually replayed onto the target branch, no merge commit at all | Keeps a fully linear history; requires understanding [rebase](06_Rebase_Cherry_Pick_Reset_Revert.md) |

Most teams standardize on **Squash and merge** for feature branches — it means `main`'s history is one clean, readable commit per PR, no matter how many "fix typo" / "actually fix it" commits happened along the way during review.

## Level 2 — Forking: contributing to a repo you don't own

A **fork** is your own full copy of someone else's repository, under your own GitHub account — used when you don't have write access to the original.

```bash
# 1. Click "Fork" on GitHub — creates asha-verma/their-project under your account
git clone https://github.com/asha-verma/their-project.git
cd their-project
git remote add upstream https://github.com/original-owner/their-project.git

# 2. Make your change on a branch, push to YOUR fork
git switch -c fix-typo
git commit -am "Fix typo in installation docs"
git push -u origin fix-typo

# 3. Open a Pull Request FROM your fork's branch INTO the original repo, on GitHub
```

This is exactly how essentially all open-source contribution works — you never need write access to the original repository at all.

---

## Level 3 — Pro corner

- **Draft Pull Requests** — mark a PR as a draft while work is still in progress; it signals "not ready for review yet" and, depending on repo settings, can skip triggering full CI until marked ready — useful for pushing WIP work for visibility without asking anyone to review it yet.
- **`CODEOWNERS` file** — a special file (`.github/CODEOWNERS`) that automatically requests review from specific people or teams whenever a PR touches specific paths (e.g. anyone touching `/infra/` must get a platform-team approval). Covered fully in [file 08](08_Branching_Strategies_and_Collaboration.md).
- **GitHub CLI (`gh`)** — lets you create PRs, review, and manage issues entirely from the terminal instead of the browser:
```bash
gh pr create --title "Reject negative quantities" --body "Fixes #42"
gh pr view --web
gh pr merge --squash
```
- **Keeping a fork in sync** long-term is a recurring chore — `upstream` can drift far ahead of your fork. GitHub's web UI has a one-click "Sync fork" button for the simple case; for anything with local unmerged work, `git fetch upstream && git merge upstream/main` (or `rebase`, [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md)) is the manual equivalent.
- **Repository visibility and access**: Public repos are visible to everyone but only writable by people explicitly granted access; Private repos are invisible to everyone else entirely. Fine-grained permissions (Read/Triage/Write/Maintain/Admin) control exactly what each collaborator can do — a common production mistake is granting broad "Write" access when "Triage" (can manage issues/PRs, cannot push code) would have sufficed.

## Checkpoint

1. Explain what a Pull Request adds on top of a plain `git merge`.
2. What's the difference between "Squash and merge" and a regular merge commit, and why do teams often prefer squash for feature branches?
3. Walk through the fork workflow: which remote do you push to, and which remote do you pull the latest upstream changes from?
4. What does referencing `Fixes #42` in a commit message do, once that commit reaches the default branch?

Next: the commands that let you rewrite and replay history deliberately → [06 — Rebase, Cherry-Pick, Reset & Revert](06_Rebase_Cherry_Pick_Reset_Revert.md)

---

## Further Learning — Docs & Videos

**Documentation**
- GitHub quickstart: https://docs.github.com/en/get-started/quickstart
- Pull requests: https://docs.github.com/en/pull-requests
- GitHub flow: https://docs.github.com/en/get-started/using-github/github-flow

**Videos**
- GitHub tutorial (PRs, issues, forks): https://www.youtube.com/results?search_query=github+tutorial+pull+requests+issues
