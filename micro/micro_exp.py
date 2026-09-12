#!/usr/bin/env python3
"""Micro-validation of the computer-use-graph hypothesis (10-minute version).

Synthetic config-admin site. Agent = Ollama Cloud (deepseek-v4-flash).
Arms: none | flat (raw exploration transcript, char-matched to graph) | graph (site map).
Same exploration data feeds both memory arms. Verbalized confidence logged per step
for a mini step/episode AUROC check (design v0.2 §6.2 signal 2, §6.3).
"""
import json, random, re, subprocess, sys, time
from pathlib import Path

OUT = Path(__file__).parent

# ---------------- synthetic site: pages = {id: {title, body, actions:[(label,target,effect)]}} ----------------
# Hard version: 3-level nav, ambiguous labels, decoy pages/actions that set decoy_* state
# (validators only credit the real effect keys, so wrong-page traps fail honestly).
PAGES = {
    "login": ("Login", "Acme Admin. You are signed out.", [("Sign in", "dashboard", None)]),
    "dashboard": ("Dashboard", "Overview. Sections: account, workspace, system, preferences, billing.",
        [("Account", "account", None), ("Workspace", "workspace", None), ("System", "system", None),
         ("Preferences", "preferences", None), ("Billing", "billing", None)]),
    "account": ("Account", "Your account details.",
        [("Profile", "profile", None), ("Security", "security", None), ("Notifications", "notifications", None),
         ("Email", "email_aliases", None), ("Back to dashboard", "dashboard", None)]),
    "profile": ("Profile", "Your profile settings.",
        [("Edit display name", "profile", "display_name"), ("Edit bio", "profile", "bio"),
         ("Back to account", "account", None)]),
    "security": ("Security", "Account security settings.",
        [("Enable 2FA", "security", "twofa"), ("Change password", "security", "password"),
         ("Sessions", "sessions", None), ("Access logs", "access_logs", None),
         ("Back to account", "account", None)]),
    "sessions": ("Active sessions", "Your active sessions.",
        [("Revoke all sessions", "sessions", "sessions_revoked"),
         ("Revoke current session", "sessions", "decoy_revoke_current"),
         ("Back to security", "security", None)]),
    "access_logs": ("Access logs", "Recent access history.", [("Back to security", "security", None)]),
    "notifications": ("Notifications", "Email notification preferences.",
        [("Email digest", "notifications", "email_digest"),
         ("Email notifications", "notifications", "decoy_email_notif"),
         ("Change notification email", "notifications", "notif_email"),
         ("Push digest", "notifications", "decoy_push_digest"),
         ("Back to account", "account", None)]),
    "email_aliases": ("Email aliases", "Your email aliases and primary address.",
        [("Change primary email", "email_aliases", "decoy_primary_email"),
         ("Add alias", "email_aliases", "decoy_alias"),
         ("Back to account", "account", None)]),
    "workspace": ("Workspace", "Workspace settings.",
        [("Integrations", "integrations", None), ("Apps", "apps", None), ("Members", "members", None),
         ("Back to dashboard", "dashboard", None)]),
    "integrations": ("Integrations", "Connected apps.",
        [("New integration", "integrations", "new_integration"),
         ("Browse directory", "integrations_dir", None),
         ("Back to workspace", "workspace", None)]),
    "integrations_dir": ("Integration directory", "Available integrations: analytics, chat.",
        [("Install analytics", "integrations", "installed_analytics"),
         ("Install chat", "integrations", "installed_chat"),
         ("Install beta analytics", "integrations", "decoy_beta_analytics"),
         ("Back to integrations", "integrations", None)]),
    "apps": ("Apps", "Workspace apps.",
        [("Install app", "apps", "decoy_app"), ("Back to workspace", "workspace", None)]),
    "members": ("Members", "Workspace members.", [("Back to workspace", "workspace", None)]),
    "system": ("System", "System configuration.",
        [("API keys", "api_keys", None), ("Webhooks", "webhooks", None), ("Advanced", "advanced", None),
         ("Back to dashboard", "dashboard", None)]),
    "api_keys": ("API keys", "Manage API keys.", [("Back to system", "system", None)]),
    "webhooks": ("Webhooks", "Outgoing webhooks.", [("Back to system", "system", None)]),
    "advanced": ("Advanced", "Advanced system settings.", [("Back to system", "system", None)]),
    "preferences": ("Preferences", "Personal preferences.",
        [("Appearance", "appearance", None), ("Language", "language", None),
         ("Notification preferences", "prefs_notifications", None),
         ("Back to dashboard", "dashboard", None)]),
    "prefs_notifications": ("Notification preferences", "Summary of your notification choices.",
        [("Email summary", "prefs_notifications", "decoy_email_summary"),
         ("Back to preferences", "preferences", None)]),
    "appearance": ("Appearance", "Theme settings.", [("Back to preferences", "preferences", None)]),
    "language": ("Language", "Language settings.", [("Back to preferences", "preferences", None)]),
    "billing": ("Billing", "Subscription and invoices.",
        [("View invoices", "invoices", None), ("Change plan", "billing", "plan"),
         ("Subscription details", "subscription", None), ("Back to dashboard", "dashboard", None)]),
    "invoices": ("Invoices", "List of past invoices.",
        [("Open invoice list", "invoices", "viewed_invoices"), ("Back to billing", "billing", None)]),
    "subscription": ("Subscription", "Your current subscription.",
        [("Change plan", "subscription", "decoy_plan_change"), ("Back to billing", "billing", None)]),
}
TOGGLES = {"email_digest", "twofa", "sessions_revoked", "installed_analytics", "installed_chat", "viewed_invoices"}

def make_tasks():
    T = []
    # single-effect tasks: 6 text effects x 2 values + 6 toggles = 18
    text_effects = [
        ("display_name", "display name", ["Ada Lovelace", "Grace Hopper"]),
        ("bio", "bio", ["We automate config.", "Reliability team."]),
        ("notif_email", "notification email", ["ops@acme.io", "alerts@acme.io"]),
        ("password", "password", ["N3wPass!", "S3cure#9"]),
        ("new_integration", "new integration", ["deploy-bot", "audit-bot"]),
        ("plan", "subscription plan", ["Enterprise", "Business"]),
    ]
    i = 1
    for eff, noun, vals in text_effects:
        for v in vals:
            T.append((f"s{i:02d}_{eff}", f"Set your {noun} to {v}.", {eff: v})); i += 1
    toggles = [
        ("twofa", "Enable two-factor authentication."),
        ("sessions_revoked", "Revoke all active sessions."),
        ("email_digest", "Turn on the email digest."),
        ("installed_analytics", "Install the analytics integration."),
        ("installed_chat", "Install the chat integration."),
        ("viewed_invoices", "View the invoices page."),
    ]
    for eff, instr in toggles:
        T.append((f"s{i:02d}_{eff}", instr, {eff: True})); i += 1
    # compositional tasks: two effects each = 6
    combos = [
        ("c01_twofa_revoke", "Enable two-factor authentication and revoke all active sessions.",
            {"twofa": True, "sessions_revoked": True}),
        ("c02_digest_email", "Turn on the email digest and set the notification email to ops@acme.io.",
            {"email_digest": True, "notif_email": "ops@acme.io"}),
        ("c03_both_ints", "Install both the chat and the analytics integrations.",
            {"installed_chat": True, "installed_analytics": True}),
        ("c04_plan_inv", "Change the subscription plan to Enterprise and view the invoices page.",
            {"plan": "Enterprise", "viewed_invoices": True}),
        ("c05_name_bio", "Set your display name to Ada Lovelace and your bio to We automate config.",
            {"display_name": "Ada Lovelace", "bio": "We automate config."}),
        ("c06_pass_2fa", "Change your password to N3wPass! and enable two-factor authentication.",
            {"password": "N3wPass!", "twofa": True}),
    ]
    T.extend(combos)
    return T

TASKS = make_tasks()

# ---------------- exploration: task-agnostic random walk (no LLM, no task text) ----------------
def explore(seed=7, n=140):
    rng = random.Random(seed)
    page, log = "login", []
    for _ in range(n):
        acts = PAGES[page][2]
        label, target, effect = rng.choice(acts)
        log.append({"from": page, "action": label, "to": target})
        page = target
    return log

def graph_block(log):
    edges = {}
    seen_pages = set()
    for e in log:
        edges[(e["from"], e["action"])] = e["to"]
        seen_pages.add(e["from"]); seen_pages.add(e["to"])
    by_page = {}
    for (src, label), to in edges.items():
        by_page.setdefault(src, []).append(f"{label}->{to}")
    lines = ["SITE MAP learned from exploring this admin panel (page: [button -> destination]):"]
    for p in sorted(seen_pages):
        lines.append(f"{p}: [{', '.join(by_page.get(p, []))}]")
    return "\n".join(lines)

def flat_block(log, budget):
    lines = [f"On page '{e['from']}' clicked '{e['action']}' and arrived at '{e['to']}'." for e in log]
    total, keep = 0, []
    for l in reversed(lines):  # recency-first, like real flat memory
        if total + len(l) + 1 > budget: break
        total += len(l) + 1; keep.append(l)
    return "NOTES from earlier exploration of this panel:\n" + "\n".join(reversed(keep))

# ---------------- Ollama Cloud call ----------------
HDR = re.compile(r"^\[.*\]$")
def oll(prompt, retries=1):
    for _ in range(retries + 1):
        try:
            r = subprocess.run(["oll", prompt], capture_output=True, text=True, timeout=60)
            out = "\n".join(l for l in r.stdout.splitlines() if not HDR.match(l.strip()))
            if out.strip(): return out.strip()
        except Exception:
            pass
    return ""

def parse(reply):
    a = re.search(r"ACTION:\s*(\d+)", reply, re.I)
    v = re.search(r"VALUE:\s*(.+)", reply, re.I)
    c = re.search(r"CONFIDENCE:\s*(\d+)", reply, re.I)
    return (int(a.group(1)) if a else None,
            v.group(1).strip() if v else None,
            min(100, max(0, int(c.group(1)))) if c else None)

def step_prompt(task, memory, page, state):
    title, body, acts = PAGES[page]
    # realistic feedback: pages show current values of settings defined there
    here = [e for _, _, e in acts if e]
    shown = [f"{e.replace('_',' ')}: {state[e]}" for e in here if e in state]
    if shown:
        body = body + "\nCurrent settings: " + "; ".join(shown) + "."
    mem = f"\n{memory}\n" if memory else "\nYou have no notes about this site.\n"
    return (f"You are operating a web admin panel. Complete the task.\n\nTASK: {task}{mem}\n"
            f"CURRENT PAGE: {title}\nPAGE CONTENT: {body}\nACTIONS:\n"
            + "\n".join(f"{i+1}. {a[0]}" for i, a in enumerate(acts))
            + "\n\nIf the chosen action changes a setting to a specific value, you MUST include VALUE: with that exact value."
            "\nReply in exactly this format:\nACTION: <action number>\nVALUE: <text, only if the action needs a value>\nCONFIDENCE: <0-100>")

def run_episode(task_id, instruction, required, memory, max_steps=12):
    state, page, confs, traj, invalid = {}, "login", [], [], 0
    for step in range(max_steps):
        acts = PAGES[page][2]
        reply = oll(step_prompt(instruction, memory, page, state))
        idx, val, conf = parse(reply)
        if idx is None or not (1 <= idx <= len(acts)):
            invalid += 1
            idx, conf = (None if invalid > 1 else None), (conf if conf is not None else 10)
            if idx is None:
                confs.append(conf if conf is not None else 10); traj.append({"page": page, "bad": reply[:80]}); continue
        label, target, effect = acts[idx - 1]
        if effect:
            state[effect] = True if effect in TOGGLES else (val if val else True)
        confs.append(conf if conf is not None else 50)
        traj.append({"page": page, "action": label, "to": target, "conf": confs[-1]})
        page = target
        if all(state.get(k) == v for k, v in required.items()):
            return {"id": task_id, "success": True, "steps": step + 1, "confs": confs, "traj": traj, "invalid": invalid}
    ok = all(state.get(k) == v for k, v in required.items())
    return {"id": task_id, "success": ok, "steps": max_steps, "confs": confs, "traj": traj, "invalid": invalid}

# ---------------- AUROC (Mann-Whitney, tie-aware) ----------------
def auroc(scores, labels):
    pos = sorted(s for s, l in zip(scores, labels) if l); neg = sorted(s for s, l in zip(scores, labels) if not l)
    if not pos or not neg: return None
    ranks, i, j, r = [], 0, 0, 1
    allv = sorted([(s, 1) for s in pos] + [(s, 0) for s in neg])
    # rank with ties
    vals = [x[0] for x in allv]
    rk = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[j + 1] == vals[i]: j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1): rk[k] = avg
        i = j + 1
    sum_pos = sum(rk[k] for k, (_, l) in enumerate(allv) if l == 1)
    n1, n0 = len(pos), len(neg)
    return (sum_pos - n1 * (n1 + 1) / 2) / (n1 * n0)

# ---------------- main ----------------
if __name__ == "__main__":
    arm = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "none"
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else f"results_{arm}.json"
    limit = int(sys.argv[sys.argv.index("--tasks") + 1]) if "--tasks" in sys.argv else len(TASKS)
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 7

    log = explore(seed=seed)
    g = graph_block(log)
    (OUT / f"memory_graph_s{seed}.txt").write_text(g)
    if arm == "graph":
        mem, budget = g, len(g)
    elif arm == "flat":
        budget = len(g); mem = flat_block(log, budget)
        (OUT / f"memory_flat_s{seed}.txt").write_text(mem)
    else:
        mem, budget = "", 0

    results = [run_episode(t[0], t[1], dict(t[2]), mem) for t in TASKS[:limit]]
    succ = sum(r["success"] for r in results)
    doc = {"arm": arm, "seed": seed, "memory_chars": len(mem), "budget": budget, "n": len(results),
           "successes": succ, "success_rate": succ / len(results),
           "mean_steps": sum(r["steps"] for r in results) / len(results),
           "invalid_actions": sum(r["invalid"] for r in results), "results": results}
    (OUT / out).write_text(json.dumps(doc, indent=1))
    print(f"[{arm} s{seed}] {succ}/{len(results)} success | mem {len(mem)} chars | "
          f"mean steps {doc['mean_steps']:.1f} | invalid {doc['invalid_actions']}")