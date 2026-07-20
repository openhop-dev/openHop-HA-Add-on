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
REQUIRED_APP_FILES = {
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


def app_directories() -> list[Path]:
    return sorted(
        path
        for path in ROOT.iterdir()
        if path.is_dir() and (path / "config.yaml").is_file()
    )


def validate_app(app: Path) -> str:
    missing = sorted(name for name in REQUIRED_APP_FILES if not (app / name).exists())
    if missing:
        fail(f"{app.name} is missing required files: {', '.join(missing)}")

    metadata = load_yaml(app / "config.yaml")
    if not isinstance(metadata, dict):
        fail(f"{app.name}/config.yaml must contain a mapping")

    slug = metadata.get("slug")
    if slug != app.name:
        fail(f"{app.name}: slug must match directory name, got {slug!r}")
    if not SEMVER.fullmatch(str(metadata.get("version", ""))):
        fail(f"{app.name}: version must be semantic versioning")
    if metadata.get("schema") is not False:
        fail(f"{app.name}: schema must be false because config.yaml is the source of truth")
    if "options" in metadata:
        fail(f"{app.name}: Home Assistant options must not duplicate runtime config.yaml")
    if metadata.get("init") is not True:
        fail(f"{app.name}: Home Assistant's default container init must remain enabled")
    if metadata.get("full_access") is True:
        redundant = sorted(
            key for key in ("devices", "gpio", "uart", "usb") if key in metadata
        )
        if redundant:
            fail(
                f"{app.name}: full_access makes these settings redundant: "
                + ", ".join(redundant)
            )
    if metadata.get("backup") != "cold":
        fail(f"{app.name}: backup must be cold for consistent runtime data")
    if "venv/**" not in metadata.get("backup_exclude", []):
        fail(f"{app.name}: generated update venv should be excluded from backups")
    if metadata.get("map") != [
        {"type": "addon_config", "path": "/config", "read_only": False}
    ]:
        fail(f"{app.name}: only the writable addon_config mount is expected")

    webui = metadata.get("webui")
    if not isinstance(webui, str) or not WEBUI.fullmatch(webui):
        fail(
            f"{app.name}: webui must use a Supervisor port placeholder, "
            "for example http://[HOST]:[PORT:8000]/"
        )

    arch = metadata.get("arch")
    if not isinstance(arch, list) or not {"aarch64", "amd64"}.issubset(set(arch)):
        fail(f"{app.name}: aarch64 and amd64 must be supported")

    template = load_yaml(app / "config.yaml.example")
    if not isinstance(template, dict):
        fail(f"{app.name}/config.yaml.example must contain a mapping")
    if "repeater" not in template or "radio_type" not in template:
        fail(f"{app.name}: full upstream configuration template is incomplete")

    run_script = app / "run.sh"
    if not run_script.stat().st_mode & stat.S_IXUSR:
        fail(f"{app.name}/run.sh is not executable")
    systemctl_shim = (
        app / "rootfs" / "usr" / "local" / "bin" / "openhop-container-systemctl"
    )
    if not systemctl_shim.is_file() or not systemctl_shim.stat().st_mode & stat.S_IXUSR:
        fail(f"{app.name}: container systemctl compatibility shim is missing")
    pip_wrapper = app / "rootfs" / "usr" / "local" / "bin" / "openhop-venv-pip"
    if not pip_wrapper.is_file() or not pip_wrapper.stat().st_mode & stat.S_IXUSR:
        fail(f"{app.name}: validated venv pip wrapper is missing")

    lib_dir = app / "rootfs" / "usr" / "local" / "lib" / "openhop-addon"
    for helper_name in (
        "branch_state.py",
        "path_utils.py",
        "config_bootstrap.py",
        "runtime_info.py",
    ):
        helper_path = lib_dir / helper_name
        if not helper_path.is_file():
            fail(f"{app.name}: helper script is missing: {helper_name}")

    run_text = run_script.read_text(encoding="utf-8")
    for required_fragment in (
        "/data/venv",
        "/opt/openhop_repeater/venv",
        ".update_channel",
        "\"${VENV_PYTHON}\" -m repeater.main",
        "repeater requested a restart; rerunning branch bootstrap",
        "unset SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENHOP_REPEATER",
        "OPENHOP_ADDON_BUILD_VERSION",
        "OPENHOP_ADDON_BASE_IMAGE_ID_FILE",
        "OPENHOP_ADDON_BASE_RUNTIME_DIR",
        "RUNTIME_COMPATIBILITY",
        ".openhop-ha-branch",
        "runtime_uses_venv",
        "merge_existing_config_with_template",
        "secure_merged_secrets",
        "umask 077",
        "config.yaml.backup",
        "OPENHOP_ADDON_RAPID_RESTARTS",
        "OPENHOP_ADDON_STOP_REQUESTED",
        "refusing a restart loop",
        "OPENHOP_ADDON_VENV_PIP_WRAPPER",
        "validated venv pip wrapper",
        "OPENHOP_ADDON_PATH_UTILS_HELPER",
        "OPENHOP_ADDON_CONFIG_HELPER",
        "OPENHOP_ADDON_RUNTIME_INFO_HELPER",
    ):
        if required_fragment not in run_text:
            fail(f"{app.name}/run.sh is missing branch runtime logic: {required_fragment}")

    dockerfile = (app / "Dockerfile").read_text(encoding="utf-8")
    expected_build_version = f"ARG BUILD_VERSION={metadata['version']}"
    if expected_build_version not in dockerfile:
        fail(
            f"{app.name}/Dockerfile BUILD_VERSION does not match config.yaml: "
            f"expected {expected_build_version}"
        )
    for required_fragment in (
        "FROM openhop/openhop-repeater:main",
        "cp /opt/openhop_repeater/config.yaml.example",
        "cp -a /opt/openhop_repeater/repeater",
        "cp /opt/openhop_repeater/radio-settings.json",
        "cp /opt/openhop_repeater/radio-presets.json",
        "base-runtime",
        "base-image-id",
        "dpkg-query -W",
        "/usr/local/bin/python3",
        "/usr/local/bin/yq",
        "COPY rootfs /",
        'io.hass.type="app"',
        "openhop-container-systemctl",
        "openhop-venv-pip",
        "branch_state.py",
        "path_utils.py",
        "config_bootstrap.py",
        "runtime_info.py",
        "python3-pip",
        "PIP_BREAK_SYSTEM_PACKAGES=1",
        'OPENHOP_ADDON_BUILD_VERSION="${BUILD_VERSION}"',
        'OPENHOP_ADDON_BASE_IMAGE_ID_FILE="/usr/share/openhop-repeater/base-image-id"',
        'OPENHOP_ADDON_BASE_RUNTIME_DIR="/usr/share/openhop-repeater/base-runtime"',
    ):
        if required_fragment not in dockerfile:
            fail(f"{app.name}/Dockerfile is missing: {required_fragment}")

    invalid_terms = ("app_config", "app_configs")
    text_files = [
        ROOT / "README.md",
        ROOT / "repository.yaml",
        app / "README.md",
        app / "DOCS.md",
        app / "config.yaml",
    ]
    for text_file in text_files:
        content = text_file.read_text(encoding="utf-8")
        for invalid in invalid_terms:
            if invalid in content:
                fail(
                    f"{text_file.relative_to(ROOT)} uses invalid Home Assistant term "
                    f"{invalid!r}"
                )

    return app.name


def main() -> int:
    validate_repository_metadata()
    apps = app_directories()
    if len(apps) != 1:
        fail(f"expected exactly one app directory, found {len(apps)}")

    slugs = [validate_app(app) for app in apps]
    if len(slugs) != len(set(slugs)):
        fail("duplicate app slugs detected")

    print(f"Validated {len(apps)} app: {slugs[0]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
