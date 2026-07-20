#!/usr/bin/env python3
"""Runtime introspection helpers for the Home Assistant app bootstrap."""

from __future__ import annotations

import os
import pathlib
import platform
import sys
import sysconfig


def _python_abi() -> int:
    print(
        "{}.{}:{}:{}".format(
            sys.version_info.major,
            sys.version_info.minor,
            platform.machine(),
            sysconfig.get_config_var("SOABI") or "unknown",
        )
    )
    return 0


def _uses_venv(site_packages: str) -> int:
    try:
        import repeater
    except ImportError:
        return 1
    if repeater.__file__ is None:
        return 1
    try:
        package_path = pathlib.Path(repeater.__file__).resolve()
        sp_path = pathlib.Path(site_packages).resolve()
        in_venv = os.path.commonpath((package_path, sp_path)) == str(sp_path)
    except (OSError, TypeError, ValueError):
        in_venv = False
    return 0 if in_venv else 1


def _package_path() -> int:
    import repeater

    file = repeater.__file__
    if file is None:
        print("[openhop-repeater-ha] ERROR: repeater package has no __file__", file=sys.stderr)
        return 1
    print(pathlib.Path(file).resolve())
    return 0


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if len(raw_args) < 1:
        print(
            "usage: runtime_info.py <python-abi|uses-venv|package-path> [args...]",
            file=sys.stderr,
        )
        return 2

    command = raw_args[0]

    if command == "python-abi":
        return _python_abi()

    if command == "uses-venv":
        if len(raw_args) != 2:
            print(
                "usage: runtime_info.py uses-venv <site_packages_path>",
                file=sys.stderr,
            )
            return 2
        return _uses_venv(raw_args[1])

    if command == "package-path":
        return _package_path()

    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
