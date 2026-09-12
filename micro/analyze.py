#!/usr/bin/env python3
"""Aggregate arm results across seeds + verbalized-confidence AUROC (step & episode level).

Seeds are repeated measures: paired stats are computed per (task, seed) pair,
pooled across seeds. McNemar exact (binomial) on the primary contrast graph vs flat.
"""
import json, math, sys
from pathlib import Path
from glob import glob

HERE = Path(__file__).parent

def auroc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]; neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg: return None
    vals = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    rk = [0.0] * len(vals); v = [x[0] for x in vals]; i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[j+1] == v[i]: j += 1
        for k in range(i, j+1): rk[k] = (i+j)/2 + 1
        i = j+1
    n1, n0 = len(pos), len(neg)
    sp = sum(rk[k] for k, (_, l) in enumerate(vals) if l == 1)
    return (sp - n1*(n1+1)/2) / (n1*n0)

def wilson(p, n, z=1.96):
    if n == 0: return (0, 0, 0)
    c = (p + z*z/(2*n)) / (1 + z*z/n)
    h = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return (p, c - h, c + h)

def mcnemar_exact(b01, b10):
    """Two-sided exact binomial test on discordant pairs."""
    n = b01 + b10
    if n == 0: return 1.0
    k = min(b01, b10)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) * (0.5 ** n) * 2
    return min(1.0, p)

def load_all(arm):
    docs = []
    for f in sorted(glob(str(HERE / f"results_{arm}_s*.json"))):
        docs.append(json.loads(Path(f).read_text()))
    return docs

def main():
    arms = ["none", "flat", "graph"]
    docs = {a: load_all(a) for a in arms}
    for a in arms:
        if not docs[a]:
            print(f"no seed files for {a} (expected results_{a}_s*.json)"); sys.exit(1)

    print("=== Arm comparison (pooled across seeds; seeds are repeated measures) ===")
    print(f"{'arm':6} {'succ':>7} {'rate':>6} {'95% CI':>16} {'steps':>6} {'invalid':>8} {'mem chars':>10} {'seeds':>6}")
    for a in arms:
        ds = docs[a]
        n = sum(d["n"] for d in ds); s = sum(d["successes"] for d in ds)
        p, lo, hi = wilson(s / n, n)
        steps = sum(d["mean_steps"] * d["n"] for d in ds) / n
        inv = sum(d["invalid_actions"] for d in ds)
        mem = max(d["memory_chars"] for d in ds)
        print(f"{a:6} {s:>4}/{n:<3} {s/n:>6.1%} [{lo:>5.1%}, {hi:>5.1%}] {steps:>6.1f} {inv:>8} {mem:>10} {len(ds):>6}")

    # paired per (task, seed): primary contrast graph vs flat
    def keymap(a):
        m = {}
        for d in docs[a]:
            for r in d["results"]:
                m[(r["id"], d["seed"])] = r["success"]
        return m
    km = {a: keymap(a) for a in arms}
    pairs = sorted(set(km["flat"]) & set(km["graph"]))
    b01 = sum(1 for k in pairs if km["flat"][k] and not km["graph"][k])
    b10 = sum(1 for k in pairs if km["graph"][k] and not km["flat"][k])
    psi = (b01 + b10) / max(1, len(pairs))
    pval = mcnemar_exact(b01, b10)
    print(f"\n=== Primary contrast: graph vs flat (paired, n={len(pairs)} task-seed pairs) ===")
    print(f"flat=1,graph=0: {b01} | graph=1,flat=0: {b10} | discordant rate psi = {psi:.3f}")
    print(f"exact McNemar p = {pval:.4f}")
    # none vs flat for reference
    pairs_nf = sorted(set(km["none"]) & set(km["flat"]))
    b01n = sum(1 for k in pairs_nf if km["none"][k] and not km["flat"][k])
    b10n = sum(1 for k in pairs_nf if km["flat"][k] and not km["none"][k])
    print(f"reference none vs flat: none=1,flat=0: {b01n} | flat=1,none=0: {b10n} | "
          f"psi = {(b01n+b10n)/max(1,len(pairs_nf)):.3f} | p = {mcnemar_exact(b01n, b10n):.4f}")

    # per-seed rates to see seed variance
    print("\n=== Per-seed success rates ===")
    for a in arms:
        rates = [f"s{d['seed']}:{d['successes']}/{d['n']}" for d in docs[a]]
        print(f"{a:6} {' '.join(rates)}")

    # AUROC pooled across arms and seeds
    step_scores, step_labels = [], []
    ep_scores, ep_labels = [], []
    bucket = {q: ([], []) for q in range(4)}
    for a in arms:
        for d in docs[a]:
            for r in d["results"]:
                n = len(r["confs"])
                for k, c in enumerate(r["confs"]):
                    if c is None: continue
                    step_scores.append(c); step_labels.append(0 if r["success"] else 1)
                    q = min(3, int(4 * k / max(1, n)))
                    bucket[q][0].append(c); bucket[q][1].append(0 if r["success"] else 1)
                if r["confs"]:
                    ep_scores.append(r["confs"][-1]); ep_labels.append(0 if r["success"] else 1)

    print("\n=== Verbalized-confidence AUROC (predicting FAILURE) ===")
    s = auroc(step_scores, step_labels)
    print(f"step-level: {s if s is None else round(s, 3)}  (n={len(step_scores)})")
    e = auroc(ep_scores, ep_labels)
    print(f"episode-level (final conf): {e if e is None else round(e, 3)}  (n={len(ep_scores)})")
    for q in range(4):
        sc, lb = bucket[q]
        v = auroc(sc, lb)
        print(f"  Q{q+1} ({25*q}-{25*(q+1)}%): {v if v is None else round(v, 3)}  (n={len(sc)})")

    # per-task failure table (which tasks fail everywhere = harness artifacts)
    print("\n=== Per-task success count across arms+seeds (out of 9) ===")
    tally = {}
    for a in arms:
        for d in docs[a]:
            for r in d["results"]:
                tally.setdefault(r["id"], [0, 0])
                tally[r["id"]][0] += r["success"]; tally[r["id"]][1] += 1
    hard = sorted(tally.items(), key=lambda kv: kv[1][0])
    for tid, (s, n) in hard[:12]:
        print(f"  {tid:24} {s}/{n}")

if __name__ == "__main__":
    main()