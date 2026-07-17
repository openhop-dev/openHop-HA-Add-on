#!/bin/sh
set -eu

log() {
    printf '%s\n' "[openhop-repeater-ha] $*"
}

warn() {
    printf '%s\n' "[openhop-repeater-ha] WARNING: $*" >&2
}

fatal() {
    printf '%s\n' "[openhop-repeater-ha] ERROR: $*" >&2
    exit 1
}

ADDON_CONFIG_DIR="${OPENHOP_ADDON_CONFIG_DIR:-/config}"
DATA_DIR="${OPENHOP_ADDON_DATA_DIR:-/data}"
RUNTIME_CONFIG_DIR="${OPENHOP_ADDON_RUNTIME_CONFIG_DIR:-/etc/openhop_repeater}"
FIRMWARE_DATA_DIR="${OPENHOP_ADDON_FIRMWARE_DATA_DIR:-/var/lib/openhop_repeater}"
UPDATE_VENV_LINK="${OPENHOP_ADDON_UPDATE_VENV_LINK:-/opt/openhop_repeater/venv}"
TEMPLATE_CONFIG_FILE="${OPENHOP_ADDON_TEMPLATE_CONFIG:-/usr/share/openhop-repeater/config.yaml.example}"
BRANCH_HELPER="${OPENHOP_ADDON_BRANCH_HELPER:-/usr/local/lib/openhop-addon/branch_state.py}"
SYSTEM_PYTHON="${OPENHOP_ADDON_SYSTEM_PYTHON:-$(command -v python3)}"
BASE_SITE_PACKAGES_GLOB="${OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB:-/home/*/.local/lib/python*/site-packages}"
UPSTREAM_GIT_URL="${OPENHOP_ADDON_UPSTREAM_GIT_URL:-https://github.com/openhop-dev/openhop_repeater.git}"
DEFAULT_BRANCH="${OPENHOP_ADDON_DEFAULT_BRANCH:-main}"

# The upstream container image exports a build-time package-specific
# setuptools-scm version. Package-specific overrides take precedence over the
# runtime version selected by the in-app updater, so do not pass the image
# build version into branch builds.
unset SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENHOP_REPEATER

CONFIG_FILE="${ADDON_CONFIG_DIR}/config.yaml"
CHANNEL_FILE="${DATA_DIR}/.update_channel"
VENV_DIR="${DATA_DIR}/venv"
PYTHON_MARKER="${VENV_DIR}/.openhop-ha-python"

mkdir -p "${ADDON_CONFIG_DIR}" "${DATA_DIR}"

if [ ! -r "${TEMPLATE_CONFIG_FILE}" ]; then
    fatal "bundled configuration template is missing: ${TEMPLATE_CONFIG_FILE}"
fi
if [ ! -r "${BRANCH_HELPER}" ]; then
    fatal "branch helper is missing: ${BRANCH_HELPER}"
fi
if [ -z "${SYSTEM_PYTHON}" ] || [ ! -x "${SYSTEM_PYTHON}" ]; then
    fatal "python3 is not available"
fi

if [ ! -f "${CONFIG_FILE}" ]; then
    cp "${TEMPLATE_CONFIG_FILE}" "${CONFIG_FILE}"
    "${SYSTEM_PYTHON}" - "${CONFIG_FILE}" <<'PY'
from __future__ import annotations

import pathlib
import secrets
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace(
    'admin_password: "admin123"',
    f'admin_password: "{secrets.token_urlsafe(24)}"',
    1,
)
text = text.replace(
    'guest_password: "guest123"',
    f'guest_password: "{secrets.token_urlsafe(24)}"',
    1,
)
path.write_text(text, encoding="utf-8")
PY
    chmod 0600 "${CONFIG_FILE}" || true
    log "created ${CONFIG_FILE} from the bundled full configuration template"
    log "generated unique admin and guest passwords; read them from config.yaml"
fi

migrate_directory_contents() {
    source_dir="$1"
    target_dir="$2"

    [ -d "${source_dir}" ] || return 0
    mkdir -p "${target_dir}"
    if "${SYSTEM_PYTHON}" - "${source_dir}" "${target_dir}" <<'PY'
import os
import sys

try:
    same = os.path.samefile(sys.argv[1], sys.argv[2])
except OSError:
    same = False
raise SystemExit(0 if same else 1)
PY
    then
        return 0
    fi

    for source_entry in "${source_dir}"/.[!.]* "${source_dir}"/..?* "${source_dir}"/*; do
        [ -e "${source_entry}" ] || continue
        entry_name="$(basename "${source_entry}")"
        target_entry="${target_dir}/${entry_name}"
        if [ -e "${target_entry}" ] || [ -L "${target_entry}" ]; then
            warn "kept existing ${target_entry}; did not overwrite it during migration"
            continue
        fi
        mv "${source_entry}" "${target_entry}"
    done
}

replace_directory_with_symlink() {
    link_path="$1"
    target_path="$2"
    migrate_existing="${3:-false}"

    mkdir -p "$(dirname "${link_path}")" "${target_path}"

    if [ -e "${link_path}" ] && [ ! -L "${link_path}" ]; then
        if "${SYSTEM_PYTHON}" - "${link_path}" <<'PY'
import os
import sys

raise SystemExit(0 if os.path.ismount(sys.argv[1]) else 1)
PY
        then
            if "${SYSTEM_PYTHON}" - "${link_path}" "${target_path}" <<'PY'
import os
import sys

try:
    same = os.path.samefile(sys.argv[1], sys.argv[2])
except OSError:
    same = False
raise SystemExit(0 if same else 1)
PY
            then
                return 0
            fi
            fatal "refusing to replace mounted path ${link_path}"
        fi
    fi

    if [ -L "${link_path}" ]; then
        if [ "$(readlink "${link_path}")" = "${target_path}" ]; then
            return 0
        fi
        rm -f "${link_path}"
    elif [ -e "${link_path}" ]; then
        if [ "${migrate_existing}" = "true" ] && [ -d "${link_path}" ]; then
            migrate_directory_contents "${link_path}" "${target_path}"
        fi
        rm -rf "${link_path}"
    fi

    ln -s "${target_path}" "${link_path}"
}

# The firmware updater hard-codes /var/lib/openhop_repeater. Home Assistant's
# persistent app storage is /data, so keep the firmware path as a symlink.
replace_directory_with_symlink "${FIRMWARE_DATA_DIR}" "${DATA_DIR}" true

PYTHON_ABI="$("${SYSTEM_PYTHON}" - <<'PY'
import platform
import sys
import sysconfig

print(
    "{}.{}:{}:{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        platform.machine(),
        sysconfig.get_config_var("SOABI") or "unknown",
    )
)
PY
)"
VENV_ABI=""
if [ -r "${PYTHON_MARKER}" ]; then
    VENV_ABI="$(cat "${PYTHON_MARKER}" 2>/dev/null || true)"
fi

if [ ! -x "${VENV_DIR}/bin/python" ] || [ "${VENV_ABI}" != "${PYTHON_ABI}" ]; then
    if [ -e "${VENV_DIR}" ]; then
        log "rebuilding persistent update environment for Python ${PYTHON_ABI}"
        rm -rf "${VENV_DIR}"
    else
        log "creating persistent update environment for Python ${PYTHON_ABI}"
    fi
    "${SYSTEM_PYTHON}" -m venv --system-site-packages "${VENV_DIR}"
    printf '%s\n' "${PYTHON_ABI}" > "${PYTHON_MARKER}"
fi

# The in-app updater installs to /opt/openhop_repeater/venv. Point that path at
# /data/venv so branch installs survive add-on upgrades and container restarts.
replace_directory_with_symlink "${UPDATE_VENV_LINK}" "${VENV_DIR}" false

VENV_PYTHON="${VENV_DIR}/bin/python"
VENV_PIP="${VENV_DIR}/bin/pip"
VENV_SITE_PACKAGES="$(${VENV_PYTHON} -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
mkdir -p "${VENV_SITE_PACKAGES}"

# The upstream image installs its packaged main build in the non-root runtime
# user's local site-packages. A .pth file exposes that build as a fallback while
# preserving normal venv precedence for a branch installed by the updater.
PTH_TMP="${VENV_SITE_PACKAGES}/openhop-base-image.pth.tmp"
PTH_FILE="${VENV_SITE_PACKAGES}/openhop-base-image.pth"
: > "${PTH_TMP}"
# Intentional word splitting expands the configured glob.
# shellcheck disable=SC2086
for site_dir in ${BASE_SITE_PACKAGES_GLOB}; do
    if [ -d "${site_dir}" ]; then
        printf '%s\n' "${site_dir}" >> "${PTH_TMP}"
    fi
done
if [ -d /opt/openhop_repeater/repeater ]; then
    printf '%s\n' /opt/openhop_repeater >> "${PTH_TMP}"
fi
mv "${PTH_TMP}" "${PTH_FILE}"

if [ ! -f "${CHANNEL_FILE}" ]; then
    printf '%s\n' "${DEFAULT_BRANCH}" > "${CHANNEL_FILE}"
fi
SELECTED_BRANCH="$(head -n 1 "${CHANNEL_FILE}" 2>/dev/null | tr -d '\r\n' || true)"
if ! "${SYSTEM_PYTHON}" "${BRANCH_HELPER}" validate "${SELECTED_BRANCH}"; then
    warn "invalid persisted branch '${SELECTED_BRANCH}'; resetting to '${DEFAULT_BRANCH}'"
    SELECTED_BRANCH="${DEFAULT_BRANCH}"
    printf '%s\n' "${SELECTED_BRANCH}" > "${CHANNEL_FILE}"
fi

installed_branch() {
    "${SYSTEM_PYTHON}" "${BRANCH_HELPER}" installed-ref "${VENV_SITE_PACKAGES}"
}

can_import_repeater() {
    "${VENV_PYTHON}" -c 'import repeater.main' >/dev/null 2>&1
}

INSTALLED_BRANCH="$(installed_branch)"
PREVIOUS_IMPORT_OK=false
if can_import_repeater; then
    PREVIOUS_IMPORT_OK=true
fi

NEEDS_BRANCH_INSTALL=false
if [ "${SELECTED_BRANCH}" = "${DEFAULT_BRANCH}" ]; then
    # No venv distribution means the packaged :main build is active. A venv
    # distribution from another branch must be replaced when returning to main.
    if [ -n "${INSTALLED_BRANCH}" ] && [ "${INSTALLED_BRANCH}" != "${SELECTED_BRANCH}" ]; then
        NEEDS_BRANCH_INSTALL=true
    fi
elif [ "${INSTALLED_BRANCH}" != "${SELECTED_BRANCH}" ]; then
    NEEDS_BRANCH_INSTALL=true
fi

if [ "${NEEDS_BRANCH_INSTALL}" = "true" ]; then
    log "activating branch '${SELECTED_BRANCH}' in the persistent update environment"
    INSTALL_SPEC="openhop_repeater[hardware] @ git+${UPSTREAM_GIT_URL}@${SELECTED_BRANCH}"
    if GIT_TERMINAL_PROMPT=0 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_DEFAULT_TIMEOUT=30 \
        "${VENV_PIP}" install --upgrade --force-reinstall --no-cache-dir "${INSTALL_SPEC}"; then
        log "installed branch '${SELECTED_BRANCH}'"
    else
        warn "could not install branch '${SELECTED_BRANCH}'; retaining the last runnable build"
        if [ "${PREVIOUS_IMPORT_OK}" != "true" ] || ! can_import_repeater; then
            fatal "the requested branch failed to install and no runnable fallback is available"
        fi
    fi
fi

if ! can_import_repeater; then
    fatal "openHop Repeater cannot be imported from either the persistent venv or the base image"
fi

ACTIVE_BRANCH="$(installed_branch)"
if [ -z "${ACTIVE_BRANCH}" ]; then
    ACTIVE_BRANCH="${DEFAULT_BRANCH} (packaged image)"
fi
ACTIVE_VERSION="$(${VENV_PYTHON} -c 'from importlib.metadata import PackageNotFoundError, version
try:
    print(version("openhop_repeater"))
except PackageNotFoundError:
    print("unknown")')"
IMPORT_PATH="$(${VENV_PYTHON} -c 'import pathlib, repeater; print(pathlib.Path(repeater.__file__).resolve())')"
log "selected branch: ${SELECTED_BRANCH}; active branch: ${ACTIVE_BRANCH}; version: ${ACTIVE_VERSION}"
log "runtime package: ${IMPORT_PATH}"

if [ -L "${RUNTIME_CONFIG_DIR}" ]; then
    if [ "$(readlink "${RUNTIME_CONFIG_DIR}")" != "${ADDON_CONFIG_DIR}" ]; then
        rm -f "${RUNTIME_CONFIG_DIR}"
    fi
elif [ -e "${RUNTIME_CONFIG_DIR}" ]; then
    rm -rf "${RUNTIME_CONFIG_DIR}"
fi
if [ ! -L "${RUNTIME_CONFIG_DIR}" ]; then
    mkdir -p "$(dirname "${RUNTIME_CONFIG_DIR}")"
    ln -s "${ADDON_CONFIG_DIR}" "${RUNTIME_CONFIG_DIR}"
fi

"${VENV_PYTHON}" - "${CONFIG_FILE}" <<'PY'
from __future__ import annotations

import pathlib
import sys

config_path = pathlib.Path(sys.argv[1])
try:
    import yaml

    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
except Exception as exc:
    print(f"[openhop-repeater-ha] ERROR: invalid configuration: {exc}", file=sys.stderr)
    raise SystemExit(1)

repeater = config.get("repeater") or {}
print(
    "[openhop-repeater-ha] configuration: "
    f"node_name={repeater.get('node_name', 'missing')}; "
    f"radio_type={config.get('radio_type', 'missing')}; "
    f"path={config_path}"
)
PY

cd "${DATA_DIR}"

# The firmware deliberately exits its process after an in-app update or restart
# request. Keep PID 1 alive long enough to rerun this bootstrap so the selected
# branch becomes active without depending on an external container restart.
CHILD_PID=""
STOP_REQUESTED=false
# Invoked indirectly by the TERM/INT trap below.
# shellcheck disable=SC2329
forward_stop() {
    STOP_REQUESTED=true
    if [ -n "${CHILD_PID}" ]; then
        kill -TERM "${CHILD_PID}" 2>/dev/null || true
    fi
}
trap forward_stop TERM INT

"${VENV_PYTHON}" -m repeater.main --config "${RUNTIME_CONFIG_DIR}/config.yaml" &
CHILD_PID=$!
EXIT_CODE=0
wait "${CHILD_PID}" || EXIT_CODE=$?

if [ "${STOP_REQUESTED}" = "true" ]; then
    wait "${CHILD_PID}" 2>/dev/null || true
    exit 0
fi

if [ "${EXIT_CODE}" -eq 0 ]; then
    log "repeater requested a restart; rerunning branch bootstrap"
    sleep 1
    exec "$0"
fi

fatal "repeater exited unexpectedly with status ${EXIT_CODE}"
