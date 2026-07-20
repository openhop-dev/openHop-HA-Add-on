# Changelog

## 3.0.0

### Home Assistant integration

- Store the editable repeater configuration in Home Assistant's writable
  `addon_config` directory and include it in cold backups.
- Exclude the generated Python environment from backups and rebuild it when the
  app image, packaged runtime, dependencies, architecture, or Python ABI changes.
- Add repository metadata validation, Python tests, ShellCheck, and app-version
  consistency checks.
- Keep full hardware and udev access for SPI/GPIO, USB, serial, and other local
  radio transports.

### Configuration safety

- Ship the complete upstream configuration template from the packaged repeater
  image instead of relying on a stale wrapper copy.
- Create new configurations atomically with unique admin and guest passwords
  and a JWT signing secret.
- Merge newly packaged defaults into existing configurations without replacing
  user values or existing passwords.
- Validate merged YAML before publishing it, restrict configuration, backup,
  and identity-key permissions, and use a private umask for new runtime files.

### Branch updates and recovery

- Support release-channel selection and branch installation from the openHop
  Repeater web interface.
- Persist the selected channel and verified branch metadata in `/data`.
- Capture `direct_url.json` before upstream metadata cleanup runs, then verify
  the actual imported package path before reporting a branch as active.
- Guard the updater's venv `pip` entry point so it accepts only version checks
  and branch installs targeting a validated Git ref in the official repository.
- Preserve a protected copy of the packaged runtime and setup-wizard JSON files
  outside the source tree removed by the upstream updater.
- Detect broken or partially modified update environments, rebuild them cleanly,
  and fall back to the protected packaged runtime after failed branch updates.
- Restart the repeater inside the same container after a successful in-app
  update while preventing rapid clean exits from becoming an infinite loop.

### Runtime lifecycle

- Install signal handling before startup work begins, preserve stop state
  across internal `exec` restarts, and honor it throughout the lifecycle.
- Forward termination to the repeater, wait for it to exit, and force-stop it
  after a bounded grace period so no orphan process survives the app wrapper.
- Keep `/var/lib/openhop_repeater` and the updater's hard-coded venv path linked
  to persistent Home Assistant app data.
- Remove the base image's package-specific setuptools-scm override from runtime
  branch builds and provide system `pip` for upstream updater cleanup commands.
