# 02 — Core Workflow: Add, Commit, Status, Log

> Prev: [Introduction to Version Control](01_Introduction_to_Version_Control.md) · Next: [Branching & Merging](03_Branching_and_Merging.md)

This is the loop you'll run dozens of times a day: **edit → check status → stage → commit**. Everything else in Git builds on top of this.

---

## `git status`: what's changed?

```bash
# inside bakery-orders/
echo "Chocolate Cake - Order #101" > orders.txt
git status
```

```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        orders.txt

nothing added to commit but untracked files present (use "git add" to track)
```

`git status` is completely safe to run constantly — it changes nothing, it only *reports*. Get in the habit of running it before and after almost every other command while learning.

---

## `git add`: staging changes

```bash
git add orders.txt
git status
```

```
On branch main
No commits yet
Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   orders.txt
```

`git add` moves a change from the **working directory** into the **staging area** — it tells Git "this is going in my next commit." The file's actual content on disk hasn't changed at all; you've just told Git which changes to include next.

```bash
git add file1.txt file2.txt   # stage specific files
git add .                     # stage everything changed in and below the current folder
git add -A                    # stage everything changed in the WHOLE repo, including deletions
```

---

## `git commit`: making it permanent

```bash
git commit -m "Add first order for chocolate cake"
```

```
[main (root-commit) a1b2c3d] Add first order for chocolate cake
 1 file changed, 1 insertion(+)
 create mode 100644 orders.txt
```

That `a1b2c3d` is the start of the commit's **SHA hash** — a unique fingerprint for this exact snapshot. `-m` provides the commit message inline; omitting `-m` opens your default text editor to write a longer message.

**Only staged changes get committed.** If you edit a file *after* `git add` but *before* `git commit`, that new edit is not included — it sits as a fresh unstaged change. This trips up nearly everyone once.

---

## `git log`: viewing history

```bash
git log
```

```
commit a1b2c3d4e5f6... (HEAD -> main)
Author: Asha Verma <asha@example.com>
Date:   Mon Jul 20 10:15:00 2026 +0530

    Add first order for chocolate cake
```

```bash
git log --oneline           # one line per commit — the everyday version
git log --oneline --graph   # + a visual branch graph (essential once branching starts)
git log -p                  # show the full diff of every commit
git log -3                  # only the 3 most recent commits
```

---

## `git diff`: seeing exactly what changed

```bash
echo "Vanilla Cupcake - Order #102" >> orders.txt
git diff                 # unstaged changes: working dir vs staging area
```

```diff
diff --git a/orders.txt b/orders.txt
index 3f2b1a0..8c9d2e1 100644
--- a/orders.txt
+++ b/orders.txt
@@ -1 +1,2 @@
 Chocolate Cake - Order #101
+Vanilla Cupcake - Order #102
```

```bash
git add orders.txt
git diff --staged        # staged changes: staging area vs last commit (what WILL be committed)
```

## `.gitignore`: telling Git what to never track

Every project generates files that should never be committed — logs, build output, secrets, dependency folders, IDE settings.

```bash
# .gitignore
*.log
__pycache__/
.env
node_modules/
.vscode/
```

```bash
git add .gitignore
git commit -m "Add .gitignore"
```

Once a pattern is in `.gitignore`, matching files won't show up in `git status` or get pulled in by `git add .` — but **only for files Git doesn't already track**. If a file was committed *before* you ignored it, `.gitignore` has no effect on it retroactively; you must explicitly remove it:

```bash
git rm --cached secrets.env    # untrack it, but keep the file on disk
echo "secrets.env" >> .gitignore
git commit -m "Stop tracking secrets.env"
```

## Writing good commit messages

```
Short summary line, 50 chars or less, imperative mood

Optional longer body explaining WHY this change was made,
wrapped at ~72 chars, not WHAT changed (the diff already
shows that).

Fixes #42
```

"Imperative mood" means write it as a command: **"Add validation"**, not "Added validation" or "Adds validation" — the convention comes from Git itself completing the sentence "If applied, this commit will ___". File [09](09_Production_Best_Practices_and_CICD.md) covers the fuller **Conventional Commits** standard teams use in production.

---

## Pro corner

- **Commit small and often.** A commit should represent one logical change — "add login validation," not "add login validation, fix typo in README, and refactor the database module." Small commits are easier to review, easier to revert individually, and make `git log` an actually useful project history instead of noise.
- **`git add -p` (patch mode)** lets you stage *parts* of a file's changes interactively, hunk by hunk — essential when you've made two unrelated edits in the same file and want them in two separate, clean commits instead of one messy one.
```bash
git add -p orders.txt
# Stage this hunk [y,n,q,a,d,s,e,?]?
```
- **`HEAD`** is a pointer to whatever commit you currently have checked out — almost always "the latest commit on my current branch." You'll see `HEAD` constantly in output and in later commands (`reset`, `checkout`) — it just means "where I am right now."
- **Amending the last commit** — `git commit --amend` replaces your most recent commit entirely (new message and/or newly staged changes folded in) rather than creating a new one. Powerful for fixing a typo you just made — but **never amend a commit that's already been pushed and shared**, since it rewrites history (see [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md) for why rewriting shared history is dangerous).
- **`git show <commit>`** displays one specific commit's full diff without needing `log -p` and scrolling — the fastest way to inspect a single change by its hash.

## Checkpoint

1. Explain the difference between `git add` and `git commit` in your own words.
2. What happens if you edit a file again after `git add` but before `git commit`?
3. Why doesn't adding a pattern to `.gitignore` remove a file that's already committed?
4. Write a properly formatted commit message (imperative mood, correct length) for "I fixed the bug where negative order quantities were accepted."

Next: working with multiple lines of development at once → [03 — Branching & Merging](03_Branching_and_Merging.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Recording changes (Pro Git): https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
- git add / commit / status / log: https://git-scm.com/docs

**Videos**
- Git add, commit, status, log explained: https://www.youtube.com/results?search_query=git+add+commit+status+log+tutorial
