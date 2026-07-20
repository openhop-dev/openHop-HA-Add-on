#!/usr/bin/env python3
"""Filesystem path helpers for the Home Assistant app bootstrap."""

from __future__ import annotations

import os
import sys


def _same_path(path_a: str, path_b: str) -> bool:
    try:
        return os.path.samefile(path_a, path_b)
    except OSError:
        return False


def _is_mount(path: str) -> bool:
    return os.path.ismount(path)


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if len(raw_args) < 1:
        print("usage: path_utils.py <same-path|is-mount> [args...]", file=sys.stderr)
        return 2

    command = raw_args[0]

    if command == "same-path":
        if len(raw_args) != 3:
            print(
                "usage: path_utils.py same-path <path1> <path2>", file=sys.stderr
            )
            return 2
        return 0 if _same_path(raw_args[1], raw_args[2]) else 1

    if command == "is-mount":
        if len(raw_args) != 2:
            print("usage: path_utils.py is-mount <path>", file=sys.stderr)
            return 2
        return 0 if _is_mount(raw_args[1]) else 1

    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
