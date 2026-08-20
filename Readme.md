# odds-and-ends

Publicly shared snippets.

This is a holding pen for small things that are worth keeping in source control but
don't justify the lift of a repository each: shell and PowerShell fragments, editor
and tooling config, reference notes, and Claude Code skills. Everything here is
public by design, so nothing in it carries real credentials or private detail —
placeholders (`xxx`, `xxx@gmail.com`) are deliberate and stay that way.

Nothing is built, tested, or deployed from this repo. Files are independent; take
what you want.

## Layout

| Path              | Contents                                                        |
| ----------------- | --------------------------------------------------------------- |
| `.claude/skills/` | Claude Code skills, one directory each with a `SKILL.md`          |
| `config/`         | Editor, shell, and tooling config kept under version control      |
| `snippets/`       | Working script and manifest fragments, mostly incomplete drafts   |

## Skills

| Skill            | What it does                                                                   |
| ---------------- | ------------------------------------------------------------------------------ |
| `asset-reviewer` | Builds browsable HTML catalogs of downloaded game-asset packs, with per-pack notes, playable animation frames, and demos of how static sprites are animated in a game |

Skills live at `.claude/skills/<name>/SKILL.md`. Because they sit in `.claude/`,
Claude Code picks them up automatically while you're working *in this repo* — which
makes this a convenient place to write and test one.

To use a skill anywhere else, copy its directory into your personal skills folder:

```powershell
Copy-Item -Recurse .claude\skills\<name> $env:USERPROFILE\.claude\skills\
```

```bash
cp -r .claude/skills/<name> ~/.claude/skills/
```

There is no sync script and nothing installs itself; the copy is a deliberate,
manual step.

## Contributing / working here

Work happens on a feature branch and reaches `main` through a PR — no direct commits
to `main`, even for a one-line snippet.

```bash
git checkout -b feature/<short-name>
# ... add or edit files ...
git add -A && git commit
git push -u origin feature/<short-name>
gh pr create --base main
```
