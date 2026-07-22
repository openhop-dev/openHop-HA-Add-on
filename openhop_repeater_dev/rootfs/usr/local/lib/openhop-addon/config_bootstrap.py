#!/usr/bin/env python3
"""Safely create and upgrade the openHop Repeater configuration."""

from __future__ import annotations

import copy
import os
import pathlib
import re
import secrets
import sys
import tempfile
from typing import Any

import yaml

_SECRET_KEYS = ("admin_password", "guest_password", "jwt_secret")


def _load_mapping(path: pathlib.Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"invalid {label}: document root must be a mapping")
    repeater = value.get("repeater")
    if not isinstance(repeater, dict):
        raise ValueError(f"invalid {label}: repeater must be a mapping")
    if not str(repeater.get("node_name", "")).strip():
        raise ValueError(f"invalid {label}: repeater.node_name must be non-empty")
    if "radio_type" not in value:
        raise ValueError(f"invalid {label}: radio_type is required")
    return value


def _new_credentials() -> dict[str, str]:
    return {
        "admin_password": secrets.token_urlsafe(24),
        "guest_password": secrets.token_urlsafe(24),
        "jwt_secret": secrets.token_hex(32),
    }


def _replace_template_credentials(source: str) -> str:
    credentials = _new_credentials()
    for key in _SECRET_KEYS:
        pattern = re.compile(rf"(?m)^([ \t]*{re.escape(key)}:[ \t]*).*$")
        source, count = pattern.subn(rf'\g<1>"{credentials[key]}"', source)
        if count != 1:
            raise ValueError(
                f"invalid packaged template: expected exactly one active {key} setting"
            )
    return source


def _merge_defaults(defaults: Any, current: Any) -> Any:
    if isinstance(defaults, dict) and isinstance(current, dict):
        merged = copy.deepcopy(defaults)
        for key, value in current.items():
            if key in merged:
                merged[key] = _merge_defaults(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(current)


def _apply_missing_credentials(
    merged: dict[str, Any], current: dict[str, Any]
) -> None:
    merged_security = merged.setdefault("repeater", {}).setdefault("security", {})
    if not isinstance(merged_security, dict):
        raise ValueError("invalid merged configuration: repeater.security must be a mapping")

    current_repeater = current.get("repeater", {})
    current_security = (
        current_repeater.get("security", {})
        if isinstance(current_repeater, dict)
        else {}
    )
    if not isinstance(current_security, dict):
        raise ValueError("invalid existing configuration: repeater.security must be a mapping")

    generated = _new_credentials()
    for key in ("admin_password", "guest_password"):
        if key not in current_security:
            merged_security[key] = generated[key]
    if not str(current_security.get("jwt_secret", "")).strip():
        merged_security["jwt_secret"] = generated["jwt_secret"]


def _atomic_write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", text=True
    )
    temporary_path = pathlib.Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def bootstrap_config(
    template_path: str | pathlib.Path, config_path: str | pathlib.Path
) -> str:
    """Create or merge config_path and return created, merged, or unchanged."""
    template = pathlib.Path(template_path)
    config = pathlib.Path(config_path)
    defaults = _load_mapping(template, "packaged template")

    if not config.exists() or config.stat().st_size == 0:
        generated_text = _replace_template_credentials(
            template.read_text(encoding="utf-8")
        )
        temporary_check = yaml.safe_load(generated_text)
        if not isinstance(temporary_check, dict):
            raise ValueError("generated configuration is not a mapping")
        _atomic_write(config, generated_text)
        return "created"

    current = _load_mapping(config, "existing configuration")
    merged = _merge_defaults(defaults, current)
    _apply_missing_credentials(merged, current)
    if merged == current:
        os.chmod(config, 0o600)
        return "unchanged"

    merged_text = yaml.safe_dump(merged, sort_keys=False, allow_unicode=True)
    _atomic_write(config, merged_text)
    return "merged"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3 or args[0] != "bootstrap":
        print(
            "usage: config_bootstrap.py bootstrap <template> <config>",
            file=sys.stderr,
        )
        return 2
    try:
        result = bootstrap_config(args[1], args[2])
    except (OSError, ValueError) as exc:
        print(f"[openhop-repeater-ha] ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"[openhop-repeater-ha] configuration bootstrap: {result}; path={args[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
