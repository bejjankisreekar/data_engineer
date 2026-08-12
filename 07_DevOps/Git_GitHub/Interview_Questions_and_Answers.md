# Git & GitHub — Interview Questions & Answers

Tagged by frequency: 🔥 very common · ⭐ common · 💡 deeper. Covers the whole module ([reading order](00_Git_GitHub_Learning_Path.md)).

Git shows up in nearly every data engineering interview — not as trivia, but as "how do you ship pipeline code safely with a team?" Expect the core workflow, branching strategy, and one or two "you broke production, fix it" scenarios.

---

## Fundamentals

**Q1. 🔥 Git vs GitHub?**
**Git** is the distributed version-control *tool* that runs locally and tracks history. **GitHub** is a *hosting platform* for Git repositories that adds collaboration features (pull requests, issues, Actions, permissions). Git works with no internet and no GitHub.

**Q2. 🔥 Centralized vs distributed version control?**
Centralized (SVN) keeps one server-side history — no server, no history, no commits. **Distributed** (Git) gives every clone a full copy of history, so you commit, branch, diff, and view log entirely offline; the remote is a sync point, not the single source of truth.

**Q3. ⭐ Explain the three areas: working directory, staging area, repository.**
**Working directory** = your actual files. **Staging area (index)** = what you've marked to go into the next commit (`git add`). **Repository** = committed history (`git commit`). Staging is what lets you commit a *subset* of your changes.

**Q4. ⭐ What is HEAD?**
A pointer to the commit you currently have checked out — normally via a branch reference. "Detached HEAD" means HEAD points directly at a commit instead of a branch, so new commits belong to no branch (and are easy to lose).

**Q5. 💡 What is a commit, really?**
An immutable snapshot object identified by a SHA hash, containing the tree (file state), parent commit pointer(s), author/committer, timestamp, and message. Because the hash covers the parent, changing any historical commit changes every SHA after it — which is why rewriting shared history is disruptive.

---

## Core workflow

**Q6. 🔥 Walk me through your basic daily workflow.**
`git pull` (or `fetch` + review) → make changes → `git status` → `git add -p`/`git add <files>` → `git commit -m "..."` → `git push`. On a team: branch first, push the branch, open a PR.

**Q7. 🔥 `git fetch` vs `git pull`?**
`fetch` downloads remote commits but **doesn't touch your working branch** — safe, lets you inspect first. `pull` = `fetch` + `merge` (or `rebase` with `--rebase`), immediately integrating changes. Prefer `fetch` + review when you're unsure what landed.

**Q8. ⭐ What is `.gitignore` and what belongs in it for a data project?**
A file listing paths Git should never track. For data/DE work: `.env` and credential files, `__pycache__/`, `.venv/`, `.ipynb_checkpoints/`, local data files (`*.csv`, `*.parquet`), Terraform state, and anything with secrets or size. **Note:** it only affects *untracked* files — already-tracked files keep being tracked.

**Q9. ⭐ How do you unstage a file vs discard a change?**
Unstage (keep edits): `git restore --staged <file>` (older: `git reset <file>`). Discard edits entirely: `git restore <file>` (older: `git checkout -- <file>`) — destructive, the change is gone.

**Q10. ⭐ What makes a good commit message?**
Imperative present tense, short summary line (~50 chars), blank line, then *why* in the body. Small, single-purpose commits — so `git log`, `revert`, and `bisect` stay useful. Many teams standardize on **Conventional Commits** (`feat:`, `fix:`, `chore:`) to drive changelogs and semantic versioning.

**Q11. 💡 `git diff` vs `git diff --staged`?**
`git diff` = working directory vs staging (unstaged changes). `git diff --staged` (`--cached`) = staging vs last commit (what you're about to commit). `git diff HEAD` = everything since the last commit.

---

## Branching & merging

**Q12. 🔥 What is a branch in Git?**
Just a lightweight, movable **pointer to a commit** — not a copy of the files. That's why creating/deleting branches is instant and cheap.

**Q13. 🔥 Fast-forward vs three-way merge?**
**Fast-forward**: the target branch hasn't diverged, so Git just moves the pointer forward — no merge commit. **Three-way**: both branches have new commits, so Git combines them using the common ancestor and creates a **merge commit** with two parents.

**Q14. 🔥 What causes a merge conflict, and how do you resolve one?**
Two branches changed **the same lines** of the same file (or one edited and one deleted it). Resolve: `git status` to list conflicts → open the file, pick/combine code, delete the `<<<<<<<`, `=======`, `>>>>>>>` markers → `git add` the file → `git commit` (or `git merge --continue`). `git merge --abort` backs out entirely.

**Q15. ⭐ `git merge --no-ff` — why would you use it?**
It forces a merge commit even when a fast-forward is possible, preserving the fact that a feature branch existed as a distinct unit of work — useful for auditability and easy whole-feature reverts.

**Q16. ⭐ How do you delete a branch locally and remotely?**
Local: `git branch -d <name>` (`-D` to force-delete unmerged work). Remote: `git push origin --delete <name>`.

**Q17. 💡 What is a squash merge, and what's the trade-off?**
It collapses all of a branch's commits into one commit on the target branch. Clean, linear main-branch history and easy reverts — but individual commit granularity and intermediate context are lost, and the source branch's commits aren't ancestors of main (so re-merging that branch behaves oddly).

---

## Remotes, GitHub & pull requests

**Q18. 🔥 What is `origin`? What about `upstream`?**
`origin` is the conventional name for the remote you cloned from. In a **fork workflow**, `origin` = your fork and `upstream` = the original repo you sync from (`git fetch upstream && git merge upstream/main`).

**Q19. 🔥 Walk through the pull request workflow.**
Branch from main → commit work → push branch → open a PR describing *what and why* → automated checks (CI, linting, tests) run → reviewers comment → address feedback with new commits → approved → merge (merge/squash/rebase) → delete branch. The PR is the review + audit boundary.

**Q20. ⭐ What is a protected branch?**
A rule on a branch (usually `main`) requiring, e.g., PR review approvals, passing status checks, no force-push, no deletion, and possibly signed commits or linear history. It's how you stop direct pushes to production branches.

**Q21. ⭐ Fork vs branch — when do you fork?**
Branch when you have write access (normal team work). **Fork** when you don't — open source or cross-org contribution: fork, branch in your fork, PR back to the original.

**Q22. ⭐ SSH vs HTTPS for authentication?**
HTTPS uses a **personal access token** (passwords are no longer accepted); SSH uses a key pair with the public key registered on GitHub. SSH avoids repeated credential prompts; HTTPS traverses restrictive corporate firewalls more reliably.

**Q23. 💡 What is `CODEOWNERS` for?**
A file mapping path patterns to owning teams/users so GitHub **auto-requests the right reviewers** — e.g. the platform team owns `/terraform/`, the analytics team owns `/models/`. Combined with protected-branch rules, it enforces that the right people review the right code.

---

## Rewriting history: rebase, reset, revert, cherry-pick

**Q24. 🔥 Merge vs rebase?**
**Merge** preserves true history and adds a merge commit (non-linear graph). **Rebase** replays your commits onto a new base, producing **new commits with new SHAs** and a clean linear history — but rewriting history. Common convention: rebase your *local/feature* branch to stay current, merge into *main* via PR.

**Q25. 🔥 What's the golden rule of rebasing?**
**Never rewrite published/shared history.** Rebasing (or amending, or resetting) commits others have already pulled forces everyone into painful recovery. Rewrite freely only on branches nobody else uses.

**Q26. 🔥 `git reset --soft` vs `--mixed` vs `--hard`?**
All move the branch pointer. `--soft` keeps changes **staged**; `--mixed` (default) keeps them in the **working directory**, unstaged; `--hard` **discards** them entirely (recoverable only via `reflog`, and untracked files aren't saved at all).

**Q27. 🔥 `git reset` vs `git revert` — which for a pushed commit?**
**`git revert`.** It creates a *new* commit that undoes the changes, leaving history intact — safe on shared branches. `reset` rewrites history and needs a force-push, which breaks everyone else's clone.

**Q28. ⭐ What is `git cherry-pick` for?**
Applying **one specific commit** from another branch onto your current branch (as a new commit). Typical use: hotfix committed on `main` that must also go into a release branch, without merging everything else.

**Q29. ⭐ What is interactive rebase used for?**
`git rebase -i HEAD~n` to clean up local history before a PR: **squash** related commits, **reword** messages, **reorder**, **edit**, or **drop** commits. Cleanup only — same golden rule applies.

**Q30. 🔥 You just ran `git reset --hard` and lost your work. What now?**
**`git reflog`** — it records every position HEAD has held, including "lost" commits. Find the SHA and `git reset --hard <sha>` (or `git checkout -b recovery <sha>`). This is Git's safety net; unreferenced commits survive until garbage collection.

---

## Branching strategies & collaboration

**Q31. 🔥 Compare GitHub Flow, Git Flow, and trunk-based development.**
**GitHub Flow** — one long-lived `main` + short-lived feature branches merged via PR; simple, suits continuous deployment. **Git Flow** — `main`, `develop`, plus `feature/`, `release/`, `hotfix/` branches; structured, suits versioned releases, heavier. **Trunk-based** — everyone commits to `main` (or very short branches) behind **feature flags**; highest velocity, demands strong CI and test discipline.

**Q32. ⭐ Which strategy would you pick for a data engineering team, and why?**
Usually **GitHub Flow** with protected `main` + environment branches or promotion pipelines: pipeline code is deployed to dev → test → prod workspaces, and short-lived PR branches keep review overhead low. Git Flow's release branches earn their weight only when you ship versioned artifacts on a schedule.

**Q33. ⭐ What are feature flags and why do they enable trunk-based development?**
Runtime switches that let unfinished code be merged and deployed while staying **off** in production. They decouple *deploy* from *release*, removing the need for long-lived branches — at the cost of flag debt you must clean up.

**Q34. ⭐ What is a merge queue?**
It serializes merges, re-testing each PR against the *latest* main before merging — preventing "both PRs passed CI separately but break together" (semantic conflicts) on busy repositories.

**Q35. 💡 What makes code review effective?**
Small PRs (large ones get rubber-stamped), reviewing for correctness/readability/tests rather than style a linter should catch, asking questions instead of issuing verdicts, and automating everything mechanical (formatting, linting, tests) so humans discuss design.

---

## Production practices & CI/CD (data-engineering angle)

**Q36. 🔥 You committed a secret (connection string / key). What do you do?**
**Rotate/revoke the credential immediately** — that's the real fix; assume it's compromised the moment it's pushed. Then purge it from history (`git filter-repo` or BFG) and force-update, coordinating with the team. Deleting it in a new commit is *not* enough — it stays in history. Prevent it with `.gitignore`, pre-commit secret scanning, and secrets in Key Vault / GitHub Secrets.

**Q37. 🔥 How do you do CI/CD for data pipelines with Git?**
PR triggers a workflow that lints, runs unit tests on transformation logic, validates config/schemas, and optionally runs a smoke pipeline on sample data; merge to `main` deploys to dev, then promotes to test/prod via approvals — deploying ADF ARM templates, Databricks bundles/notebooks, or dbt projects. See [CI/CD for ADF and Databricks](../../14_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md).

**Q38. ⭐ What are Git hooks, and a practical use?**
Scripts triggered by Git events. `pre-commit` for formatting/linting/secret scanning, `commit-msg` to enforce Conventional Commits. Local hooks aren't shared automatically — use the `pre-commit` framework and enforce the same checks in CI, since hooks can be bypassed with `--no-verify`.

**Q39. ⭐ Why are Jupyter/Databricks notebooks awkward in Git, and what do you do?**
`.ipynb` is JSON containing outputs and execution counts, so diffs are noisy and merge conflicts are frequent. Mitigate: strip outputs before commit (`nbstripout`), use Databricks source-format (`.py` with `# MAGIC`/`# COMMAND` markers) via Repos, review logic in `.py` modules, and keep heavy logic in tested modules the notebook merely calls.

**Q40. 💡 Monorepo vs polyrepo for data platforms?**
**Monorepo** — one repo for pipelines, dbt models, IaC: atomic cross-cutting changes, shared standards, easier refactors; needs path-filtered CI to stay fast. **Polyrepo** — independent lifecycles and access control per component, at the cost of cross-repo coordination and duplicated tooling.

**Q41. 💡 What is Git LFS and when do you need it?**
Large File Storage replaces large binaries with small pointers, keeping the repo clone-able. But for data engineering the usual answer is **don't commit data at all** — data belongs in ADLS/Blob, with only code, config, and small fixtures in Git.

---

## Real-world troubleshooting scenarios

**Q42. 🔥 You committed to the wrong branch (not pushed). Fix it?**
Create/switch to the right branch carrying the work, then remove it from the wrong one: `git branch feature-x` → `git reset --hard HEAD~1` (on the wrong branch) → `git switch feature-x`. Or `git stash` before switching if it's uncommitted.

**Q43. ⭐ You need to switch branches immediately but have uncommitted work.**
`git stash` (or `git stash -u` to include untracked), switch, do the urgent work, then `git stash pop`. A WIP commit on your own branch works too — Git switches branches cleanly only when nothing conflicts.

**Q44. ⭐ How do you find which commit introduced a bug among hundreds?**
**`git bisect`** — `git bisect start`, mark a `bad` and a known `good` commit, and Git binary-searches, checking out midpoints for you to test (`git bisect good`/`bad`) until it names the culprit. `git bisect run <test-script>` automates it.

**Q45. ⭐ How do you find who changed a specific line and why?**
`git blame <file>` for the per-line commit/author, then `git show <sha>` for the full change and message — and the PR it came from for the discussion.

**Q46. 💡 `git pull` reports diverged branches. What's happening and what are your options?**
Both you and the remote committed since your last sync. Options: `git pull --rebase` (replay your local commits on top — linear, preferred for unpushed local work), `git pull --no-rebase` (merge commit), or fetch and inspect first. Never resolve it by force-pushing over a shared branch.

---

## Common interview mistakes
- Saying "Git and GitHub are the same thing."
- Using `git reset`/force-push to undo an **already-pushed** commit on a shared branch instead of `git revert`.
- Claiming a secret is safe because a later commit deleted it — it's in history, and it must be **rotated**.
- Not knowing `git reflog` exists when asked to recover lost commits.
- Describing rebase without mentioning that it rewrites SHAs / the golden rule.
- Committing data files, notebook outputs, or `.env` because `.gitignore` was an afterthought.

## Related Topics
[Testing & DataOps](../../14_Testing_and_DataOps/04_DataOps_and_CICD_for_Data.md) · [CI/CD for ADF & Databricks](../../14_Testing_and_DataOps/05_CICD_for_ADF_and_Databricks.md) · [Databricks Notebooks & Repos](../../08_Databricks/04_Notebooks_Repos_and_Jobs.md) · [dbt](../../13_dbt/01_What_is_dbt.md) · [Data Governance & Security](../../06_Data_Engineering/Data_Governance/01_Data_Governance_and_Security.md) · [Projects & Portfolio](../../18_Projects/05_Portfolio_and_GitHub_Presentation.md)
