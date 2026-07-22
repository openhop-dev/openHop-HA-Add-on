<p align="center">
  <img src="https://raw.githubusercontent.com/openhop-dev/openHop-HA-Add-on/main/openhop_repeater_main/icon.png" alt="openHop Repeater Main" width="150">
</p>

<h1 align="center">Home Assistant Add-on: openHop Repeater Main</h1>

<p align="center">
  Run the openHop Repeater mainline image on Home Assistant with persistent configuration, runtime data, and hardware access.
</p>

<p align="center">
  <a href="https://hub.docker.com/r/openhop/openhop-repeater"><img src="https://img.shields.io/badge/channel-main-2563EB?style=for-the-badge&logo=docker&logoColor=white" alt="Main image channel"></a>
  <a href="https://discord.gg/3s8MMaSTzq"><img src="https://img.shields.io/discord/1489331292309946508?style=for-the-badge&logo=discord&logoColor=white&label=Discord&color=5865F2" alt="openHop Discord"></a>
</p>

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

## About

This add-on wraps `openhop/openhop-repeater:main`. It follows the published upstream mainline image without switching branches or installing application code at container startup.

Choose Main for the normal openHop Repeater channel. To test the newest upstream development changes, install [openHop Repeater Dev](../openhop_repeater_dev/).

## Highlights

- Continuous MeshCore-compatible LoRa packet forwarding and routing
- Browser-based setup, configuration, logs, monitoring, and API access on port `8000`
- Real-time packet statistics, neighbor discovery, signal data, and historical metrics
- Native SX1262 SPI, CH341 USB-to-SPI, pyMC TCP/USB modem, and KISS serial radio backends
- MQTT, GPS, external sensors, companion identities, and optional [openHop Glass](https://github.com/openhop-dev/openHop-Glass) integration
- Companion Home Assistant integration for Repeater telemetry and controls
- Mainline upstream features through the dedicated `:main` channel
- Native `aarch64` and `amd64` support
- Persistent configuration, node identity, API-token database, and runtime state
- Unique first-start credentials plus conservative configuration upgrades
- Cold Home Assistant backups and clean process lifecycle handling
- Direct SPI, GPIO, USB, serial, host-network, and dynamic companion-service access

## Supported architectures

The current `openhop/openhop-repeater:main` manifest provides:

| Home Assistant architecture | Container platform |
|---|---|
| `aarch64` | `linux/arm64` |
| `amd64` | `linux/amd64` |

## Installation

1. Add `https://github.com/openhop-dev/openHop-HA-Add-on` to the Home Assistant Add-on Store repositories.
2. Install **openHop Repeater Main**.
3. If you use local GPIO or SPI hardware, disable **Protection mode** in the add-on settings.
4. Start the add-on once so it creates a complete configuration with unique credentials.
5. Stop the add-on and edit `config.yaml` in the private add-on configuration folder matching:

   ```text
   addon_config/*_openhop_repeater_main/config.yaml
   ```

6. Start the add-on again and open its web UI.

See [`DOCS.md`](DOCS.md) for Raspberry Pi host preparation and detailed radio configuration.

## Configuration and storage

The generated YAML file at `/config/config.yaml` is the single source of truth. On updates, settings newly introduced by the upstream Main template are merged into the existing file while user values, custom keys, passwords, and secrets are preserved.

| Container path | Purpose |
|---|---|
| `/config/config.yaml` | Repeater configuration and generated credentials |
| `/config/identity.key` | Persistent node identity when generated |
| `/var/lib/openhop_repeater` | Database, API-token state, and runtime data |

Invalid YAML is never silently replaced. Startup stops with an error so the existing file can be corrected.

## Hardware and network access

> [!WARNING]
> This add-on uses `full_access`, has AppArmor disabled, and runs on the host network. These permissions are required for supported GPIO, SPI, USB, serial, radio, and companion-service configurations, but they also increase the impact of an unsafe image or configuration.

Keep the Repeater web interface and API on a trusted local network or VPN.

## Related projects

- [openHop Repeater](https://github.com/openhop-dev/openhop_repeater)
- [openHop Repeater Home Assistant integration](https://github.com/openhop-dev/openHop-HA-Integration)
- [Dev add-on](../openhop_repeater_dev/)
- [openHop Discord](https://discord.gg/3s8MMaSTzq)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
