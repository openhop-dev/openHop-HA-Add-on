# Changelog

## 3.0.0

- Replace the separate main/dev add-ons with one branch-aware add-on.
- Retain the `openhop_repeater_main` slug for existing main-installation data.
- Persist the firmware update channel in Home Assistant's `/data` directory.
- Persist the updater virtual environment and start the repeater from it.
- Automatically reconcile a selected branch after container recreation.
- Keep the packaged `main` build as a runnable fallback.
- Add a container-safe `systemctl` compatibility shim for the firmware updater.
- Restart the bootstrap internally after firmware update and restart requests.
- Replace the old reduced config template with the complete upstream template.
- Generate unique admin and guest passwords for newly created configurations.
- Use Home Assistant's standard `/data` path for persistent runtime data.
- Keep Home Assistant's default container init enabled and forward stop signals.
- Use cold backups while excluding the reconstructable persistent venv.
- Remove obsolete upstream-sync metadata, duplicate add-on files, and dummy
  Home Assistant options.
- Add repository validation, shell checks, and branch-state unit tests.

## 2.0.1

- Previous split-channel wrapper release.
