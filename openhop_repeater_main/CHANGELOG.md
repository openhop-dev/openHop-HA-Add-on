# Changelog

## 2.0.0

- Breaking rebrand to openHop Repeater add-on identifiers.
- Rename the add-on folder, slug, Home Assistant config folder hint, runtime config path, persistent data path, and bundled example file to openHop names.
- Remove automatic migration from legacy add-on config subfolders; copy any existing config and identity files into the new openHop add-on config folder before starting this version.

## 1.0.7

- Rebrand the add-on to openHop Repeater in Home Assistant metadata, docs, and bundled assets.
- Update upstream repository links and sync automation to `openhop-dev/openhop_repeater`.

## 1.0.6

- Track upstream `MAIN` commit `e17d113` from `openhopdev/openhop-repeater:main`
- Previous tracked commit: `a36cb6a`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/a36cb6af44ab63247dd6d0f414afc6e53de18012...e17d1137ab2d2d5b86d03c99523272289b7688aa
- Included upstream commits:
  - `18300cb` feat: add GPS diagnostics web UI
  - `9cd2de9` chore: move GPS diagnostics UI to frontend repo
  - `8ae1c0f` feat: sync system time from GPS
  - `53f6e8a` fix: Remove old letsmesh_handler.py file
  - `3a6da40` fix: Always parse additional brokers
  - `b3fdfee` fix: Handle TLS for all MQTT connections
  - `d4aecf7` fix: Stop warning spam if brokers are disabled
  - `bdb98f3` fix(docs): Updated example config with TLS information

## 1.0.5

- Add user-local Python site-packages directories to `PYTHONPATH` before startup

## 1.0.4

- Make startup config inspection resilient when the inline Python YAML import fails

## 1.0.3

- Handle rootless upstream image builds in the add-on Dockerfiles
- Run the add-on wrapper as root so startup can manage `/etc/openhop_repeater`

## 1.0.2

- Handle rootless upstream image builds in the add-on Dockerfiles
- Run the add-on wrapper as root so startup can manage `/etc/openhop_repeater`

## 1.0.1

- Enable host networking so companion nodes can bind dynamic host ports

## 1.0.0

- Initial release of the Home Assistant add-on repository
- Add separate `dev` and `main` channel add-ons with aligned behavior
- Prepare `openhop_repeater_main` to track upstream `openhopdev/openhop-repeater:main`
