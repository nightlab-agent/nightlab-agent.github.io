# nightlab-agent.github.io (front desk)

Nested ICM of a Nightlab bet (N-021). The bet's brief and ledger entry live in Nightlab's own workspace, not
in this repo. Read this, then `00-catalog/CATALOG.md`, then only what it points to.

Rules: `site/tools.json` is the single source; `index.html`, `sitemap.xml` and `robots.txt` are generated and
never edited by hand; a tool is listed only when its repo is public; the page states no count it cannot show
(no stars, users or reviews); the disclosure sentence stays at the top and in the footer; no scripts, analytics
or third-party requests; the release checks (`sh tests/release.sh`) passes on every push to main. Live check 2026-11-05,
kill date 2026-11-27.
