---
name: movist-changelog
description: Movist Pro 릴리스의 최종 소스와 의존성 상태를 확인해 한국어 CHANGELOG.md를 작성하고, 사용자 승인 후 그 파일만 커밋한 다음 cleanroom과 www의 한국어·영어·중국어 간체·번체 릴리스 노트를 갱신한다. Movist Pro changelog나 릴리스 노트 작성·번역 요청에 사용하며 appcast, 배포, push, 제품 코드 변경에는 사용하지 않는다.
---

# Movist Pro 릴리스 노트

한국어 원문을 승인 기준점으로 삼아 다음 세 단계를 순서대로 수행한다. 최초 요청이 전체 작업을 말하더라도 아직 존재하지 않는 한국어 초안에 대한 리뷰 승인으로 간주하지 않는다.

기본 경로는 다음과 같다. 사용자가 다른 checkout이나 경로를 지정하면 그 지시를 따른다.

- 제품 저장소: 현재 작업 중인 Movist checkout
- cleanroom: `~/devel/Movist/Support/cleanroom`
- www: `~/devel/Movist/Support/www`

## 1. 한국어 CHANGELOG 작성

먼저 세 저장소의 `git status --short --branch`, staged diff, unstaged diff와 untracked 파일을 확인한다. 대상 버전이 제품 저장소의 HEAD·작업 트리, cleanroom, www 중 어디까지 반영됐는지도 확인해 완료된 단계를 반복하거나 버전 절을 중복 추가하지 않는다. 기존 변경을 reset, stash, stage하거나 덮어쓰지 않는다.

제품 저장소에서 이전 Movist Pro 릴리스와 대상 릴리스 커밋을 확정한 뒤 그 사이의 로그와 실제 diff를 조사한다.

- 커밋 제목만 릴리스 노트로 옮기지 않는다. 이전 버전과 최종 트리, 실제 실행 경로를 비교해 신규 기능, 기본값 변경, 버그 수정, 내부 변경을 구분한다.
- 이미 지원되던 기능, 빠진 기본값, 내부 정리와 의존성 갱신 자체를 새 기능으로 쓰지 않는다.
- 직접 수정이 revert됐더라도 후속 package pin이나 외부 의존성으로 옮겨졌을 수 있다. 최종 릴리스가 고정한 의존성 리비전과 그 구현까지 확인한다.
- Movist와 Movist Pro 버전이 다를 수 있으므로 Pro 버전과 릴리스 날짜를 릴리스 커밋 및 프로젝트 버전에서 확인한다.
- Pro 전용 변경에는 기존 문서 형식대로 `(Pro)`를 표시한다.

대상 Pro 버전의 릴리스 커밋과 프로젝트 버전이 없거나 서로 맞지 않으면 임의로 HEAD를 릴리스 기준으로 삼지 않는다. 사용자가 특정 커밋 또는 “현재 HEAD까지”를 기준으로 확정할 때까지 CHANGELOG를 쓰지 않는다.

`CHANGELOG.md`의 맨 위에 기존 형식과 문체로 한국어 항목만 추가한다. 메뉴·환경설정·기능 이름은 실제 `.strings`, XIB와 `Docs/Localization.md`를 우선한다. 이 단계에서는 번역, cleanroom, www, appcast를 수정하지 않는다.

`git diff --check`와 `CHANGELOG.md`의 staged/unstaged diff를 확인하고, 포함·제외 판단 중 사용자가 검토해야 할 내용과 한국어 초안을 제시한 뒤 멈춘다.

## 2. 리뷰 승인 후 CHANGELOG만 커밋

초안을 제시할 때 “승인하면 이 `CHANGELOG.md`만 커밋하고 다국어 HTML 단계로 진행한다”고 명시한다. 사용자가 그 메시지에 현재 초안을 가리켜 “승인”, “이대로”, “좋아”, “커밋해”라고 답한 경우에만 승인과 커밋 지시로 본다. 일반적인 확인 표현이나 수정 의견은 승인이 아니다. 원문을 고치고 다시 검증한 뒤 새 승인을 기다린다.

승인 뒤에는 다시 상태를 읽어 사용자가 본 초안과 현재 파일이 같은지 확인한다. 최근 `git log`의 메시지 형식과 저장소 지침 파일(`AGENTS.md`, `CLAUDE.md` 등)을 따르고, 승인된 `CHANGELOG.md` 변경만 커밋한다. 한 파일 안에 승인 범위 밖 변경이 섞여 안전하게 분리할 수 없으면 그때만 사용자에게 묻는다.

- unrelated staged 변경이 없으면 승인된 hunk만 stage한다.
- unrelated staged 변경이 있으면 그 index diff를 기록하고 `git commit --only -- CHANGELOG.md`처럼 경로를 한정해 커밋한다. 커밋 전에는 `git diff HEAD -- CHANGELOG.md`가 승인본과 같은지 확인하고, 커밋 뒤에는 unrelated staged diff가 이전과 같은지 대조한다.
- 다른 staged 변경을 함께 커밋하거나 기존 staged/unstaged 구분을 바꾸지 않는다.

커밋 직전에 실제 커밋 후보 diff와 whitespace를 확인한다. rebase, merge, push, amend는 요청 없이는 하지 않는다. 커밋 명령이 timeout이나 불명확한 오류를 반환하면 재시도하기 전에 HEAD와 최근 로그를 확인한다. 커밋 뒤 hash·제목, 실제 커밋 내용과 남은 변경을 확인한다.

## 3. 커밋된 원문으로 cleanroom과 www 갱신

커밋이 성공한 뒤 해당 커밋의 `CHANGELOG.md`를 다시 읽어 번역 원문으로 고정한다. 세 저장소의 상태를 다시 확인하고, 이전 실행에서 일부 HTML이 이미 만들어졌다면 현재 원문과 대조해 이어서 고친다. 번역 중 한국어의 의미 오류를 발견하면 HTML 작업을 멈추고 1단계로 돌아간다. 수정은 다시 승인받아 후속 커밋으로 남기며, 요청 없이 기존 커밋을 amend하지 않는다.

영어, 한국어, `zh-Hans`, `zh-Hant` 네 언어를 같은 항목 수와 순서로 작성한다. 영어·중국어 용어는 각 locale의 실제 앱 문자열과 `Docs/Localization.md`에서 확인한다.

- cleanroom에 `MovistPro_<version>.{ko,en,zh-Hans,zh-Hant}.html` 네 파일을 만든다. 직전 릴리스 파일의 구조와 이전 이력을 보존하고 다운로드 링크는 넣지 않는다.
- www의 `changelog.html`, `ko/changelog.html`, `zh-Hans/changelog.html`, `zh-Hant/changelog.html` 맨 위에 새 버전을 추가한다. 주변 릴리스의 DMG URL 형식과 locale별 다운로드 라벨을 그대로 따른다.
- 기존 파일의 UTF-8, 들여쓰기, 줄바꿈과 EOF 형식을 보존한다.

검증에는 다음을 포함한다.

1. 커밋된 한국어 항목과 한국어 HTML의 항목 수·순서·본문 일치
2. locale별 cleanroom/www 본문 일치와 네 언어 항목 수 일치
3. 실제 앱 용어, 대상 버전 DMG URL과 다운로드 라벨 확인
4. 이전 릴리스 이하 이력과 EOF 보존
5. 세 저장소의 status, staged/unstaged diff와 `git diff --check`

`scripts/verify_release_notes.py --version <version> --previous-version <previous-version>`으로 구조적 검사를 실행한다. 문서 작업만으로 제품 빌드를 실행하지 않는다.

cleanroom과 www는 수정·검증한 상태로 사용자에게 보여 주되 기본 범위에서는 커밋하지 않는다. 각 저장소 커밋, `appcast.xml`, 업로드·배포와 push는 별도 명시 요청이 있을 때만 수행한다.
