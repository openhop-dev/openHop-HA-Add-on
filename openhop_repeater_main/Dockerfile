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

ENV PIP_BREAK_SYSTEM_PACKAGES=1

COPY --chmod=755 run.sh /run.sh
COPY config.yaml.example /usr/share/openhop-repeater/config.yaml.example
COPY rootfs /

RUN if [ ! -e /bin/systemctl ]; then \
      ln -s /usr/local/bin/openhop-container-systemctl /bin/systemctl; \
    fi

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}" \
  org.opencontainers.image.title="Home Assistant Add-on: openHop Repeater" \
  org.opencontainers.image.description="Home Assistant add-on for openHop Repeater with persistent branch selection" \
  org.opencontainers.image.source="https://github.com/Bjorkan/openHop-HA-Add-on" \
  org.opencontainers.image.licenses="MIT"

STOPSIGNAL SIGTERM
ENTRYPOINT ["/run.sh"]
