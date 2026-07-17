# Home Assistant Add-on: openHop Repeater

## About

This add-on runs openHop Repeater as a managed Home Assistant service.

All repeater settings are stored in one editable YAML file:

```text
/config/config.yaml
```

On the Home Assistant host, the file is available under:

```text
app_configs/*_openhop_repeater_main/config.yaml
```

The add-on creates the file on first start from the bundled openHop Repeater
configuration template. Unique admin and guest passwords are generated for a
new configuration. An existing configuration file is never overwritten.

## Installation

1. Add the openHop Repeater repository to the Home Assistant add-on store.
2. Install **openHop Repeater**.
3. Disable **Protection mode** when using local SPI or GPIO radio hardware.
4. Start the add-on once to create `config.yaml`.
5. Stop the add-on and edit the generated file.
6. Start the add-on and select **Open Web UI**.

The initial configuration uses `radio_type: null`. This allows the service to
start before radio hardware has been configured.

## Configuration

`/config/config.yaml` is the only source of repeater settings. Home Assistant
add-on options are not used for the openHop Repeater configuration.

Review at least the following values before normal operation:

- `repeater.node_name`
- `repeater.security.admin_password`
- `repeater.security.guest_password`
- `radio_type`
- the configuration section for the selected radio backend
- radio frequency, bandwidth, spreading factor, coding rate, and transmit power
- identity, MQTT, companion, and policy settings used by the installation

The bundled template contains the configuration sections and comments supplied
with the openHop Repeater version included in the add-on image.

## Selecting an openHop Repeater branch

Branches are managed from the repeater web interface:

1. Open the web interface.
2. Open the update dialog.
3. Select the required **Release Channel**.
4. Apply the selection.
5. Choose **Install Update**.

The release channel may contain a branch name such as `main` or `dev`. Branch
names are validated before installation.

The selected branch is stored in:

```text
/data/.update_channel
```

The installed branch is stored in a persistent Python environment:

```text
/data/venv
```

Both paths are part of the add-on's private Home Assistant data directory and
survive service restarts, container recreation, and add-on upgrades.

After an in-app update, openHop Repeater exits so the selected code can be
loaded. The add-on starts the service again inside the same container and uses
the persistent environment on the next launch.

At startup, the add-on checks whether the selected branch matches the installed
branch. When they differ, it attempts to install the selected branch. If the
installation cannot be completed, the last runnable version is used when
available and installation is attempted again after the next restart.

To return to the default branch, select `main` in **Release Channel** and run
**Install Update**.

## Persistent storage

| Path | Contents |
|---|---|
| `/config/config.yaml` | User-editable openHop Repeater configuration |
| `/data/.update_channel` | Selected openHop Repeater branch |
| `/data/venv` | Python environment containing the installed branch |
| `/data/venv/.openhop-ha-python` | Python compatibility marker for the environment |
| `/var/lib/openhop_repeater` | Internal link to `/data` used by openHop Repeater |
| `/opt/openhop_repeater/venv` | Internal link to `/data/venv` used by the updater |

The `/data` directory is private to the add-on. Home Assistant removes it when
the add-on is uninstalled.

The generated virtual environment is excluded from add-on backups because it is
specific to the system architecture and Python version. It is rebuilt from the
stored release channel when required.

The user-editable configuration under `app_configs` is managed separately by
Home Assistant. Whether it is removed during uninstallation depends on the
configuration-removal choice made in Home Assistant.

## Networking

The add-on uses host networking. openHop Repeater companion identities can
listen on ports defined in `config.yaml`, so the complete port set cannot be
declared statically in the add-on metadata.

The web interface listens on port `8000` by default. The Home Assistant
**Open Web UI** action uses this port. When `http.port` is changed, open the
configured port directly in a browser.

## Hardware access

Supported transports include:

- local SPI/GPIO radios;
- USB radio adapters;
- serial KISS modems;
- TCP modems;
- companion services using local network ports.

The add-on requests full hardware access and mounts the host udev database for
device discovery. Disable **Protection mode** when local SPI or GPIO devices are
required.

Network or USB-based radio connections generally require less host-specific
configuration than direct SPI/GPIO access.

For Raspberry Pi SPI hardware, enable SPI in the host boot configuration and
use BCM GPIO numbering in `config.yaml`.

## Updates

There are two independent update paths:

- **openHop Repeater updates** are installed from the repeater web interface and
  control the selected upstream branch.
- **Home Assistant add-on updates** are installed from Home Assistant and update
  the container image, startup scripts, and bundled default version.

Installing an openHop Repeater branch does not update the Home Assistant add-on
itself.

## Backups

The add-on uses cold backups so the service is stopped while its persistent data
is captured. The generated `/data/venv` directory is excluded and is rebuilt
after restore when necessary.

The configuration file under `app_configs` should be included in the Home
Assistant backup configuration used for the system.

## Troubleshooting

### The selected branch is not active

Check the add-on log for entries similar to:

```text
selected branch: ...; active branch: ...
runtime package: ...
```

A branch installed by the updater should load from `/data/venv`. The default
package included in the image is used when no separate branch installation is
active.

### A branch cannot be installed

Branch installation requires:

- working DNS;
- HTTPS access to GitHub;
- a valid branch name;
- a branch that can be installed by `pip` for the current architecture.

The add-on continues with the last runnable installation when possible. Review
the complete installation error in the add-on log before retrying.

### The add-on does not start after editing `config.yaml`

The add-on validates the YAML syntax before starting openHop Repeater. Correct
the reported error and restart the add-on. The configuration file is not reset
automatically.

### The Web UI link opens the wrong port

The Home Assistant link targets port `8000`. When `http.port` uses another
value, open `http://<home-assistant-host>:<configured-port>/` directly.

### Local SPI or GPIO hardware is unavailable

Confirm that:

- **Protection mode** is disabled;
- the required host interface is enabled;
- the device and GPIO values in `config.yaml` match the host;
- no other service is using the same hardware.

## License

The Home Assistant add-on files are licensed under the MIT License. See the
repository root `LICENSE` file. openHop Repeater remains subject to its upstream
license.
