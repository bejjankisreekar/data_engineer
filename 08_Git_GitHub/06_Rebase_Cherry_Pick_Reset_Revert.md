# 06 — Rebase, Cherry-Pick, Reset & Revert

> Prev: [GitHub Essentials](05_GitHub_Essentials.md) · Next: [Stash, Tags & Other Commands](07_Stash_Tags_and_Other_Commands.md)

This file covers Git's "rewrite history" commands — genuinely powerful, genuinely dangerous if misused. Every command here gets both *how it works* and *when not to use it*.

---

## Level 1 — `git rebase`: replaying commits onto a new base

**Rebase** takes the commits unique to your branch and **replays them one by one on top of a different starting point** — producing a straight, linear history instead of a merge commit with two parent lines.

```bash
# main has moved ahead since you branched off it
git switch feature-order-totals
git rebase main
```

```
Successfully rebased and updated refs/heads/feature-order-totals.
```

### Rebase vs Merge — the same goal, two different results

```
Before:                          After MERGE:                    After REBASE:
main:    A---B---C                main:  A---B---C-------M         main:  A---B---C
              \                              \         /                          \
feature:       D---E              feature:    D---E---/           feature:         D'--E'
```

- **Merge** preserves exactly what happened, including a merge commit joining both histories — messier graph, but a fully honest record of "these two things happened in parallel and were joined here."
- **Rebase** rewrites your branch's commits (`D` and `E` become new commits `D'` and `E'` — different hashes, same content) as if they'd been written *starting from* the new base all along — a clean, linear history, but the original commits are gone, replaced by new ones.

---

## Level 1 — `git cherry-pick`: taking one specific commit

**Cherry-pick** applies the changes from **one specific commit** on another branch onto your current branch — without merging or rebasing the whole branch, just that one commit.

```bash
git log --oneline hotfix-branch
```
```
9f8e7d6 Fix critical payment rounding bug
a1b2c3d Add experimental new checkout flow (not ready)
```

You want *only* the rounding fix on `main`, not the experimental checkout flow:

```bash
git switch main
git cherry-pick 9f8e7d6
```

```
[main 4d5e6f7] Fix critical payment rounding bug
 Date: Mon Jul 20 11:02:00 2026 +0530
 1 file changed, 3 insertions(+), 1 deletion(-)
```

A new commit (`4d5e6f7`, different hash) is created on `main` with the *same changes* as `9f8e7d6`. The classic real-world use: a critical bug fix was made on a feature branch, and you need it on `main` (or a release branch) immediately, without pulling in the rest of that feature branch's unfinished work.

---

## Level 2 — `git reset`: moving your branch pointer backward

**Reset** moves your current branch's pointer to a different commit — with three modes controlling what happens to your working directory and staging area along the way.

```bash
git log --oneline
```
```
c3d4e5f (HEAD -> main) Oops, bad commit
b2c3d4e Good commit
a1b2c3d Initial commit
```

```bash
git reset --soft b2c3d4e
```
Moves `HEAD`/`main` back to `b2c3d4e`. The changes from the "bad commit" are **kept, fully staged** — ready to be re-committed differently. Use when: "I want to redo my last commit(s) as a different commit."

```bash
git reset --mixed b2c3d4e   # this is the DEFAULT if you just run: git reset b2c3d4e
```
Same as above, but changes are **unstaged** (back in the working directory only). Use when: "I want to undo the commit AND the staging, but keep my edits to work with."

```bash
git reset --hard b2c3d4e
```
Moves back to `b2c3d4e` and **discards the changes entirely** — working directory and staging area both reset to match that commit exactly. This is genuinely destructive to uncommitted work.

| Mode | Commit undone? | Staging area | Working directory (your files) |
|---|---|---|---|
| `--soft` | Yes | Kept (still staged) | Unchanged |
| `--mixed` (default) | Yes | Cleared | Unchanged (edits still there, just unstaged) |
| `--hard` | Yes | Cleared | **Reset — uncommitted changes are lost** |

> **Never run `git reset --hard` without being certain** — there's no undo dialog. (There *is* a real recovery path via `reflog` — see Level 3.)

---

## Level 2 — `git revert`: undoing a commit *without* rewriting history

**Revert** creates a **new commit** that applies the exact opposite of a previous commit's changes — the history stays fully intact, nothing is deleted or rewritten, it just adds "undo this" as a new, visible step.

```bash
git log --oneline
```
```
c3d4e5f (HEAD -> main) Add buggy discount calculation
b2c3d4e Good commit
```

```bash
git revert c3d4e5f
```
```
[main 8a9b0c1] Revert "Add buggy discount calculation"
```

```bash
git log --oneline
```
```
8a9b0c1 (HEAD -> main) Revert "Add buggy discount calculation"
c3d4e5f Add buggy discount calculation
b2c3d4e Good commit
```

**This is why `revert` is the safe choice for anything already pushed and shared**: `reset` rewrites history (dangerous on shared branches); `revert` adds new history that cancels out the old (safe anywhere, since nobody else's history is invalidated).

---

## Level 3 — Pro corner

### Golden Rule: never rewrite published (pushed, shared) history

Rebase and (hard) reset both **change existing commit hashes or remove commits entirely**. If anyone else has already pulled the original commits, rewriting them on your side creates a divergence: their history and yours no longer agree, and reconciling it is painful and error-prone (often requiring a forced push that can silently drop someone else's work — see [file 04](04_Remotes_Push_Pull_Fetch_Clone.md#force-push--the-command-that-can-destroy-shared-history)).

**The practical rule**: rebase and reset are for **your own local, not-yet-pushed** commits — clean them up all you like before sharing. Once pushed to a shared branch, prefer `revert` to undo something, and prefer `merge` over `rebase` to integrate.

### Interactive rebase — the power tool

```bash
git rebase -i HEAD~3
```

Opens an editor listing your last 3 commits, each with a command you can change:

```
pick 7f3e1a2 Add calculate_total scaffold
pick 4d5e6f7 fix typo
pick 8a9b0c1 actually fix the typo this time
```

Change `pick` to:
- `squash` (or `s`) — combine this commit into the one above it (merges their messages too)
- `fixup` (or `f`) — like squash, but discards this commit's message entirely
- `reword` (or `r`) — keep the commit, but let you edit its message
- `drop` (or `d`) — remove the commit entirely

```
pick   7f3e1a2 Add calculate_total scaffold
fixup  4d5e6f7 fix typo
fixup  8a9b0c1 actually fix the typo this time
```

Result: three messy WIP commits become **one clean commit** — exactly how a thoughtful engineer tidies up a feature branch before opening a Pull Request, so reviewers see a coherent story instead of a stream-of-consciousness commit log.

### Rebase conflicts work differently than merge conflicts

A rebase conflict happens **per replayed commit**, and you resolve them one at a time:

```bash
git rebase main
# CONFLICT (content): Merge conflict in config.py
# ... resolve the file exactly as in file 03 ...
git add config.py
git rebase --continue     # move on to replaying the NEXT commit
# (if another conflict appears, repeat)
git rebase --abort        # bail out entirely, back to how things were before the rebase started
```

### `git reflog` — the safety net for "I think I just destroyed my work"

Git doesn't actually delete commits immediately, even after a `reset --hard` or a botched rebase — they remain reachable (temporarily) via the **reflog**, a local log of everywhere `HEAD` has pointed:

```bash
git reflog
```
```
4d5e6f7 HEAD@{0}: reset: moving to b2c3d4e
c3d4e5f HEAD@{1}: commit: Oops, bad commit
b2c3d4e HEAD@{2}: commit: Good commit
```

```bash
git reset --hard c3d4e5f      # recover the "lost" commit — it was never truly gone
```

This is the single most valuable "I broke something" escape hatch in Git — full recovery walkthroughs live in [file 10](10_Troubleshooting_and_Real_World_Scenarios.md). Note: the reflog is **local only** and expires after ~90 days by default — it's a personal safety net, not a substitute for real backups or careful pushing.

## Checkpoint

1. Explain the difference between what `merge` and `rebase` each do to a branch's history graph.
2. Why is `git revert` safer than `git reset` for a commit that's already been pushed and shared?
3. Walk through using `cherry-pick` to move one bug fix from a feature branch onto `main`.
4. You just ran `git reset --hard` and realized you needed those commits. What command do you run first to find them again?

Next: the supporting commands every engineer eventually needs → [07 — Stash, Tags & Other Commands](07_Stash_Tags_and_Other_Commands.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Rewriting history / rebase (Pro Git): https://git-scm.com/book/en/v2/Git-Branching-Rebasing
- Reset demystified: https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified
- git revert vs reset (Atlassian): https://www.atlassian.com/git/tutorials/undoing-changes

**Videos**
- Git rebase, cherry-pick, reset, revert: https://www.youtube.com/results?search_query=git+rebase+cherry+pick+reset+revert+explained
