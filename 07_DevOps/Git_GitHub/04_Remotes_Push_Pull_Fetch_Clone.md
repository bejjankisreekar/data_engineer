# 04 — Remotes: Push, Pull, Fetch, Clone

> Prev: [Branching & Merging](03_Branching_and_Merging.md) · Next: [GitHub Essentials](05_GitHub_Essentials.md)

Everything so far has been 100% local — no internet involved. This file connects your local repository to a **remote** — a copy of the repository hosted elsewhere (GitHub, in almost all of this series' examples) — which is how collaboration actually happens.

---

## What is a remote?

A **remote** is just a named URL pointing at another copy of the repository. The conventional name for your primary remote is `origin` — it's a convention, not a keyword; you could name it anything.

### Starting from an existing GitHub repo: `git clone`

```bash
git clone https://github.com/asha-verma/bakery-orders.git
cd bakery-orders
```

`clone` downloads the **entire repository** — full history, every branch, every commit — and automatically sets up a remote named `origin` pointing back at that GitHub URL.

### Connecting an *existing* local repo to GitHub

If you already ran `git init` locally (as in file 01) and now want to push it to a new, empty GitHub repository:

```bash
git remote add origin https://github.com/asha-verma/bakery-orders.git
git remote -v
```
```
origin  https://github.com/asha-verma/bakery-orders.git (fetch)
origin  https://github.com/asha-verma/bakery-orders.git (push)
```

---

## `git push`: sending your commits up

```bash
git push -u origin main
```

```
Enumerating objects: 6, done.
...
To https://github.com/asha-verma/bakery-orders.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

`-u` (short for `--set-upstream`) links your local `main` branch to `origin/main` **permanently** — after this one-time setup, a plain `git push` (no arguments) knows exactly where to send commits from now on.

```bash
# after the first -u push, subsequent pushes are just:
git push
```

---

## `git pull`: bringing remote changes down

```bash
git pull
```

`git pull` is actually **two commands combined**: `git fetch` (download new commits from the remote) followed immediately by `git merge` (integrate them into your current branch). If a teammate pushed changes that conflict with your local uncommitted work, `git pull` can produce a merge conflict exactly like the ones in [file 03](03_Branching_and_Merging.md#level-2--merge-conflicts-when-git-cant-decide-for-you) — resolve it the same way.

---

## `git fetch`: the safer way to check for updates

```bash
git fetch origin
```

`fetch` downloads new commits and updates your knowledge of the remote's state (`origin/main`) — but **does not touch your working directory or your local `main` branch at all**. It's the "look before you leap" version of `pull`.

```bash
git fetch origin
git log --oneline main..origin/main    # see exactly what's new on the remote before merging
git merge origin/main                  # now merge it in, once you've reviewed it
```

**Pro habit**: many experienced engineers `fetch` by default and only `merge`/`pull` deliberately, specifically to avoid an unexpected surprise merge (or conflict) landing in the middle of uncommitted work.

---

## Tracking branches, explained properly

A **tracking branch** is a local branch that's linked to a specific remote branch, so `git push`/`git pull` know their target without you specifying it every time.

```bash
git branch -vv
```
```
* main                a1b2c3d [origin/main] Add cinnamon roll order
  feature-order-totals 7f3e1a2 Add calculate_total scaffold
```

`main` shows `[origin/main]` — it's tracking. `feature-order-totals` shows nothing — it's local-only; pushing it for the first time needs the `-u` flag to establish tracking:

```bash
git push -u origin feature-order-totals
```

## `git clone` options worth knowing

```bash
git clone --branch develop https://github.com/org/repo.git   # clone starting on a specific branch
git clone --depth 1 https://github.com/org/repo.git          # shallow clone — only latest commit, no history (fast, for CI)
```

---

## Pro corner

### Authentication: SSH vs. HTTPS

| Method | How it works | Trade-off |
|---|---|---|
| **HTTPS** | Username + a **Personal Access Token (PAT)** — GitHub stopped accepting plain passwords for Git operations years ago | Simple to set up; token needs periodic rotation/renewal |
| **SSH** | An SSH key pair — public key uploaded to GitHub, private key stays on your machine | Set up once, never re-authenticate; the standard for daily engineering work |

```bash
# Generate an SSH key (once per machine)
ssh-keygen -t ed25519 -C "asha@example.com"
# Add the PUBLIC key (id_ed25519.pub) to GitHub → Settings → SSH and GPG keys
# Then clone/add remotes using the SSH URL instead of HTTPS:
git remote add origin git@github.com:asha-verma/bakery-orders.git
```

### `origin` vs. `upstream` — the fork workflow

When you **fork** someone else's repository (covered fully in [file 05](05_GitHub_Essentials.md)), the convention is: `origin` = *your* fork, `upstream` = the *original* repository you forked from.

```bash
git remote add upstream https://github.com/original-owner/project.git
git fetch upstream
git merge upstream/main       # pull the original project's latest changes into your fork
```

### Force push — the command that can destroy shared history

```bash
git push --force            # DANGEROUS: overwrites the remote branch with your local history, no matter what
git push --force-with-lease # SAFER: refuses if someone else pushed since you last fetched
```

`--force` unconditionally overwrites whatever is on the remote — if a teammate pushed commits you don't have locally, `--force` **deletes their work from the remote branch's history** with no warning. `--force-with-lease` is the professional default when a force push is genuinely needed (e.g. after a rebase — [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md)): it checks the remote hasn't changed since your last fetch and refuses if it has, protecting against exactly this disaster. Never force-push to a shared branch like `main` without explicit team agreement — see [file 08](08_Branching_Strategies_and_Collaboration.md) for branch protection rules that prevent this at the platform level.

### What actually gets transferred

Git push/pull/fetch are efficient — they transfer only the **objects** (commits, file versions) the other side doesn't already have, not the entire repository every time. This is why day-to-day pushes/pulls after the initial clone are fast even on large, old repositories.

## Checkpoint

1. Explain the difference between `git fetch` and `git pull` precisely.
2. What does `-u` do the first time you push a branch, and why don't you need it on later pushes?
3. Why is `--force-with-lease` safer than `--force`?
4. In a fork workflow, what do `origin` and `upstream` each conventionally point to?

Next: the GitHub-specific layer on top of everything so far → [05 — GitHub Essentials](05_GitHub_Essentials.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Working with remotes (Pro Git): https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes
- git fetch vs pull (Atlassian): https://www.atlassian.com/git/tutorials/syncing

**Videos**
- Git push, pull, fetch, clone explained: https://www.youtube.com/results?search_query=git+push+pull+fetch+clone+explained
