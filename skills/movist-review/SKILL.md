---
name: movist-review
description: Review a Movist code change (staged changes, a commit, a branch, or named files). Report only what meets the fixed blocker criteria, give a verdict of pass or needs changes, and on re-review look only at what changed since the previous review. The review itself changes no code. Not for reviewing design or plan documents, or for cause investigation.
---

# Movist change review

Decide whether a change can be committed. The implementation standard is [movist-code](../movist-code/SKILL.md); this skill decides which violations of it to report and when the review ends. The user is the person who asked for the review; the end user is the person using the app. The review itself changes no code.

## The line

1. A blocker is only something that meets an entry of `Blocker criteria` below and comes with the evidence that entry requires. No evidence, no blocker. The review reports nothing else as a problem to fix.
2. With no blockers the verdict is pass. Do not attach "would be better" notes to a change that passes.
3. The first review covers the whole change. A re-review covers only what changed since the previous review's `기준점` and whether the previous blockers were fixed.
4. A re-review raises a new blocker only when what changed since the previous review causes it, wherever the blocker shows up. For anything else the only exceptions are a crash, a hang, and data loss, and each is marked `앞 리뷰에서 놓친 것`.
5. When one instruction asked you to review, fix, and review again, end after one re-review. If blockers still remain, do not fix again; report the remaining blockers and what the user can choose for each: fix, leave, or record.

It is a re-review when the conversation holds an earlier review result for the same change or the user gives a `기준점`. Otherwise it is a first review. When the user explicitly asks to review the whole change again, it is a first review too.

A blocker the user declined is closed. Do not count it toward the verdict or raise it again.

## Blocker criteria

| ID | What blocks | Evidence the blocker must give |
| --- | --- | --- |
| C1 Behavior | The requested behavior is wrong or missing. The change breaks an existing caller or test. | Which input or operation produces which wrong result |
| C2 Stability | A crash, a hang, data loss, a resource that is never released, or a violated lifetime or concurrency invariant. | The execution path that actually reaches it |
| C3 Cost | A copy, allocation, lock, thread or actor hop, condition test on every call, or timer was added on a playback hot path (code that runs tens to hundreds of times per second while media plays). Or an operation became slower by an amount the end user can notice. | For a hot path, how often it is called and what work was added. For a slower operation, which operation, at what input size, and what extra work it now does |
| C4 Unneeded code | A feature, option, generalization, defensive code, or compatibility code outside the request; dead code; a pass-through wrapper; leftover temporary instrumentation. | That the requested behavior stays the same when it is removed |
| C5 Duplication | Something was newly written although an existing implementation, the standard library, or a platform API does the same job. | Where the existing implementation is |
| C6 Scope | A change unrelated to the request is mixed in. | That no part of the request needs that change |
| C7 Boundary | It breaks a module dependency direction or a contract set by the repository's documents. Implementation was put in one type although another type owns that job. Test-only code is in product code. | Where the broken rule is; or which type owns the job and on what basis; or where the test-only code is |
| C8 Name | A name says something different from what the code does. | What the name says and what the code does |
| C9 Document | A public or package contract or behavior visible to callers changed, but its owner document did not. | The changed contract and the document location to update |

To report "this can be simpler" under C4 or C5, give a concrete alternative that does the same job with less code and fewer branches, and how much it removes. If you cannot write the alternative, do not report it.

## Do not report

- A situation unlikely to happen in real use.
- A demand to add defensive code, rollback, retry, a validation step, or a test. When one is needed to fix C1 or C2, write it in that blocker's fix.
- An optimization the compiler does, and a cost that is neither on a playback hot path nor noticeable to the end user.
- A demand for measurement on a question that reasoning about the design decides, where measuring adds nothing.
- Precision the end user cannot perceive, and anything without effect at the scale the product is used at, such as one person's library.
- Behavior and supported range already decided by the request or the documents.
- Lint and formatting, taste about names and structure, and "consider" suggestions.
- A defect that already existed on lines the change did not touch. If it is at the C1 or C2 level, write one line under `기록할 것`.
- Work already assigned to a later step of the plan.
- Something the change itself records in `Docs/Issues` with a `처리` value, unless it is a crash, a hang, or data loss.
- A platform-specific special case outside the current work.

## Steps

1. Identify the target. Review what the user named. If nothing was named, review the staged changes; if there are none, the uncommitted changes; if there are none, the last commit. Do not raise blockers on changes outside the target. If the change has untracked files, ask the user to stage them before a first review, because `기준점` leaves them out.
2. Find out what this change was asked to do, from the conversation, the `Docs/Issues` entry it fixes, the feature's `Docs/Working` document, or the commit message. If you cannot tell, ask. C4 and C6 are judged against the request.
3. Even when reviewing inside the conversation that implemented the change, read the actual diff, not your memory of it. In a re-review the diff is `git diff <기준점>`. Read the callers of each changed function, the code it calls, and the related tests. When a function signature, return value, or behavior changed, find every caller.
4. In the first review, check the whole change against C1 through C9 in order. Be complete here, because a re-review cannot raise these later.
5. For each candidate blocker, read the lines again and confirm the evidence: the caller really exists, the value can really reach that state, the code really is unused. Re-check the evidence of any claim that contradicts what the user knows.
6. When reading cannot settle a C1 or C2 suspicion, settle it with a run that changes nothing in the repository, such as one test method or a read-only command, within movist-code's verification rules. If no such run settles it, do not report it as a blocker; write it under `확인 못 한 것` with what would settle it. Drop every other unconfirmed suspicion.

## Report

Write the report in Korean. Refer to types, functions, and properties by their real identifiers, and do not use nicknames made up during the review. Write each item so that it reads on its own.

- `이 변경이 하는 일:` two or three sentences.
- `판정: 통과` or `판정: 수정 필요 (차단 N개)`.
- List C1, C2, and C3 blockers first and number all blockers. Give each blocker these four parts, one or two sentences each.
  - Title, ID, and location (`file:line`).
  - `상황`: which file or operation shows what. For C4 through C9, what is unneeded or which rule it breaks, and why.
  - `근거`: what the blocker criterion requires.
  - `고치는 방법`: the smallest fix that works. If code shrinks, by how much; if it grows, why.
- `기록할 것:` real defects on lines the change did not touch. They are candidates for `Docs/Issues` and do not count toward the verdict.
- `확인 못 한 것:` one line each, if any.
- `기준점:` the hash that `git stash create` prints, or the `HEAD` hash when it prints nothing. It records the working tree at the time of the review without changing it. Always write it, also when the verdict is pass.
- In a re-review, first mark each previous blocker `고쳐짐`, `남음`, or `받아들이지 않음`.

With no blockers, write `이 변경이 하는 일:`, `판정: 통과`, one line on what you read and confirmed, any `기록할 것` and `확인 못 한 것`, and `기준점:`.

## After the review

- When told to fix, fix only the blockers, following movist-code. Record `기록할 것` items in `Docs/Issues` when the user decides to.
- When asked to review and then commit if nothing is wrong, commit with [movist-commit](../movist-commit/SKILL.md) only when the verdict is pass. Otherwise do not commit; report.
