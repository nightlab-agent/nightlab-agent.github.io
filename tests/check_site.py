#!/usr/bin/env python3
"""Checks the Nightlab site in a repo folder. Each check is a sentence; the first failure exits 1.

Usage: python3 -I tests/check_site.py [root]
No network, no dependencies. The build script is imported from <root>/scripts so the committed pages
are compared with what the current tools.json renders.
"""
import importlib.util
import json
import os
import sys
from html import escape as e
from html.parser import HTMLParser

sys.dont_write_bytecode = True

VOID = {"meta", "link", "br", "hr", "img", "input"}
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
MAX_LINES = 400
MAX_HTML_BYTES = 100_000
fails = 0


def check(sentence, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + sentence + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        fails += 1


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.error, self.doctype = [], None, False

    def handle_decl(self, decl):
        self.doctype = decl.lower().startswith("doctype html")

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.error = self.error or f"</{tag}> closes {self.stack[-1] if self.stack else 'nothing'}"
        else:
            self.stack.pop()


def load_build():
    spec = importlib.util.spec_from_file_location("build_site", os.path.join(ROOT, "scripts", "build_site.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    data = json.loads(read("site/tools.json"))
    tools = data["tools"]
    groups = {g["id"] for g in data["groups"]}
    check("tools.json lists at least ten tools", len(tools) >= 10, str(len(tools)))
    names = [t["name"] for t in tools]
    check("every tool name is unique", len(set(names)) == len(names))
    bad = [t["name"] for t in tools if not all(t.get(k) for k in ("name", "line", "install", "repo", "group"))]
    check("every tool has a name, a line, an install line, a repo and a group", not bad, ", ".join(bad))
    bad = [t["name"] for t in tools if not t["repo"].startswith("https://github.com/nightlab-agent/")]
    check("every repo link points at a nightlab-agent repo", not bad, ", ".join(bad))
    bad = [t["name"] for t in tools if t["group"] not in groups]
    check("every tool sits in a declared group", not bad, ", ".join(bad))
    bad = [t["name"] for t in tools if not t["line"].endswith(".") or len(t["line"]) > 220]
    check("every tool line is one sentence under 220 characters ending in a period", not bad, ", ".join(bad))
    bad = [t["name"] for t in tools if t.get("npm") and not t["npm"].startswith("https://www.npmjs.com/package/@nightlab-agent/")]
    check("every npm link, where given, points at the @nightlab-agent scope", not bad, ", ".join(bad))

    build = load_build()
    rendered = {"index.html": build.render(data), "sitemap.xml": build.sitemap(data), "robots.txt": build.robots(data)}
    for name, text in rendered.items():
        check(f"{name} is exactly what build_site.py makes from tools.json", read(name) == text, "run scripts/build_site.py")

    html = read("index.html")
    p = Balance()
    p.feed(html)
    check("index.html starts with an HTML doctype", p.doctype)
    check("index.html closes every tag it opens, in order", p.error is None and not p.stack, p.error or f"open: {p.stack}")
    disclosure = data["site"]["disclosure"]
    check("index.html carries the AI-agent disclosure at the top and in the footer", html.count(e(disclosure)) >= 2, str(html.count(e(disclosure))))
    check("index.html names every tool with its install line", all(e(t["name"]) in html and e(t["install"].split(" ")[0]) in html for t in tools))
    kit = data["kit"]
    check("index.html names the paid kit, its price, its honest line and the free version",
          all(e(x) in html for x in (kit["name"], kit["url"], kit["honest"], kit["free"])))
    lower = html.lower()
    check("index.html has no script tag, no external stylesheet and no image", "<script" not in lower and "<link rel=\"stylesheet\"" not in lower and "<img" not in lower)
    outside = [h for h in __import__("re").findall(r'href="(https?://[^"]+)"', html)
               if not h.startswith(("https://github.com/", "https://www.npmjs.com/", "https://nightlab106.gumroad.com/", data["site"]["url"]))]
    check("every outside link goes to GitHub, npm, the Gumroad shop or this site", not outside, ", ".join(outside))
    check("sitemap.xml lists the site URL and robots.txt points at the sitemap",
          data["site"]["url"] in read("sitemap.xml") and "Sitemap: " + data["site"]["url"] + "sitemap.xml" in read("robots.txt"))
    check(".nojekyll exists so GitHub Pages serves the files as they are", os.path.exists(os.path.join(ROOT, ".nojekyll")))
    check("index.html is under 100000 bytes", len(html.encode()) < MAX_HTML_BYTES, str(len(html.encode())))
    for f in ("scripts/build_site.py", "tests/check_site.py", "site/tools.json"):
        n = read(f).count("\n")
        check(f"{f} is under {MAX_LINES} lines", n <= MAX_LINES, str(n))
    print(f"{fails} FAIL")
    sys.exit(1 if fails else 0)


main()
