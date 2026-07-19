# 01 — Introduction to Version Control

> Series: [Git & GitHub Learning Path](00_Git_GitHub_Learning_Path.md) · Next: [Core Workflow](02_Core_Workflow_Add_Commit_Status_Log.md)

## Why does version control exist?

Imagine writing a report in a Word file, and every time you make a big change you save a new copy: `report_final.docx`, `report_final_v2.docx`, `report_final_v2_REALLY_FINAL.docx`, `report_final_v2_REALLY_FINAL_useThisOne.docx`. Now imagine two people editing that report at once, over email, trying to merge their changes by hand. This is the exact problem every software team had before version control — and it gets unworkable fast with more than one person or more than a few changes.

**Version control** is a system that records changes to files over time, so you can:

- See the full history of every change, who made it, and why.
- Go back to any previous version instantly.
- Let multiple people work on the same files simultaneously without overwriting each other.
- Experiment safely (try something, and throw it away cleanly if it doesn't work).

**Git** is, by a wide margin, the most widely used version control system in the world today — created in 2005 by Linus Torvalds (the creator of Linux) specifically to manage the Linux kernel's source code, which involved thousands of contributors.

---

## Centralized vs. Distributed version control

| | Centralized (e.g. old SVN) | Distributed (Git) |
|---|---|---|
| Where's the full history? | One central server only | **Every** clone has the *entire* project history |
| Working offline | Can't commit without the server | Commit, branch, view history — all offline; only *sharing* needs a network |
| If the server dies | History can be lost entirely | Any clone can restore the full project — the history is duplicated everywhere |

This distributed nature is the single most important fact about Git's design: when you `git clone` a repository, you don't get a snapshot — you get the **entire history**, on your own machine, immediately.

---

## Git vs GitHub — worth repeating clearly

- **Git** = the tool. Runs locally. Free, open-source. No internet required.
- **GitHub** = a website that *hosts* Git repositories in the cloud, and adds collaboration tooling (Pull Requests, Issues, code review, Actions/CI) on top of plain Git.
- **GitLab, Bitbucket** = direct competitors to GitHub — same idea, different company. Everything in this series about "GitHub" (Pull Requests, Issues) has a near-identical equivalent on those platforms; the underlying Git commands are 100% identical everywhere, since Git itself doesn't care which host you use.

---

## Level 1 — Installing and configuring Git

### Install

```bash
# Windows: download from git-scm.com, or via winget
winget install --id Git.Git -e

# macOS
brew install git

# Linux (Debian/Ubuntu)
sudo apt install git
```

Verify:
```bash
git --version
# git version 2.44.0
```

### First-time configuration (do this once per machine)

```bash
git config --global user.name "Asha Verma"
git config --global user.email "asha@example.com"
```

This name/email is stamped onto **every commit you make** — it's how Git (and GitHub) know who did what. `--global` means this applies to every repository on your machine; omit it to set a different identity for just one project (e.g. a work email vs. a personal one).

```bash
# See everything currently configured
git config --list
```

---

## Level 1 — Your first repository

```bash
mkdir bakery-orders
cd bakery-orders
git init
```

```
Initialized empty Git repository in /home/asha/bakery-orders/.git/
```

`git init` turns an ordinary folder into a Git repository by creating a hidden `.git` subfolder — that's where Git stores the *entire* history, every version of every file, all metadata. Delete `.git` and you've deleted all Git history (the actual files in your folder remain, but they're no longer version-controlled).

---

## Level 2 — Core terminology, defined precisely

These four words are used constantly from here on — get them exactly right now:

| Term | Meaning |
|---|---|
| **Repository (repo)** | A project tracked by Git — the folder plus its `.git` history |
| **Working Directory** | The actual files on your disk, as you see and edit them right now |
| **Staging Area (Index)** | A holding area where you list *exactly* which changes you want in your *next* commit |
| **Commit** | A permanent, named snapshot of the staged changes, saved into the repository's history forever |

```
Working Directory  →  (git add)  →  Staging Area  →  (git commit)  →  Repository History
   (your edits)                    (what's "next")                    (permanent record)
```

This three-stage flow — edit, stage, commit — is the single most important mental model in all of Git, and file [02](02_Core_Workflow_Add_Commit_Status_Log.md) is entirely about using it well.

---

## Level 3 — Pro corner

- **`.git` is the entire product.** Nothing about Git lives anywhere else — no external database, no hidden server state for a local repo. This is *why* distributed version control works: copying the `.git` folder (which is exactly what `git clone` does) copies the complete project history.
- **Git tracks content, not files by name.** Internally, Git stores objects (blobs, trees, commits) addressed by a SHA-1/SHA-256 hash of their *content* — if you rename a file but its content is unchanged, Git recognizes it as the same underlying object. This is why `git mv` is really just a convenience wrapper — a plain filesystem rename followed by `git add` achieves the identical result.
- **A commit is a snapshot, not a diff**, even though `git diff`/`git log -p` *display* commits as diffs for human readability. Internally each commit points to a complete tree of the entire project at that moment — Git computes diffs on the fly for display, it doesn't store them that way.
- **Global vs. local config precedence**: `git config --local` (the default when run inside a repo, no flag needed) overrides `--global`, which overrides `--system`. A common real mistake: committing under a personal email on a work repo because only global config was ever set — set `user.email` locally per work repo if you use multiple identities.

## Checkpoint — you should now be able to

1. Explain the difference between Git and GitHub in one sentence each.
2. Explain why distributed version control lets you work fully offline.
3. Run `git init` and know exactly what folder Git created and why.
4. Name the three stages a change passes through, in order, before it's permanent history.

Next: the daily loop of actually recording changes → [02 — Core Workflow: Add, Commit, Status, Log](02_Core_Workflow_Add_Commit_Status_Log.md)
