#!/usr/bin/env python3
"""Draw the explored site graph (seed 7) as an SVG, and a thumbnails montage of the pages."""
import html, subprocess
from pathlib import Path
from micro_exp import PAGES, explore

HERE = Path(__file__).parent
IMG = HERE / "img"
PAGES_DIR = IMG / "pages"

log = explore(seed=7)
edges = {}
for e in log:
    edges[(e["from"], e["action"])] = e["to"]
visited = sorted({e["from"] for e in log} | {e["to"] for e in log})

# layered layout by depth from login
depth = {"login": 0}
frontier = ["login"]
while frontier:
    nxt = []
    for u in frontier:
        for (src, _act), to in edges.items():
            if src == u and to not in depth:
                depth[to] = depth[u] + 1
                nxt.append(to)
    frontier = nxt
for p in visited:
    depth.setdefault(p, 0)

layers = {}
for p in visited:
    layers.setdefault(depth[p], []).append(p)

W, NODE_W, NODE_H, GAP_X, GAP_Y = 1180, 150, 46, 40, 110
max_layer = max(len(v) for v in layers.values())
H = (max(layers) * GAP_Y) + 140

pos = {}
for d, pages in sorted(layers.items()):
    n = len(pages)
    total = n * NODE_W + (n - 1) * GAP_X
    x0 = (W - total) / 2
    for i, p in enumerate(pages):
        pos[p] = (x0 + i * (NODE_W + GAP_X), 80 + d * GAP_Y)

def esc(s): return html.escape(s)

lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="-apple-system,Helvetica,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#f8fafc"/>',
         f'<text x="{W/2}" y="34" text-anchor="middle" font-size="17" font-weight="600" fill="#111827">Explored site graph — 21 pages, seed 7 (task-agnostic random walk, 140 steps)</text>']

# edges
for (src, act), to in sorted(edges.items()):
    x1, y1 = pos[src]; x2, y2 = pos[to]
    x1c, y1c = x1 + NODE_W/2, y1 + NODE_H
    x2c, y2c = x2 + NODE_W/2, y2 - 4
    if to == src:
        continue  # self-loops omitted for clarity
    color = "#94a3b8"
    lines.append(f'<path d="M{x1c},{y1c} C{x1c},{y1c+30} {x2c},{y2c-30} {x2c},{y2c}" fill="none" stroke="{color}" stroke-width="1.4" marker-end="url(#arr)"/>')

lines.append('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/></marker></defs>')

# nodes
for p in visited:
    x, y = pos[p]
    title = PAGES[p][0]
    lines.append(f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" rx="9" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>')
    lines.append(f'<text x="{x+NODE_W/2}" y="{y+NODE_H/2+5}" text-anchor="middle" font-size="13" fill="#111827">{esc(title)}</text>')
    lines.append(f'<text x="{x+NODE_W/2}" y="{y+NODE_H/2+21}" text-anchor="middle" font-size="10" fill="#64748b">{esc(p)}</text>')

lines.append(f'<text x="20" y="{H-16}" font-size="11" fill="#64748b">Edges: affordance → destination, as learned by exploration. Self-effect actions (toggles, text fields) omitted; see micro_exp.py graph_block.</text>')
lines.append('</svg>')
(IMG / "site_graph.svg").write_text("\n".join(lines))
print("svg written:", IMG / "site_graph.svg")

# montage: 4 columns of thumbnails using Chrome on a grid HTML
cols = 4
items = []
for p in visited:
    t = PAGES[p][0]
    items.append(f'<figure><img src="pages/{p}.png"><figcaption>{esc(t)}<span>{esc(p)}</span></figcaption></figure>')
grid = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body {{ font-family: -apple-system, sans-serif; background: #f4f5f7; margin: 0; padding: 24px; }}
h1 {{ font-size: 18px; color: #111827; }}
.grid {{ display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 18px; }}
figure {{ margin: 0; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; }}
img {{ width: 100%; display: block; border-bottom: 1px solid #e5e7eb; }}
figcaption {{ padding: 8px 12px; font-size: 13px; color: #111827; font-weight: 600; }}
figcaption span {{ display: block; font-weight: 400; color: #6b7280; font-size: 11px; }}
</style></head><body><h1>Pages explored (seed 7) — {len(visited)} pages</h1>
<div class="grid">{''.join(items)}</div></body></html>"""
gp = IMG / "grid.html"
gp.write_text(grid)
n = len(visited)
rows = (n + cols - 1) // cols
subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless",
                "--disable-gpu", "--hide-scrollbars", f"--screenshot={IMG / 'pages_grid.png'}",
                f"--window-size=1240,{rows * 340 + 120}", str(gp)],
               check=True, capture_output=True, timeout=60)
gp.unlink()
print("montage written:", IMG / "pages_grid.png")