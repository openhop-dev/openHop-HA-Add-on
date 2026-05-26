# Changelog

## 1.0.15

- Track upstream `DEV` commit `dc317b6` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `ab55748`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/ab55748f3f7856db207e093a00dbbc5e8bdd69aa...dc317b6568f14d1a9b97d0c942eccb693e0ad796
- Included upstream commits:
  - `e17d113` Merge pull request #259 from pyMC-dev/dev
  - `e20eaa7` feat: add LAFVIN UPS Module 3S sensor plugin (lafvin_ups_3s)
  - `dc317b6` Merge pull request #261 from CarlsonCustoms/feat/lafvin-ups-3s-sensor

## 1.0.14

- Track upstream `DEV` commit `ab55748` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `85f2823`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/85f282357ca6cd6516d961eb8650ecc2a6286f74...ab55748f3f7856db207e093a00dbbc5e8bdd69aa
- Included upstream commits:
  - `ab55748` fix: prevent advert echos in the packet table

## 1.0.13

- Track upstream `DEV` commit `85f2823` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `a48b298`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/a48b29837acab532f576c5486b6aeae6ee458ed3...85f282357ca6cd6516d961eb8650ecc2a6286f74
- Included upstream commits:
  - `85f2823` feat: expand allowed sections for configuration imports to include additional radio types

## 1.0.12

- Track upstream `DEV` commit `a48b298` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `4cf04f8`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/4cf04f87d1b2fa6c4ddcbd8a8bc9591077ca2295...a48b29837acab532f576c5486b6aeae6ee458ed3
- Included upstream commits:
  - `5c68707` feat: add endpoint to discover available serial/USB modem device paths
  - `3244f7b` feat: add validation for TX power settings and update API endpoint for serial ports
  - `2a031b7` feat: add validate_config endpoint to check config.yaml syntax and required settings
  - `78648f2` feat: add site_info endpoint to return site identification name without authentication
  - `a48b298` feat: pre-restart config validation and site identification

## 1.0.11

- Track upstream `DEV` commit `4cf04f8` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `8f3477d`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/8f3477ddd6fa879368dad99e18b258770bdeb380...4cf04f87d1b2fa6c4ddcbd8a8bc9591077ca2295
- Included upstream commits:
  - `d25e97a` feat: implement setup status check and reject subsequent setups after completion
  - `5b93d10` fix: update loop detection thresholds and improve path hash handling in API endpoints
  - `b464fa8` docs: update example configuration for Waveshare UPS D and E Hats
  - `22b39e5` fix: update maintainer information in changelog, control, and build scripts
  - `4cf04f8` test: sensor tests with mock implementations and additional assertions

## 1.0.10

- Track upstream `DEV` commit `8f3477d` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `22adbd1`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/22adbd1a84b48bf2143065dca03504b0c3dbcaaa...8f3477ddd6fa879368dad99e18b258770bdeb380
- Included upstream commits:
  - `6e89272` Add Waveshare UPS HAT (E) sensor plug-in
  - `8f3477d` Merge pull request #256 from CarlsonCustoms/add-waveshare-ups-hat-e

## 1.0.9

- Track upstream `DEV` commit `22adbd1` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `6aab7ec`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/6aab7ec67632cb00ff29cb4e8dab2404cf788339...22adbd1a84b48bf2143065dca03504b0c3dbcaaa
- Included upstream commits:
  - `22adbd1` feat: add setup usb/tcp details on setup

## 1.0.8

- Track upstream `DEV` commit `6aab7ec` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `cbfcb69`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/cbfcb69c07adc893a5f4eaac8f3aa1cb47afb970...6aab7ec67632cb00ff29cb4e8dab2404cf788339
- Included upstream commits:
  - `7d54859` Add example configurations for SHTC3 and Waveshare UPS Hat sensors
  - `6aab7ec` fix:update-restart-functions

## 1.0.7

- Track upstream `DEV` commit `cbfcb69` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `13ea672`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/13ea67259711913c498081071fe5b86eb6b283f0...cbfcb69c07adc893a5f4eaac8f3aa1cb47afb970
- Included upstream commits:
  - `9c1661f` Add SHTC3 and Waveshare UPS HAT (D) sensor plug-ins
  - `8b0607a` Add NMEA GPS sensor plug-in
  - `f88d3c5` Revert "Add NMEA GPS sensor plug-in"
  - `cbfcb69` Merge pull request #255 from CarlsonCustoms/add-shtc3-waveshare-sensors

## 1.0.6

- Track upstream `DEV` commit `13ea672` from `pymcdev/pymc-repeater:dev`
- Previous tracked commit: `193b428`
- Upstream diff: https://github.com/pyMC-dev/pyMC_Repeater/compare/193b428cc2949695f3c3434ef3349d32ee3a207d...13ea67259711913c498081071fe5b86eb6b283f0
- Included upstream commits:
  - `7b6babd` service: restart containers by exiting process
  - `ab8ae30` web: clarify docker restart update messaging
  - `11e2b90` ci: route docker publish by repository owner
  - `f21aba0` docker: mount config directory in compose
  - `13ea672` Merge pull request #254 from yellowcooln/dev

## 1.0.5

- Add user-local Python site-packages directories to `PYTHONPATH` before startup

## 1.0.4

- Make startup config inspection resilient when the inline Python YAML import fails

## 1.0.3

- Handle rootless upstream image builds in the add-on Dockerfiles
- Run the add-on wrapper as root so startup can manage `/etc/pymc_repeater`

## 1.0.2

- Handle rootless upstream image builds in the add-on Dockerfiles
- Run the add-on wrapper as root so startup can manage `/etc/pymc_repeater`

## 1.0.1

- Enable host networking so companion nodes can bind dynamic host ports

## 1.0.0

- Initial release of the Home Assistant add-on repository
- Add separate `dev` and `main` channel add-ons with aligned behavior
- Track upstream `pymcdev/pymc-repeater:dev` in `pymc_repeater_dev`
