# 09 — Production Best Practices & CI/CD

> Prev: [Branching Strategies & Collaboration](08_Branching_Strategies_and_Collaboration.md) · Next: [Troubleshooting & Real-World Scenarios](10_Troubleshooting_and_Real_World_Scenarios.md)

Everything up to here is "how Git works." This file is "how a production engineering team actually operates it" — the habits, automation, and safety nets that separate a hobby repo from something a company relies on.

---

## Level 1 — Conventional Commits: a commit message standard

```
<type>(<optional scope>): <short description>

[optional longer body]

[optional footer(s)]
```

```
feat(checkout): add support for gift card redemption
fix(orders): reject negative quantities
docs(readme): add local setup instructions
refactor(totals): extract tax calculation into its own function
chore(deps): bump pandas to 2.2.0
```

| Type | Meaning |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or correcting tests |
| `chore` | Maintenance (dependency bumps, config, tooling) |

This isn't just style — a `fix:` or `feat:` prefix is machine-readable, and tools (`semantic-release`, changelog generators) parse commit history to **automatically determine the next version number and generate release notes**, connecting directly to the SemVer tagging covered in [file 07](07_Stash_Tags_and_Other_Commands.md#level-3--pro-corner).

---

## Level 1 — Git hooks: automation triggered by Git events

A **hook** is a script Git runs automatically at a specific point in the workflow — stored in `.git/hooks/`, or managed more reliably across a team via a tool like **Husky** or **pre-commit**.

```bash
# .git/hooks/pre-commit (must be executable: chmod +x)
#!/bin/sh
npm run lint
npm test
```

If this script exits non-zero, **the commit is blocked** — catching lint failures or broken tests before they ever enter history, not after a CI job fails minutes later.

| Hook | Fires | Common use |
|---|---|---|
| `pre-commit` | Before a commit is created | Linting, formatting, quick tests |
| `commit-msg` | After the message is written, before the commit finalizes | Enforce Conventional Commits format |
| `pre-push` | Before a push leaves your machine | Run the full test suite, block pushing broken code |

Since `.git/hooks/` itself isn't version-controlled or shared automatically, real teams use a shareable hook manager (**Husky** for Node projects, **pre-commit** for Python/general use) committed into the repo so every contributor gets the same hooks automatically on clone/install.

---

## Level 2 — GitHub Actions: CI/CD basics

**GitHub Actions** runs automated workflows in response to repository events (a push, a PR, a schedule) — defined as YAML files in `.github/workflows/`.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest
```

This runs automatically on every Pull Request targeting `main` — combined with a branch protection rule requiring this check to pass, no PR can be merged if the tests fail, enforced by the platform rather than trusted to human discipline. This is the technical foundation the [branch protection](08_Branching_Strategies_and_Collaboration.md#level-2--protected-branches) discussion in file 08 assumed was already in place.

A deployment workflow extends the same idea — on merge to `main`, automatically build and deploy:

```yaml
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh
```

---

## Level 2 — Handling secrets: the rule that matters most

**Never commit secrets** — API keys, passwords, connection strings, private keys — to a Git repository, even a private one, even "just for a moment before I remove it." Once committed, a secret exists **permanently in history**, recoverable via `git log -p` or `git show` by anyone with repo access, even after you delete it in a later commit.

- Keep secrets in environment variables, a secret manager (Azure Key Vault, GitHub Actions **Secrets**), or a `.env` file that is **listed in `.gitignore` from before it's ever created**.
- If a secret is accidentally committed: rotating/revoking the actual credential is mandatory — removing it from Git history (via `git filter-repo` or the **BFG Repo-Cleaner** tool) only helps *going forward*; the leaked value must be treated as compromised regardless, since it may already be cloned elsewhere.
```bash
# scanning for secrets before they're ever committed — gitleaks / git-secrets, run as a pre-commit hook
gitleaks protect --staged
```

## Level 2 — Large files: Git LFS

Git is fundamentally bad at storing large binary files (videos, datasets, model weights) — every version of a large file bloats the repository forever, since Git stores full snapshots. **Git LFS (Large File Storage)** replaces large files in the repo with small text pointers, storing the actual content in separate LFS storage:

```bash
git lfs install
git lfs track "*.parquet"
git add .gitattributes
git add large_dataset.parquet
git commit -m "Add training dataset via LFS"
```

---

## Level 3 — Pro corner

### Signed commits — proving a commit really came from you

```bash
git config --global commit.gpgsign true
git config --global user.signingkey <your-GPG-key-id>
git commit -m "Add payment validation"    # now automatically GPG-signed
```

GitHub shows a **"Verified"** badge on signed commits — proof the commit genuinely came from the claimed author's key, not just a matching name/email (which anyone can set with `git config`, trivially spoofable otherwise). Regulated environments and security-conscious open-source projects often require signed commits via branch protection.

### Monorepo vs. polyrepo

| | Monorepo | Polyrepo |
|---|---|---|
| Structure | One repository, many projects/services | One repository per project/service |
| Cross-project changes | One atomic commit/PR across everything | Coordinated changes across multiple PRs/repos |
| Tooling | Needs care at scale (sparse checkout, path-based CI triggers) | Simpler per-repo, harder to coordinate across repos |
| Used by | Google, Meta (famously, enormous monorepos) | Most small-to-mid teams, microservice architectures |

Neither is universally "correct" — the trade-off is coordination cost (easier in a monorepo) vs. blast radius and tooling complexity (easier to isolate in a polyrepo).

### The senior habit: treat pipeline/infra config the same as code

Everything in this file — hooks, CI workflows, branch protection as code (some platforms support this) — follows one underlying principle already established in [Data Pipelines](../../05_Data_Engineering/ETL_ELT/03_Data_Pipelines.md#pipeline-as-code-and-cicd): **infrastructure and process definitions belong in version control, reviewed the same way application code is**, not configured by hand through a UI where changes are invisible and unaudited.

### Field-tested gotchas

- **A `.gitignore` added after secrets are already committed does nothing retroactively** — always set up `.gitignore` for `.env`/credentials *before* the first commit of a new project, not after.
- **CI passing on a PR branch doesn't guarantee `main` stays green** — if the PR branch was out of date with `main` when tests ran, an incompatible change merged elsewhere can still break `main` after merge; "require branches to be up to date before merging" (file 08) closes this gap.
- **Rotating a leaked secret is not optional even if you `git filter-repo` it out** — assume any committed secret is compromised the moment it's pushed, since forks, clones, and cached CI logs may already have it.
- **Signed commits require actual key management discipline** — a lost or leaked GPG private key undermines the entire "Verified" guarantee; treat it with the same care as any other credential.

## Checkpoint

1. Write a Conventional Commits-formatted message for "added a new endpoint to export orders as CSV."
2. What's the difference between a `pre-commit` hook and a GitHub Actions CI check — and why might you want both?
3. Why is removing a secret from Git history not sufficient on its own after an accidental commit?
4. When would a monorepo's coordination advantage outweigh its tooling complexity?

Next: fixing it when something goes wrong → [10 — Troubleshooting & Real-World Scenarios](10_Troubleshooting_and_Real_World_Scenarios.md)

---

## Further Learning — Docs & Videos

**Documentation**
- GitHub Actions (CI/CD): https://docs.github.com/en/actions
- CI/CD concepts (GitLab): https://docs.gitlab.com/ee/ci/
- Git best practices (Atlassian): https://www.atlassian.com/git/tutorials/comparing-workflows

**Videos**
- CI/CD with GitHub Actions: https://www.youtube.com/results?search_query=github+actions+ci+cd+tutorial
- Git best practices for teams: https://www.youtube.com/results?search_query=git+best+practices+for+teams
