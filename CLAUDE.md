# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A holding pen for small things worth keeping in source control that don't justify a
repository each: script fragments, editor/tooling config, reference notes, and Claude
Code skills. It is not an application. There is no build, no test suite, no lint
config, no package manifest, and no CI. Files are independent of one another.

Do not add tooling (package.json, Makefile, workflows, test harnesses) unless asked.

## Repository is public

`CuriousJC/odds-and-ends` is a **public** GitHub repo. Everything committed is world
readable, so credentials and identity are placeholdered rather than real —
`config/git_setup.ps1` ships `"xxx"` / `"xxx@gmail.com"` deliberately. Keep that
pattern; never substitute real values in, and don't write anything into a skill or
snippet that you wouldn't publish.

## Branch workflow

Always work on a feature branch; `main` is reached only through a PR.

```bash
git checkout -b feature/<short-name>
```

Never commit directly to `main`. Per the user's global instructions: leave changes
unstaged, and stop before staging, committing, or pushing unless asked for that
specific step.

## Layout

- `.claude/skills/<name>/SKILL.md` — Claude Code skills. Living under `.claude/` means
  they are auto-discovered while working in this repo, so a skill can be written and
  exercised here directly. They are *not* installed globally; using one elsewhere is a
  manual copy into `~/.claude/skills/`, documented in the Readme. There is no sync
  script and nothing should write to `~/.claude` on its own.
- `config/` — editor, shell, and tooling config under version control.
- `snippets/` — script and manifest fragments.

## Conventions that aren't obvious

- `snippets/working.*` are scratch drafts, one per format, and are expected to be
  incomplete. `working.sh` references `$selected_environment` and `$yaml_directory`
  that are never assigned — that is a fragment, not a bug to fix. `working.ps1` is
  empty on purpose.
- `config/vimrc.viminfo` is a `.vimrc` body despite the extension; it is not a real
  Vim viminfo file. `config/vscode.settings.json` is user-level VS Code settings, not
  a workspace `.vscode/settings.json`. Dotfile bodies are stored under non-dotfile
  names so they stay visible and diffable.
- `.gitignore` and `.gitattributes` are large vendored templates (toptal Terraform
  template; VS/msysgit boilerplate), not hand-tuned. Append to them; don't reformat
  or prune.
