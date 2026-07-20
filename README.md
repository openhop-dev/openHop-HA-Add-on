# openHop Repeater Home Assistant App

This repository provides a Home Assistant app for
[openHop Repeater](https://github.com/openhop-dev/openhop_repeater).

The app runs the repeater as a managed Home Assistant service while keeping
all repeater settings in a single YAML file. Missing packaged defaults are
merged without replacing user values. Branches can be selected and installed
from the openHop Repeater web interface.

## Installation

1. Add this repository to the Home Assistant app store.
2. Install **openHop Repeater**.
3. Start the app once to create the configuration file.
4. Stop the app and edit `/addon_configs/*_openhop_repeater_main/config.yaml`.
5. Start the app and open its web interface.

Directly attached SPI, GPIO, USB, or serial hardware requires **Protection
mode** to be disabled in the app settings. Network-only operation can remain
protected.

## Configuration

The complete openHop Repeater configuration is stored in:

```text
/addon_configs/*_openhop_repeater_main/config.yaml
```

Inside the app, the same file is available as:

```text
/config/config.yaml
```

Home Assistant app options are not used for repeater settings. The YAML file
is the only configuration source.

## Branch selection

Open the update dialog in the repeater web interface to select and install an
openHop Repeater branch. The selected branch, verified branch marker, and
Python environment are stored in the app's persistent `/data` directory.
The selected channel survives restarts and app upgrades; the generated
environment is rebuilt whenever its app-image compatibility changes. Startup
verifies the real import path before reporting a branch as active.

See [DOCS.md](./openhop_repeater_main/DOCS.md) for complete installation,
configuration, hardware, update, storage, and troubleshooting instructions.

## Repository structure

```text
openhop_repeater_main/
├── config.yaml          # Home Assistant app metadata
├── config.yaml.example  # openHop Repeater configuration template
├── Dockerfile
├── DOCS.md
├── README.md
├── CHANGELOG.md
├── run.sh
└── rootfs/              # app runtime helpers
```

## License

The Home Assistant app files in this repository are licensed under the MIT
License. openHop Repeater is distributed under its own upstream license.
