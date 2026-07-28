# 03 — Branching & Merging

> Prev: [Core Workflow](02_Core_Workflow_Add_Commit_Status_Log.md) · Next: [Remotes: Push, Pull, Fetch, Clone](04_Remotes_Push_Pull_Fetch_Clone.md)

## What is a branch?

A **branch** is an independent line of development — a way to work on something (a new feature, a fix, an experiment) without touching the stable code everyone else relies on. Every repository starts with one default branch (conventionally called `main`, historically `master`).

Analogy: `main` is the published, agreed-upon version of a document. A branch is your own private photocopy — you can scribble all over it, try three different rewrites, and throw two away, and the original stays untouched until you deliberately fold your good changes back in.

Technically, a branch is nothing more than a **movable pointer to a commit**. That's it — no copying of files happens when you create one, which is why branching in Git is instant and nearly free, unlike some older version control systems where branching was slow and expensive.

---

## Level 1 — Creating and switching branches

```bash
git branch feature-order-totals      # create a new branch (doesn't switch to it)
git branch                            # list branches — * marks the current one
```
```
  feature-order-totals
* main
```

```bash
git switch feature-order-totals       # switch to it (modern command, Git 2.23+)
# or the older, still-common equivalent:
git checkout feature-order-totals

# Create AND switch in one step:
git switch -c feature-order-totals
git checkout -b feature-order-totals   # older equivalent
```

Once switched, your working directory changes to match that branch — any edits and commits you now make only affect `feature-order-totals`, and `main` is completely unaffected.

```bash
echo "def calculate_total(): pass" > totals.py
git add totals.py
git commit -m "Add calculate_total scaffold"
git log --oneline --graph --all
```
```
* 7f3e1a2 (HEAD -> feature-order-totals) Add calculate_total scaffold
* a1b2c3d (main) Add first order for chocolate cake
```

Notice `main` didn't move — it still points at the original commit. Your new commit only exists on `feature-order-totals`.

---

## Level 1 — Merging: bringing branches back together

```bash
git switch main
git merge feature-order-totals
```

```
Updating a1b2c3d..7f3e1a2
Fast-forward
 totals.py | 1 +
 1 file changed, 1 insertion(+)
```

That was a **fast-forward merge**: since `main` hadn't changed at all since the branch was created, Git just moved `main`'s pointer forward to match `feature-order-totals` — no new "merge commit" was needed, because there was nothing to reconcile.

---

## Level 2 — The other kind of merge: three-way merges

If `main` *has* moved since your branch diverged (someone else committed to `main` while you were working), Git can't just fast-forward — it must combine both histories:

```bash
git switch main
echo "Cinnamon Roll - Order #103" >> orders.txt
git commit -am "Add cinnamon roll order"     # -am = stage all tracked changes + commit, in one step

git switch feature-order-totals
echo "def calculate_tax(): pass" >> totals.py
git commit -am "Add calculate_tax scaffold"

git switch main
git merge feature-order-totals
```

```
Merge made by the 'ort' strategy.
 totals.py | 1 +
 1 file changed, 1 insertion(+)
```

Because both branches added *different* content, Git automatically combines them into a new **merge commit** — a special commit with **two parents** (the tip of `main` and the tip of `feature-order-totals`), joining the two histories back into one line.

```bash
git log --oneline --graph --all
```
```
*   9k4l5m6 (HEAD -> main) Merge branch 'feature-order-totals'
|\
| * 7f3e1a2 (feature-order-totals) Add calculate_tax scaffold
* | b2c3d4e Add cinnamon roll order
|/
* a1b2c3d Add first order for chocolate cake
```

---

## Level 2 — Merge conflicts: when Git can't decide for you

A conflict happens when **the same lines** of the same file were changed differently on both branches — Git has no way to know which change you actually want, so it stops and asks you.

```bash
git switch main
echo "TAX_RATE = 0.08" > config.py
git add config.py
git commit -m "Set tax rate to 8%"

git switch -c fix-tax-rate
echo "TAX_RATE = 0.12" > config.py
git commit -am "Correct tax rate to 12%"

git switch main
echo "TAX_RATE = 0.10" > config.py
git commit -am "Update tax rate to 10% per new policy"

git merge fix-tax-rate
```

```
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Automatic merge failed; fix conflicts and then commit the result.
```

Open `config.py` — Git has inserted **conflict markers** directly into the file:

```python
<<<<<<< HEAD
TAX_RATE = 0.10
=======
TAX_RATE = 0.12
>>>>>>> fix-tax-rate
```

- Everything between `<<<<<<< HEAD` and `=======` is **your current branch's** version.
- Everything between `=======` and `>>>>>>> fix-tax-rate` is the **incoming branch's** version.

### Resolving it — step by step

1. **Decide the correct outcome** (this is a human, business-logic decision — Git cannot make it for you). Say the 10% policy update should win:
```python
TAX_RATE = 0.10
```
2. **Delete the conflict markers entirely** — `<<<<<<<`, `=======`, `>>>>>>>` must all be removed; leaving any of them in is a common beginner mistake that breaks the file.
3. **Stage the resolved file** — this tells Git "I've resolved this conflict":
```bash
git add config.py
```
4. **Check status to confirm nothing else is still conflicted:**
```bash
git status
```
```
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
        modified:   config.py
```
5. **Commit** — Git already prepared a merge commit message; you can accept it or edit it:
```bash
git commit
```
```
[main 3d4e5f6] Merge branch 'fix-tax-rate'
```

The conflict is resolved and both branches' histories are joined. If at any point you want to bail out entirely and go back to before the merge started:

```bash
git merge --abort
```

---

## Level 2 — Deleting a branch

```bash
git branch -d feature-order-totals    # safe delete — refuses if unmerged commits would be lost
git branch -D feature-order-totals    # force delete — deletes regardless, use with care
```

---

## Level 3 — Pro corner

- **Multiple files can conflict, and one file can have multiple conflict blocks.** `git status` lists every file still marked as "both modified" — resolve and `git add` each one before committing.
- **Merge tools**: instead of hand-editing conflict markers, `git mergetool` launches a configured visual diff/merge tool (VS Code, Beyond Compare, KDiff3) that shows both versions side by side — far easier for large or numerous conflicts.
- **A conflict is not a bug — it's Git correctly refusing to guess.** The most common root cause of frequent painful conflicts is branches living too long without merging back — the longer two branches diverge, the more likely the same code gets touched differently on both sides. Merging (or rebasing — [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md)) `main` into your feature branch *regularly*, not just at the end, keeps conflicts small and frequent instead of one huge, terrifying conflict at the end.
- **`git log --graph --oneline --all --decorate`** is worth aliasing (`git config --global alias.lg "log --graph --oneline --all --decorate"`) — visualizing branch topology is how you build real intuition for what merges actually do.
- **Detached HEAD**: `git checkout <commit-hash>` (checking out a specific commit instead of a branch name) puts you in a state where `HEAD` points directly at a commit, not at a branch. Any new commits made here aren't on any branch and can be lost once you switch away — Git warns you explicitly when this happens. Covered fully with the recovery technique in [file 10](10_Troubleshooting_and_Real_World_Scenarios.md).

## Checkpoint

1. Explain what a branch actually *is* internally (not what it's used for — what it technically points to).
2. What's the difference between a fast-forward merge and a three-way merge?
3. Walk through, in order, the exact steps to resolve a merge conflict in one file.
4. Why do frequent small merges usually cause fewer conflict headaches than one big merge at the end?

Next: sharing your work and collaborating with others → [04 — Remotes: Push, Pull, Fetch, Clone](04_Remotes_Push_Pull_Fetch_Clone.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Git branching (Pro Git): https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
- Merging vs rebasing (Atlassian): https://www.atlassian.com/git/tutorials/merging-vs-rebasing

**Videos**
- Git branching and merging explained: https://www.youtube.com/results?search_query=git+branching+and+merging+explained
