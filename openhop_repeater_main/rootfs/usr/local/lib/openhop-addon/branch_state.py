#!/usr/bin/env python3
"""Small, dependency-free helpers for the Home Assistant add-on bootstrap."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

_SAFE_REF = re.compile(r"^[A-Za-z0-9._/-]+$")
_DIST_INFO_GLOB = "openhop_repeater-*.dist-info/direct_url.json"


def is_valid_git_ref(ref: str) -> bool:
    """Validate a branch-like Git ref without invoking a shell or Git."""
    if not ref or len(ref.encode("utf-8")) > 255:
        return False
    if ref == "@" or ref.startswith("-"):
        return False
    if not _SAFE_REF.fullmatch(ref):
        return False
    if ".." in ref or "@{" in ref or "//" in ref:
        return False
    if ref.startswith(("/", ".")) or ref.endswith(("/", ".", ".lock")):
        return False

    for component in ref.split("/"):
        if not component or component.startswith(".") or component.endswith(".lock"):
            return False
    return True


def _candidate_direct_urls(site_packages: Path) -> Iterable[Path]:
    return sorted(
        site_packages.glob(_DIST_INFO_GLOB),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )


def installed_ref(site_packages: Path) -> str:
    """Return the requested VCS revision for the newest installed distribution."""
    for direct_url_path in _candidate_direct_urls(site_packages):
        try:
            data = json.loads(direct_url_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        url = str(data.get("url", "")).lower().rstrip("/")
        if not url.endswith(("openhop_repeater.git", "openhop_repeater")):
            continue

        vcs_info = data.get("vcs_info")
        if not isinstance(vcs_info, dict):
            continue

        revision = vcs_info.get("requested_revision")
        if isinstance(revision, str) and revision:
            return revision
    return ""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("ref")

    installed = subparsers.add_parser("installed-ref")
    installed.add_argument("site_packages", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "validate":
        return 0 if is_valid_git_ref(args.ref) else 1
    if args.command == "installed-ref":
        print(installed_ref(args.site_packages))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
