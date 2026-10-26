---
name: full-stop
description: Finish the current change through a ready pull request and stop before merge. Use when the user says "full stop".
---

# Full stop

The user is not watching this thread. Take the work from its current state to a pull request that is ready to merge, then stop. Leave the PR open and unmerged.

An explicit "full stop" is permission for this task's branch: commit, push, rebase, and `git push --force-with-lease` against the head SHA you observed before the rebase. It is also permission for the checks proof needs, including computer use, browser automation, simulators, running the app, and screenshots, even when a project file says to ask first. Follow rules that name the correct command, fixture, or check.

Leave these for a separate explicit ask: merging, auto-merge, a merge queue, pushing the default branch, bypassing branch protection, deleting data, production changes, closing a PR, and force-pushing any other branch. `babysit-pr` may merge when the user asked for a merge. This request does not.

## Steps

1. **Finish the change.** Smallest change that meets the request. If you are on the default branch, create a branch first.
2. **Prove it.** Evidence you observed in this session. Reproduce the original failure, apply the fix, and watch the same reproduction pass. Run the checks the repo's CI runs. Add one focused test that fails without the fix when the behavior has none and the repo has a test setup. For UI and runtime behavior, run the app and look. Green mocked tests do not prove the user experience. When you cannot prove a change, ask.
3. **Review** with the `thermo-nuclear-review` skill. Fix real bugs in the intended case. Decline nits, extra tests, and guards for edge cases that do not matter, with a one-line reason, and list them as follow-ups. Prefer a fix that deletes or narrows code. One review pass is enough unless a medium or high finding is still open.
4. **File or update the PR** with the `pr` skill. Rebase onto the latest default branch first. Add one short line to the description that says how you proved the change.
5. **Babysit** with the `babysit-pr` skill until the readiness check below passes. Stay with its watcher. If you end the turn while checks are pending, the work stops, because nobody will prompt you again.
6. **Stop.** Leave the PR open. In T3 Code, call `unwatch_pull_request` before the handoff or a question.

## Readiness

All of these are true on the latest commit:

- Proof covers every change in the diff.
- Required checks are green.
- Each review finding is fixed or dismissed with a written reason. Use the `leaving-pr-comments` skill for those replies.
- No human review still requests changes.
- The branch is up to date with the default branch, and GitHub reports it mergeable.

Fetch the target branch and read the live PR's head, base, checks, reviews, and mergeability before you call it ready. Confirm the PR is open, not a draft, and not set to merge on its own. Disable existing auto-merge and remove the PR from any merge queue before work begins, and check again before each push. If you cannot prevent automatic merging, report that and stop. If someone else already merged it, report that.

- **Ready:** the check above passes. Leave the PR open.
- **Waiting for required approval:** human approval is the only remaining blocker. Say so.
- **Blocked:** say what prevents readiness, what you tried, and what is needed.

## Asking

A normal message goes unseen. Use the harness question tool. Put the PR link, the blocker, and the options in the question, with your recommendation first.

Ask only when you cannot continue alone:

- You cannot prove the change.
- The readiness check cannot pass, and you cannot fix that yourself.
- The next step is outside the permission above.
- The goal is ambiguous in a way that changes the result.
- Another PR makes this one obsolete.

Decide everything else yourself, and list those decisions in the report. If no question tool is available, or it returns no answer, leave the PR open and start the final message with the question.

## Report

Lead with the PR link and whether it is still open and unmerged. Then the final head SHA, the verdict (ready, waiting for approval, or blocked), the proof, the review outcome, the decisions you made, and any remaining risk.
