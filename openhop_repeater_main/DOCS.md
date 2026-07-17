# Home Assistant Add-on: openHop Repeater

## About

This add-on runs the upstream openHop Repeater container and keeps the full
repeater configuration in one editable file:

```text
/config/config.yaml
```

On the Home Assistant host, the file is located in an add-on config directory
matching:

```text
addon_configs/*_openhop_repeater_main/config.yaml
```

The first start copies the complete upstream example configuration and replaces
the insecure example login passwords with unique generated values. Existing
configuration files are never overwritten.

## Installation

1. Add the openHop Repeater add-on repository to Home Assistant.
2. Install **openHop Repeater**.
3. For local SPI or GPIO radio hardware, disable **Protection mode** in the
   add-on settings.
4. Start the add-on once, then stop it.
5. Edit the generated `config.yaml` with Studio Code Server, File editor, SSH,
   or another tool that can access the add-on config directory.
6. Start the add-on and select **Open Web UI**.

The starter configuration uses `radio_type: null`, so the service can start
without radio hardware while it is being configured.

## Configuration

`/config/config.yaml` is the only runtime configuration source. Home Assistant
add-on options are intentionally not used for repeater settings because that
would duplicate the upstream schema and split configuration across two places.

At minimum, review:

- `repeater.node_name`
- `repeater.security.admin_password`
- `repeater.security.guest_password`
- `radio_type`
- the selected radio backend
- `radio.frequency`, bandwidth, spreading factor, coding rate, and TX power
- identity, MQTT, companion, and policy settings relevant to the installation

The bundled template follows the upstream firmware supplied with this add-on
release and includes all available sections and comments.

## Switching branch from the web interface

The former separate `main` and `dev` add-ons have been replaced by one add-on.
To switch:

1. Open the repeater web interface.
2. Open the update dialog.
3. Select the desired **Release Channel**.
4. Apply the channel and choose **Install Update**.

The firmware writes the selected branch to:

```text
/var/lib/openhop_repeater/.update_channel
```

Inside this add-on, `/var/lib/openhop_repeater` points to Home Assistant's
persistent `/data` directory. The firmware updater installs branches into
`/opt/openhop_repeater/venv`; that path points to `/data/venv`. Consequently,
both the selected branch and installed code survive a process restart, container
recreation, and add-on upgrade.

The upstream updater performs legacy systemd cleanup before installing. Home
Assistant containers do not run systemd, so the image supplies a no-op
`/bin/systemctl` compatibility command only when the base image has no real
`systemctl`. This prevents the update thread from failing before it reaches pip.

After an update, the firmware intentionally exits its process. The add-on
wrapper catches that clean exit and reruns its bootstrap inside the same
container. This activates the selected branch even when the Supervisor or
container runtime would otherwise leave a cleanly exited container stopped.

The add-on always starts the repeater with the persistent virtual environment.
If only the packaged `main` build is present, the virtual environment falls back
to that image-provided package. Once a branch is installed, its package takes
precedence.

When the selected branch and installed branch differ at startup, the add-on
attempts to install the selected branch automatically. If GitHub is temporarily
unreachable, the last runnable build is retained and the installation is retried
on the next restart.

### Returning to `main`

Select `main` in **Release Channel** and install the update. The `main` branch is
then installed into the persistent environment. A later add-on image update can
still replace the packaged fallback build.

## Persistent paths

| Path | Purpose |
|---|---|
| `/config/config.yaml` | Complete user-editable runtime configuration |
| `/data` | Persistent add-on data provided by Home Assistant |
| `/data/.update_channel` | Selected upstream branch |
| `/data/venv` | Branch installed by the in-app updater |
| `/var/lib/openhop_repeater` | Compatibility symlink to `/data` |
| `/opt/openhop_repeater/venv` | Updater compatibility symlink to `/data/venv` |

Home Assistant takes cold backups of the add-on data. The generated `venv`
directory is excluded because it is architecture- and Python-version-specific
and can be reconstructed from the persisted release channel after restore.

## Migration from the previous repository layout

### Existing `openHop Repeater Main` installation

The slug remains `openhop_repeater_main`, so the existing config and persistent
add-on data are retained. After updating the repository, rebuild or reinstall
the add-on image if Home Assistant does not do so automatically.

### Existing `openHop Repeater Dev` installation

The separate `openhop_repeater_dev` add-on no longer exists. Before uninstalling
it:

1. Back up its `config.yaml`, identity, and any required data.
2. Install the unified **openHop Repeater** add-on.
3. Start it once to create its config directory.
4. Replace the generated config with the backed-up dev configuration.
5. Start the add-on, open the update dialog, and select `dev`.

Home Assistant uses a different data directory for each add-on slug, so dev data
cannot be migrated automatically by the unified main-slug add-on.

## Networking

The add-on uses host networking. This is required because companion identities
can expose arbitrary TCP ports configured inside `config.yaml`; those dynamic
ports cannot be declared individually in static add-on metadata.

The web interface listens on port `8000` by default. If `http.port` is changed,
the Home Assistant **Open Web UI** link still points to port `8000`; open the
configured port manually instead.

## Hardware access

The add-on supports several radio transports, including local SPI/GPIO devices,
USB adapters, serial KISS modems, and TCP modems. It requests full hardware
access rather than combining that setting with redundant per-device flags. The
host udev database is also mounted read-only for device discovery.

`full_access: true` and disabled AppArmor are retained as an explicit exception
for local SPI/GPIO hardware whose device paths vary by host and cannot be safely
expressed as one static device list. Home Assistant's **Protection mode** must be
disabled for those local hardware configurations. Network and USB-based setups
should still be preferred where broad host hardware access is not required.

For Raspberry Pi SPI hardware, enable SPI in the host boot configuration and use
BCM GPIO numbering in `config.yaml`.

## Updating the add-on wrapper

The repeater's in-app updater changes the selected upstream firmware branch. It
does not update this Home Assistant wrapper, its base container image, or the
bundled fallback build. Install add-on updates from Home Assistant as usual in
addition to using the repeater update dialog.

## Troubleshooting

### The requested branch is not active

Check the add-on log for these lines:

```text
selected branch: ...; active branch: ...
runtime package: ...
```

A branch-installed package should resolve from `/data/venv`. The packaged
fallback resolves from the upstream image's site-packages directory.

### Branch installation fails

Branch installation requires DNS, HTTPS access to GitHub, Git, and Python build
tools. These are supplied by the upstream image, but a network outage or broken
upstream branch can still cause installation to fail. The add-on keeps the last
runnable build when possible.

### Configuration validation fails

The add-on validates YAML before starting the repeater. Correct the reported
syntax error in `config.yaml` and restart it. The file is not replaced or reset.


## License

This add-on wrapper is licensed under the MIT License. See the repository root
`LICENSE` file. The bundled openHop Repeater software remains subject to its
upstream license.
