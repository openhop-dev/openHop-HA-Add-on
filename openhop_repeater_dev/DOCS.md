# Home Assistant Add-on: openHop Repeater Dev

## About

This add-on wraps the upstream openHop Repeater `:dev` container and keeps
the openHop Repeater runtime configuration in the add-on config directory.

This is the development-tracking add-on. It is intentionally pinned to the
upstream `:dev` image, not a stable release image.

Current upstream support in this add-on image follows the openHop Repeater
project itself, including newer radio backends when they are present in the
published `:dev` image.

The first time the add-on starts it will create:

- `/config/config.yaml`
- `/config/identity.key` when openHop Repeater generates its node identity
- `/var/lib/openhop_repeater` for runtime data

Inside the add-on, `/config` is the add-on's private config mount. On the host,
those files are stored in the add-on's own `addon_config` directory, separate
from Home Assistant's main `/config` folder.

## Install

1. Add this repository to Home Assistant.
2. Install the `openHop Repeater Dev` add-on.
3. If you are using local Pi GPIO or SPI hardware, disable `Protection mode`
   in the add-on settings before starting the add-on.
4. Start the add-on once so it creates a complete configuration with unique
   credentials, then stop it before editing hardware settings.
5. Open your Home Assistant file editor, such as Studio Code Server, and edit
   the add-on config file `config.yaml` in the add-on's own config folder.
   You are looking for a folder matching `addon_config/*_openhop_repeater_dev`.
6. Start the add-on again and open the web UI on port `8000`.

## Configuration

This add-on uses a real YAML file at `/config/config.yaml`.
On first start, the add-on creates that file atomically from the full template
included in the current upstream `:dev` image. It replaces the template's shared
defaults with unique admin and guest passwords and a unique JWT signing secret.
Read those generated values from `config.yaml` before signing in.

The file then remains the single source of truth. On later image updates, new
template settings are merged into the existing file while configured values,
custom settings, passwords, and secrets are preserved. Invalid YAML is never
silently replaced; startup stops with an error so the file can be corrected.

The bundled starter config is aimed at an SX1262 SPI radio. At minimum, review:

- `repeater.node_name`
- `repeater.security.admin_password`
- `repeater.security.guest_password`
- `radio.frequency`
- `sx1262.bus_id`
- `sx1262.cs_id`
- `sx1262.cs_pin`
- `sx1262.reset_pin`
- `sx1262.busy_pin`
- `sx1262.irq_pin`

Other radio backends supported by the upstream `:dev` image should be
configured directly in `config.yaml` using the upstream schema.

## Backups and shutdown

Home Assistant uses cold backups for this add-on so configuration, identity,
and persistent repeater data are captured while the process is stopped. The
startup wrapper forwards stop signals to openHop Repeater, waits for it to exit,
and bounds repeated clean restart requests to avoid a rapid restart loop.

## Raspberry Pi Host Setup

If you are using an SX1262 or other local Pi-attached hardware, enable the
required host interfaces in Home Assistant OS before starting the add-on.

On the `hassos-boot` partition of the SD card:

- Edit `config.txt` and add `dtparam=spi=on`
- Add `dtparam=i2c_arm=on` and `dtparam=i2c_vc=on` only if you also need I2C
- Create `CONFIG/modules/rpi-i2c.conf` containing `i2c-dev` only if you need I2C

For local GPIO or SPI access inside Home Assistant:

- Disable add-on `Protection mode`
- Keep this add-on on hardware-capable hosts such as Raspberry Pi
- Use BCM GPIO numbering in `config.yaml`, for example `irq_pin: 16` means
  BCM GPIO 16, not physical header pin 16

## Hardware Access

This add-on currently runs with `full_access: true` and AppArmor disabled.
That is deliberate so openHop Repeater can access SPI, GPIO, USB, and serial
hardware used by supported radio setups.

This add-on also runs on the host network so openHop Repeater companion services
can bind dynamic ports directly on the Home Assistant host.

## Web UI

The upstream container exposes its web interface on port `8000`.

## Upstream Project

- Upstream repo: <https://github.com/openhop-dev/openhop_repeater>
- Container image used by this add-on: `openhop/openhop-repeater:dev`
