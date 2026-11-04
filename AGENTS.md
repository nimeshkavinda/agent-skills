# Global agent instructions

These apply in every project and every AI tool. A project's own `AGENTS.md` or `CLAUDE.md` wins where the two disagree.

## Context

- Stack and platform rules come from the project's own instructions and from the platform packs turned on for it, not from here.
- When the project has its own planning method installed (for example BMAD), use it. Don't run a second planning process alongside it.

## Principles

Apply each one when its trigger fits. Name the principle in your reply when it changed a decision.

- **Smallest change.** When sizing a diff or tempted to add layers or abstractions, prefer deletion and the smallest change that solves the problem.
- **Subtract before you add.** Remove dead code and redundant checks first, then build on the simpler base.
- **Fix root causes.** When debugging, trace the symptom to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate.
- **Attack the premise.** After two fixes built on the same assumption fail, write the assumption down and test it directly before a third.
- **Boundary discipline.** Validate and handle errors where data enters (requests, env, external APIs, DB rows). Trust types inside. Keep business logic in pure functions.
- **Type-system discipline.** Make illegal states unrepresentable. Discriminated unions over optional-field bags, `unknown` over `any`, parse with a schema instead of casting with `as`.
- **Test behavior, not implementation.** Assert what users of the code can observe.
- **Prove it works.** Before saying done, check the real thing: run the feature, read the actual value, inspect the diff. "It compiles" is not proof. Use the project's `verify` skill when it has one.
- **Encode repeated lessons.** If you correct the same mistake twice, make it impossible (types, lint, test) instead of adding another line of instructions. The `correct` skill does this.

## Security habits

- Every request handler is a public endpoint, however the UI reaches it. Authorize inside each one, never only in the UI or a parent layout.
- Secrets fail closed. Never write `if (secret && ...)`.
- Give database roles the least access that works.
- An endpoint that takes an id needs a test proving another user's or organisation's id is refused.

## Git

- Don't commit, push, or open a PR unless asked.
- Branch before editing on the default branch.
- Never force-push a shared branch, run `git reset --hard`, or delete branches without asking.

## Writing

All prose written for people follows the `unslop` skill: replies, commit messages, PR descriptions, docs, READMEs and code comments. Never apply it to code itself. If the skill isn't loaded, at least:

- No em dashes. Use periods or commas.
- No chatbot phrases ("I hope this helps", "Great question", "Certainly!") and no sycophancy.
- Plain words: "use" not "leverage" or "utilize", "is" not "serves as". Skip "crucial", "delve", "robust", "seamless".
- Short declarative sentences in active voice. Sentence-case headings, no decorative emojis.
- Code comments only for a non-obvious *why*.
