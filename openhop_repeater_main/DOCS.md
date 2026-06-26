# Home Assistant Add-on: openHop Repeater Main

## About

This add-on wraps the upstream openHop Repeater `:main` container and keeps
the openHop Repeater runtime configuration in the add-on config directory.

This is the mainline-tracking add-on. It is pinned to the upstream `:main`
image.

Current upstream support in this add-on image follows the openHop Repeater
project itself, including newer radio backends when they are present in the
published `:main` image.

The first time the add-on starts it will create:

- `/config/config.yaml`
- `/config/identity.key` when openHop Repeater generates its node identity
- `/var/lib/openhop_repeater` for runtime data

Inside the add-on, `/config` is the add-on's private config mount. On the host,
those files are stored in the add-on's own `addon_config` directory, separate
from Home Assistant's main `/config` folder.

## Install

1. Add this repository to Home Assistant.
2. Install the `openHop Repeater Main` add-on.
3. If you are using local Pi GPIO or SPI hardware, disable `Protection mode`
   in the add-on settings before starting the add-on.
4. Open your Home Assistant file editor, such as Studio Code Server.
5. Edit the add-on config file `config.yaml` in the add-on's own config folder.
   You are looking for a folder matching `addon_config/*_openhop_repeater_main`.
6. Start the add-on and open the web UI on port `8000`.

## Configuration

This add-on uses a real YAML file at `/config/config.yaml`.
The add-on seeds that file on first start and then treats it as the single
source of truth. If openHop Repeater updates the file itself, those changes are
preserved across restarts.

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

Other radio backends supported by the upstream `:main` image should be
configured directly in `config.yaml` using the upstream schema.

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
- Container image used by this add-on: `openhop/openhop-repeater:main`
