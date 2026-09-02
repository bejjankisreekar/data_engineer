# 08 — Branching Strategies & Collaboration

> Prev: [Stash, Tags & Other Commands](07_Stash_Tags_and_Other_Commands.md) · Next: [Production Best Practices & CI/CD](09_Production_Best_Practices_and_CICD.md)

Everything so far has been commands. This file is about **how real teams organize their use of those commands** — the agreed-upon rules that keep a shared repository sane with more than one person committing to it.

---

## Why teams need a branching strategy at all

Without an agreed convention, a team ends up with branches named inconsistently, nobody sure which branch is "safe to build from," and features half-merged into `main` at random points. A **branching strategy** is a team-wide agreement on: what branches exist, what each one means, and exactly how code moves between them.

---

## Three common strategies

### 1. GitHub Flow — the simplest, most common for continuous deployment

```
main (always deployable)
  └── feature branches, short-lived, merged via PR, deleted after merge
```

Rules: `main` is always in a deployable state. Every change is a short-lived branch off `main`, opened as a Pull Request, reviewed, and merged straight back into `main` — which typically triggers an automatic deploy. No long-lived `develop` branch, no complex hierarchy.

**Best for**: web apps and services deployed continuously (multiple times a day/week), which is the majority of modern SaaS engineering teams.

### 2. Git Flow — the traditional, structured model

```
main       (production releases only)
develop    (integration branch — the "next release" in progress)
  ├── feature/*   (branched from develop, merged back into develop)
  ├── release/*   (branched from develop when preparing a release, merged into BOTH main and develop)
  └── hotfix/*    (branched from main for urgent production fixes, merged into BOTH main and develop)
```

Rules: `main` only ever contains released, tagged, production code. All ongoing work integrates on `develop` first. A `release/*` branch freezes scope for final testing before merging into `main` (tagged as a release) and back into `develop`. A `hotfix/*` branch lets an urgent production fix skip the normal `develop` cycle and go straight to `main`, then gets merged back into `develop` too so the fix isn't lost on the next release.

**Best for**: software with scheduled, versioned releases (desktop apps, mobile apps, on-prem enterprise software) where multiple release versions may need active support simultaneously — genuinely more overhead than most continuously-deployed web services need.

### 3. Trunk-Based Development — the high-velocity model

```
main (the "trunk") — everyone commits here directly or via very short-lived branches (hours, not days)
```

Rules: branches, if used at all, live for hours, not days — merged back constantly. Unfinished features are hidden behind **feature flags** (a runtime toggle) rather than being kept isolated on a long-lived branch, so `main` can be deployed at any moment even with incomplete work present but switched off.

**Best for**: teams with strong automated testing and CI, deploying very frequently, prioritizing avoiding the "long-lived branch drifts and conflicts painfully" problem entirely by never letting branches live long enough for that to happen.

| | GitHub Flow | Git Flow | Trunk-Based |
|---|---|---|---|
| Branch lifespan | Days | Days to weeks | Hours |
| Complexity | Low | High | Low (but requires feature flags) |
| Release cadence | Continuous | Scheduled/versioned | Continuous, very frequent |
| Good fit | Most SaaS/web teams | Versioned software, multiple supported releases | High-maturity CI/CD teams |

---

## Protected branches

GitHub lets repository admins configure **branch protection rules** on `main` (or any branch) — enforced by the platform, not just team agreement:

- Require Pull Requests before merging (no direct pushes at all, even for admins, if configured strictly).
- Require a minimum number of approving reviews.
- Require status checks (CI tests, linters) to pass before merge is even allowed.
- Require branches to be up to date with `main` before merging (forces resolving conflicts *before* merge, not after).
- **Restrict force pushes** to the branch entirely — the platform-level guardrail against the [force-push disaster](04_Remotes_Push_Pull_Fetch_Clone.md#force-push--the-command-that-can-destroy-shared-history) described in file 04.

This is how the "Golden Rule" from [file 06](06_Rebase_Cherry_Pick_Reset_Revert.md#golden-rule-never-rewrite-published-pushed-shared-history) gets enforced automatically rather than relying purely on everyone remembering it.

## Code review, done well

A Pull Request is only as useful as the review it gets. Practical habits that make review effective rather than a rubber stamp:

- **Keep PRs small** — a 40-line PR gets a careful review; a 2,000-line PR gets a skim and an approve. Break large features into a sequence of smaller, reviewable PRs where possible.
- **Write a real PR description** — what changed, why, and how to test it; don't make reviewers reverse-engineer intent from a diff alone.
- **Review the diff, not the whole file** — focus comments on what actually changed; flag pre-existing issues separately rather than scope-creeping the review.
- **Distinguish blocking comments from suggestions** — "this will break in production" vs. "consider renaming this" are very different levels of urgency; say which one you mean.

## `CODEOWNERS`: automatic review routing

```
# .github/CODEOWNERS
/infra/           @platform-team
/src/payments/     @asha-verma @ravi-kumar
*.sql              @data-team
```

Any Pull Request touching a matched path automatically requests review from the listed people/teams — and, combined with branch protection's "require CODEOWNERS review," can *block* a merge until the right domain expert has actually looked at it. This is exactly the technical enforcement mechanism behind [data mesh's](../../02_Databases/Data_Warehousing/03_Data_Mesh.md) "domain ownership" principle, applied to code review.

---

## Pro corner

### Choosing a strategy for a real team

The honest, senior-level answer: **start with GitHub Flow** unless you have a specific, concrete reason not to. Git Flow's complexity earns its keep only when you genuinely maintain multiple released versions in parallel (e.g. a mobile app supporting `v2.x` and `v3.x` simultaneously in the wild) — most teams that adopt Git Flow "because it's the proper way" pay its overhead without ever needing its actual benefit. Trunk-based development is the highest-velocity option but requires investment in feature flags and strong CI *before* it's safe to adopt, not after.

### Feature flags — the technology that makes trunk-based development possible

```python
if feature_flags.is_enabled("new_checkout_flow", user):
    return new_checkout(request)
return legacy_checkout(request)
```

Unfinished or risky code merges to `main` (and deploys to production) constantly, but stays **inactive** behind a runtime toggle until it's ready — decoupling "merged" from "live" entirely. This is the mechanism that lets trunk-based teams avoid long-lived branches without ever shipping half-finished features to real users.

### Merge queues

At high PR volume, two PRs can each pass CI individually but **break when combined** (both independently valid, but incompatible together). A **merge queue** (GitHub's built-in feature, or tools like Bors historically) serializes merges — each PR is tested *against the current state of `main` plus everything ahead of it in the queue*, not just against `main` alone — catching this class of bug before it ever lands.

### Field-tested gotchas

- **A branching strategy nobody actually follows is worse than none** — if "everyone just pushes to `main` directly" despite a documented Git Flow policy, the documentation is actively misleading; enforce via branch protection, don't rely on discipline alone.
- **Long-lived branches under any strategy rot** — the strategy's name doesn't matter as much as the *lifespan* discipline; a "GitHub Flow" feature branch left open for three weeks has all of Git Flow's merge-conflict pain with none of its structure.
- **Squash-merging every PR into a trunk-based or GitHub Flow setup, combined with feature flags**, is the combination most modern high-velocity teams actually converge on in practice — a clean, linear `main` history, continuous deployment, and safety via flags rather than branch isolation.

## Checkpoint

1. Compare GitHub Flow, Git Flow, and trunk-based development on branch lifespan and typical use case.
2. What does a branch protection rule enforce that a team's documented policy alone cannot?
3. Explain how a `CODEOWNERS` file changes what happens when a PR touches `/infra/`.
4. What problem do feature flags solve for trunk-based development specifically?

Next: the habits that make Git production-ready, not just functional → [09 — Production Best Practices & CI/CD](09_Production_Best_Practices_and_CICD.md)

---

## Further Learning — Docs & Videos

**Documentation**
- Git branching workflows (Atlassian): https://www.atlassian.com/git/tutorials/comparing-workflows
- Gitflow workflow: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
- Trunk-based development: https://trunkbaseddevelopment.com/

**Videos**
- Git branching strategies (Gitflow, trunk-based): https://www.youtube.com/results?search_query=git+branching+strategies+gitflow+trunk+based
