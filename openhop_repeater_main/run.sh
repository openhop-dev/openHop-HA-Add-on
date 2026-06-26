#!/bin/sh
set -eu

ADDON_CONFIG_ROOT="/config"
PERSISTENT_CONFIG_DIR="${ADDON_CONFIG_ROOT}"
PERSISTENT_CONFIG_FILE="${PERSISTENT_CONFIG_DIR}/config.yaml"
TEMPLATE_CONFIG_FILE="/usr/share/openhop-repeater/config.yaml.example"
RUNTIME_CONFIG_DIR="/etc/openhop_repeater"
DATA_DIR="/var/lib/openhop_repeater"
CONFIG_SOURCE="unknown"

mkdir -p "${ADDON_CONFIG_ROOT}"
mkdir -p "${DATA_DIR}"

# Some upstream images install Python packages into a non-root user's local
# site-packages directory. The add-on wrapper starts as root so it can manage
# /etc/openhop_repeater, so make those user-local site-packages visible too.
for site_dir in /home/*/.local/lib/python*/site-packages; do
    if [ -d "${site_dir}" ]; then
        PYTHONPATH="${site_dir}${PYTHONPATH:+:${PYTHONPATH}}"
    fi
done
export PYTHONPATH

if [ ! -f "${PERSISTENT_CONFIG_FILE}" ]; then
    cp "${TEMPLATE_CONFIG_FILE}" "${PERSISTENT_CONFIG_FILE}"
    echo "[openhop-repeater-ha] created ${PERSISTENT_CONFIG_FILE} from bundled template"
    CONFIG_SOURCE="bundled template"
elif [ "${CONFIG_SOURCE}" = "unknown" ]; then
    CONFIG_SOURCE="existing persistent config"
fi

if [ "$(readlink "${RUNTIME_CONFIG_DIR}" 2>/dev/null || true)" != "${PERSISTENT_CONFIG_DIR}" ]; then
    rm -rf "${RUNTIME_CONFIG_DIR}"
    ln -s "${PERSISTENT_CONFIG_DIR}" "${RUNTIME_CONFIG_DIR}"
fi

python3 - "${PERSISTENT_CONFIG_FILE}" "${CONFIG_SOURCE}" <<'PY'
import pathlib
import sys

config_path = pathlib.Path(sys.argv[1])
config_source = sys.argv[2]

radio_type = "unknown"
node_name = "unknown"
try:
    import yaml
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    radio_type = str(config.get("radio_type", "missing"))
    node_name = str(config.get("repeater", {}).get("node_name", "missing"))
except Exception as exc:
    print(f"[openhop-repeater-ha] failed to inspect effective config: {exc}")
else:
    print(
        f"[openhop-repeater-ha] effective config source: {config_source}; "
        f"radio_type={radio_type}; node_name={node_name}; path={config_path}"
    )
PY

exec python3 -m repeater.main --config "${RUNTIME_CONFIG_DIR}/config.yaml"
