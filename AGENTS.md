# Repository Guidelines

## Project Structure & Module Organization

This repository ships two Home Assistant add-ons for openHop Repeater:

- `pymc_repeater_dev/` tracks the upstream openHop Repeater `:dev` image
- `pymc_repeater_main/` tracks the upstream openHop Repeater `:main` image

Each add-on folder contains `config.yaml`, `Dockerfile`, `run.sh`, `pymc-repeater.example.yaml`, docs, and UI assets. Root files are `repository.yaml`, `.github/workflows/sync-upstream-channels.yml`, `.github/upstream-*.json`, and `scripts/sync_upstream_channel.py`.

Keep both add-ons functionally identical. Only the channel-specific name, slug, config-path hint, changelog text, and upstream image tag should differ.

## Build, Test, and Development Commands

- `docker build -t openhop-repeater-dev-test ./pymc_repeater_dev` builds the dev add-on.
- `docker build -t openhop-repeater-main-test ./pymc_repeater_main` builds the main add-on when the upstream `:main` tag exists.
- `sh -n pymc_repeater_dev/run.sh` and `sh -n pymc_repeater_main/run.sh` check shell syntax.
- `python3 -m py_compile scripts/sync_upstream_channel.py` validates the sync helper.
- `python3 - <<'PY'` with `yaml.safe_load(...)` is the expected YAML sanity check after manifest or docs edits.

There is no formal test suite yet; validation is build-, syntax-, and config-based.

## Coding Style & Naming Conventions

- Use 2-space indentation in YAML and 4 spaces in Python.
- Keep shell scripts POSIX `sh` compatible.
- Preserve Home Assistant file names such as `config.yaml`, `DOCS.md`, and `translations/en.yaml`.
- When changing shared behavior, update both add-on folders in the same pass.

## Commit & Pull Request Guidelines

- Use short imperative commit subjects, for example `Split repo into main and dev add-ons`.
- Keep commits scoped to one change area.
- PRs should summarize user-visible behavior, changed config paths, and validation performed.

## Security & Configuration Notes

- Both add-ons run with `full_access: true` and AppArmor disabled so they can access SPI, GPIO, USB, and serial hardware.
- Host-side config files live in `addon_config/*_pymc_repeater_dev/config.yaml` and `addon_config/*_pymc_repeater_main/config.yaml`.
