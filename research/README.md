# Research record

How the evidence in this folder was produced, and what affects how far to trust it.

## Files

| File | What it is | Mutability |
|---|---|---|
| `00-verification-log.md` | Root spot-checks of worker citations, corrections, derived observations | Append as checks happen |
| `00-worker-briefs.md` | Exact prompts given to each worker, including follow-ups | Frozen |
| `R0-action-space-layers.md` | Action-space ladder, real stacks, trusted events, code-as-action, options framing | Frozen |
| `R1-state-abstraction.md` | Site-graph prior art, state identity, hidden state, exploration safety, staleness | Frozen |
| `R2-graph-as-memory.md` | Memory results, macro replay, graph tools, context budget, verification; flat-memory addendum | Frozen |
| `R3-uncertainty-perplexity.md` | UQ calibration, agent UQ, length confound, curiosity and noisy TV, logprob instrumentation | Frozen |
| `R4-benchmarks.md` | Benchmark verification, fit ranking, harness, known problems, CI and power tables | Frozen |
| `R5-experimental-design.md` | Confound audit, arms, amortization accounting, statistics, reproducibility | Frozen |

Dossiers quote lines from `docs/01-foundations.md` (v0.1), which is why that file is frozen too.
Distilled, maintained knowledge lives in `knowledge/`.

## Method (2026-09-12)

1. **Foundations first.** The root session (Claude Opus 5) wrote `docs/01-foundations.md` from
   memory and marked uncertain claims `[verify]`.
2. **Six parallel research workers** (Claude Sonnet 5), one per thread R0–R5, each told to:
   - verify, correct, and deepen the foundations doc, not agree with it
   - use live web search and fetch
   - **never fabricate a citation** (retrieved URL, or `[could not verify]` plus what was searched)
   - include `## Corrections to docs/01-foundations.md`, `## Design implications`, and `## Open questions`
   - stay clean-room: public sources only
3. **Root verification.** The root session re-fetched the claims that would change the design if
   wrong, and recomputed the statistics. Results are in `00-verification-log.md`.
4. **Synthesis.** Findings went into `docs/02-design-v0.2.md` and then into `knowledge/`.

## Incidents that affect trust

- **API usage limit mid-run.** A session limit killed R0, R4, R5, and R2's follow-up task.
  - **R0 and R5** had already written complete files; every required section was present.
  - **R4** had written nothing. It was resumed with its context intact and finished.
  - **R2's addendum** (flat-memory baseline question) was resumed and appended.
  - R0 had spawned three sub-workers of its own; all were killed and not resumed. R0 finished directly.
- **Shared search budget exhausted.** R0 and R5 report the WebSearch budget (apparently shared across
  workers) ran out mid-task. Later lookups used direct fetches and arXiv/Semantic Scholar APIs. Some
  planned queries never ran; they're listed in the dossiers' open questions.
- **Summarizer fabrication caught (R4).** A page-summarizer returned invented LLM-judge agreement
  percentages for AgentRewardBench. R4 caught it by reading the PDF table directly. Lesson: numbers
  from any automated summary are suspect until traced to a quoted table or sentence.
- **Root found two worker errors:**
  - **R5 arithmetic:** the structure-over-flat benefit is 4.9pp, not 9.1pp.
  - **R3 vLLM characterization:** the bug is a crash, not silent missing logprobs.
- **Possible injection flag (R2).** During its follow-up, R2 reported a fetched result containing a
  block claiming the user's account had changed, and ignored it. The operator had in fact switched
  accounts via `/login` during the session, so this was most likely harness context surfacing, not
  a page injection. No effect on the research either way.
- **R2 WILBUR extraction discrepancy.** Two fetches of the same ablation table differed on
  intermediate rows. Root's fetch confirmed the granular version (34.4 / 40.6 / 48.4 / 49.9 / 52.6).

## Trust summary

- Treat **✓ root** items as verified.
- Treat worker-only citations as likely real but unchecked. Citation-level status is in
  `bibliography/references.md`.
- Treat anything marked `[could not verify]` or `[unverified]` as absent.
