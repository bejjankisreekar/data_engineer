# HR / Behavioral Interview — Data Engineer

## Overview
The final round tests communication, ownership, teamwork, and fit. Use the **STAR** method (Situation, Task, Action, Result) and keep answers concrete with metrics. Prepare 4–5 real project stories you can flex to any question.

---

## Most-asked HR/behavioral questions

| # | Question | Prep angle |
|---|---|---|
| 1 | Tell me about yourself. | 60–90s: role, core Azure stack, biggest impact, what you're looking for |
| 2 | Walk me through a project you're proud of. | STAR + architecture + your specific contribution + metrics |
| 3 | Describe a challenging bug/incident you solved. | Diagnosis approach, fix, prevention |
| 4 | A time you optimized a slow pipeline. | 8hr→2hr type story with numbers |
| 5 | How do you handle conflicting priorities/deadlines? | Prioritization, stakeholder communication |
| 6 | A disagreement with a teammate/lead. | Respectful, data-driven resolution |
| 7 | A time you failed / a mistake. | Ownership + what you learned + prevention |
| 8 | How do you ensure data quality? | Validation, tests, monitoring, ownership |
| 9 | Why do you want to leave / join us? | Growth-focused, positive, specific to the role |
| 10 | Where do you see yourself in 5 years? | Growth into senior/architect, deepening cloud/data skills |
| 11 | How do you handle production incidents? | Calm process: triage, communicate, fix, RCA |
| 12 | Strengths & weaknesses. | Genuine weakness + active improvement |

---

## STAR template (use for every story)
- **Situation:** brief context (project, scale, your role).
- **Task:** what needed to happen / the problem.
- **Action:** what **you specifically** did (technical detail, decisions).
- **Result:** the outcome with **metrics** (runtime cut X%, cost down Y%, SLA met).

**Example (pipeline optimization):**
> *S:* Nightly pipeline for 300 tables was taking 8 hours, breaching the 6 AM SLA. *T:* I owned bringing it under 2 hours. *A:* Profiled with Spark UI, found data skew and full loads; switched to incremental watermark loads, parallelized the ADF ForEach, added ZORDER and broadcast joins, right-sized the job cluster. *R:* Runtime dropped to 1h40m, SLA consistently met, and cluster cost fell ~30% by moving to job clusters.

---

## Tips
- Prepare **4–5 flexible stories** (an optimization win, an incident, a conflict, a failure/learning, a proud project).
- Always include **metrics** — seniors quantify impact.
- Show **ownership** ("I drove...", "I decided...") not just "the team".
- Be **honest** about weaknesses/failures + what you changed.
- Research the company; tailor "why us".
- Keep it **positive** about past employers.

## Common Mistakes
- Vague, no-metrics answers.
- Blaming others in conflict/failure stories.
- Rambling (structure with STAR).
- Negative about current/past employer.
- No questions for the interviewer (always ask 2–3).

## Good questions to ask them
- What does the data platform/stack look like today, and where is it heading?
- How is the team structured; what would my first 90 days focus on?
- How do you handle on-call / production incidents?
- What does success in this role look like in 6–12 months?

## Related Topics
Scenario Based Questions, Cheat Sheets
