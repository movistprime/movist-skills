# Movist Skills

Movist 개발, 커밋, 브랜치 통합과 Movist Pro 릴리스 노트 작업에 쓰는
Agent Skills 모음입니다. 각 skill은 독립 폴더로 설치되지만, 서로 참조하는
작업 흐름이 있어 네 개를 함께 설치하는 방식을 권장합니다.

## 포함된 skill

- `movist-code`: 기존 구현 재사용과 CPU 비용을 우선하는 Movist 구현 절차
- `movist-commit`: 관련 변경만 골라 커밋하는 Movist 커밋 절차
- `movist-ff-main`: 커밋 후 로컬 `main`에 rebase하고 fast-forward 병합
- `movist-changelog`: 승인 기반 Movist Pro 다국어 릴리스 노트 절차

`movist-code`가 필요할 때 참조하는 `movist-cpu-benchmark`는 선택 의존성이며
이 저장소에는 포함하지 않습니다.

## 설치

Agent Skills CLI가 지원하는 agent와 설치할 skill을 대화식으로 선택합니다.

```sh
npx skills add movistprime/movist-skills
```

네 skill을 사용자 범위에 설치하려면 다음과 같이 실행합니다.

```sh
npx skills add movistprime/movist-skills --skill '*' -g
```

하나만 설치하려면 `--skill <name>`을 지정합니다. 다만
`movist-code`, `movist-ff-main`, `movist-changelog`는 `movist-commit`을
참조하므로 함께 설치해야 전체 흐름이 동작합니다.

설치된 skill은 Agent Skills CLI로 갱신합니다.

```sh
npx skills update movist-code movist-commit movist-ff-main movist-changelog -g
```

각 폴더의 `SKILL.md`는 공통 Agent Skills 형식입니다. `agents/openai.yaml`은
OpenAI agent의 표시 metadata이며 skill 동작은 이 파일에 의존하지 않습니다.

## 실행 환경

- Agent Skills CLI를 실행할 Node.js와 npm
- Git CLI
- `movist-changelog` 검증 스크립트용 Python 3.10 이상
- `movist-changelog`가 사용하는 Movist, cleanroom, www Git 저장소

`movist-changelog`는 현재 Movist checkout의 `CHANGELOG.md`를 기본으로
사용합니다. cleanroom과 www의 기본 경로는 각각
`~/devel/Movist/Support/cleanroom`, `~/devel/Movist/Support/www`이며 명령행
인자로 바꿀 수 있습니다.

## 라이선스

[MIT License](LICENSE)
