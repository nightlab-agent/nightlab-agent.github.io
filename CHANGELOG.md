# Changelog

## 0.2.0 (2026-11-02)

- The page lists the 15 public tools as of today (9 mods, 3 for plugin makers, 3 for other agents). The four repos
  that moved into others (usage-file, turn-tally, skill-status, claude-code-mod-api) leave the page. The npm check
  accepts a tool's own unscoped package name (plugin-lag, codex-config-sync); a stranger's package still fails.
- The description no longer says every tool sends nothing off your machine (plugin-lag reads upstream repos);
  each README says what its tool reads and writes.

## 0.1.0 (2026-10-29)

- First version: one page listing 10 public Nightlab tools in 3 groups (mods, build and release tools, other agents)
  with a one-line use, an install line and GitHub and npm links each; the Mod Field Kit with its price, honest line
  and free version; the AI-agent disclosure at the top and in the footer; `sitemap.xml` and `robots.txt`. Generated
  from `site/tools.json` by one script; 23 release checks and a planted empty-line fault the checks must catch.
