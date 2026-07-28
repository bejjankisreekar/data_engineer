# 10 — Troubleshooting & Real-World Scenarios (Capstone)

> Prev: [Production Best Practices & CI/CD](09_Production_Best_Practices_and_CICD.md) · Series home: [Learning Path](00_Git_GitHub_Learning_Path.md)

A reference for the moment something has already gone wrong — organized by symptom, not by command, so you can find your specific disaster fast. Every fix here builds on commands taught earlier in this series; cross-links point back to the full explanation.

---

## "I need to undo my last commit"

```bash
# Keep the changes, just uncommit them (most common — you want to redo the commit):
git reset --soft HEAD~1

# Uncommit AND unstage (changes stay in your working directory):
git reset HEAD~1

# Throw the commit and its changes away completely:
git reset --hard HEAD~1
```
See [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md#level-2--git-reset-moving-your-branch-pointer-backward) for the full explanation of the three modes.

## "I already pushed that bad commit — everyone else has it too"

Don't `reset` — that rewrites shared history. Use `revert` instead:
```bash
git revert HEAD
git push
```
This adds a new commit undoing the change, safe for anything already shared. Full reasoning: [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md#golden-rule-never-rewrite-published-pushed-shared-history).

## "I want to change my last commit's message (not yet pushed)"

```bash
git commit --amend -m "Correct commit message"
```

## "I committed to the wrong branch"

```bash
# You're on 'main' but the commit belongs on 'feature-x'
git log --oneline -1              # note the commit hash, e.g. a1b2c3d
git reset --soft HEAD~1           # undo the commit on main, keep the changes staged
git switch -c feature-x           # or: git switch feature-x, if it already exists
git commit -m "The commit that belonged here"
```

## "I have uncommitted changes but need to switch branches right now"

```bash
git stash
git switch other-branch
# ...do what you needed to do...
git switch original-branch
git stash pop
```
Full detail: [file 07](07_Stash_Tags_and_Other_Commands.md#level-1--git-stash-shelving-unfinished-work).

## "My branch has a merge conflict and I'm stuck"

```bash
git status                     # lists every file still "both modified"
# open each conflicted file, resolve manually (see below), then:
git add <resolved-file>
git commit                     # for a merge conflict
git rebase --continue          # for a rebase conflict, instead of commit
```

If it's too tangled and you just want to start over:
```bash
git merge --abort      # bail out of an in-progress merge
git rebase --abort     # bail out of an in-progress rebase
```
Full walkthrough with a real conflicting file: [file 03](03_Branching_and_Merging.md#level-2--merge-conflicts-when-git-cant-decide-for-you).

## "I accidentally deleted a branch with unmerged work"

```bash
git reflog
```
```
a1b2c3d HEAD@{2}: commit: Add important feature
7f3e1a2 HEAD@{3}: checkout: moving from feature-x to main
```
```bash
git branch feature-x a1b2c3d     # recreate the branch pointing at the last known commit
```
The reflog remembers where `HEAD` has been recently, even after a branch pointing at it is deleted — as long as you catch it before Git's garbage collection eventually cleans up genuinely unreachable commits (typically weeks later, not immediately). Concept fully explained in [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md#git-reflog--the-safety-net-for-i-think-i-just-destroyed-my-work).

## "I'm in a 'detached HEAD' state and don't know what that means"

```bash
git status
```
```
HEAD detached at a1b2c3d
```

You've checked out a specific commit rather than a branch — any new commits here aren't attached to any branch name, and can become unreachable (recoverable only via reflog, and only temporarily) the moment you switch away. Fix, depending on intent:

```bash
# You want to KEEP work committed here:
git switch -c rescue-branch     # creates a real branch pointing at your current commit — now it's safe

# You just want to leave, discarding nothing that was already committed elsewhere:
git switch main
```

## "I need to combine my last 3 messy commits into one clean commit before opening a PR"

```bash
git rebase -i HEAD~3
# change 'pick' to 'squash' (or 'fixup') on the 2nd and 3rd lines, save and close
```
Full walkthrough: [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md#interactive-rebase--the-power-tool).

## "I pushed something I shouldn't have and need to force-update the remote"

```bash
git push --force-with-lease
```
Use `--force-with-lease`, not plain `--force` — it refuses if someone else pushed since you last fetched, protecting against silently deleting a teammate's work. Full reasoning: [file 04](04_Remotes_Push_Pull_Fetch_Clone.md#force-push--the-command-that-can-destroy-shared-history). **Only do this on a branch you're certain nobody else is actively using** — never on a shared `main` without explicit team agreement, and ideally never at all if branch protection disallows it (file 08).

## "`git pull` says I have unmerged changes / diverging branches and I don't know what to do"

```bash
git status     # see exactly what's conflicting first
git stash      # if you have uncommitted changes in the way
git pull
git stash pop
```
If `git pull` itself produces a merge conflict (someone else's remote changes conflict with your already-committed local commits), resolve it exactly like any other merge conflict — file 03's walkthrough applies unchanged, since `pull` is just `fetch` + `merge` under the hood ([file 04](04_Remotes_Push_Pull_Fetch_Clone.md#level-1--git-pull-bringing-remote-changes-down)).

## "I want to see exactly what changed between two commits, or two branches"

```bash
git diff commit1..commit2
git diff main..feature-x
git log main..feature-x --oneline    # commits on feature-x not yet on main
```

## "I need to find which commit introduced a bug, and there are hundreds of commits"

```bash
git bisect start
git bisect bad                 # current state is broken
git bisect good v1.0.0          # this tag/commit was known good
# test each commit Git checks out, then: git bisect good / git bisect bad
git bisect reset               # when done
```
Full explanation: [file 07](07_Stash_Tags_and_Other_Commands.md#level-2--git-bisect-binary-searching-for-the-commit-that-broke-something).

---

## The full anatomy of resolving a real merge conflict (one complete example)

Putting everything from this series together, start to finish:

```bash
git switch main
git pull                                    # get the latest shared state first
git switch -c fix-shipping-cost
# ...edit shipping.py...
git add shipping.py
git commit -m "fix(shipping): correct rounding on international orders"
git push -u origin fix-shipping-cost
# ...open a Pull Request on GitHub...
```

CI reports the PR branch is out of date and conflicts with `main` (someone else merged a change to the same file):

```bash
git switch fix-shipping-cost
git fetch origin
git merge origin/main
```
```
Auto-merging shipping.py
CONFLICT (content): Merge conflict in shipping.py
```

Open `shipping.py`:
```python
<<<<<<< HEAD
def calculate_shipping(order):
    return round(order.weight * 0.08, 2)
=======
def calculate_shipping(order):
    return round(order.weight * RATE_PER_KG, 2)
>>>>>>> origin/main
```

Both changes matter — `main` introduced a named constant (better practice), your branch fixed the rounding logic. Combine them deliberately:

```python
def calculate_shipping(order):
    return round(order.weight * RATE_PER_KG, 2)
```

```bash
git add shipping.py
git commit -m "Merge main into fix-shipping-cost, keep RATE_PER_KG constant"
git push
```

The PR updates automatically, CI reruns, and once green and approved, it's merged — exactly the loop covered across files 02, 03, 04, 05, and 08, now as one continuous real scenario.

---

## Checkpoint (series final)

1. Your teammate says "I force-pushed and now my last three commits are gone from GitHub, but I still have them locally — what do I do?" Walk them through it.
2. A Pull Request shows a conflict on GitHub's web UI. Name two different ways to actually resolve it (one from your local machine, one using GitHub's own tools) and when you'd choose each.
3. Design the exact Git workflow — from `git switch -c` to a merged PR — for fixing a typo in documentation, following GitHub Flow.
4. Explain, from memory, the difference between `reset --hard`, `revert`, and `rebase` — specifically when each one is the *wrong* choice.

**You've reached the end of the series.** From here: use these commands daily on real work — Git fluency comes from repetition, not re-reading. Revisit any file's Pro corner before a technical interview; they're written to double as interview prep.

---

## Further Learning — Docs & Videos

**Documentation**
- Undoing things (Pro Git): https://git-scm.com/book/en/v2/Git-Basics-Undoing-Things
- Oh Sh*t, Git!?! (common fixes): https://ohshitgit.com/
- git reflog (recovering lost commits): https://git-scm.com/docs/git-reflog

**Videos**
- Fixing common Git mistakes: https://www.youtube.com/results?search_query=how+to+fix+common+git+mistakes
- Git troubleshooting scenarios: https://www.youtube.com/results?search_query=git+troubleshooting+real+world+scenarios
