---
name: movist-changelog
description: Movist Pro 릴리스의 최종 소스와 의존성 상태를 확인해 한국어 CHANGELOG.md를 작성하고, 사용자가 초안을 확인한 뒤 명시적으로 지시하면 그 파일을 원문으로 cleanroom과 www의 한국어·영어·중국어 간체·번체 릴리스 노트를 갱신한다. Movist Pro changelog나 릴리스 노트 작성·번역 요청에 사용하며 appcast, 배포, push, 제품 코드 변경에는 사용하지 않는다.
---

# Movist Pro 릴리스 노트

한국어 `CHANGELOG.md`를 원문으로 삼아 다음 두 단계를 순서대로 수행한다. 최초 요청이 전체 작업을 말하더라도 아직 존재하지 않는 한국어 초안을 확인받은 것으로 보지 않는다.

기본 경로는 다음과 같다. 사용자가 다른 checkout이나 경로를 지정하면 그 지시를 따른다.

- 제품 저장소: 현재 작업 중인 Movist checkout
- cleanroom: `~/devel/Movist/Support/cleanroom`
- www: `~/devel/Movist/Support/www`

## 1. 한국어 CHANGELOG 작성

먼저 세 저장소의 `git status --short --branch`, staged diff, unstaged diff와 untracked 파일을 확인한다. 대상 버전이 제품 저장소의 HEAD·작업 트리, cleanroom, www 중 어디까지 반영됐는지도 확인해 완료된 단계를 반복하거나 버전 절을 중복 추가하지 않는다. 기존 변경을 reset, stash, stage하거나 덮어쓰지 않는다.

제품 저장소에서 `CHANGELOG.md`에 직전 버전 절을 추가한 커밋을 이전 릴리스 기준으로 삼고, 대상 릴리스 커밋을 확정한 뒤 그 사이의 로그와 실제 diff를 조사한다.

- 커밋 제목만 릴리스 노트로 옮기지 않는다. 이전 버전과 최종 트리, 실제 실행 경로를 비교해 신규 기능, 기본값 변경, 버그 수정, 내부 변경을 구분한다.
- 이미 지원되던 기능, 빠진 기본값, 내부 정리와 의존성 갱신 자체를 새 기능으로 쓰지 않는다.
- 직접 수정이 revert됐더라도 후속 package pin이나 외부 의존성으로 옮겨졌을 수 있다. 최종 릴리스가 고정한 의존성 리비전과 그 구현까지 확인한다.
- Movist와 Movist Pro 버전이 다를 수 있으므로 Pro 버전과 릴리스 날짜를 릴리스 커밋 및 프로젝트 버전에서 확인한다.
- Pro 전용 변경에는 기존 문서 형식대로 `(Pro)`를 표시한다.

대상 Pro 버전의 릴리스 커밋과 프로젝트 버전이 없거나 서로 맞지 않으면 임의로 HEAD를 릴리스 기준으로 삼지 않는다. 사용자가 특정 커밋 또는 “현재 HEAD까지”를 기준으로 확정할 때까지 CHANGELOG를 쓰지 않는다.

`CHANGELOG.md`의 맨 위에 기존 형식과 문체로 한국어 항목만 추가한다. 메뉴·환경설정·기능 이름은 실제 `.strings`, XIB와 `Docs/Localization.md`를 우선한다. 이 단계에서는 번역, cleanroom, www, appcast를 수정하지 않는다.

`git diff --check`와 `CHANGELOG.md`의 staged/unstaged diff를 확인하고, 포함·제외 판단 중 사용자가 검토해야 할 내용과 한국어 초안을 제시한 뒤 멈춘다. 수정 의견이 있으면 고친 뒤 다시 검증해 제시한다. 2단계는 초안을 제시한 뒤 사용자가 cleanroom·www 갱신을 명시적으로 지시했을 때만 시작한다. 초안에 대한 동의나 일반적인 진행 표현은 그 지시로 보지 않는다.

## 2. CHANGELOG로 cleanroom과 www 갱신

현재 `CHANGELOG.md` 파일의 대상 버전 절을 번역 원문으로 삼는다. 세 저장소의 상태를 다시 확인하고, 이전 실행에서 일부 HTML이 이미 만들어졌다면 현재 원문과 대조해 이어서 고친다. 번역 중 한국어의 의미 오류를 발견하면 HTML 작업을 멈추고 `CHANGELOG.md` 수정안을 제시한다.

영어, 한국어, `zh-Hans`, `zh-Hant` 네 언어를 같은 항목 수와 순서로 작성한다. 영어·중국어 용어는 각 locale의 실제 앱 문자열과 `Docs/Localization.md`에서 확인한다.

- cleanroom에 `MovistPro_<version>.{ko,en,zh-Hans,zh-Hant}.html` 네 파일을 만든다. 직전 릴리스 파일을 그대로 복사하고 맨 위에 새 버전 절만 추가하며, 다운로드 링크는 넣지 않는다.
- www의 `changelog.html`, `ko/changelog.html`, `zh-Hans/changelog.html`, `zh-Hant/changelog.html` 맨 위에 새 버전을 추가한다. 주변 릴리스의 DMG URL 형식과 locale별 다운로드 라벨을 그대로 따른다.
- 기존 파일의 UTF-8, 들여쓰기, 줄바꿈과 EOF 형식을 보존한다.

`scripts/verify_release_notes.py --version <version> --previous-version <previous-version>`으로 구조적 검사를 실행한다. 스크립트는 `CHANGELOG.md`의 한국어 항목과 한국어 HTML의 일치, locale별 cleanroom/www 일치와 네 언어 항목 수, 대상 버전 DMG URL과 다운로드 라벨, 이전 이력과 EOF 보존을 검사하므로 이 항목들은 다시 직접 확인하지 않는다. 스크립트가 통과하면 다음만 직접 확인한다.

1. 각 locale의 메뉴·환경설정·기능 이름이 실제 앱 문자열과 맞는지
2. 세 저장소의 status, staged/unstaged diff와 `git diff --check`

문서 작업만으로 제품 빌드를 실행하지 않는다.

cleanroom과 www는 수정·검증한 결과를 사용자에게 보여 준다. `appcast.xml`, 업로드·배포와 push는 별도 명시 요청이 있을 때만 수행한다.
