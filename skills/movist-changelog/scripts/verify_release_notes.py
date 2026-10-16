#!/usr/bin/env python3

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys


LOCALES = {
    "ko": ("ko/changelog.html", "Download"),
    "en": ("changelog.html", "Download"),
    "zh-Hans": ("zh-Hans/changelog.html", "下载"),
    "zh-Hant": ("zh-Hant/changelog.html", "下載"),
}


def fail(message: str) -> None:
    raise AssertionError(message)


def git_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path if path.is_dir() else path.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"{path}: not inside a Git repository")
    return Path(result.stdout.strip()).resolve()


def relative_to_repo(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        fail(f"{path}: not inside {repo}")


def git_ref_bytes(repo: Path, reference: str, relative_path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{reference}:{relative_path}"],
        cwd=repo,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        fail(f"{repo}: cannot read {reference}:{relative_path}")
    return result.stdout


def website_baseline(
    repo: Path, relative_path: str, version: str, previous_version: str
) -> tuple[str, bytes]:
    result = subprocess.run(
        ["git", "rev-list", "--first-parent", "HEAD", "--", relative_path],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"{repo}: cannot inspect history for {relative_path}")
    revisions = result.stdout.splitlines()
    if not revisions:
        fail(f"{repo}: no history for {relative_path}")

    for revision in revisions:
        data = git_ref_bytes(repo, revision, relative_path)
        release = first_release_version(
            decode_utf8(data, f"{revision}:{relative_path}")
        )
        if release == version:
            continue
        if release == previous_version:
            return revision, data
        fail(
            f"{relative_path}: release before {version} is {release}, "
            f"not {previous_version}"
        )
    fail(f"{relative_path}: cannot find baseline {previous_version}")


def decode_utf8(data: bytes, label: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeError as error:
        fail(f"{label}: not UTF-8: {error}")


def read_utf8(path: Path) -> tuple[bytes, str]:
    try:
        data = path.read_bytes()
    except OSError as error:
        fail(f"{path}: {error}")
    text = decode_utf8(data, str(path))
    if not re.search(r'<meta\s+charset=["\']utf-8["\']\s*/?>', text, re.I):
        fail(f"{path}: missing UTF-8 meta tag")
    return data, text


def first_release_version(text: str) -> str:
    match = re.search(
        r"<h5\b[^>]*>\s*([0-9]+(?:\.[0-9]+)+)(?=\s|<).*?</h5>",
        text,
        re.I | re.S,
    )
    if not match:
        fail("cannot find the first release heading")
    return match.group(1)


class ReleaseFragmentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.roots: list[str] = []
        self.items: list[str] = []
        self.item_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"h5", "a", "ul", "li"}:
            fail(f"unexpected <{tag}> in release section")
        if not self.stack:
            self.roots.append(tag)
        if tag == "a" and (not self.stack or self.stack[-1] != "h5"):
            fail("<a> must be inside <h5>")
        if tag == "li":
            if not self.stack or self.stack[-1] != "ul" or self.item_parts is not None:
                fail("<li> must be directly inside <ul>")
            self.item_parts = []
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            fail(f"unexpected </{tag}> in release section")
        self.stack.pop()
        if tag == "li":
            assert self.item_parts is not None
            self.items.append(re.sub(r"\s+", " ", "".join(self.item_parts)).strip())
            self.item_parts = None

    def handle_data(self, data: str) -> None:
        if self.item_parts is not None:
            self.item_parts.append(data)

    def finish(self) -> list[str]:
        if self.stack:
            fail(f"unclosed <{self.stack[-1]}> in release section")
        if self.roots != ["h5", "ul"]:
            fail(f"release section roots must be h5, ul; found {self.roots}")
        if not self.items:
            fail("release section contains no items")
        return self.items


def release_block(text: str, version: str, label: str) -> tuple[int, int, str, list[str]]:
    escaped = re.escape(version)
    heading_pattern = re.compile(
        rf"<h5\b[^>]*>\s*{escaped}(?=\s|<).*?</h5>",
        re.I | re.S,
    )
    headings = list(heading_pattern.finditer(text))
    if len(headings) != 1:
        fail(f"{label}: expected one {version} heading, found {len(headings)}")

    heading = headings[0]
    ul_match = re.match(r"\s*<ul\b[^>]*>.*?</ul>", text[heading.end() :], re.I | re.S)
    if not ul_match:
        fail(f"{label}: {version} heading is not followed by a list")

    section_end = heading.end() + ul_match.end()
    line_start = text.rfind("\n", 0, heading.start()) + 1
    if text[line_start : heading.start()].strip():
        fail(f"{label}: unexpected text before {version} heading")
    line_end = text.find("\n", section_end)
    block_end = len(text) if line_end < 0 else line_end + 1
    section = text[heading.start() : section_end]

    parser = ReleaseFragmentParser()
    parser.feed(section)
    parser.close()
    items = parser.finish()
    for line_number, line in enumerate(section.splitlines(), 1):
        if line.rstrip(" \t") != line:
            fail(f"{label}: release section line {line_number} has trailing whitespace")
    return line_start, block_end, section, items


def remove_release_block(text: str, version: str, label: str) -> tuple[bytes, str, list[str]]:
    start, end, section, items = release_block(text, version, label)
    return (text[:start] + text[end:]).encode("utf-8"), section, items


def markdown_items(text: str, version: str) -> list[str]:
    escaped = re.escape(version)
    matches = list(
        re.finditer(
            rf"^## {escaped}(?: \([^\n]+\))?\n\n(.*?)(?=\n## |\Z)",
            text,
            re.M | re.S,
        )
    )
    if len(matches) != 1:
        fail(f"expected one CHANGELOG section for {version}, found {len(matches)}")
    items = [
        line[2:] for line in matches[0].group(1).splitlines() if line.startswith("- ")
    ]
    if not items:
        fail(f"no CHANGELOG items for {version}")
    return items


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Movist Pro localized release-note structure and preservation."
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--previous-version", required=True)
    parser.add_argument(
        "--changelog", type=Path, default=Path.cwd() / "CHANGELOG.md"
    )
    parser.add_argument(
        "--cleanroom",
        type=Path,
        default=Path.home() / "devel/Movist/Support/cleanroom",
    )
    parser.add_argument(
        "--www", type=Path, default=Path.home() / "devel/Movist/Support/www"
    )
    args = parser.parse_args()
    args.changelog = args.changelog.expanduser().resolve()
    args.cleanroom = args.cleanroom.expanduser().resolve()
    args.www = args.www.expanduser().resolve()

    cleanroom_repo = git_root(args.cleanroom)
    www_repo = git_root(args.www)

    source_items = markdown_items(
        decode_utf8(args.changelog.read_bytes(), str(args.changelog)), args.version
    )

    locale_items: dict[str, list[str]] = {}
    for locale, (web_relative_from_root, download_label) in LOCALES.items():
        clean_path = args.cleanroom / f"MovistPro_{args.version}.{locale}.html"
        previous_path = (
            args.cleanroom / f"MovistPro_{args.previous_version}.{locale}.html"
        )
        web_path = args.www / web_relative_from_root

        clean_bytes, clean_text = read_utf8(clean_path)
        previous_bytes, previous_text = read_utf8(previous_path)
        web_bytes, web_text = read_utf8(web_path)

        previous_relative = relative_to_repo(previous_path, cleanroom_repo)
        previous_head_bytes = git_ref_bytes(cleanroom_repo, "HEAD", previous_relative)
        previous_head_text = decode_utf8(
            previous_head_bytes, f"HEAD:{previous_relative}"
        )
        if previous_bytes != previous_head_bytes:
            fail(f"{locale}: previous cleanroom template has uncommitted changes")
        if first_release_version(previous_head_text) != args.previous_version:
            fail(f"{locale}: previous cleanroom file does not start with {args.previous_version}")

        web_relative = relative_to_repo(web_path, www_repo)
        baseline_ref, baseline_web_bytes = website_baseline(
            www_repo, web_relative, args.version, args.previous_version
        )

        clean_without_release, clean_section, clean_items = remove_release_block(
            clean_text, args.version, str(clean_path)
        )
        web_without_release, web_section, web_items = remove_release_block(
            web_text, args.version, str(web_path)
        )
        if clean_without_release != previous_head_bytes:
            fail(f"{locale}: cleanroom differs from the prior template beyond the new release")
        if web_without_release != baseline_web_bytes:
            fail(
                f"{locale}: www differs from baseline {baseline_ref[:12]} "
                "beyond the new release"
            )
        if clean_items != web_items:
            fail(f"{locale}: cleanroom and www items differ")
        if re.search(r"<a\b|href\s*=", clean_section, re.I):
            fail(f"{locale}: cleanroom section contains a link")

        expected_url = f"https://update.cocoable.com/MovistPro_{args.version}.dmg"
        expected_link = re.compile(
            rf'<a\b[^>]*href=["\']{re.escape(expected_url)}["\'][^>]*>'
            rf"\s*{re.escape(download_label)}\s*</a>",
            re.I,
        )
        if not expected_link.search(web_section):
            fail(f"{locale}: missing expected download link or label")

        locale_items[locale] = clean_items
        print(f"{locale}: {len(clean_items)} items, cleanroom/www match")

    locale_counts = {locale: len(items) for locale, items in locale_items.items()}
    if len(set(locale_counts.values())) != 1:
        fail(f"locale item counts differ: {locale_counts}")

    if locale_items["ko"] != source_items:
        fail("Korean HTML does not match CHANGELOG")

    print("Korean HTML matches CHANGELOG")
    print("All structural release-note checks passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
