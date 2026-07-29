# Git — Interview Questions & Answers

## Overview
Git version-controls pipeline code and enables CI/CD. DE interviews keep this practical: everyday commands, branching/merging, conflict resolution, and undo operations. See `07_DevOps/Git_GitHub` for depth.

Difficulty: 🟢 · 🟡 · 🔴 · Confidence: ★.

---

## Interview Questions & Answers

### 🟢 Q1. Git vs GitHub? ★★★★☆
**Git** = the distributed version-control tool (runs locally). **GitHub** = a cloud hosting platform for Git repos adding PRs, issues, reviews, Actions. Git is the engine; GitHub is a service around it.

### 🔴 Q2. merge vs rebase? ★★★★★
**merge** joins branches with a merge commit, preserving history (non-destructive, safe on shared branches). **rebase** replays your commits onto a new base for a **linear** history (rewrites commit hashes — never rebase shared/public branches).

### 🟡 Q3. git fetch vs pull? ★★★★☆
**fetch** downloads remote changes but doesn't touch your working branch (inspect first). **pull** = fetch + merge (or rebase) into your current branch in one step.

### 🟡 Q4. How do you resolve a merge conflict? ★★★★★
Git marks conflicts with `<<<<<<<`, `=======`, `>>>>>>>`. Open each file, choose/combine the correct code, remove the markers, test, then `git add` the files and commit (or `git rebase --continue`).

### 🔴 Q5. reset vs revert vs checkout? ★★★★☆
**reset** moves the branch pointer (`--soft` keeps changes staged, `--mixed` unstages, `--hard` discards — can lose work). **revert** creates a **new** commit that undoes a previous one (safe on shared branches). **checkout/switch** moves between branches/commits (or restores files).

### 🟢 Q6. What is a PR? Review workflow? ★★★★☆
A **Pull Request** proposes merging a branch, enabling code review, CI checks, and discussion before merge. Workflow: branch → commit → push → open PR → review + checks → merge → delete branch.

### 🟡 Q7. Branching strategy (Git Flow / trunk)? ★★★★☆
**Git Flow** = long-lived develop/release/hotfix branches (heavier). **GitHub Flow / trunk-based** = short-lived feature branches off `main`, merge often, keep `main` deployable (preferred for CI/CD).

### 🟢 Q8. git stash — when? ★★★☆☆
Temporarily shelve uncommitted changes (`git stash`) to switch context (e.g., urgent fix), then restore with `git stash pop`. Keeps a dirty working tree out of the way without committing.

### 🟡 Q9. cherry-pick — when? ★★★☆☆
Apply a specific commit from one branch onto another (`git cherry-pick <sha>`) — e.g., port a hotfix commit to `main` without merging the whole branch.

### 🔴 Q10. How do you undo a pushed bad commit? ★★★★☆
On a **shared** branch use `git revert <sha>` (adds a safe undo commit). Avoid `reset --hard` + force-push on shared history (rewrites others' history). Force-push only on your own private branch.

### 🟡 Q11. .gitignore — purpose? ★★★☆☆
Lists files/patterns Git should not track (build artifacts, `.venv/`, secrets, large data). Prevents committing generated or sensitive files.

### 🔴 Q12. How do you recover a lost commit? ★★★☆☆
`git reflog` shows where HEAD/branches pointed recently; find the lost commit's SHA and `git checkout`/`git reset` to it. Reflog is the safety net after a bad reset.

### 🟡 Q13. Squash — what/why? ★★★☆☆
Combine multiple commits into one (interactive rebase or "squash merge" on a PR) for a clean, single logical commit in history.

---

## Scenario Questions
**🟡 S1. "Two engineers edited the same notebook; conflict on pull." ★★★★☆** → resolve markers in the conflicted files, test, `git add`, commit.
**🔴 S2. "A bug shipped to main." ★★★★☆** → `git revert <sha>` and redeploy (safe, keeps history).
**🟡 S3. "Need one hotfix commit from a feature branch on main." ★★★☆☆** → `git cherry-pick <sha>`.
**🟡 S4. "Accidentally committed a secret." ★★★☆☆** → rotate the secret immediately, remove from history (filter-repo/BFG), add to `.gitignore`.

---

## Quick Revision
- ✔ merge (safe, merge commit) vs rebase (linear, rewrites — not on shared)
- ✔ fetch (download only) vs pull (fetch+merge)
- ✔ revert (safe undo) vs reset (moves pointer, can lose work)
- ✔ Conflict = edit markers → add → commit
- ✔ PR + review + branch protection for collaboration
- ✔ Undo shared history with **revert**, not force-push
- ✔ `reflog` recovers lost commits; `stash` shelves work

## Common Interview Mistakes
- Rebasing/force-pushing shared branches.
- `reset --hard` losing work.
- Committing secrets (use .gitignore + Key Vault).
- Confusing revert vs reset.

## Senior-Level Discussion
Seniors enforce trunk/GitHub-flow, PR reviews, branch protection, CODEOWNERS, conventional commits, and safe undo (revert) — treating pipeline code with software discipline and wiring it into CI/CD.

## Follow-up Questions
- "Why is rebase dangerous on shared branches?" → it rewrites commit history others already have.
- "Difference between reset --soft/--mixed/--hard?" → keep staged / unstage / discard changes.

## Related Topics
CI-CD, Azure DevOps, Azure Data Factory, Azure Databricks
