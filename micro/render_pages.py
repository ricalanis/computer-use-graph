#!/usr/bin/env python3
"""Render the synthetic site's pages as HTML and screenshot them headlessly (Chrome).

Produces docs/img/pages/<page>.png for every page the exploration visited,
plus a thumbnails grid page. Run from micro/: python3 render_pages.py
"""
import subprocess, sys, html
from pathlib import Path
from micro_exp import PAGES, explore

HERE = Path(__file__).parent
IMG = HERE / "img" / "pages"
IMG.mkdir(parents=True, exist_ok=True)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
body { font-family: -apple-system, 'Helvetica Neue', sans-serif; margin: 0; background: #f4f5f7; }
.topbar { background: #1f2733; color: #fff; padding: 14px 28px; font-size: 20px; font-weight: 600;
          display: flex; align-items: center; gap: 12px; }
.topbar .logo { background: #4f6bed; border-radius: 6px; padding: 4px 10px; font-size: 14px; }
.crumbs { padding: 10px 28px; color: #6b7280; font-size: 13px; background: #fff;
          border-bottom: 1px solid #e5e7eb; }
.crumbs b { color: #111827; }
.wrap { display: flex; gap: 28px; padding: 28px; }
.main { flex: 1; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 24px 28px; }
.side { width: 220px; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; }
.side h4 { margin: 0 0 8px; font-size: 12px; text-transform: uppercase; color: #6b7280; letter-spacing: .04em; }
.side a { display: block; padding: 7px 10px; border-radius: 6px; color: #374151; text-decoration: none; font-size: 14px; }
.side a.cur { background: #eef2ff; color: #1a37a8; font-weight: 600; }
h1 { font-size: 22px; margin: 0 0 6px; color: #111827; }
p.desc { color: #4b5563; margin: 0 0 18px; font-size: 14px; }
.settings { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 10px 14px; margin-bottom: 18px; font-size: 13px; color: #374151; }
.actions { display: flex; flex-wrap: wrap; gap: 10px; }
.actions a { background: #fff; border: 1px solid #d1d5db; border-radius: 8px; padding: 9px 16px;
             font-size: 14px; color: #111827; text-decoration: none; }
.actions a:hover { border-color: #4f6bed; }
.actions a.decoy { border-style: dashed; }
"""

NAV = {
    "dashboard": ["Account", "Workspace", "System", "Preferences", "Billing"],
    "account": ["Profile", "Security", "Notifications", "Email", "Back to dashboard"],
    "workspace": ["Integrations", "Apps", "Members", "Back to dashboard"],
    "system": ["API keys", "Webhooks", "Advanced", "Back to dashboard"],
    "preferences": ["Appearance", "Language", "Notification preferences", "Back to dashboard"],
    "billing": ["View invoices", "Change plan", "Subscription details", "Back to dashboard"],
}
NAV_TARGET = {"Account": "account", "Workspace": "workspace", "System": "system",
              "Preferences": "preferences", "Billing": "billing", "Profile": "profile",
              "Security": "security", "Notifications": "notifications", "Email": "email_aliases",
              "Integrations": "integrations", "Apps": "apps", "Members": "members",
              "API keys": "api_keys", "Webhooks": "webhooks", "Advanced": "advanced",
              "Appearance": "appearance", "Language": "language",
              "Notification preferences": "prefs_notifications", "View invoices": "invoices",
              "Change plan": "billing", "Subscription details": "subscription",
              "Back to dashboard": "dashboard"}

DECOYS = {"Email notifications", "Push digest", "Install beta analytics", "Revoke current session",
          "Change primary email", "Add alias", "Install app", "Email summary", "Change plan"}

def page_html(pid, state=None):
    title, body, acts = PAGES[pid]
    state = state or {}
    nav = NAV.get(pid)
    side = ""
    if nav:
        items = "".join(
            f'<a class="{"cur" if False else ""}">{html.escape(n)}</a>' for n in nav)
        side = f'<div class="side"><h4>Sections</h4>{items}</div>'
    here = [e for _, _, e in acts if e]
    shown = "; ".join(f"{e.replace('_',' ')}: {state[e]}" for e in here if e in state)
    settings = f'<div class="settings"><b>Current settings:</b> {html.escape(shown)}</div>' if shown else ""
    buttons = "".join(
        f'<a class="{"decoy" if a[0] in DECOYS else ""}">{html.escape(a[0])}</a>' for a in acts)
    crumbs = " &rsaquo; ".join(["Acme Admin", html.escape(title)])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
<div class="topbar"><span class="logo">ACME</span> Acme Admin Panel</div>
<div class="crrumbs-wrap"><div class="crumbs">{crumbs}</div></div>
<div class="wrap">{side}<div class="main">
<h1>{html.escape(title)}</h1>
<p class="desc">{html.escape(body)}</p>
{settings}
<div class="actions">{buttons}</div>
</div></div></body></html>"""

def shot(html_path, png_path, width=900):
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                   f"--screenshot={png_path}", f"--window-size={width},560",
                   "--default-background-color=FFFFFFFF", str(html_path)],
                  check=True, capture_output=True, timeout=60)

if __name__ == "__main__":
    log = explore(seed=7)
    visited = sorted({e["from"] for e in log} | {e["to"] for e in log})
    print(f"exploration visited {len(visited)} pages: {visited}")
    for pid in visited:
        p = IMG / f"{pid}.html"
        p.write_text(page_html(pid))
        shot(p, IMG / f"{pid}.png")
        p.unlink()
    print("screenshots in", IMG)