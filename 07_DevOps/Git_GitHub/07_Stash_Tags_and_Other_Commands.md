# 07 — Stash, Tags & Other Commands

> Prev: [Rebase, Cherry-Pick, Reset & Revert](06_Rebase_Cherry_Pick_Reset_Revert.md) · Next: [Branching Strategies & Collaboration](08_Branching_Strategies_and_Collaboration.md)

The commands you'll reach for less often than `add`/`commit`/`branch` — but that solve real, recurring problems when you need them.

---

## `git stash`: shelving unfinished work

You're mid-edit on `feature-order-totals`, uncommitted and not ready to commit — and suddenly need to switch branches to fix an urgent bug on `main`. Git won't let you switch cleanly with conflicting uncommitted changes in the way. **Stash** temporarily shelves your changes so your working directory is clean again.

```bash
git status
```
```
On branch feature-order-totals
Changes not staged for commit:
        modified:   totals.py
```

```bash
git stash
```
```
Saved working directory and index state WIP on feature-order-totals: 7f3e1a2 Add calculate_total scaffold
```

```bash
git switch main
# ...fix the urgent bug, commit, push...
git switch feature-order-totals
git stash pop
```
```
On branch feature-order-totals
Changes not staged for commit:
        modified:   totals.py
Dropped refs/stash@{0}
```

`stash pop` reapplies the shelved changes **and removes them from the stash list**. Use `git stash apply` instead if you want to reapply without removing it from the stash (e.g. to apply the same stash to two different branches).

```bash
git stash list                    # see everything currently stashed
git stash push -m "WIP: totals refactor"   # stash with a descriptive message
git stash drop stash@{0}          # delete a specific stash without applying it
git stash clear                   # delete ALL stashes
```

---

## `git tag`: marking specific points in history

A **tag** is a permanent, named pointer to a specific commit — used almost universally for marking **releases** (`v1.0.0`, `v2.1.3`).

```bash
git tag v1.0.0                                  # lightweight tag — just a name, on the current commit
git tag -a v1.0.0 -m "First stable release"     # annotated tag — has its own message, author, date (recommended)
git tag                                          # list all tags
```

```bash
git push origin v1.0.0        # tags are NOT pushed automatically — must push explicitly
git push origin --tags        # push every tag at once
```

Unlike a branch, a tag doesn't move — it's meant to permanently mark "this exact commit was release v1.0.0," forever.

---

## `git blame`: who changed this line, and when?

```bash
git blame totals.py
```
```
7f3e1a2 (Asha Verma  2026-07-20 10:22:00 +0530  1) def calculate_total():
4d5e6f7 (Ravi Kumar   2026-07-21 09:15:00 +0530  2)     return sum(item.price for item in items)
```

Every line is annotated with the commit, author, and date that last changed it — the standard first step when debugging "why is this line here / who do I ask about this logic."

## `git bisect`: binary-searching for the commit that broke something

When a bug appeared somewhere in the last 200 commits and you don't know exactly where, `bisect` finds it via binary search instead of manual guessing:

```bash
git bisect start
git bisect bad                    # the current commit is known broken
git bisect good v1.0.0             # this older tagged commit is known to work
```

```
Bisecting: 99 revisions left to test after this (roughly 7 steps)
[a1b2c3d...] Some commit message
```

Git checks out a commit roughly halfway between "good" and "bad." Test it, then tell Git the result:

```bash
git bisect good     # or:
git bisect bad
```

Repeat — each answer halves the remaining range — until Git identifies the exact first bad commit:

```
a1b2c3d is the first bad commit
```

```bash
git bisect reset    # done — return to where you started
```

Seven steps to search 100 commits, versus checking them one by one — this is genuinely how experienced teams hunt down "when did this regression get introduced" in a large codebase.

---

## Pro corner

- **`git stash` is a stack** — multiple stashes pile up (`stash@{0}` is most recent), and it's easy to forget one exists. `git stash list` regularly, and treat a growing stash list as a signal you're context-switching too much without committing — a WIP commit on a branch (`git commit -m "WIP"`, amended or squashed away later) is often a more visible, safer alternative to a long-lived stash.
- **Semantic Versioning (SemVer)** is the convention almost every tag naming scheme follows: `vMAJOR.MINOR.PATCH` — MAJOR increments on breaking changes, MINOR on backward-compatible new features, PATCH on backward-compatible bug fixes. `v2.1.3` → `v2.2.0` (new feature) → `v2.2.1` (bug fix) → `v3.0.0` (breaking change). Covered further in [file 09](09_Production_Best_Practices_and_CICD.md).
- **`git bisect run`** automates the entire bisect loop by handing it a script that exits 0 (good) or non-zero (bad) — e.g. a test command — letting Git bisect an entire history unattended instead of you manually testing at each step:
```bash
git bisect start HEAD v1.0.0
git bisect run npm test
```
- **Lightweight vs. annotated tags**: a lightweight tag is genuinely just a name on a commit (no metadata of its own); an annotated tag is a full Git object with its own author, date, and message — and, importantly, can be **GPG-signed** for verified releases. For anything resembling a real release, always use `-a` (or `-s` for a signed tag).
- **`git worktree`** lets you check out *multiple branches simultaneously* into separate folders from the same repository — useful when you need to run the old version and the new version side by side without stashing or duplicating a full clone:
```bash
git worktree add ../bakery-orders-hotfix hotfix-branch
```

## Checkpoint

1. When would you use `git stash` instead of just committing your unfinished work?
2. What's the difference between `git stash pop` and `git stash apply`?
3. Why do tags need to be pushed explicitly, unlike commits on a tracked branch?
4. Explain, in your own words, why `bisect` is faster than manually checking commits one at a time to find a bug's origin.

Next: how teams organize branches at scale → [08 — Branching Strategies & Collaboration](08_Branching_Strategies_and_Collaboration.md)

---

## Further Learning — Docs & Videos

**Documentation**
- git stash (Atlassian): https://www.atlassian.com/git/tutorials/saving-changes/git-stash
- Tagging (Pro Git): https://git-scm.com/book/en/v2/Git-Basics-Tagging

**Videos**
- Git stash and tags explained: https://www.youtube.com/results?search_query=git+stash+and+tags+explained
