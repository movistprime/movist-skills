#!/usr/bin/env python3
"""ko/의 한국어 번역본이 영어 원문과 같은 판인지 확인한다.

번역본 첫 줄은 원문 경로와 번역할 때의 원문 sha256을 적는다. 원문이 바뀌면 실패한다.
번역을 고친 뒤 `--update`로 기록된 hash를 새로 쓴다.
"""
import hashlib
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
header = re.compile(r"<!-- 원문: (\S+) sha256=(\w*) -->")
update = "--update" in sys.argv
problems = []
for ko in sorted((root / "ko").glob("*.md")):
    lines = ko.read_text().split("\n")
    match = header.fullmatch(lines[0])
    if not match:
        problems.append(f"{ko.name}: 첫 줄에 원문 표시가 없다")
        continue
    digest = hashlib.sha256((root / match[1]).read_bytes()).hexdigest()
    if digest == match[2]:
        continue
    if update:
        lines[0] = f"<!-- 원문: {match[1]} sha256={digest} -->"
        ko.write_text("\n".join(lines))
    else:
        problems.append(f"{ko.name}: {match[1]}이 바뀌었다. 번역을 고친 뒤 scripts/check_ko.py --update를 실행한다")
if problems:
    sys.exit("\n".join(problems))
