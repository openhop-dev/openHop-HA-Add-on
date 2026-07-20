FROM openhop/openhop-repeater:main

ARG BUILD_VERSION=3.0.0
ARG BUILD_ARCH

USER root

# The upstream updater performs best-effort cleanup through /usr/bin/python3.
# The Python base image also contains Debian's system interpreter, which does
# not include pip unless it is installed explicitly.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    OPENHOP_ADDON_BUILD_VERSION="${BUILD_VERSION}" \
    OPENHOP_ADDON_BASE_IMAGE_ID_FILE="/usr/share/openhop-repeater/base-image-id" \
    OPENHOP_ADDON_BASE_RUNTIME_DIR="/usr/share/openhop-repeater/base-runtime"

COPY --chmod=755 run.sh /run.sh
COPY rootfs /

# Generate new installations from the template that belongs to the packaged
# repeater code, not from a potentially stale copy in the wrapper repository.
# The deterministic runtime fingerprint also invalidates a persistent update
# venv when a rebuilt app image contains different packaged code or dependencies.
RUN set -eu; \
    mkdir -p /usr/share/openhop-repeater/base-runtime; \
    cp -a /opt/openhop_repeater/repeater \
      /usr/share/openhop-repeater/base-runtime/repeater; \
    cp /opt/openhop_repeater/config.yaml.example \
      /usr/share/openhop-repeater/config.yaml.example; \
    cp /opt/openhop_repeater/radio-settings.json \
      /usr/share/openhop-repeater/base-runtime/radio-settings.json; \
    cp /opt/openhop_repeater/radio-presets.json \
      /usr/share/openhop-repeater/base-runtime/radio-presets.json; \
    { \
      find /usr/share/openhop-repeater/base-runtime/repeater \
        -type f -exec sha256sum {} +; \
      find /home -type f -path '*/site-packages/*' \
        -exec sha256sum {} +; \
      dpkg-query -W -f='${binary:Package}=${Version}\n'; \
      sha256sum \
        /usr/local/bin/python3 \
        /usr/local/bin/yq \
        /usr/share/openhop-repeater/config.yaml.example \
        /usr/share/openhop-repeater/base-runtime/radio-settings.json \
        /usr/share/openhop-repeater/base-runtime/radio-presets.json \
        /run.sh \
        /usr/local/bin/openhop-container-systemctl \
        /usr/local/bin/openhop-venv-pip \
        /usr/local/lib/openhop-addon/branch_state.py \
        /usr/local/lib/openhop-addon/path_utils.py \
        /usr/local/lib/openhop-addon/config_bootstrap.py \
        /usr/local/lib/openhop-addon/runtime_info.py; \
    } | sort | sha256sum | cut -d ' ' -f 1 \
      > /usr/share/openhop-repeater/base-image-id

RUN if [ ! -e /bin/systemctl ]; then \
      ln -s /usr/local/bin/openhop-container-systemctl /bin/systemctl; \
    fi

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}" \
  org.opencontainers.image.title="Home Assistant App: openHop Repeater" \
  org.opencontainers.image.description="Home Assistant app for openHop Repeater with persistent branch selection" \
  org.opencontainers.image.source="https://github.com/Bjorkan/openHop-HA-Add-on" \
  org.opencontainers.image.licenses="MIT"

STOPSIGNAL SIGTERM
ENTRYPOINT ["/run.sh"]
