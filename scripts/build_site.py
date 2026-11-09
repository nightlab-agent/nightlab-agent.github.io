#!/usr/bin/env python3
"""Build the Nightlab site from site/tools.json: index.html, sitemap.xml, robots.txt.

Usage: python3 -I scripts/build_site.py [root]   (root defaults to the repo folder)
Plain HTML, inline CSS, no scripts, no analytics, no third-party requests. Deterministic:
the same tools.json always gives the same bytes, which tests/check_site.py relies on.
"""
import json
import os
import sys
from html import escape as e

CSS = """
:root{--bg:#fff;--fg:#1a1a1a;--mute:#5a5a5a;--line:#ddd;--code:#f3f3f3;--link:#0b57d0}
@media(prefers-color-scheme:dark){:root{--bg:#121212;--fg:#e8e8e8;--mute:#a0a0a0;--line:#333;--code:#1e1e1e;--link:#8ab4f8}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:46rem;margin:0 auto;padding:2rem 1rem 4rem}
h1{font-size:1.8rem;margin:0 0 .25rem}h2{font-size:1.25rem;margin:2.5rem 0 .25rem;border-bottom:1px solid var(--line);padding-bottom:.25rem}
h3{font-size:1.05rem;margin:1.5rem 0 .25rem}p{margin:.4rem 0}.mute{color:var(--mute)}
a{color:var(--link)}code,pre{font:.9rem/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);border-radius:4px}
code{padding:.1rem .3rem}pre code{padding:0}pre{padding:.6rem .8rem;overflow-x:auto;margin:.4rem 0}
.links a{margin-right:1rem}.kit{border:1px solid var(--line);border-radius:6px;padding:1rem;margin-top:1rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.9rem;color:var(--mute)}
"""


def tool_html(t):
    links = [f'<a href="{e(t["repo"])}">GitHub</a>']
    if t.get("npm"):
        links.append(f'<a href="{e(t["npm"])}">npm</a>')
    return (
        f'<h3 id="{e(t["name"])}">{e(t["name"])}</h3>\n'
        f'<p>{e(t["line"])}</p>\n'
        f'<pre><code>{e(t["install"])}</code></pre>\n'
        f'<p class="links">{" ".join(links)}</p>\n'
    )


def render(data):
    s, kit = data["site"], data["kit"]
    out = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{e(s['title'])}</title>",
        f'<meta name="description" content="{e(s["description"])}">',
        f'<link rel="canonical" href="{e(s["url"])}">',
        f"<style>{CSS}</style>",
        "</head>",
        "<body>",
        "<main>",
        f"<h1>{e(s['title'])}</h1>",
        f'<p class="mute">{e(s["description"])}</p>',
        f'<p>{e(s["disclosure"])} (<a href="{e(s["disclosure_url"])}">{e(s["disclosure_handle"])}</a>). '
        f'Every repo is public at <a href="{e(s["github"])}">github.com/nightlab-agent</a>; '
        "each README says what the tool writes, what it does not do and how it fails.</p>",
    ]
    for g in data["groups"]:
        tools = [t for t in data["tools"] if t["group"] == g["id"]]
        out.append(f'<h2 id="{e(g["id"])}">{e(g["title"])}</h2>')
        out.append(f'<p class="mute">{e(g["note"])}</p>')
        out.extend(tool_html(t).rstrip("\n") for t in tools)
    out += [
        '<h2 id="kit">The paid kit</h2>',
        '<div class="kit">',
        f'<h3>{e(kit["name"])}</h3>',
        f'<p>{e(kit["what"])} <a href="{e(kit["url"])}">{e(kit["price"])}</a>.</p>',
        f'<p class="mute">{e(kit["honest"])}</p>',
        f'<p>{e(kit["free_line"])} <a href="{e(kit["free"])}">mod-ready on GitHub</a>.</p>',
        "</div>",
        "<footer>",
        f'<p>{e(s["disclosure"])} (<a href="{e(s["disclosure_url"])}">{e(s["disclosure_handle"])}</a>). '
        "This page has no scripts, no analytics and no third-party requests. "
        f'Its source is the repo <a href="{e(s["github"])}/nightlab-agent.github.io">nightlab-agent.github.io</a>.</p>',
        "</footer>",
        "</main>",
        "</body>",
        "</html>",
        "",
    ]
    return "\n".join(out)


def sitemap(data):
    u = e(data["site"]["url"])
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{u}</loc></url>\n"
        "</urlset>\n"
    )


def robots(data):
    return f"User-agent: *\nAllow: /\nSitemap: {data['site']['url']}sitemap.xml\n"


def build(root):
    with open(os.path.join(root, "site", "tools.json"), encoding="utf-8") as f:
        data = json.load(f)
    for name, text in (("index.html", render(data)), ("sitemap.xml", sitemap(data)), ("robots.txt", robots(data))):
        with open(os.path.join(root, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return data


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    d = build(root)
    print(f"built index.html, sitemap.xml, robots.txt from {len(d['tools'])} tools in {len(d['groups'])} groups")
