# openHop Repeater Home Assistant Add-on

Run [openHop Repeater](https://github.com/openhop-dev/openhop_repeater) as a
Home Assistant add-on, while keeping the complete repeater configuration in one
editable YAML file.

## Add-on

### [openHop Repeater](./openhop_repeater_main)

The repository now contains one add-on instead of separate `main` and `dev`
variants. The release branch is selected from the repeater web interface and is
persisted across restarts and add-on upgrades.

The existing slug, `openhop_repeater_main`, is intentionally retained so users
of the former main add-on keep their add-on config and data directory.

## Install

1. Add this repository to the Home Assistant add-on store.
2. Install **openHop Repeater**.
3. Start it once to create the full `config.yaml` template.
4. Edit `addon_configs/*_openhop_repeater_main/config.yaml`.
5. Start the add-on and open its web interface.

See the [add-on documentation](./openhop_repeater_main/DOCS.md) for hardware,
configuration, branch switching, and migration details.

## Repository layout

```text
openhop_repeater_main/
├── config.yaml          # Home Assistant add-on metadata
├── config.yaml.example  # complete openHop runtime configuration
├── Dockerfile
├── DOCS.md
├── README.md
├── CHANGELOG.md
├── run.sh
└── rootfs/              # small add-on-specific runtime helpers
```

The runtime configuration is deliberately not duplicated into Home Assistant
add-on options. `/config/config.yaml` remains the single source of truth.
