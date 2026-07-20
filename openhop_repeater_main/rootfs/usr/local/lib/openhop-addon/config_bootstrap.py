#!/usr/bin/env python3
"""Configuration bootstrap helpers for the Home Assistant app."""

from __future__ import annotations

import pathlib
import re
import secrets
import sys


def _replace_secret(source: str, key: str, value: str) -> str:
    pattern = re.compile(rf"(?m)^([ \t]*{re.escape(key)}:[ \t]*).*$")
    replacement = rf'\g<1>"{value}"'
    updated, count = pattern.subn(replacement, source)
    if count != 1:
        raise RuntimeError(f"could not locate exactly one {key} setting in template")
    return updated


def _generate_secrets(template_path: str) -> int:
    path = pathlib.Path(template_path)
    text = path.read_text(encoding="utf-8")
    text = _replace_secret(text, "admin_password", secrets.token_urlsafe(24))
    text = _replace_secret(text, "guest_password", secrets.token_urlsafe(24))
    text = _replace_secret(text, "jwt_secret", secrets.token_hex(32))
    path.write_text(text, encoding="utf-8")
    return 0


def _validate_config(config_path: str) -> int:
    path = pathlib.Path(config_path)
    try:
        import yaml

        config = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("the document root must be a mapping")
        repeater = config.get("repeater")
        if not isinstance(repeater, dict):
            raise ValueError("repeater must be a mapping")
        if not str(repeater.get("node_name", "")).strip():
            raise ValueError("repeater.node_name must be a non-empty value")
        security = repeater.get("security")
        if security is not None and not isinstance(security, dict):
            raise ValueError("repeater.security must be a mapping")
        if "radio_type" not in config:
            raise ValueError("radio_type is required")
    except Exception as exc:
        print(
            f"[openhop-repeater-ha] ERROR: invalid configuration: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "[openhop-repeater-ha] configuration: "
        f"node_name={repeater.get('node_name', 'missing')}; "
        f"radio_type={config.get('radio_type', 'missing')}; "
        f"path={path}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    if len(raw_args) < 1:
        print(
            "usage: config_bootstrap.py <generate-secrets|validate-config> [args...]",
            file=sys.stderr,
        )
        return 2

    command = raw_args[0]

    if command == "generate-secrets":
        if len(raw_args) != 2:
            print(
                "usage: config_bootstrap.py generate-secrets <template_path>",
                file=sys.stderr,
            )
            return 2
        try:
            return _generate_secrets(raw_args[1])
        except (OSError, RuntimeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    if command == "validate-config":
        if len(raw_args) != 2:
            print(
                "usage: config_bootstrap.py validate-config <config_path>",
                file=sys.stderr,
            )
            return 2
        return _validate_config(raw_args[1])

    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
