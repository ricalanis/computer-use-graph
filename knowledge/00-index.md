# Knowledge base — index

Distilled, topic-organized knowledge for the **computer-use-graph** project. This is the layer to
read and maintain. The raw research dossiers (`research/R0`–`R5`) are frozen evidence; the design
docs (`docs/`) are versioned plans. When a finding changes, update the note here and, if it
changes a plan, add an entry to the decisions log.

**Snapshot:** 2026-09-12. Phase: design v0.2 complete, no code yet. Next step: Phase 0a kill tests.

## Provenance legend (used in every note)

| Mark | Meaning |
|---|---|
| **✓** | Root session re-fetched the primary source or recomputed the number. See `research/00-verification-log.md`. |
| *(unmarked)* | Retrieved by a research worker. The source exists per the worker, but root didn't re-check it. Re-verify before citing externally. |
| **[unverified]** | Searched for and not confirmed. Don't cite. |

## Notes

| # | Note | What it answers |
|---|---|---|
| 01 | [Computer-use taxonomy](01-computer-use-taxonomy.md) | What the computer-use problem decomposes into: observation, action, control loop, sub-problems, task archetypes |
| 02 | [Action-space ladder](02-action-space-ladder.md) | Mouse/keyboard vs elements vs DOM vs API: the 8 rungs, what real stacks do, and why this project uses layer 2 |
| 03 | [Benchmarks and evaluation](03-benchmarks-and-evaluation.md) | Which benchmarks exist, what's broken about them, validators vs judges, CI and power tables |
| 04 | [State abstraction and site graphs](04-state-abstraction-and-site-graphs.md) | Prior art on graphs and maps for agents, the "same state" problem, hidden state, exploration safety, staleness |
| 05 | [Memory, replay, and retrieval](05-memory-replay-and-retrieval.md) | Does agent memory help, flat vs structured, macro replay brittleness, graph tools, context budgets |
| 06 | [Uncertainty and exploration](06-uncertainty-and-exploration.md) | Which uncertainty signals work, agent-specific failure, length confound, curiosity, noisy TV, logprob instrumentation |
| 07 | [Experimental methodology](07-experimental-methodology.md) | Confounds, arm design, amortized cost accounting, statistics, sample size, reproducibility |
| 08 | [Key findings](08-key-findings.md) | The findings that changed the design, each with evidence strength and consequence |
| 09 | [Decisions log](09-decisions-log.md) | Every design decision: status, rationale, sources |
| 10 | [Open questions](10-open-questions.md) | Consolidated and prioritized, with which phase resolves each |
| 11 | [Glossary](11-glossary.md) | Terms used across the project |

## Reading paths

- **New to the project:** 08 → 02 → `docs/02-design-v0.2.md` → 09.
- **About to implement Phase 0/1:** 09 → 06 (instrumentation) → 04 (schema, safety) → 03 (harness) → 10.
- **Reviewing the method:** 07 → 03 → 08 → `research/00-verification-log.md`.
- **Checking a citation:** `bibliography/references.md` (status column) → the dossier named there.

## Elsewhere in the repo

- `docs/02-design-v0.2.md` — current design. `docs/01-foundations.md` — v0.1, frozen (dossiers quote its lines).
- `research/README.md` — how the research was produced, including incidents that affect trust.
- `research/00-verification-log.md` — root spot-checks and the corrections that came out of them.
- `research/00-worker-briefs.md` — exact prompts given to the research workers.
- `bibliography/` — every cited source with verification status. Regenerate with `python3 bibliography/build_references.py`.
