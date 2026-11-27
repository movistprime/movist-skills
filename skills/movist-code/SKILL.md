---
name: movist-code
description: Implement features, fix confirmed bugs, and refactor in Movist. Build only what was asked with the simplest control flow, reuse existing code first, and keep playback CPU cost down. Use movist-review to review a change. Not for cause investigation or performance measurement alone.
---

# Movist implementation and refactoring

Finish everything the request needs with the least new code. Follow the working repository's instruction files (`AGENTS.md`, `CLAUDE.md`, and so on) and the edit and verification scope the user set.

## Terms

- The user: the person who gave you the task.
- End user: the person using the app.
- Playback hot path: code that runs tens to hundreds of times per second while media plays.
- Simpler control flow: fewer branches, states, call layers, and thread or actor hops.

## Scope

- Build only what was asked. If a feature, option, generalization, defensive code, or refactoring outside the request seems necessary, say what you want to add and why, and get approval before adding it.
- The callers, tests, fixtures, and documents the change must reach are part of the request. Do not leave them out.
- Before finishing, revert your own edits outside the request. If one turned out to be needed, report it and why. Never touch changes you did not make.
- When the work needs a change with a wide blast radius that the request did not call for, such as actor isolation across several types, a public contract, or a stored format, announce it and get approval before making it.
- If asked only for a design, do not implement. If told to stop, stop at once.
- Do not fix a symptom by guessing while its root cause is unconfirmed. Before adding code that hides a symptom, find the root cause in the whole code path and fix it there.

## The smallest complete change

Take the first of these that works.

1. Does it need to exist? First see whether removing an option, branch, or feature makes the control flow simpler. If it looks removable, ask the user.
2. Does it already exist? Check the affected call paths and which type owns the data and state, and use the existing function, type, constant, default, or fallback that does the same job. Do not build a near-copy; add a missing capability to the module that owns it.
3. Does the standard library or a platform API do it? Use that. Do not adopt a general-purpose component for capabilities this code does not need.
4. If it is still needed, write the minimum that works.

- Add an abstraction, defensive check, compatibility code, retry, cache, or rollback only when a current requirement, a real execution condition, or a contract that must hold explains why it is needed. Do use shared code that removes real duplication and makes responsibility clearer.
- Do not add code that defends against a failure that almost never happens or after which the end user can simply try again. Surface the failure and return without attempting recovery: an alert when the end user started the operation, a log otherwise. Keep what must hold on failure paths too, such as releasing resources.
- Do not add types, protocols, parameters, or indirection for speculative callers or platforms the product does not target. Keep the ones a planned feature will use.
- Do not add a version, migration, or compatibility code to a stored format that has never shipped or to an API used only inside the repository. Give a new serialized field whose absence is valid an Optional type or a decoding default.
- When macOS and iOS can handle something as the same concept, write shared code. Leave a special case that exists on only one platform as a simple fallback.
- When asked for the same behavior as Movist 2, the shipped app kept in the repository's `__original/`, check the feature's settings, order of operations, and state transitions there. Follow the behavior without dropping or widening it, but find the simplest implementation in the current code.
- If product code grew after the change, check again that all of the added code is needed. If code grew in a change meant to simplify, report why.

## Simplest result first

Design for the result first. Choose the design whose control flow is simplest once the change is in, even when that means rewriting more of the existing code than the smallest edit would. Among designs that are equally simple, choose the one with the fewest edits to the code as it stands.

- The rewriting this takes on the code paths the request changes is part of the request. Cleaning up code the change does not pass through is not.
- A change with a wide blast radius still needs the approval the Scope section asks for.
- When the chosen design rewrites noticeably more than the smallest edit would, say so in one line of the design or work report: what the smallest edit was and what the chosen design makes simpler. Do not ask the user to choose between the two.

## CPU cost and simpler control flow

- On playback hot paths the priority is: lower CPU load in the real app → simpler control flow → less code → easier review. Judge in this order while keeping the feature correct and the lifetime and concurrency invariants intact. Do not, in order to cut lines, add copies, allocations, thread or actor hops, synchronization, or work done inside callbacks on a playback hot path, gather unrelated responsibilities in one object, put several statements on one line with semicolons, or write terse code that needs decoding.
- Judge the value of a CPU optimization by how call frequency and per-call cost affect the real app's CPU load. Put first the paths with large accumulated cost, such as playback hot paths. Do not assume a new API or library path is more efficient.
- Do not complicate the control flow or blur the boundaries of responsibility and object lifetime to save a one-time cost or for a gain that is negligible in the real app. Examples are hand-inlining a function or condensing a calculation the compiler can optimize, and merging function layers that should stay separate. Object initialization at seek, video start, and video end is an example of one-time cost.
- Reduce duplicate defaults, stored state that can be derived from other state, booleans that must stay in sync, pass-through wrappers, arguments that can be computed from an object already held, and extra call layers.
- When cutting needless repeated work of hidden UI or a disabled feature, keep the state and behavior needed when it is turned back on. Before adding unsubscribe and resubscribe or a separate state machine, check whether the existing code path can solve it.

## Names, responsibility, and removal scope

- Make function, argument, and type names show the real behavior and conditions. Make clear who is responsible for a state change and under what condition a callback must be called, and put the implementation where that responsibility lives.
- Do not add implementation to a type that already receives many actions and callbacks, such as a document or app delegate, just because it is convenient. Put it in the type that owns the job, or ask where it should go if no such type exists.
- Represent kinds of values with types, not strings. Do not merge values with different meanings into one case such as `.other`.
- Do not hard-code a tuning value where it is used; name it and define it once. Register setting defaults in one place.
- Do not add a keyword or construct whose effect you cannot explain. Examples are `nonisolated` and `withExtendedLifetime` when you cannot say what goes wrong without them.
- When asked to remove a behavior, do not keep the same behavior by moving it to another layer. When asked only to disable or detach something, do not delete the implementation needed to use it again.
- Clean up only unused APIs inside the requested scope, after checking external use and contracts that must hold. Do not widen the change to unused APIs nearby. Do not keep compatibility code just because something is `public` or `package`, and do not delete something just because it has no caller now.
- Correct artifacts the repository generates by changing the generator and inputs tracked in the repository, so the correction survives regeneration.

## Logs, diagnostics, and test-only code

- Log only what is needed to confirm the cause when a problem occurs. Do not add a timer for logging, accumulated statistics, or a test of the enabled flag on every call of a playback hot path.
- Separate logging and diagnostic code that stays in the product into extension files named `<Type>+Debug.swift` so it does not obscure the product code.
- Remove temporary instrumentation and experimental changes when the investigation ends. When experimenting, disable product code temporarily instead of deleting it.
- Keep code used only by tests in the test target.

## Technical writing and change summaries

- In comments, design explanations, and work reports, refer to a specific type, function, or property by its real identifier. Avoid a translation or generalization that makes the reader guess the target, such as writing “재생 세션” for `PlaybackSession`.
- Keep familiar technical terms such as `IPC`, `actor`, and `callback` as they are. Do not force a Korean translation that blurs the meaning.
- Do not refer to something by a nickname made up during the work. Say which file or input, what the code does, and what the end user sees.
- Write a change summary as the target and the actual change. For example, write “PlaybackSession 주석 정리”, not “재생 세션 소유권 주석 정리”. When explaining object lifetime or a responsibility boundary itself, say concretely who creates, holds, releases, or changes what.
- Commit only when the user says so. When asked to commit, read and follow [movist-commit](../movist-commit/SKILL.md). When asked to review, read and follow [movist-review](../movist-review/SKILL.md).

## Document updates

- This applies in a repository that has the documents named here. When a code change alters a public or package contract, behavior visible to callers, or a wire contract, update its owner document (the matching `*API.md` or `*Spec.md` in `Docs/3.0`) at that document's level of detail and touch no other document. When status or completion conditions change, update the matching area row of `Docs/3.0/Migration-Plan.md` too. If the feature being implemented has a `Docs/Working` document linked from the Migration Plan, read its relevant sections first; in the commit that carries a step's code, move the implemented contract to the API document and the decision to the Design document, then delete that part and the finished step from the working document. Write verification results only in the work report, and record remaining defects and limits in `Docs/Issues` with a `처리` value. When you fix an Issues entry, move it to the `해결된 항목` table in the same commit and do not write the commit hash.

## Comments

- Do not add a comment that repeats what the code shows. Keep or explain constraints and reasons the code alone does not show, such as locks, cancellation, object lifetime, external or platform behavior, API contracts, and compatibility. Keep copyright headers, shebangs, and formatter or linter directives in their original form.
- Write comments in Korean. If English is clearly clearer, write the new comment in English too, and keep existing English comments. Write one sentence on one line; do not split it across several `///` lines.
- A type comment starts with what the type manages and its role. Do not just list `identity`, `generation`, or “보호 상태”.
- A behavior comment ties to the real function and state and explains the condition, order, and reason. Stay technically accurate and avoid unclear literal translation.

## Verification that fits the change

- Choose the verification the changed behavior and the affected platforms need. When the user asked only for code changes or said they will verify the app, keep to that boundary. Repeat finished verification only when its input changed or a new concern arose.
- Run only the test methods that execute the changed code. Do not retest areas that did not change.
- Verify what you can verify yourself instead of handing it to the user. Check the running app through the IPC or command line the repository provides, and avoid operations that take over the user's screen and keyboard.
- Report separately what a successful build or test shows and what was confirmed on screen, in sound, or on a device. Mark what was not confirmed as unverified.
- Do not ask for measurement on a question that reasoning about the design decides, where measuring adds nothing. Do not require a full build, signing, device verification, or CPU measurement for every change. When measuring and comparing Release app CPU repeatedly, follow the available `movist-cpu-benchmark` skill. Mark a cost improvement that was not measured as an estimate.
