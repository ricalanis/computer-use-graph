#!/usr/bin/env python3
"""Regenerate bibliography/references.md from the research dossiers.

Extracts every link and arXiv id from research/R0-R5, attaches a curated title where the dossier
link text isn't one, groups by the first dossier that cites it, and stamps verification status.
Edit TITLES / ROOT_VERIFIED / NOTES / EXTRA below; never hand-edit references.md.
"""
import collections, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPIC = {"R0": "Action space & harnesses", "R1": "State abstraction, site graphs & safety",
         "R2": "Memory, replay & retrieval", "R3": "Uncertainty & exploration",
         "R4": "Benchmarks & evaluation", "R5": "Experimental methodology"}

# Root session re-fetched these (see research/00-verification-log.md).
ROOT_VERIFIED = {"arXiv:2608.29685", "arXiv:2509.25438", "arXiv:2502.11371", "arXiv:2507.14293",
                 "arXiv:2603.23610", "arXiv:2404.05902", "arXiv:2403.07718", "arXiv:2407.05291",
                 "arXiv:2504.08942", "https://github.com/ServiceNow/BrowserGym",
                 "https://github.com/ServiceNow/WorkArena",
                 "https://github.com/vllm-project/vllm/issues/3251",
                 "https://github.com/vllm-project/vllm/issues/16838",
                 "https://github.com/vllm-project/vllm/issues/8268"}
PARTIAL = {"arXiv:2504.08942": "direction of validator bias confirmed; Table 1 values worker-only",
           "arXiv:2403.07718": "task counts confirmed",
           "https://github.com/ServiceNow/BrowserGym": "ACTION_SUBSETS confirmed"}

TITLES = {
 "2307.13854": "WebArena: A Realistic Web Environment for Building Autonomous Agents",
 "2404.07972": "OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments",
 "2405.14573": "AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents",
 "2401.13919": "WebVoyager: Building an End-to-End Web Agent with Large Multimodal Models",
 "2401.10935": "SeeClick: Harnessing GUI Grounding for Advanced Visual GUI Agents (introduces ScreenSpot)",
 "2504.07981": "ScreenSpot-Pro: GUI Grounding for Professional High-Resolution Computer Use",
 "2402.01030": "CodeAct: Executable Code Actions Elicit Better LLM Agents",
 "1802.08802": "Reinforcement Learning on Web Interfaces Using Workflow-Guided Exploration",
 "2409.07429": "Agent Workflow Memory",
 "2410.02907": "NNetNav: Unsupervised Learning of Browser Agents Through Environment Interaction in the Wild",
 "2410.06703": "ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents",
 "2504.18575": "WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks",
 "2409.19669": "(cited by R0 as NNetNav-family; identity unconfirmed — NNetNav is 2410.02907)",
 "2404.05902": "WILBUR: Adaptive In-Context Learning for Robust and Accurate Web Agents",
 "2306.07863": "Synapse: Trajectory-as-Exemplar Prompting with Memory for Computer Control",
 "2308.10144": "ExpeL: Learning from experience (insights vs trajectory retrieval)",
 "2510.01524": "WALT: Web Agents that Learn Tools",
 "2510.15863": "PolySkill: polymorphic cross-site skills for web agents",
 "2305.16291": "Voyager: An Open-Ended Embodied Agent with Large Language Models",
 "2504.06943": "Case-based reasoning for LLM agents (review)",
 "2504.19413": "Mem0: scalable long-term memory for AI agents",
 "2510.23883": "Long-horizon WebArena consistency study (GPT-4 consistent on 4/61 templates)",
 "2606.17929": "PreAct: cached action sequences with fallback for computer-use agents",
 "2604.09718": "Agentic Compilation: compiled web trajectories with lazy replanning",
 "2604.14872": "SkillDroid: Compile Once, Reuse Forever (speculative replay)",
 "2404.16130": "From Local to Global: A GraphRAG Approach to Query-Focused Summarization",
 "2502.11371": "RAG vs. GraphRAG: A Systematic Evaluation and Key Insights",
 "2604.01610": "GraphWalk: tool-based graph navigation benchmark for LLMs",
 "2607.06273": "ToolMaze / AgentTether: tool-graph traps and trace-graph repair",
 "2307.03172": "Lost in the Middle: How Language Models Use Long Contexts",
 "2503.18492": "VeriSafe Agent: logic-based action verification for mobile GUI agents",
 "2606.15673": "Where Did It Go Wrong? Process-level evaluation via semantic state tracking",
 "2604.21375": "VLAA-GUI: completion gate and independent verifier",
 "2506.03533": "Go-Browse: Training Web Agents with Structured Exploration",
 "2605.09195": "Geometry of Forgetting (OOD comparison of truthfulness probes)",
 "2604.17112": "Complementing Self-Consistency with Cross-Model Disagreement",
 "2306.10193": "Conformal Language Modeling",
 "2305.18404": "Conformal Prediction with Large Language Models for Multi-Choice QA",
 "2403.01216": "API Is Enough: Conformal Prediction for LLMs Without Logit Access",
 "2608.29685": "Last Step Matters: Early Uncertainty Cannot Predict Failure in Long-Horizon Agents",
 "2602.05073": "Uncertainty Quantification in LLM Agents: Foundations, Emerging Challenges, and Opportunities",
 "2602.11409": "TRACER: Trajectory Risk Aggregation for Critical Episodes",
 "2601.15703": "Agentic Uncertainty Quantification",
 "2606.19559": "Uncertainty Decomposition for Clarification Seeking in LLM Agents",
 "2306.06070": "Mind2Web: Towards a Generalist Agent for the Web",
 "2402.05930": "WebLINX: Real-World Website Navigation with Multi-Turn Dialogue",
 "2307.10088": "Android in the Wild (AITW)",
 "2406.08451": "GUI-Odyssey: cross-app GUI navigation dataset",
 "2602.13559": "OpAgent (WebArena 71.6% claim)",
 "2510.19949": "Surfer 2 (WebArena label corrections; 5-judge ensemble)",
 "2401.13649": "VisualWebArena",
 "2403.07718": "WorkArena: How Capable Are Web Agents at Solving Common Knowledge Work Tasks?",
 "2407.05291": "WorkArena++: Towards Compositional Planning and Reasoning-based Common Knowledge Work Tasks",
 "2412.14161": "TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks",
 "2207.01206": "WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents",
 "2504.01382": "An Illusion of Progress? Assessing the Current State of Web Agents (Online-Mind2Web)",
 "2406.12373": "WebCanvas / Mind2Web-Live",
 "2311.12983": "GAIA: A Benchmark for General AI Assistants",
 "2409.08264": "Windows Agent Arena",
 "2504.08942": "AgentRewardBench: Evaluating Automatic Evaluations of Web Agent Trajectories",
 "2406.13352": "AgentDojo: prompt injection attacks and defenses for LLM agents",
 "2412.05467": "The BrowserGym Ecosystem for Web Agent Research",
 "2603.23610": "Environment Maps: Structured Environmental Representations for Long-Horizon Agents",
 "2604.09666": "RAGSearch: Do We Still Need GraphRAG?",
 "2408.03314": "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters",
 "2605.00428": "A Practical Playbook for Defensible Results (BH-FDR recommendation)",
 "2605.21404": "Reproducibility audit of LLM-agent benchmark papers (five-field disclosure schema)",
 "2606.10677": "Infini Memory",
 "2509.25438": "Beyond Noisy-TVs: Noise-Robust Exploration Via Learning Progress Monitoring",
 "2507.14293": "WebGuard: Building a Generalizable Guardrail for Web Agents",
 "1810.12894": "Exploration by Random Network Distillation (RND)",
 "1605.09674": "VIME: Variational Information Maximizing Exploration",
}
URL_TITLES = {  # non-arXiv sources whose dossier link text is not a usable title
 "https://github.com/crawljax/crawljax": "Crawljax (source code)",
 "https://github.com/EmergenceAI/Agent-E": "Agent-E (source code)",
 "https://github.com/kohjingyu/search-agents": "Tree Search for Language Model Agents (source code)",
 "https://github.com/microsoft/ExACT": "ExACT: Reflective-MCTS (source code)",
 "https://github.com/segev-shlomov/ST-WebAgentBench": "ST-WebAgentBench (source code)",
 "https://github.com/zorazrw/agent-workflow-memory": "Agent Workflow Memory (source code)",
 "https://github.com/chroma-core/context-rot": "Context Rot replication kit (Chroma)",
 "https://github.com/pig-dot-dev/muscle-mem": "Muscle-Mem: trajectory cache with agent fallback (open-source SDK)",
 "https://link.springer.com/chapter/10.1007/978-3-032-33865-5_21": "Case-based memory for GUI agents (Springer chapter; identity partially verified by R2)",
 "https://proceedings.mlr.press/v70/pathak17a/pathak17a.pdf": "Curiosity-driven Exploration by Self-supervised Prediction (ICM), ICML 2017",
}
NOTES = {"arXiv:2504.19413": "conversational QA benchmarks, not GUI evidence",
         "arXiv:2409.19669": "do not cite",
         "https://atlan.com/know/vector-database-vs-knowledge-graph-agent-memory/": "secondary / blog",
         "https://hindsight.vectorize.io/blog/2026/08/24/knowledge-graphs-vs-vector-search-agent-memory": "secondary / blog",
         "https://agenthandbook.chainofthought.xyz/inside-the-loop": "secondary / blog",
         "https://www.uipath.com/blog/product-and-updates/technical-tuesday-how-healing-agent-solves-ui-automation-challenges": "vendor claim",
         "https://www.techmahindra.com/insights/whitepapers/afterlife-of-rpa/": "vendor case study",
         "https://dev.to/custodiaadmin/visual-verification-for-ai-agents-how-to-confirm-web-actions-actually-worked-30n4": "secondary / blog",
         "https://community.openai.com/t/why-doesnt-the-responses-api-support-logprobs/1148097": "community report",
         "https://dl.acm.org/doi/10.1145/3736162": "full text 403; via citing survey"}
GENERIC = {"code", "github", "repo", "pdf", "icml pdf", "springer chapter", "github replication kit"}
EXTRA = [  # sources cited without a parseable link in the dossiers, or root-only
 ("https://github.com/vllm-project/vllm/issues/8268", "vLLM #8268: AssertionError with automatic prefix caching + prompt_logprobs (closed stale)", "R3"),
 ("https://openreview.net/pdf?id=CSIo4D7xBG", "WebArena Verified (audited WebArena; 258-task Hard subset)", "R5"),
 ("https://pith.science/paper/2608.11323", "Deployment Decision Reliability (generalizability theory on agent leaderboards)", "R5"),
 ("https://doi.org/10.1016/S0004-3702(99)00052-1", "Sutton, Precup & Singh (1999). Between MDPs and Semi-MDPs: A Framework for Temporal Abstraction in RL", "R0"),
]

link = re.compile(r'\[([^\]]{2,300})\]\((https?://[^\s)]+(?:\([^\s)]*\)[^\s)]*)?)\)')
bare = re.compile(r'(?<![(\[])https?://[^\s)>\]`|,]+')
arx = re.compile(r'arxiv\.org/(?:abs|pdf|html)/(\d{4}\.\d{4,5})')
refs = collections.OrderedDict()

def key_for(u):
    a = arx.search(u)
    return ("arXiv:" + a.group(1)) if a else u.split('#')[0].rstrip('.')

def add(k, url, label, tag):
    r = refs.setdefault(k, {"url": url, "labels": [], "in": []})
    if label: r["labels"].append(" ".join(label.split()))
    if tag not in r["in"]: r["in"].append(tag)

for f in sorted(glob.glob(os.path.join(ROOT, "research", "R[0-5]-*.md"))):
    tag = os.path.basename(f)[:2]
    txt = open(f).read()
    for m in link.finditer(txt):
        u = m.group(2).rstrip('.')
        if u.startswith("https://doi.org/10.1016/S0004-3702("): continue
        add(key_for(u), u, m.group(1), tag)
    for m in bare.finditer(txt):
        u = m.group(0).rstrip('.').rstrip("'\"")
        if "doi.org/10.1016/S0004-3702" in u or u.endswith("/"+"raw.githubusercontent.com"): continue
        if "raw.githubusercontent.com" in u: continue
        add(key_for(u), u, None, tag)
    for m in re.finditer(r'arXiv[: ](\d{4}\.\d{4,5})', txt):
        add("arXiv:" + m.group(1), "https://arxiv.org/abs/" + m.group(1), None, tag)
for u, t, tag in EXTRA:
    add(key_for(u), u, t, tag)

def title(k, r):
    if k.startswith("arXiv:") and k[6:] in TITLES: return TITLES[k[6:]]
    if k in URL_TITLES: return URL_TITLES[k]
    good = [l for l in r["labels"] if l.lower() not in GENERIC and not l.lower().startswith("arxiv")]
    return max(good, key=len) if good else k

def status(k):
    if k in ROOT_VERIFIED:
        return "✓ root" + (f" ({PARTIAL[k]})" if k in PARTIAL else "")
    return "worker"

groups = collections.OrderedDict((t, []) for t in TOPIC)
for k, r in refs.items():
    groups[r["in"][0]].append((k, r))

out = ["# References", "",
       "Generated by `bibliography/build_references.py` from `research/R0`–`R5`. **Do not hand-edit**; change the script.",
       "", "**Status:** `✓ root` = re-fetched by the root session (see `research/00-verification-log.md`). "
       "`worker` = retrieved by a research worker only; re-verify before external citation. "
       "Grouped by the first dossier that cites the source.", "",
       f"Total: {len(refs)} sources · {sum(k.startswith('arXiv:') for k in refs)} arXiv · "
       f"{sum(k in ROOT_VERIFIED for k in refs)} root-verified.", ""]
for tag, items in groups.items():
    if not items: continue
    out += [f"## {TOPIC[tag]} ({tag})", "", "| Source | Link | Status | Cited in | Note |", "|---|---|---|---|---|"]
    for k, r in sorted(items, key=lambda kr: title(*kr).lower()):
        t = title(k, r).replace("|", "\\|")
        shown = k if k.startswith("arXiv:") else r["url"]
        out.append(f"| {t} | [{shown if len(shown) < 60 else shown[:57] + '…'}]({r['url']}) | {status(k)} | {', '.join(r['in'])} | {NOTES.get(k, '')} |")
    out.append("")
open(os.path.join(ROOT, "bibliography", "references.md"), "w").write("\n".join(out))
print(f"wrote references.md: {len(refs)} sources, {sum(k in ROOT_VERIFIED for k in refs)} root-verified")
