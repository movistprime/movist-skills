---
name: movist-task
description: Take a task from the Movist task board and start it. Rebase onto local main, claim the task as the user's board person, read its spec and the source, check overlap with tasks in progress, and report a design for confirmation. Stops before any code or document edit. Use when the user asks to take, pick up, or start a board task, with or without a task key ("할일 가져와", "보드에서 다음 일", "M1-4 시작"). Not for setting up or changing the board, and not for implementing, reviewing, or merging.
---

# Movist board task start

Take one task from the task board and bring it to a design the user can confirm. The user is the person who gave you the task; the end user is the person using the app.

How to read and write the board is in the repository's board rules file, which the `Task board` block of `AGENTS.md` names. Follow that file and the board's `meta/rules` for every board read and write. This skill decides only what they leave open: who you claim as, which task you take, what you do before designing, and where you stop.

## The line

1. Claim only as the board person your instructions name. Never guess the person.
2. Every timestamp you write to the board comes from `date -u +%Y-%m-%dT%H:%M:%SZ`, run immediately before that write. Never estimate a time or reuse an earlier one.
3. Until the user confirms the design, change no code and no document. The only changes this skill makes are the rebase, the board writes, and the session title named below.

## Steps

1. Rebase the current branch onto local `main` with `git rebase main`. Do this every time, before reading the board. If git refuses because of uncommitted changes, or the rebase conflicts, run `git rebase --abort` if a rebase is in progress, report which files are involved, and stop before touching the board. Do not stash, discard, or resolve conflicts without the user.
2. Find your board person. Your instructions state it on a line of the form `Task board id: <id>`. If no such line is in your context, ask the user which person to claim as. Do not infer it from the git user, the account, an email address, or the owner of other tasks. Check that the id is one of `people` in `meta/config`; if it is not, ask.
3. Read the board as its rules say for the start of work. Then query the ready tasks (`todo` with an empty `waitingOn`) and the tasks in `doing`, `review`, or `blocked`.
4. Choose the task.
   - If the user gave a key, take that task. If it is not `todo`, still waits on another task, or is owned by another person, do not claim it; report its state and stop.
   - If the user gave no key, drop the ready tasks that `meta/rules` says you must not take and the ones owned by another person, then take the one with the lowest key number. List the other ready tasks in the report, one line each.
   - If there is no task you may take, report which tasks are in progress and what each waiting task waits on, and stop.
5. Read `details/<key>`, then claim the task in one batch as the board rules say. Put the worktree name in `claimedBy.session` and the current branch in `branch`. In the claim message, say which branch you work on and what you will read first. If the claim fails because someone else took the task, go back to step 4. Once the claim succeeds, rename this session to the task's key and board title (`<key> <title>`) if you have a tool that renames the current session, such as `set_session_title` with `session_id` `self`. Without such a tool, skip this.
6. Read what the task needs. Start from the `spec` location in `details`, read the documents `AGENTS.md` requires before work on that area, then trace the source: the types and functions the task will change, their callers, and the related tests. When a document describes the current behavior, confirm it in the source and report every mismatch.
7. Check overlap. For each task in `doing` or `review` that another session holds, compare the files this task will change with the files changed on its `branch` (`git diff --name-only main...<branch>`) and, when its worktree is on this machine, with its uncommitted changes. If they overlap, post a `note` in that task's thread naming the files before you report.
8. Design the change by the rules of [movist-code](../movist-code/SKILL.md): build only what the task asks, reuse what exists, work out both the smallest change and the simplest result, and call out any change with a wide blast radius. Do not implement.
9. Post the proposal in the task's thread in at most three lines: type `question` when the user must decide something, `update` otherwise. Then report and stop.

## Report

Write the report in Korean. Refer to types, functions, and properties by their real identifiers. Leave out a part that has nothing to say; for a small task each part is one line.

- First line: the task key and title, and the kind of work: `코드 변경`, `문서만`, or `결정만`. State the kind before anything else, so the user knows whether there is code to change.
- `작업 위치:` the worktree path, the branch, and what the rebase did (from which commit to which, or already up to date).
- `지금 동작:` what the source shows, with `file:line`. Include mismatches between the documents and the source.
- `제안:` the design. For each decision, say what changes for the end user. When the smallest change and the simplest result differ, give both as `최소 수정안` and `단순 흐름안`, and for each say what it changes and how the control flow reads afterward.
- `고칠 곳:` the types, files, and documents to change. Mark a change to a public or package contract, a stored format, or actor isolation. When the two designs differ, list this per design.
- `겹치는 작업:` the task key, its holder, and the shared files. Give the choices: go on and coordinate in the thread, or release this task and take the next one.
- `정하실 것:` what only the user can decide, each with your recommendation. When the two designs differ, the choice between them comes first.
- `확인 못 한 것:` one line each.
- `이 작업 뒤:` the tasks that have this one in `deps` and what else each still waits on. If the user gave no key, the other ready tasks.

## After the report

- When the user confirms or changes the design, post the confirmed design in the thread as an `update`, naming the files to change. If the task's work is the decision itself, write the confirmed answers where its `acceptance` says.
- Implement only when the user says so, following movist-code. When asked to review, follow [movist-review](../movist-review/SKILL.md). Commit and merge only when the user says so, with [movist-commit](../movist-commit/SKILL.md) and [movist-ff-main](../movist-ff-main/SKILL.md).
- Change the task's status after that as the board rules and `meta/rules` say.
- If the user chooses to release the task, leave it as the board rules say for unfinished work, then start again from step 4.
