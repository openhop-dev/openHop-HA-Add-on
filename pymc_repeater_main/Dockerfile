ARG BUILD_VERSION=0.1.0
ARG BUILD_ARCH=amd64

FROM pymcdev/pymc-repeater:main

ARG BUILD_VERSION
ARG BUILD_ARCH

USER root

COPY --chmod=755 run.sh /run.sh
COPY pymc-repeater.example.yaml /usr/share/pymc-repeater/config.yaml.example

USER repeater

LABEL \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}" \
  org.opencontainers.image.title="Home Assistant Add-on: pyMC Repeater Main" \
  org.opencontainers.image.description="Home Assistant wrapper for pyMC Repeater main channel" \
  org.opencontainers.image.source="https://github.com/pyMC-dev/pyMC_Repeater"

ENTRYPOINT ["/run.sh"]
