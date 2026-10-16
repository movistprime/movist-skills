---
name: movist-ff-main
description: "현재 작업을 커밋하고 로컬 main 위로 rebase한 뒤 main에 fast-forward merge한다. 'commit하고 main으로 rebase한 뒤 ff merge', 'commit, rebase onto main, and ff merge'처럼 전체 통합 순서를 요청할 때 사용한다. 별도 worktree와 기존 staged 변경을 보존하며, push는 별도 요청 범위다."
---

# Movist FF Main

현재 작업에 속한 변경을 커밋하고 작업 브랜치를 로컬 `main` 위로 rebase한 다음, `main`을 `--ff-only`로 전진시킨다. 저장소 경로와 브랜치 이름은 현재 상태에서 찾고 특정 프로젝트의 경로를 하드코딩하지 않는다.

## 범위

- 사용자가 이 순서를 요청하거나 이 스킬의 실행을 지시했다면 커밋·rebase·FF merge는 승인된 범위다. 단계마다 승인을 다시 묻지 않는다. 자동으로 스킬이 선택됐다는 사실만으로 Git 변경을 시작하지 않는다.
- 기준과 통합 대상은 원격이 아닌 로컬 `main`이다. 다른 기준 브랜치에 통합하는 작업에는 이 스킬을 사용하지 않는다.
- 이 스킬은 통합 전 코드 리뷰를 수행하지 않는다. 커밋이 필요하면 리뷰는 `movist-commit` 실행 전에 끝난 것으로 보고, 커밋할 변경이 없으면 스킬 실행 요청을 사용자의 리뷰 완료와 통합 결정으로 본다. 어느 경우에도 rebase 전에 `main...HEAD`의 정확성·품질을 다시 리뷰하거나 별도 승인을 기다리지 않는다.

## 실행 순서

### 1. 저장소 상태 확인

`git status --short --branch`로 현재 브랜치와 변경 유무를 확인하고, 현재 브랜치와 main의 HEAD를 기록한다. 진행 중인 다른 rebase·merge를 임의로 이어가거나 취소하지 않는다. `main`이 없으면 임의로 원격이나 다른 브랜치를 대입하지 말고 기준을 확인한다. 새 커밋이 필요한데 현재가 `main` 또는 detached HEAD라면 먼저 작업 브랜치를 만든다. 저장소 규칙이 없으면 실행 환경의 기본 작업 브랜치 관례를 따른다.

### 2. 관련 변경만 커밋

[movist-commit](../movist-commit/SKILL.md)을 읽고 현재 작업에 속한 변경에 적용한다. 커밋할 변경이 없으면 빈 커밋을 만들지 않고 기존 작업 커밋으로 계속한다.

### 3. 작업 브랜치를 main 위로 rebase

`git rebase main`을 실행한다. 이미 최신 기준이면 변경 없이 끝난 결과를 그대로 인정한다. 남은 무관한 작업이 rebase를 막으면 현재 worktree에서 staged/unstaged/untracked 구분을 보존하는 임시 stash를 사용할 수 있다. 보관 식별자를 기록하고, 복원에는 `git stash apply --index`를 사용하며 복원 확인 전에는 보관본을 삭제하지 않는다. 다른 worktree의 변경을 stash하거나 reset하지 않는다.

충돌은 현재 작업과 main 양쪽의 의도를 보존해 해결하고 관련 검증을 실행한다. 전체 `ours`/`theirs`, `rebase --skip`, 강제 reset으로 통과시키지 않는다. 제품 결정이 필요한 충돌은 파일과 선택지를 정리해 해당 결정만 묻는다.

### 4. main에서 fast-forward merge

`git worktree list --porcelain`으로 현재 main worktree를 찾는다. 해당 폴더의 branch가 main이고 작업 폴더가 깨끗한지 확인한 뒤 그 경로에서 `git merge --ff-only <작업 브랜치>`를 실행한다. 경로와 브랜치 이름은 실제 값으로 치환하고 셸에서 인용한다.

main worktree에 다른 작업의 미커밋 변경이 있으면 그 폴더를 변경하지 않고 병합 단계만 보류한다. 5단계에서 가능한 복원을 마친 뒤 이미 완료한 커밋·rebase와 남은 조건을 보고한다. main을 checkout한 worktree가 없다면 현재 작업 폴더가 깨끗할 때 main으로 전환해 병합할 수 있다. 이 경우 병합 후 원래 작업 브랜치로 돌아온다.

Rebase 후 main이 전진해 FF가 거절되면 새 main HEAD와 커밋 범위를 확인하고 한 번 더 rebase·FF merge한다. 계속 main이 바뀌거나 충돌의 의미를 확정할 수 없으면 현재 상태를 보고한다. merge commit이나 강제 ref 이동으로 방식을 바꾸지 않는다.

### 5. 복원과 결과 확인

임시 보관한 변경이 있으면 원래 worktree·브랜치에서 복원하고 기존 staged/unstaged/untracked 상태가 유지됐는지 확인한다. 복원 충돌이 있으면 stash를 보존하고 통합 성공과 미완료 복원을 구분해 보고한다.

`git rev-list --left-right --count main...<작업 브랜치>`가 `0 0`이고 `git diff --exit-code main <작업 브랜치>`가 성공하는지 확인한다. 두 worktree의 최종 상태를 점검한다. 처음부터 무관한 변경이 있었다면 그 변경의 보존을 확인하고 깨끗하다고 보고하지 않는다.

결과는 커밋 hash·제목, rebase 결과와 충돌 여부, main의 이전·이후 HEAD와 그 사이에 통합된 커밋 목록(`git log --oneline <이전 main>..main`), worktree 상태로 짧게 정리한다. Push를 수행했는지 분명히 하고, fetch 없이 확인한 원격 대비 차이는 로컬 remote-tracking ref 기준임을 구분한다.
