# Changelog

## 1.0.3

- Track upstream `DEV` commit `193b428` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `baec25b`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/baec25b7bb57064e7cb9e3b545aa911dfd789f6f...193b428cc2949695f3c3434ef3349d32ee3a207d
- Included upstream commits:
  - `5f43085` ci: restrict docker publish workflow
  - `f4d8948` Merge pull request #251 from yellowcooln/chore/manual-docker-workflow
  - `13b8004` wip: null-radio defaults and needs_setup updates
  - `d7f2d2c` setup wizard: pymc_tcp / pymc_usb hardware tiles
  - `052474c` feat: add connection type for KISS and pymc modems in radio settings
  - `56113c2` feat: update radio status handling to show radio errors
  - `0e10312` update ui for setup
  - `a08c4d0` Update repository conditions in docker-publish.yml

## 1.0.2

- Track upstream `DEV` commit `baec25b` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `5b95be3`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/5b95be3db5b245607fd2d2f6d401a27eefaa4004...baec25b7bb57064e7cb9e3b545aa911dfd789f6f
- Included upstream commits:
  - `d5903c3` Add Southern California radio preset
  - `7a0aec7` feat(presets): expose bundled broker presets via GET /api/broker_presets
  - `3baf115` Dispatch add-on sync after Docker publish
  - `a7ae704` Merge pull request #245 from dmduran12/broker_template-UIsync
  - `4f278f1` Merge pull request #243 from dmduran12/patch-1
  - `ce1acab` fix: parse sync_word as integer in get_radio_for_board function
  - `2d875ae` Derive Docker dev version from git metadata
  - `baec25b` Merge pull request #247 from yellowcooln/addon-sync-workflow

## 1.0.1

- Enable host networking so companion nodes can bind dynamic host ports

## 1.0.0

- Initial release of the Home Assistant add-on repository
- Add separate `dev` and `main` channel add-ons with aligned behavior
- Track upstream `pymcdev/pymc-repeater:dev` in `pymc_repeater_dev`
