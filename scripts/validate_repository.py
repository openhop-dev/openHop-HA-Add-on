#!/usr/bin/env python3
"""Validate the repository structure without depending on Home Assistant internals."""

from __future__ import annotations

import re
import stat
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
WEBUI = re.compile(r"^(?:https?|\[PROTO:\w+\]):\/\/\[HOST\]:\[PORT:\d+\].*$")
REQUIRED_ADDON_FILES = {
    "CHANGELOG.md",
    "DOCS.md",
    "Dockerfile",
    "README.md",
    "config.yaml",
    "config.yaml.example",
    "icon.png",
    "logo.png",
    "run.sh",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser exception varies
        fail(f"{path.relative_to(ROOT)} is not valid YAML: {exc}")


def validate_repository_metadata() -> None:
    metadata = load_yaml(ROOT / "repository.yaml")
    if not isinstance(metadata, dict):
        fail("repository.yaml must contain a mapping")
    for key in ("name", "url", "maintainer"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            fail(f"repository.yaml is missing a non-empty {key}")


def addon_directories() -> list[Path]:
    return sorted(
        path
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "config.yaml").is_file()
    )


def validate_addon(addon: Path) -> str:
    missing = sorted(name for name in REQUIRED_ADDON_FILES if not (addon / name).exists())
    if missing:
        fail(f"{addon.name} is missing required files: {', '.join(missing)}")

    metadata = load_yaml(addon / "config.yaml")
    if not isinstance(metadata, dict):
        fail(f"{addon.name}/config.yaml must contain a mapping")

    slug = metadata.get("slug")
    if slug != addon.name:
        fail(f"{addon.name}: slug must match directory name, got {slug!r}")
    if not SEMVER.fullmatch(str(metadata.get("version", ""))):
        fail(f"{addon.name}: version must be semantic versioning")
    if metadata.get("schema") is not False:
        fail(f"{addon.name}: schema must be false because config.yaml is the source of truth")
    if "options" in metadata:
        fail(f"{addon.name}: Home Assistant options must not duplicate runtime config.yaml")
    if metadata.get("init") is not True:
        fail(f"{addon.name}: Home Assistant's default container init must remain enabled")
    if metadata.get("full_access") is True:
        redundant = sorted(
            key for key in ("devices", "gpio", "uart", "usb") if key in metadata
        )
        if redundant:
            fail(
                f"{addon.name}: full_access makes these settings redundant: "
                + ", ".join(redundant)
            )
    if metadata.get("backup") != "cold":
        fail(f"{addon.name}: backup must be cold for consistent runtime data")
    if "venv/**" not in metadata.get("backup_exclude", []):
        fail(f"{addon.name}: generated update venv should be excluded from backups")
    if metadata.get("map") != [
        {"type": "app_config", "path": "/config", "read_only": False}
    ]:
        fail(f"{addon.name}: only the writable app_config mount is expected")

    webui = metadata.get("webui")
    if not isinstance(webui, str) or not WEBUI.fullmatch(webui):
        fail(
            f"{addon.name}: webui must use a Supervisor port placeholder, "
            "for example http://[HOST]:[PORT:8000]/"
        )

    arch = metadata.get("arch")
    if not isinstance(arch, list) or not {"aarch64", "amd64"}.issubset(set(arch)):
        fail(f"{addon.name}: aarch64 and amd64 must be supported")

    template = load_yaml(addon / "config.yaml.example")
    if not isinstance(template, dict):
        fail(f"{addon.name}/config.yaml.example must contain a mapping")
    if "repeater" not in template or "radio_type" not in template:
        fail(f"{addon.name}: full upstream configuration template is incomplete")

    run_script = addon / "run.sh"
    if not run_script.stat().st_mode & stat.S_IXUSR:
        fail(f"{addon.name}/run.sh is not executable")
    systemctl_shim = (
        addon / "rootfs" / "usr" / "local" / "bin" / "openhop-container-systemctl"
    )
    if not systemctl_shim.is_file() or not systemctl_shim.stat().st_mode & stat.S_IXUSR:
        fail(f"{addon.name}: container systemctl compatibility shim is missing")
    run_text = run_script.read_text(encoding="utf-8")
    for required_fragment in (
        "/data/venv",
        "/opt/openhop_repeater/venv",
        ".update_channel",
        "\"${VENV_PYTHON}\" -m repeater.main",
        "repeater requested a restart; rerunning branch bootstrap",
    ):
        if required_fragment not in run_text:
            fail(f"{addon.name}/run.sh is missing branch runtime logic: {required_fragment}")

    dockerfile = (addon / "Dockerfile").read_text(encoding="utf-8")
    expected_build_version = f"ARG BUILD_VERSION={metadata['version']}"
    if expected_build_version not in dockerfile:
        fail(
            f"{addon.name}/Dockerfile BUILD_VERSION does not match config.yaml: "
            f"expected {expected_build_version}"
        )
    for required_fragment in (
        "FROM openhop/openhop-repeater:main",
        "COPY config.yaml.example",
        "COPY rootfs /",
        'io.hass.type="app"',
        "openhop-container-systemctl",
    ):
        if required_fragment not in dockerfile:
            fail(f"{addon.name}/Dockerfile is missing: {required_fragment}")

    deprecated_terms = ("addon_config", "addon_configs")
    text_files = [
        ROOT / "README.md",
        ROOT / "repository.yaml",
        addon / "README.md",
        addon / "DOCS.md",
        addon / "config.yaml",
    ]
    for text_file in text_files:
        content = text_file.read_text(encoding="utf-8")
        for deprecated in deprecated_terms:
            if deprecated in content:
                fail(
                    f"{text_file.relative_to(ROOT)} uses deprecated Home Assistant term "
                    f"{deprecated!r}"
                )

    return slug


def main() -> int:
    validate_repository_metadata()
    addons = addon_directories()
    if len(addons) != 1:
        fail(f"expected exactly one add-on directory, found {len(addons)}")

    slugs = [validate_addon(addon) for addon in addons]
    if len(slugs) != len(set(slugs)):
        fail("duplicate add-on slugs detected")

    print(f"Validated {len(addons)} add-on: {slugs[0]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
