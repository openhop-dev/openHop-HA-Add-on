# Home Assistant App: openHop Repeater

## About

This app runs openHop Repeater as a managed Home Assistant service.

All repeater settings are stored in one editable YAML file:

```text
/config/config.yaml
```

On the Home Assistant host, the file is available under:

```text
/addon_configs/*_openhop_repeater_main/config.yaml
```

The app creates the file on first start from the bundled openHop Repeater
configuration template. Unique admin and guest passwords plus a JWT signing
secret are generated for a new configuration. On later starts, missing settings
from the packaged template are merged into the existing file while user values
are preserved. If a merge
introduces missing main admin, guest password, or JWT secret fields, unique
values are generated before the file is published atomically. Security fields
already present in the user configuration are never silently changed by this
merge, except that an empty JWT secret is replaced before startup.

## Installation

1. Add the openHop Repeater repository to the Home Assistant app store.
2. Install **openHop Repeater**.
3. Disable **Protection mode** when using directly attached SPI, GPIO, USB, or
   serial radio hardware.
4. Start the app once to create `config.yaml`.
5. Stop the app and edit the generated file.
6. Start the app and select **Open Web UI**.

The initial configuration uses `radio_type: null`. This allows the service to
start before radio hardware has been configured.

## Configuration

`/config/config.yaml` is the only source of repeater settings. Home Assistant
app options are not used for the openHop Repeater configuration.

Review at least the following values before normal operation:

- `repeater.node_name`
- `repeater.security.admin_password`
- `repeater.security.guest_password`
- `radio_type`
- the configuration section for the selected radio backend
- radio frequency, bandwidth, spreading factor, coding rate, and transmit power
- identity, MQTT, companion, and policy settings used by the installation

The bundled template contains the configuration sections and comments supplied
with the openHop Repeater version included in the app image.

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

Both paths are part of the app's private Home Assistant data directory. The
selected channel survives service restarts, container recreation, and app
upgrades. The generated environment is retained only while it remains
compatible with the current app image and Python runtime.

After an in-app update, openHop Repeater exits so the selected code can be
loaded. The app starts the service again inside the same container and uses
the persistent environment on the next launch.

At startup, the app checks both branch metadata and the actual Python import
path. A branch is considered active only when the selected branch matches the
verified installation in `/data/venv`. The verified branch is also stored in a
small marker file so startup still works if upstream metadata cleanup removes a
`direct_url.json` file. If an installation fails or leaves the environment
unusable, the app discards that environment and reconstructs a clean one
that runs the protected version packaged in the app image. The selected channel
is retained so installation can be retried after the next restart.

To return to the default branch, select `main` in **Release Channel** and run
**Install Update**.

## Persistent storage

| Path | Contents |
|---|---|
| `/config/config.yaml` | User-editable openHop Repeater configuration |
| `/data/.update_channel` | Selected openHop Repeater branch |
| `/data/venv` | Python environment containing the installed branch |
| `/data/venv/.openhop-ha-python` | App-image and Python compatibility marker for the environment |
| `/data/venv/.openhop-ha-branch` | Last branch whose venv installation was verified by the app |
| `/var/lib/openhop_repeater` | Internal link to `/data` used by openHop Repeater |
| `/opt/openhop_repeater/venv` | Internal link to `/data/venv` used by the updater |

The `/data` directory is private to the app. Home Assistant removes it when
the app is uninstalled.

The generated virtual environment is excluded from app backups because it is
specific to the app image, packaged Python runtime and dependencies, system
architecture, and Python version. It is rebuilt from the stored release channel
when required.

The app image also contains a protected copy of its packaged `main` runtime
outside `/opt/openhop_repeater`, because the upstream updater removes source
trees from that directory before installing a branch. The image also preserves
the radio hardware and preset JSON files required by the first-run setup wizard
and exposes them beside packages installed into the persistent venv.

The user-editable configuration under `addon_configs` is managed by Home
Assistant and included with the app backup. Whether it is removed during
uninstallation depends on the configuration-removal choice made in Home
Assistant.

## Networking

The app uses host networking. openHop Repeater companion identities can
listen on ports defined in `config.yaml`, so the complete port set cannot be
declared statically in the app metadata.

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

The app requests full hardware access and mounts the host udev database for
device discovery. Home Assistant only grants `full_access` when **Protection
mode** is disabled, so disable it for directly attached SPI, GPIO, USB, or
serial devices. TCP modems and other network-only connections do not require
that hardware access.

Network-based radio connections generally require less host-specific
configuration than direct hardware access.

For Raspberry Pi SPI hardware, enable SPI in the host boot configuration and
use BCM GPIO numbering in `config.yaml`.

## Updates

There are two independent update paths:

- **openHop Repeater updates** are installed from the repeater web interface and
  control the selected upstream branch.
- **Home Assistant app updates** are installed from Home Assistant and update
  the container image, startup scripts, bundled default version, and packaged
  configuration template. Missing template settings are merged into the user
  configuration on the next start.

Installing an openHop Repeater branch does not update the Home Assistant app
itself.

## Backups

The app uses cold backups so the service is stopped while its persistent data
is captured. The generated `/data/venv` directory is excluded and is rebuilt
after restore when necessary.

Home Assistant includes the configuration file under `addon_configs` with the
app backup.

## Troubleshooting

### The selected branch is not active

Check the app log for entries similar to:

```text
selected branch: ...; active branch: ...
runtime package: ...
```

A branch installed by the updater should load from `/data/venv`. The protected
default package included in the image is used when no separate branch
installation is active. Startup logs report the resolved package path rather
than trusting installation metadata alone.

### A branch cannot be installed

Branch installation requires:

- working DNS;
- HTTPS access to GitHub;
- a valid branch name;
- a branch that can be installed by `pip` for the current architecture.

The app removes a failed or partially modified branch environment and falls
back to the protected runtime included in the app image. Review the complete
installation error in the app log before retrying.

### The app does not start after editing `config.yaml`

The app validates the YAML syntax before starting openHop Repeater. Correct
the reported error and restart the app. The configuration file is not reset
automatically.

### The Web UI link opens the wrong port

The Home Assistant link targets port `8000`. When `http.port` uses another
value, open `http://<home-assistant-host>:<configured-port>/` directly.

### Directly attached hardware is unavailable

Confirm that:

- **Protection mode** is disabled;
- the required host interface is enabled;
- the device and GPIO values in `config.yaml` match the host;
- no other service is using the same hardware.

## License

The Home Assistant app files are licensed under the MIT License. See the
repository root `LICENSE` file. openHop Repeater remains subject to its upstream
license.
