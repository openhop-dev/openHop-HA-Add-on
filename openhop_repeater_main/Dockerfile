ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64

FROM openhopdev/openhop-repeater:main

ARG BUILD_VERSION
ARG BUILD_ARCH

USER root

COPY --chmod=755 run.sh /run.sh
COPY openhop-repeater.example.yaml /usr/share/openhop-repeater/config.yaml.example

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}" \
  org.opencontainers.image.title="Home Assistant Add-on: openHop Repeater Main" \
  org.opencontainers.image.description="Home Assistant wrapper for openHop Repeater main channel" \
  org.opencontainers.image.source="https://github.com/openhop-dev/openhop_repeater"

ENTRYPOINT ["/run.sh"]
