# openHop Repeater Home Assistant Add-on

This repository provides a Home Assistant add-on for
[openHop Repeater](https://github.com/openhop-dev/openhop_repeater).

The add-on runs the repeater as a managed Home Assistant service while keeping
all repeater settings in a single YAML file. Branches can be selected and
installed from the openHop Repeater web interface.

## Installation

1. Add this repository to the Home Assistant add-on store.
2. Install **openHop Repeater**.
3. Start the add-on once to create the configuration file.
4. Edit `app_configs/*_openhop_repeater_main/config.yaml`.
5. Start the add-on and open its web interface.

Local SPI or GPIO hardware requires **Protection mode** to be disabled in the
add-on settings.

## Configuration

The complete openHop Repeater configuration is stored in:

```text
app_configs/*_openhop_repeater_main/config.yaml
```

Inside the add-on, the same file is available as:

```text
/config/config.yaml
```

Home Assistant add-on options are not used for repeater settings. The YAML file
is the only configuration source.

## Branch selection

Open the update dialog in the repeater web interface to select and install an
openHop Repeater branch. The selected branch and its Python environment are
stored in the add-on's persistent `/data` directory, so they survive restarts
and add-on upgrades.

See [DOCS.md](./openhop_repeater_main/DOCS.md) for complete installation,
configuration, hardware, update, storage, and troubleshooting instructions.

## Repository structure

```text
openhop_repeater_main/
├── config.yaml          # Home Assistant add-on metadata
├── config.yaml.example  # openHop Repeater configuration template
├── Dockerfile
├── DOCS.md
├── README.md
├── CHANGELOG.md
├── run.sh
└── rootfs/              # add-on runtime helpers
```

## License

The Home Assistant add-on files in this repository are licensed under the MIT
License. openHop Repeater is distributed under its own upstream license.
