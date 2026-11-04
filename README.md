# agent-skills

My AI setup in one place: global instructions plus the skills I want in every project, for any tool that reads Agent Skills (`SKILL.md` folders).

The core has no platform in it. Anything tied to a platform or language (Supabase, Vercel, Expo, TypeScript) lives in a pack, and a pack is only turned on in projects that use it.

## Layout

- `AGENTS.md` holds global instructions: principles, security habits, git rules, writing rules.
- `skills/` holds the core skills, one folder each. Some are mine, some are vendored from upstream (see `sources.json`).
- `packs/<name>/` holds a platform pack: a `pack.json` (how to detect it, which Claude Code plugins it turns on) and optional `skills/`.
- `claude/plugins.json` lists the Claude Code plugins to enable globally. It gets merged into `~/.claude/settings.json`. Pack plugins are listed as `false` so they only run where a pack turns them on.
- `install.sh` links the core into each tool it finds.
- `project.py` turns on the right packs in one project.
- `scripts/upstream-diff.sh` compares vendored skills with upstream.

## Set up a machine

```bash
git clone https://github.com/nimeshkavinda/agent-skills.git ~/Documents/Projects/agent-skills
cd ~/Documents/Projects/agent-skills
./install.sh --dry-run
./install.sh
```

The installer is safe to rerun. Anything it replaces goes to `~/.agent-skills-backup/<timestamp>/`.

| Tool | Skills | Instructions |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `~/.claude/CLAUDE.md` |
| Codex, Gemini CLI, Copilot, OpenCode | `~/.agents/skills/` | `~/.codex/AGENTS.md`, `~/.gemini/GEMINI.md` |
| Cursor | `~/.cursor/skills/` | paste `AGENTS.md` into Settings > Rules |
| Claude.ai / desktop chat | upload a skill folder as a zip in Claude's skill settings | |

Each skill is linked into place, not copied. Editing a skill from any tool edits this repo.

## Platform packs

Run this in a project (or pass its path) to turn on the packs it needs:

```bash
~/Documents/Projects/agent-skills/project.py ~/Documents/Projects/my-app --dry-run
~/Documents/Projects/agent-skills/project.py ~/Documents/Projects/my-app
```

It detects packs from the project's files, for example `@supabase/supabase-js` in a `package.json` turns on `supabase`. For each active pack it:

- links the pack's skills into the project's `.claude/skills`, `.agents/skills` and `.cursor/skills`
- turns on the pack's Claude Code plugins in `.claude/settings.local.json`
- lists everything it created in `.git/info/exclude`, so the project's git status stays clean and teammates see nothing

Add a pack that isn't detected with `--add figma`, and turn off a detected one with `--remove vercel`. Both are saved in the project's `.agent-packs` file, also excluded from git. Rerun after pulling this repo or changing a project's dependencies. A skill the project already ships itself is left alone.

| Pack | Detected by | Gives |
|---|---|---|
| `typescript` | `tsconfig.json` | `typescript-best-practices` skill |
| `supabase` | `@supabase/supabase-js`, `@supabase/ssr`, `supabase/config.toml` | `supabase-safety` skill, Supabase plugin |
| `vercel` | `vercel.json`, `vercel.ts`, `.vercel/project.json` | Vercel plugin |
| `expo` | `expo` dependency | Expo plugin |
| `figma` | not detected, use `--add figma` | Figma plugin |

To add a pack, create `packs/<name>/pack.json` with a `description`, `detect` rules (`{"file": "path"}` or `{"dependency": "npm-name"}`), optional `plugins`, and optional `skills/`.

## Day to day

- **Change a skill or rule:** edit it (here, or through the linked path), then commit and push.
- **Add a skill:** create `skills/<name>/SKILL.md` for every project, or `packs/<pack>/skills/<name>/SKILL.md` for one platform. Run `./install.sh` (core) or `./project.py <project>` (pack), then commit.
- **Remove a skill:** delete its folder and rerun `./install.sh`. That also cleans up the broken links.
- **Another machine:** `git pull && ./install.sh`, then `./project.py <project>` in each project you work on.
- **Upstream updates:** run `scripts/upstream-diff.sh pstack` (or `mattpocock`, or `tstack`), copy in what you want, and update the commit in `sources.json`.

## Core skills

| Skill | From | Use it for |
|---|---|---|
| `unslop` | pstack | Cleaning AI tells out of any prose meant for people |
| `correct` | pstack | Making a repeated agent mistake impossible (types, lint, test) |
| `deslop` | pstack | Removing AI code slop from a branch before commit |
| `thermo-nuclear-review` | pstack | Deep security and correctness audit of a branch |
| `create-verification-skill` | pstack | Generating a project `verify` skill that drives the real app |
| `how` | pstack | "How does X work" walkthroughs |
| `ketchup` | pstack | "Catch me up" after time away from a session |
| `bro` | pstack | Restating the last reply in plain words, no jargon |
| `diagnosing-bugs` | Matt Pocock | Hard bugs and perf regressions |
| `tdd` | Matt Pocock | Test-first work |
| `grilling`, `grill-me` | Matt Pocock | Stress-testing a plan |
| `pr` | Matt Pocock | Writing PR descriptions |
| `wizard` | Matt Pocock | Interactive scripts for steps only a human can do (dashboards, secrets) |
| `prototype` | Matt Pocock | Throwaway sketches to settle a design question |
| `handoff` | Matt Pocock | Writing a handoff doc for the next session |
| `research` | Matt Pocock | Researching from primary sources into a Markdown file |
| `writing-for-agents` | Matt Pocock | Editing skills, `AGENTS.md`, `CLAUDE.md` |
| `git-guardrails-claude-code` | Matt Pocock | Hooks that block destructive git commands |
| `improve-codebase-architecture`, `codebase-design`, `domain-modeling` | Matt Pocock | Architecture reviews and module design |
| `find-skills` | vercel-labs | Finding installable skills |
| `babysit-pr` | tstack | Watching a PR through CI and review bots, and fixing real findings |
| `modernize` | tstack | Rebasing an old PR, or deciding it should be reworked or closed |
| `leaving-pr-comments` | tstack | Formatting comments an agent posts on your behalf |
| `full-stop` | tstack | Taking a change to a ready PR and stopping before merge |
