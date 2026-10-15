# Movist Skills

Movist 개발, 커밋, 브랜치 통합과 Movist Pro 릴리스 노트 작업에 쓰는
Codex skill 모음입니다. 각 skill은 독립 폴더로 설치되지만, 서로 참조하는
작업 흐름이 있어 네 개를 함께 설치하는 방식을 권장합니다.

## 포함된 skill

- `movist-code`: 기존 구현 재사용과 CPU 비용을 우선하는 Movist 구현 절차
- `movist-commit`: 관련 변경만 골라 커밋하는 Movist 커밋 절차
- `movist-ff-main`: 커밋 후 로컬 `main`에 rebase하고 fast-forward 병합
- `movist-changelog`: 승인 기반 Movist Pro 다국어 릴리스 노트 절차

`movist-code`가 필요할 때 참조하는 `movist-cpu-benchmark`는 선택 의존성이며
이 저장소에는 포함하지 않습니다.

## 설치

Codex의 `skill-installer`로 네 skill을 한 번에 설치합니다.

```sh
python3 "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo moosoy/movist-skills \
  --path skills/movist-code \
         skills/movist-commit \
         skills/movist-ff-main \
         skills/movist-changelog
```

하나만 설치하려면 `--path`에 해당 폴더 하나만 지정합니다. 다만
`movist-code`와 `movist-ff-main`은 `movist-commit`을 참조하므로 함께
설치해야 전체 흐름이 동작합니다.

설치기는 같은 이름의 대상 폴더를 덮어쓰지 않습니다. 이미 설치된 skill을
갱신할 때는 기존 폴더를 직접 백업하거나 제거한 뒤 다시 설치하세요. 설치를
마치면 Codex를 다시 시작해야 새 skill이 인식됩니다.

## 실행 환경

- Git CLI
- `movist-changelog` 검증 스크립트용 Python 3.10 이상
- `movist-changelog`가 사용하는 Movist, cleanroom, www Git 저장소

`movist-changelog`는 현재 Movist checkout의 `CHANGELOG.md`를 기본으로
사용합니다. cleanroom과 www의 기본 경로는 각각
`~/devel/Movist/Support/cleanroom`, `~/devel/Movist/Support/www`이며 명령행
인자로 바꿀 수 있습니다.

## 라이선스

[MIT License](LICENSE)
