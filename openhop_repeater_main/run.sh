#!/bin/sh
set -eu
# All newly created files and directories are private by default.  The umask
# persists across the internal exec restart on line ~675 so that a restarted
# bootstrap cannot accidentally create world‑readable runtime artefacts.
umask 077

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
PATH_UTILS_HELPER="${OPENHOP_ADDON_PATH_UTILS_HELPER:-/usr/local/lib/openhop-addon/path_utils.py}"
CONFIG_HELPER="${OPENHOP_ADDON_CONFIG_HELPER:-/usr/local/lib/openhop-addon/config_bootstrap.py}"
RUNTIME_INFO_HELPER="${OPENHOP_ADDON_RUNTIME_INFO_HELPER:-/usr/local/lib/openhop-addon/runtime_info.py}"
SYSTEM_PYTHON="${OPENHOP_ADDON_SYSTEM_PYTHON:-$(command -v python3)}"
BASE_SITE_PACKAGES_GLOB="${OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB:-/home/*/.local/lib/python*/site-packages}"
UPSTREAM_GIT_URL="https://github.com/openhop-dev/openhop_repeater.git"
DEFAULT_BRANCH="${OPENHOP_ADDON_DEFAULT_BRANCH:-main}"
ADDON_BUILD_VERSION="${OPENHOP_ADDON_BUILD_VERSION:-unknown}"
BASE_IMAGE_ID_FILE="${OPENHOP_ADDON_BASE_IMAGE_ID_FILE:-/usr/share/openhop-repeater/base-image-id}"
BASE_RUNTIME_DIR="${OPENHOP_ADDON_BASE_RUNTIME_DIR:-/usr/share/openhop-repeater/base-runtime}"
YQ_CMD="${OPENHOP_ADDON_YQ:-/usr/local/bin/yq}"
VENV_PIP_WRAPPER="${OPENHOP_ADDON_VENV_PIP_WRAPPER:-/usr/local/bin/openhop-venv-pip}"
TEST_WITHOUT_PIP="${OPENHOP_ADDON_TEST_WITHOUT_PIP:-false}"

case "${TEST_WITHOUT_PIP}" in
    true|false) : ;;
    *) fatal "OPENHOP_ADDON_TEST_WITHOUT_PIP must be true or false" ;;
esac

# Install the stop handler before any startup work. Home Assistant may stop the
# app while configuration migration or venv preparation is still in progress.
CHILD_PID=""
STOP_REQUESTED="${OPENHOP_ADDON_STOP_REQUESTED:-false}"
case "${STOP_REQUESTED}" in
    true|false) : ;;
    *) fatal "OPENHOP_ADDON_STOP_REQUESTED must be true or false" ;;
esac
# Invoked indirectly by the TERM/INT trap below.
# shellcheck disable=SC2329
forward_stop() {
    STOP_REQUESTED=true
    export OPENHOP_ADDON_STOP_REQUESTED=true
    if [ -n "${CHILD_PID}" ]; then
        kill -TERM "${CHILD_PID}" 2>/dev/null || true
    fi
}
trap forward_stop TERM INT

# A stop signal can arrive after the final restart check but immediately before
# exec replaces this wrapper. Preserve that state across exec and terminate the
# replacement process before it performs any startup work.
if [ "${STOP_REQUESTED}" = "true" ]; then
    exit 0
fi
unset OPENHOP_ADDON_STOP_REQUESTED

# The upstream container image exports a build-time package-specific
# setuptools-scm version. Package-specific overrides take precedence over the
# runtime version selected by the in-app updater, so do not pass the image
# build version into branch builds.
unset SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENHOP_REPEATER

CONFIG_FILE="${ADDON_CONFIG_DIR}/config.yaml"
CHANNEL_FILE="${DATA_DIR}/.update_channel"
VENV_DIR="${DATA_DIR}/venv"
PYTHON_MARKER="${VENV_DIR}/.openhop-ha-python"
BRANCH_MARKER="${VENV_DIR}/.openhop-ha-branch"

mkdir -p "${ADDON_CONFIG_DIR}" "${DATA_DIR}"

if [ ! -r "${TEMPLATE_CONFIG_FILE}" ]; then
    fatal "bundled configuration template is missing: ${TEMPLATE_CONFIG_FILE}"
fi
if [ ! -r "${BRANCH_HELPER}" ]; then
    fatal "branch helper is missing: ${BRANCH_HELPER}"
fi
if [ ! -r "${PATH_UTILS_HELPER}" ]; then
    fatal "path utilities helper is missing: ${PATH_UTILS_HELPER}"
fi
if [ ! -r "${CONFIG_HELPER}" ]; then
    fatal "configuration bootstrap helper is missing: ${CONFIG_HELPER}"
fi
if [ ! -r "${RUNTIME_INFO_HELPER}" ]; then
    fatal "runtime introspection helper is missing: ${RUNTIME_INFO_HELPER}"
fi
if [ -z "${SYSTEM_PYTHON}" ] || [ ! -x "${SYSTEM_PYTHON}" ]; then
    fatal "python3 is not available"
fi

if [ -d "${CONFIG_FILE}" ]; then
    fatal "configuration path is a directory, expected a file: ${CONFIG_FILE}"
fi

CONFIG_CREATED=false
if [ ! -s "${CONFIG_FILE}" ]; then
    CONFIG_TMP="$(mktemp "${CONFIG_FILE}.tmp.XXXXXX")"
    if ! cp "${TEMPLATE_CONFIG_FILE}" "${CONFIG_TMP}"; then
        rm -f "${CONFIG_TMP}"
        fatal "could not copy the bundled configuration template"
    fi
    if ! "${SYSTEM_PYTHON}" "${CONFIG_HELPER}" generate-secrets "${CONFIG_TMP}"; then
        rm -f "${CONFIG_TMP}"
        fatal "could not generate unique credentials in the initial configuration"
    fi
    if ! chmod 0600 "${CONFIG_TMP}" || ! mv -f "${CONFIG_TMP}" "${CONFIG_FILE}"; then
        rm -f "${CONFIG_TMP}"
        fatal "could not publish the initial configuration atomically"
    fi
    log "created ${CONFIG_FILE} from the bundled full configuration template"
    log "generated unique admin and guest passwords plus a JWT secret; read them from config.yaml"
    CONFIG_CREATED=true
fi

secure_merged_secrets() {
    target_file="$1"
    user_had_admin="$2"
    user_had_guest="$3"
    user_had_jwt="$4"
    changed_secrets=""

    if [ "${user_had_admin}" = "false" ]; then
        generated_password="$("${SYSTEM_PYTHON}" -c 'import secrets; print(secrets.token_urlsafe(24))')"
        if ! OPENHOP_GENERATED_PASSWORD="${generated_password}" "${YQ_CMD}" eval -i \
            '.repeater.security.admin_password = strenv(OPENHOP_GENERATED_PASSWORD)' \
            "${target_file}" >/dev/null 2>&1; then
            return 1
        fi
        changed_secrets="admin_password"
    fi

    if [ "${user_had_guest}" = "false" ]; then
        generated_password="$("${SYSTEM_PYTHON}" -c 'import secrets; print(secrets.token_urlsafe(24))')"
        if ! OPENHOP_GENERATED_PASSWORD="${generated_password}" "${YQ_CMD}" eval -i \
            '.repeater.security.guest_password = strenv(OPENHOP_GENERATED_PASSWORD)' \
            "${target_file}" >/dev/null 2>&1; then
            return 1
        fi
        if [ -n "${changed_secrets}" ]; then
            changed_secrets="${changed_secrets},guest_password"
        else
            changed_secrets="guest_password"
        fi
    fi

    if [ "${user_had_jwt}" = "false" ]; then
        generated_secret="$("${SYSTEM_PYTHON}" -c 'import secrets; print(secrets.token_hex(32))')"
        if ! OPENHOP_GENERATED_SECRET="${generated_secret}" "${YQ_CMD}" eval -i \
            '.repeater.security.jwt_secret = strenv(OPENHOP_GENERATED_SECRET)' \
            "${target_file}" >/dev/null 2>&1; then
            return 1
        fi
        if [ -n "${changed_secrets}" ]; then
            changed_secrets="${changed_secrets},jwt_secret"
        else
            changed_secrets="jwt_secret"
        fi
    fi

    printf '%s\n' "${changed_secrets}"
}

merge_existing_config_with_template() {
    if [ ! -x "${YQ_CMD}" ]; then
        warn "configuration merge skipped because mikefarah yq is unavailable: ${YQ_CMD}"
        return 0
    fi
    if ! "${YQ_CMD}" --version 2>&1 | grep -q 'mikefarah/yq'; then
        warn "configuration merge skipped because ${YQ_CMD} is not mikefarah yq"
        return 0
    fi

    merge_dir="$(mktemp -d "${ADDON_CONFIG_DIR}/.openhop-merge.XXXXXX")"
    stripped_user="${merge_dir}/config.user.yaml"
    merged_config="${merge_dir}/config.merged.yaml"

    # Match the upstream merge policy: preserve the packaged template comments
    # and remove comments from the user overlay to avoid duplication on upgrades.
    if ! "${YQ_CMD}" eval '... comments=""' "${CONFIG_FILE}" > "${stripped_user}" 2>/dev/null; then
        if ! cp "${CONFIG_FILE}" "${stripped_user}"; then
            rm -rf "${merge_dir}"
            fatal "could not prepare the existing configuration for template merge"
        fi
    fi

    if ! user_has_admin="$("${YQ_CMD}" eval \
        '(.repeater.security // {}) | has("admin_password")' \
        "${CONFIG_FILE}" 2>/dev/null)" \
        || ! user_has_guest="$("${YQ_CMD}" eval \
        '(.repeater.security // {}) | has("guest_password")' \
        "${CONFIG_FILE}" 2>/dev/null)" \
        || ! user_has_jwt="$("${YQ_CMD}" eval \
        '((.repeater.security // {}).jwt_secret // "") != ""' \
        "${CONFIG_FILE}" 2>/dev/null)"; then
        rm -rf "${merge_dir}"
        warn "could not inspect existing credential fields; keeping the existing configuration unchanged"
        return 0
    fi
    case "${user_has_admin}:${user_has_guest}:${user_has_jwt}" in
        true:true:true|true:true:false|true:false:true|true:false:false|false:true:true|false:true:false|false:false:true|false:false:false) : ;;
        *)
            rm -rf "${merge_dir}"
            warn "credential-field inspection returned an unexpected result; keeping the existing configuration unchanged"
            return 0
            ;;
    esac

    # $item is yq syntax and must not be expanded by the shell.
    # shellcheck disable=SC2016
    if ! "${YQ_CMD}" eval-all '. as $item ireduce ({}; . * $item)' \
        "${TEMPLATE_CONFIG_FILE}" "${stripped_user}" > "${merged_config}" 2>/dev/null; then
        rm -rf "${merge_dir}"
        warn "could not merge new template defaults; keeping the existing configuration unchanged"
        return 0
    fi
    if ! "${YQ_CMD}" eval '.' "${merged_config}" >/dev/null 2>&1; then
        rm -rf "${merge_dir}"
        warn "template merge produced invalid YAML; keeping the existing configuration unchanged"
        return 0
    fi

    if ! changed_secrets="$(secure_merged_secrets \
        "${merged_config}" "${user_has_admin}" "${user_has_guest}" "${user_has_jwt}")"; then
        rm -rf "${merge_dir}"
        fatal "could not generate credentials introduced by the configuration template merge"
    fi
    if ! "${YQ_CMD}" eval '.' "${merged_config}" >/dev/null 2>&1; then
        rm -rf "${merge_dir}"
        fatal "credential generation produced invalid YAML"
    fi

    if ! cmp -s "${CONFIG_FILE}" "${merged_config}"; then
        if ! chmod 0600 "${merged_config}" || ! mv -f "${merged_config}" "${CONFIG_FILE}"; then
            rm -rf "${merge_dir}"
            fatal "could not publish the merged configuration atomically"
        fi
        log "merged missing settings from the packaged configuration template"
        if [ -n "${changed_secrets}" ]; then
            log "generated unique credentials and JWT secret for fields introduced by the template merge"
        fi
    fi
    rm -rf "${merge_dir}"
}

if [ "${CONFIG_CREATED}" != "true" ]; then
    merge_existing_config_with_template
fi

# Restrict permissions on known sensitive files in the configuration directory.
# The identity.key path is the default location; a custom repeater.identity_file
# configured elsewhere is not enforced here and must be secured externally.
for sensitive_file in \
    "${CONFIG_FILE}" \
    "${ADDON_CONFIG_DIR}/config.yaml.backup" \
    "${ADDON_CONFIG_DIR}/identity.key"; do
    if [ -f "${sensitive_file}" ] && ! chmod 0600 "${sensitive_file}"; then
        fatal "could not restrict permissions on ${sensitive_file}"
    fi
done

migrate_directory_contents() {
    source_dir="$1"
    target_dir="$2"

    [ -d "${source_dir}" ] || return 0
    mkdir -p "${target_dir}"
    if "${SYSTEM_PYTHON}" "${PATH_UTILS_HELPER}" same-path "${source_dir}" "${target_dir}"; then
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

    if [ -e "${link_path}" ] && [ -e "${target_path}" ] \
        && "${SYSTEM_PYTHON}" "${PATH_UTILS_HELPER}" same-path "${link_path}" "${target_path}"; then
        return 0
    fi

    if [ -e "${link_path}" ] && [ ! -L "${link_path}" ]; then
        if "${SYSTEM_PYTHON}" "${PATH_UTILS_HELPER}" is-mount "${link_path}"; then
            if "${SYSTEM_PYTHON}" "${PATH_UTILS_HELPER}" same-path "${link_path}" "${target_path}"; then
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

PYTHON_ABI="$("${SYSTEM_PYTHON}" "${RUNTIME_INFO_HELPER}" python-abi)"
BASE_IMAGE_ID="unknown"
if [ -r "${BASE_IMAGE_ID_FILE}" ]; then
    BASE_IMAGE_ID="$(head -n 1 "${BASE_IMAGE_ID_FILE}" | tr -d '\r\n')"
fi
RUNTIME_COMPATIBILITY="addon=${ADDON_BUILD_VERSION};base=${BASE_IMAGE_ID};python=${PYTHON_ABI}"

set_venv_paths() {
    VENV_PYTHON="${VENV_DIR}/bin/python"
    VENV_PIP="${VENV_DIR}/bin/pip"
    if [ ! -x "${VENV_PYTHON}" ]; then
        fatal "persistent update environment is incomplete: ${VENV_DIR}"
    fi
    VENV_SITE_PACKAGES="$("${VENV_PYTHON}" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
    mkdir -p "${VENV_SITE_PACKAGES}"
}

configure_venv_runtime() {
    set_venv_paths

    # A .pth file exposes the packaged dependencies and the protected copy of
    # packaged main. A branch installed in this venv still takes precedence.
    pth_file="${VENV_SITE_PACKAGES}/openhop-base-image.pth"
    pth_tmp="${pth_file}.tmp.$$"
    : > "${pth_tmp}"
    if [ -d "${BASE_RUNTIME_DIR}/repeater" ]; then
        printf '%s\n' "${BASE_RUNTIME_DIR}" >> "${pth_tmp}"
    fi
    # Intentional word splitting expands the configured glob.
    # shellcheck disable=SC2086
    for site_dir in ${BASE_SITE_PACKAGES_GLOB}; do
        if [ -d "${site_dir}" ]; then
            printf '%s\n' "${site_dir}" >> "${pth_tmp}"
        fi
    done
    chmod 0644 "${pth_tmp}"
    mv -f "${pth_tmp}" "${pth_file}"

    # The web setup endpoints resolve these files two levels above the imported
    # repeater.web package. They are not included in pip's package metadata, so
    # publish the protected image copies next to a venv-installed package.
    for support_name in radio-settings.json radio-presets.json; do
        support_source="${BASE_RUNTIME_DIR}/${support_name}"
        support_target="${VENV_SITE_PACKAGES}/${support_name}"
        support_tmp="${support_target}.tmp.$$"
        if [ ! -r "${support_source}" ]; then
            warn "packaged support file is unavailable: ${support_source}"
            continue
        fi
        if ! cp "${support_source}" "${support_tmp}" \
            || ! chmod 0644 "${support_tmp}" \
            || ! mv -f "${support_tmp}" "${support_target}"; then
            rm -f "${support_tmp}"
            fatal "could not publish packaged support file: ${support_target}"
        fi
    done

    if [ ! -x "${VENV_PIP_WRAPPER}" ]; then
        fatal "validated venv pip wrapper is unavailable: ${VENV_PIP_WRAPPER}"
    fi
    if ! ln -sfn "${VENV_PIP_WRAPPER}" "${VENV_PIP}"; then
        fatal "could not install the validated venv pip wrapper"
    fi
}

create_clean_venv() {
    reason="$1"
    if [ -e "${VENV_DIR}" ] || [ -L "${VENV_DIR}" ]; then
        log "rebuilding persistent update environment (${reason})"
        rm -rf "${VENV_DIR}"
    else
        log "creating persistent update environment (${reason})"
    fi
    if [ "${TEST_WITHOUT_PIP}" = "true" ]; then
        venv_result=0
        "${SYSTEM_PYTHON}" -m venv --system-site-packages --without-pip "${VENV_DIR}" \
            || venv_result=$?
    else
        venv_result=0
        "${SYSTEM_PYTHON}" -m venv --system-site-packages "${VENV_DIR}" \
            || venv_result=$?
    fi
    if [ "${venv_result}" -ne 0 ]; then
        fatal "could not create persistent update environment"
    fi
    marker_tmp="${PYTHON_MARKER}.tmp.$$"
    if ! printf '%s\n' "${RUNTIME_COMPATIBILITY}" > "${marker_tmp}" \
        || ! mv -f "${marker_tmp}" "${PYTHON_MARKER}"; then
        rm -f "${marker_tmp}"
        fatal "could not persist update-environment compatibility marker"
    fi

    # The in-app updater installs to /opt/openhop_repeater/venv. Point that
    # path at /data/venv so updates survive app upgrades and container restarts.
    replace_directory_with_symlink "${UPDATE_VENV_LINK}" "${VENV_DIR}" false
    configure_venv_runtime
}

VENV_COMPATIBILITY=""
if [ -r "${PYTHON_MARKER}" ]; then
    VENV_COMPATIBILITY="$(cat "${PYTHON_MARKER}" 2>/dev/null || true)"
fi
VENV_REBUILD_REASON=""
if [ ! -x "${VENV_DIR}/bin/python" ]; then
    VENV_REBUILD_REASON="Python interpreter is missing"
elif [ "${VENV_COMPATIBILITY}" != "${RUNTIME_COMPATIBILITY}" ]; then
    VENV_REBUILD_REASON="runtime compatibility changed to ${RUNTIME_COMPATIBILITY}"
elif [ "${TEST_WITHOUT_PIP}" != "true" ] \
    && ! "${VENV_DIR}/bin/python" -c 'import pip' >/dev/null 2>&1; then
    VENV_REBUILD_REASON="pip is missing from the update environment"
fi

if [ -n "${VENV_REBUILD_REASON}" ]; then
    create_clean_venv "${VENV_REBUILD_REASON}"
else
    replace_directory_with_symlink "${UPDATE_VENV_LINK}" "${VENV_DIR}" false
    configure_venv_runtime
fi

if [ ! -f "${CHANNEL_FILE}" ]; then
    printf '%s\n' "${DEFAULT_BRANCH}" > "${CHANNEL_FILE}"
fi
SELECTED_BRANCH="$(head -n 1 "${CHANNEL_FILE}" 2>/dev/null | tr -d '\r\n' || true)"
if ! "${SYSTEM_PYTHON}" "${BRANCH_HELPER}" validate "${SELECTED_BRANCH}"; then
    warn "invalid persisted branch '${SELECTED_BRANCH}'; resetting to '${DEFAULT_BRANCH}'"
    SELECTED_BRANCH="${DEFAULT_BRANCH}"
    printf '%s\n' "${SELECTED_BRANCH}" > "${CHANNEL_FILE}"
fi

detected_installed_branch() {
    "${SYSTEM_PYTHON}" "${BRANCH_HELPER}" installed-ref "${VENV_SITE_PACKAGES}"
}

read_branch_marker() {
    marker_branch=""
    if [ -r "${BRANCH_MARKER}" ]; then
        marker_branch="$(head -n 1 "${BRANCH_MARKER}" 2>/dev/null | tr -d '\r\n' || true)"
        if ! "${SYSTEM_PYTHON}" "${BRANCH_HELPER}" validate "${marker_branch}"; then
            warn "discarding invalid installed-branch marker '${marker_branch}'"
            marker_branch=""
            rm -f "${BRANCH_MARKER}"
        fi
    fi
    printf '%s\n' "${marker_branch}"
}

write_branch_marker() {
    branch="$1"
    marker_tmp="${BRANCH_MARKER}.tmp.$$"
    if ! printf '%s\n' "${branch}" > "${marker_tmp}" || ! mv -f "${marker_tmp}" "${BRANCH_MARKER}"; then
        rm -f "${marker_tmp}"
        fatal "could not persist verified installed branch '${branch}'"
    fi
}

can_import_repeater() {
    "${VENV_PYTHON}" -c 'import repeater.main' >/dev/null 2>&1
}

runtime_uses_venv() {
    "${VENV_PYTHON}" "${RUNTIME_INFO_HELPER}" uses-venv "${VENV_SITE_PACKAGES}"
}

runtime_package_path() {
    "${VENV_PYTHON}" "${RUNTIME_INFO_HELPER}" package-path
}

reset_to_packaged_runtime() {
    reason="$1"
    warn "${reason}; rebuilding a clean environment and falling back to the packaged runtime"
    create_clean_venv "recovering the packaged runtime"
    if ! can_import_repeater; then
        fatal "the protected packaged runtime cannot be imported after recovery"
    fi
}

# Read installation metadata before importing repeater.main. Importing the web
# package runs upstream dist-info cleanup, which may remove direct_url.json when
# a packaged distribution and a newly installed branch report competing
# versions. Capturing the ref first lets the app verify and persist a successful
# first in-app branch update instead of needlessly reinstalling it.
DETECTED_BRANCH="$(detected_installed_branch)"
MARKED_BRANCH="$(read_branch_marker)"

# A failed or interrupted in-app pip operation can leave the persistent venv in
# a partially uninstalled state. Recover deterministically rather than trusting
# captured metadata from a package that cannot actually be imported.
if ! can_import_repeater; then
    reset_to_packaged_runtime "the persistent update environment is not runnable"
    DETECTED_BRANCH=""
    MARKED_BRANCH=""
fi

RUNTIME_FROM_VENV=false
if runtime_uses_venv; then
    RUNTIME_FROM_VENV=true
fi

# A successful update performed from the web interface writes direct_url.json.
# Adopt it only after verifying that Python actually imports from the venv.
if [ "${RUNTIME_FROM_VENV}" = "true" ] \
    && [ -n "${DETECTED_BRANCH}" ] \
    && [ "${DETECTED_BRANCH}" = "${SELECTED_BRANCH}" ]; then
    if [ "${MARKED_BRANCH}" != "${DETECTED_BRANCH}" ]; then
        write_branch_marker "${DETECTED_BRANCH}"
        MARKED_BRANCH="${DETECTED_BRANCH}"
    fi
fi

if [ -n "${DETECTED_BRANCH}" ]; then
    INSTALLED_BRANCH="${DETECTED_BRANCH}"
else
    INSTALLED_BRANCH="${MARKED_BRANCH}"
fi

# The protected base-image build is a valid main runtime only when no branch
# distribution is active. Every installed branch must match the selected ref
# and must actually be the package Python imports from the persistent venv.
NEEDS_BRANCH_INSTALL=false
if [ "${SELECTED_BRANCH}" = "${DEFAULT_BRANCH}" ] \
    && [ -z "${INSTALLED_BRANCH}" ] \
    && [ "${RUNTIME_FROM_VENV}" != "true" ]; then
    :
elif [ "${INSTALLED_BRANCH}" != "${SELECTED_BRANCH}" ] \
    || [ "${RUNTIME_FROM_VENV}" != "true" ]; then
    NEEDS_BRANCH_INSTALL=true
fi

if [ "${NEEDS_BRANCH_INSTALL}" = "true" ]; then
    log "activating branch '${SELECTED_BRANCH}' in the persistent update environment"
    INSTALL_SPEC="openhop_repeater[hardware] @ git+${UPSTREAM_GIT_URL}@${SELECTED_BRANCH}"
    INSTALL_VERIFIED=false
    if GIT_TERMINAL_PROMPT=0 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_DEFAULT_TIMEOUT=30 \
        "${VENV_PIP}" install --upgrade --force-reinstall --no-cache-dir "${INSTALL_SPEC}"; then
        DETECTED_BRANCH="$(detected_installed_branch)"
        if [ "${DETECTED_BRANCH}" = "${SELECTED_BRANCH}" ] \
            && can_import_repeater \
            && runtime_uses_venv; then
            write_branch_marker "${SELECTED_BRANCH}"
            INSTALLED_BRANCH="${SELECTED_BRANCH}"
            INSTALL_VERIFIED=true
            log "installed and verified branch '${SELECTED_BRANCH}'"
        else
            warn "branch '${SELECTED_BRANCH}' installation completed but runtime verification failed"
        fi
    else
        warn "could not install branch '${SELECTED_BRANCH}'"
    fi

    if [ "${INSTALL_VERIFIED}" != "true" ]; then
        reset_to_packaged_runtime "branch '${SELECTED_BRANCH}' could not be activated safely"
        DETECTED_BRANCH=""
        MARKED_BRANCH=""
        INSTALLED_BRANCH=""
        RUNTIME_FROM_VENV=false
    fi
fi

if ! can_import_repeater; then
    fatal "openHop Repeater cannot be imported from either the persistent venv or the protected base image"
fi

IMPORT_PATH="$(runtime_package_path)"
if runtime_uses_venv; then
    ACTIVE_BRANCH="$(detected_installed_branch)"
    if [ -z "${ACTIVE_BRANCH}" ]; then
        ACTIVE_BRANCH="$(read_branch_marker)"
    fi
    if [ -z "${ACTIVE_BRANCH}" ]; then
        ACTIVE_BRANCH="unknown (persistent venv)"
    fi
else
    ACTIVE_BRANCH="${DEFAULT_BRANCH} (packaged image)"
fi
ACTIVE_VERSION="$("${VENV_PYTHON}" -c 'import repeater; print(getattr(repeater, "__version__", "unknown"))')"
log "selected branch: ${SELECTED_BRANCH}; active branch: ${ACTIVE_BRANCH}; version: ${ACTIVE_VERSION}"
log "runtime package: ${IMPORT_PATH}"

replace_directory_with_symlink "${RUNTIME_CONFIG_DIR}" "${ADDON_CONFIG_DIR}" false

if ! "${VENV_PYTHON}" "${CONFIG_HELPER}" validate-config "${CONFIG_FILE}"; then
    fatal "invalid configuration file: ${CONFIG_FILE}"
fi

cd "${DATA_DIR}"

stop_child_and_wait() {
    child_pid="$1"
    [ -n "${child_pid}" ] || return 0

    kill -TERM "${child_pid}" 2>/dev/null || true
    (
        sleep 8
        if kill -0 "${child_pid}" 2>/dev/null; then
            warn "repeater did not stop after SIGTERM; sending SIGKILL"
            kill -KILL "${child_pid}" 2>/dev/null || true
        fi
    ) &
    stop_watchdog_pid=$!

    # Reap the real child. The first wait in the main path may have been
    # interrupted by SIGTERM before the child itself had exited.
    wait "${child_pid}" 2>/dev/null || true
    kill "${stop_watchdog_pid}" 2>/dev/null || true
    wait "${stop_watchdog_pid}" 2>/dev/null || true
}

# The firmware deliberately exits its process after an in-app update or restart
# request. Keep PID 1 alive long enough to rerun this bootstrap so the selected
# branch becomes active without depending on an external container restart.
if [ "${STOP_REQUESTED}" = "true" ]; then
    exit 0
fi

CHILD_STARTED_AT="$(date +%s)"
"${VENV_PYTHON}" -m repeater.main --config "${RUNTIME_CONFIG_DIR}/config.yaml" &
CHILD_PID=$!
if [ "${STOP_REQUESTED}" = "true" ]; then
    kill -TERM "${CHILD_PID}" 2>/dev/null || true
fi
log "repeater process started"
EXIT_CODE=0
WAITED_CHILD_PID="${CHILD_PID}"
wait "${WAITED_CHILD_PID}" || EXIT_CODE=$?

if [ "${STOP_REQUESTED}" = "true" ]; then
    stop_child_and_wait "${WAITED_CHILD_PID}"
    CHILD_PID=""
    exit 0
fi
CHILD_PID=""

if [ "${EXIT_CODE}" -eq 0 ]; then
    now="$(date +%s)"
    runtime_seconds=$((now - CHILD_STARTED_AT))
    rapid_restarts="${OPENHOP_ADDON_RAPID_RESTARTS:-0}"
    case "${rapid_restarts}" in
        ''|*[!0-9]*) rapid_restarts=0 ;;
    esac
    if [ "${runtime_seconds}" -ge 30 ]; then
        rapid_restarts=0
    fi
    rapid_restarts=$((rapid_restarts + 1))
    if [ "${rapid_restarts}" -gt 3 ]; then
        fatal "repeater exited cleanly too many times before reaching 30 seconds of stable runtime; refusing a restart loop"
    fi
    export OPENHOP_ADDON_RAPID_RESTARTS="${rapid_restarts}"
    log "repeater requested a restart; rerunning branch bootstrap"
    sleep 1 || true
    if [ "${STOP_REQUESTED}" = "true" ]; then
        exit 0
    fi
    exec "$0"
fi

fatal "repeater exited unexpectedly with status ${EXIT_CODE}"
