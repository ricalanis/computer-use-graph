# Micro-validation run (2026-09-12)

Ten-minute minimal experiment validating the harness mechanics of the main hypothesis
(`../docs/02-design-v0.2.md`), on a synthetic config-admin site instead of WebArena.

## Setup

- **Agent:** Ollama Cloud via `oll` (deepseek-v4-flash), one call per step.
- **Site:** 25 pages, 67 actions, 3-level nav, decoy labels ("Email digest" vs "Email
  notifications", "Install analytics" vs "Install beta analytics"), decoy effects that validators
  ignore. Pages show current setting values (state visibility — added after it proved to be the
  binding constraint).
- **Tasks:** 24 = 18 single-effect + 6 compositional (two effects).
- **Arms:** `none` / `flat` (recency-ordered exploration transcript, char-matched) / `graph`
  (typed page map with affordance→destination edges). Both memory arms built from the **same
  task-agnostic random-walk exploration** (the crawl/eval firewall, in miniature).
- **Seeds:** 3 exploration seeds (7, 11, 23) × 3 arms × 24 tasks = 216 paired episodes.
- **Budget:** max 12 steps/episode; memory char-matched between arms (~1.2–1.7k chars).

## Results (n=72 task-seed pairs per arm)

| arm | success | 95% Wilson CI | mean steps |
|---|---|---|---|
| none | 59.7% | [48.2%, 70.3%] | 7.3 |
| flat | 70.8% | [59.5%, 80.1%] | 6.5 |
| graph | 73.6% | [62.4%, 82.4%] | 6.4 |

- **Primary contrast graph vs flat:** +2.8pp, ψ=0.111, exact McNemar p=0.73 (not significant).
- **Memory vs none:** flat +11.1pp, ψ=0.194, p=0.057.
- **Verbalized-confidence AUROC vs failure:** 0.46–0.51 across all progress quartiles (n=1,459
  steps) — uninformative, consistent with *Last Step Matters* (F4).

## What it validated

1. **Mechanism end-to-end:** task-agnostic exploration → same-data graph/flat memories,
   char-matched → controlled contrast → programmatic validators → paired McNemar + Wilson +
   per-quartile AUROC. The analysis code transfers unchanged to a real benchmark.
2. **F2 reproduced in miniature:** flat memory takes ~79% of the total memory gain (11.1 of
   14.0pp) — the primary contrast is small, as the literature predicts.
3. **Power math is live:** at ψ=0.111 the observed +2.8pp needs ~1,000+ pairs; the design's
   McNemar tables (knowledge/03, knowledge/07) are confirmed empirically.
4. **State visibility was the binding constraint**, not memory: compositional tasks went 0/9 →
   partially solvable in all arms once pages displayed current setting values.

## Known limitations

- n=72/arm is a smoke test, not evidence (±11pp CI half-widths).
- One model, one site family, no distractor-graph control (arm 5), no oracle (arm 7).
- Verbalized confidence only — the D4 action-entropy scorer is not yet instrumented.

## Files

- `micro_exp.py` — site, exploration, memory builders, agent loop, validators.
- `analyze.py` — pooled stats: Wilson CIs, exact McNemar, AUROC by progress quartile.
- `results_{arm}_s{seed}.json` — per-run episodes with full trajectories and per-step confidence.
- `memory_{graph,flat}_s{seed}.txt` — the exact memory blocks injected per arm/seed.
- `log_*.txt` — one-line run summaries.