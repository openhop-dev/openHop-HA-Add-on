#!/usr/bin/env python3
"""Small, dependency-free helpers for the Home Assistant app bootstrap."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

_SAFE_REF = re.compile(r"^[A-Za-z0-9._/-]+$")
_DIST_INFO_GLOB = "openhop_repeater-*.dist-info/direct_url.json"
_ALLOWED_REPOSITORY_URLS = {
    "https://github.com/openhop-dev/openhop_repeater",
    "https://github.com/openhop-dev/openhop_repeater.git",
}
_PIP_INSTALL_PREFIX = (
    "openhop_repeater[hardware] @ "
    "git+https://github.com/openhop-dev/openhop_repeater.git@"
)


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
        if (
            not component
            or component.startswith(".")
            or component.endswith((".", ".lock"))
        ):
            return False
    return True


def _candidate_direct_urls(site_packages: Path) -> Iterable[Path]:
    candidates: list[tuple[int, Path]] = []
    for path in site_packages.glob(_DIST_INFO_GLOB):
        try:
            modified = path.stat().st_mtime_ns
        except OSError:
            continue
        candidates.append((modified, path))
    ordered = sorted(candidates, key=lambda item: item[0], reverse=True)
    return (path for _, path in ordered)


def installed_ref(site_packages: Path) -> str:
    """Return the requested VCS revision for the newest installed distribution."""
    for direct_url_path in _candidate_direct_urls(site_packages):
        try:
            data = json.loads(direct_url_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        url = str(data.get("url", "")).lower().rstrip("/")
        if url not in _ALLOWED_REPOSITORY_URLS:
            continue

        vcs_info = data.get("vcs_info")
        if not isinstance(vcs_info, dict) or vcs_info.get("vcs") != "git":
            continue

        revision = vcs_info.get("requested_revision")
        if isinstance(revision, str) and is_valid_git_ref(revision):
            return revision
    return ""


def are_safe_pip_args(args: list[str]) -> bool:
    """Allow only version checks and the branch-update commands the app issues."""
    if args in (["--version"], ["-V"]):
        return True

    allowed_prefixes = (
        ["install", "--upgrade", "--no-cache-dir"],
        ["install", "--upgrade", "--force-reinstall", "--no-cache-dir"],
    )
    matching_prefix = next(
        (prefix for prefix in allowed_prefixes if args[:-1] == prefix),
        None,
    )
    if matching_prefix is None or len(args) != len(matching_prefix) + 1:
        return False

    install_spec = args[-1]
    if not install_spec.startswith(_PIP_INSTALL_PREFIX):
        return False
    return is_valid_git_ref(install_spec[len(_PIP_INSTALL_PREFIX) :])


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("ref")

    installed = subparsers.add_parser("installed-ref")
    installed.add_argument("site_packages", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    # pip options are intentionally opaque here. argparse otherwise tries to
    # interpret flags such as --version before REMAINDER can capture them.
    if raw_args[:1] == ["validate-pip-args"]:
        return 0 if are_safe_pip_args(raw_args[1:]) else 1

    args = _build_parser().parse_args(raw_args)
    if args.command == "validate":
        return 0 if is_valid_git_ref(args.ref) else 1
    if args.command == "installed-ref":
        print(installed_ref(args.site_packages))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
