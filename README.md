# agent-skills

My AI setup in one place: global instructions plus the skills I want in every project, for any tool that reads Agent Skills (`SKILL.md` folders).

Project-specific skills such as BMAD, Expo or marketing packs stay in each project. This repo is only for what should follow me everywhere.

## Layout

- `AGENTS.md` holds global instructions: stack, principles, security habits, git rules, writing rules.
- `skills/` holds one folder per skill. Some are mine, some are vendored from upstream (see `sources.json`).
- `claude/plugins.json` lists the Claude Code plugins to enable globally. It gets merged into `~/.claude/settings.json`.
- `install.sh` links everything into each tool it finds.
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

## Day to day

- **Change a skill or rule:** edit it (here, or through the linked path), then commit and push.
- **Add a skill:** create `skills/<name>/SKILL.md`, run `./install.sh`, commit.
- **Remove a skill:** delete its folder and rerun `./install.sh`. That also cleans up the broken links.
- **Another machine:** `git pull && ./install.sh`.
- **Upstream updates:** run `scripts/upstream-diff.sh pstack` (or `mattpocock`), copy in what you want, and update the commit in `sources.json`.

## Skills

| Skill | From | Use it for |
|---|---|---|
| `unslop` | pstack | Cleaning AI tells out of any prose meant for people |
| `correct` | pstack | Making a repeated agent mistake impossible (types, lint, test) |
| `deslop` | pstack | Removing AI code slop from a branch before commit |
| `typescript-best-practices` | pstack | Loads automatically on `.ts`/`.tsx` work |
| `thermo-nuclear-review` | pstack | Deep security and correctness audit of a branch |
| `create-verification-skill` | pstack | Generating a project `verify` skill that drives the real app |
| `how` | pstack | "How does X work" walkthroughs |
| `ketchup` | pstack | "Catch me up" after time away from a session |
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
