# Changelog

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
