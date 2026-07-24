# Changelog

## 2.0.12

- Track upstream `DEV` commit `b1ea257` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `c2d6396`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/c2d63968bb79af37a8407f0632194ac361d2a92d...b1ea25727cbe086e422d8671cf77032597ce2621
- Included upstream commits:
  - `72e874f` fix(regions): scope flood replies to the request's region
  - `95555e0` fix(repeater): relax identity prefix guard to same-namespace collisions
  - `6e5d029` fix(repeater): report identity config errors without a stack trace
  - `b1ea257` Merge pull request #370 from agessaman/fix/more-things

## 2.0.11

- Track upstream `DEV` commit `c2d6396` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `5d75cb9`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/5d75cb9ad409bd73520e0f7530f3ee7bdf7c783e...c2d63968bb79af37a8407f0632194ac361d2a92d
- Included upstream commits:
  - `6f61365` feat: enhance flood loop detection with hash size validation and update tests
  - `e5d72ea` feat: update advert packet sending with error handling and add corresponding tests
  - `e2172c2` refactor: separate import statements for clarity
  - `a0eb0fc` feat: TX delay update calculation with route-aware random window and update tests
  - `8875177` fix(router): consume packets only on authenticated local handling (#353)
  - `8d766c8` Merge pull request #357 from agessaman/fix/consume-on-decrypt
  - `62ad742` fix(router): consume PATH and RESPONSE only after MAC authentication
  - `059065c` fix(router): never forward control packets to the engine

## 2.0.10

- Track upstream `DEV` commit `5d75cb9` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `86a2ac3`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/86a2ac308329387c1323a79f583b14c5bcff89e3...5d75cb9ad409bd73520e0f7530f3ee7bdf7c783e
- Included upstream commits:
  - `fac5b1b` feat: add CAD calibration session configuration and manual check endpoint
  - `0485023` feat: add CAD symbol number configuration with validation and logging
  - `4990322` feat: implement dynamic serving of frontend static assets and enhance error handling for unraisable exceptions
  - `ad87ca3` feat: enhance CAD configuration with dynamic symbol number handling and update OpenAPI documentation
  - `5d75cb9` feat: add manual cad tests to cad UI

## 2.0.9

- Track upstream `DEV` commit `86a2ac3` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `25db2d1`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/25db2d19fcb9120e6523f1a65473abbf41e88456...86a2ac308329387c1323a79f583b14c5bcff89e3
- Included upstream commits:
  - `86a2ac3` feat: enhance CAD calibration thresholds and sensitivity scoring

## 2.0.8

- Track upstream `DEV` commit `25db2d1` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `95500ec`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/95500ece09e8a5badc1973b5e62623769dff6f0b...25db2d19fcb9120e6523f1a65473abbf41e88456
- Included upstream commits:
  - `b2eb45b` feat: Add LBT diagnostics endpoint with correlation analysis
  - `25db2d1` feat:add LBT reporting chart/heat map UI

## 2.0.7

- Track upstream `DEV` commit `95500ec` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `ff53b25`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/ff53b2520b1f56815025001fcf27727dcc9b27ba...95500ece09e8a5badc1973b5e62623769dff6f0b
- Included upstream commits:
  - `fa046a1` feat: allow unauthenticated config import during first-run setup
  - `95500ec` feat:add restore config to first time setup

## 2.0.6

- Track upstream `DEV` commit `ff53b25` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `05d1e39`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/05d1e391d65e951ba5628d987293372162db3da2...ff53b2520b1f56815025001fcf27727dcc9b27ba
- Included upstream commits:
  - `17f8bcc` feat: Allow setting max. flood interval to 50
  - `667169c` feat: Bump to 168 hours to match docs.meshcore.io
  - `d1a9230` feat: allow API key authentication in WebSocket handler
  - `4a12478` Replace favicon with openhop favicon
  - `d8bc448` fix: update dependencies for platform-specific installation of openhop_core
  - `676e2ce` perf: add covering index for airtime chart queries
  - `e225148` perf: force timestamp range scan for windowed packet-stats GROUP BYs
  - `9231023` fix: correct model name in MeshCoreToMqttPusher class

## 2.0.5

- Track upstream `DEV` commit `05d1e39` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `143c763`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/143c7633bf61e80c3242ac2d54b3d72463d4907d...05d1e391d65e951ba5628d987293372162db3da2
- Included upstream commits:
  - `141126a` Clean up radio-settings.json by removing unused fields
  - `f158845` Merge branch 'dev' into patch-1
  - `90d63d6` Merge branch 'pr-340' into dev
  - `1a0823b` fix: rename radio settings entry for rak6421-13300x-slot2 to rak6421-13300x-slot2-hw-mod
  - `9177d1a` feat: add repeat on/off to status for mqtt
  - `4a055be` fix(router): try both companion and server on colliding dest hash
  - `630f2cf` Merge branch 'pr-343' into dev
  - `05d1e39` Merge branch 'dev' of https://github.com/rightup/pyMC_Repeater into dev

## 2.0.4

- Track upstream `DEV` commit `143c763` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `7d30dd4`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/7d30dd42476051bd96461368b14f1b9cb0cb6917...143c7633bf61e80c3242ac2d54b3d72463d4907d
- Included upstream commits:
  - `c14d8b2` fix: refresh bundled console in docker builds
  - `143c763` Merge pull request #344 from yellowcooln/fix/docker-console-cache-bust

## 2.0.3

- Track upstream `DEV` commit `7d30dd4` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `0561803`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/0561803eeb5766382fc2e4128b32cd305added3f...7d30dd42476051bd96461368b14f1b9cb0cb6917
- Included upstream commits:
  - `172c8cc` Initialise MQTT handler only when at least one broker is configured to save some lil cpu and logging
  - `a53df3d` feat: implement MeshCore-compatible key generation for all identity keys with guards for 0x00 and 0xff prefixs
  - `38efb05` fix: expose effective drop reason to PacketRouter
  - `9be74ef` Merge remote-tracking branch 'origin/feat-std-key-formats' into dev
  - `a964062` Merge branch 'pr-323' into dev
  - `823308a` fix: update drop reason handling in PacketRouter and RepeaterHandler
  - `baa89e8` updated working zebra duo config radio 0 / 1
  - `b84479d` fixed rak6421 config.

## 2.0.2

- Track upstream `DEV` commit `0561803` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `6de2b23`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/6de2b23266c771cc4e0a8062eb6ac032213cc13f...0561803eeb5766382fc2e4128b32cd305added3f
- Included upstream commits:
  - `60357f5` Merge pull request #320 from openhop-dev/dev
  - `add7011` feat: bundle PyMC Console in Docker image
  - `4a7720e` fix: route fork Docker image publishes
  - `f3d3129` fix: route fork Docker image publishes
  - `a88ac21` Merge pull request #330 from yellowcooln/dev
  - `0561803` merge: sync dev with main

## 2.0.1

- Track upstream `DEV` commit `6de2b23` from `openhop/openhop-repeater:dev`
- Previous tracked commit: `2b07e79`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/2b07e79ccd3f5077f08b5ad12aa987c19f771638...6de2b23266c771cc4e0a8062eb6ac032213cc13f
- Included upstream commits:
  - `b4b4483` feat: integrate openHop Glass inform policy sync
  - `44a2d2f` feat: add system info to hardware stats sensor
  - `71f4e47` Bundle policy objects UI
  - `cf896b2` Revert "Bundle policy objects UI"
  - `2b67dea` refactor:rename-project-to-openhop
  - `ffb0836` refactor: update legacy paths and cleanup in management scripts
  - `6f6e984` refactor: simplify hardware dependency in optional dependencies
  - `16e8857` refactor: migrate legacy pymc paths to openhop and clean up system packages

## 2.0.0

- Breaking rebrand to openHop Repeater add-on identifiers.
- Rename the add-on folder, slug, Home Assistant config folder hint, runtime config path, persistent data path, and bundled example file to openHop names.
- Remove automatic migration from legacy add-on config subfolders; copy any existing config and identity files into the new openHop add-on config folder before starting this version.

## 1.0.42

- Rebrand the add-on to openHop Repeater in Home Assistant metadata, docs, and bundled assets.
- Update upstream repository links and sync automation to `openhop-dev/openhop_repeater`.

## 1.0.41

- Track upstream `DEV` commit `2b07e79` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `c0d919c`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/c0d919c0e2ae9a0232e2f7249c814fa82ea11b34...2b07e79ccd3f5077f08b5ad12aa987c19f771638
- Included upstream commits:
  - `f1e860d` feat(presets): add Meshat.se broker preset
  - `2b07e79` Merge pull request #309 from Bjorkan/dev

## 1.0.40

- Track upstream `DEV` commit `c0d919c` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `0c6d27a`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/0c6d27a9b109042cc1713a8bc529c0e103115a4d...c0d919c0e2ae9a0232e2f7249c814fa82ea11b34
- Included upstream commits:
  - `77fc244` fix: baseline openHop modem CRC stats
  - `dde487b` fix: add generic openHop modem stats sensor
  - `642c019` fix: preserve modem GPS satellites in view
  - `5d3733a` fix: satisfy pre-commit for modem HTTP telemetry
  - `f2b7d25` fix: slow sensor polling to 60 seconds
  - `1c186d7` fix: throttle only openHop modem sensor polling
  - `5aebb4d` style: format sensor manager polling change
  - `1881ad9` feat: derive modem battery percent from voltage

## 1.0.39

- Track upstream `DEV` commit `0c6d27a` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `0f980e4`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/0f980e4e03e90625da3bb3310ce42e0c3ce2d9cc...0c6d27a9b109042cc1713a8bc529c0e103115a4d
- Included upstream commits:
  - `2435757` feat: enhance SQLiteHandler and StorageCollector for improved caching and async performance
  - `cd763e2` feat: implement threaded stats broadcasting in StorageCollector
  - `0c6d27a` Merge pull request #304 from agessaman/feat/database-load-mitigations

## 1.0.38

- Track upstream `DEV` commit `0f980e4` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `19ae451`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/19ae4516da2d68683d1473f0d8af9d9efaa0d1aa...0f980e4e03e90625da3bb3310ce42e0c3ce2d9cc
- Included upstream commits:
  - `0ccc353` feat: improve Proxmox LXC installer prompts
  - `0f980e4` Merge pull request #302 from yellowcooln/feat/lxc-installer-curl-container-id

## 1.0.37

- Track upstream `DEV` commit `19ae451` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `6e9b798`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/6e9b798ef389ac93d5ed6998be2153932ac771a3...19ae4516da2d68683d1473f0d8af9d9efaa0d1aa
- Included upstream commits:
  - `8fd28b7` added zebra hat duo
  - `a152e0e` Update radio-settings.json
  - `bca3f37` Update radio-settings.json
  - `19ae451` Merge pull request #297 from Littleaton/dev

## 1.0.36

- Track upstream `DEV` commit `6e9b798` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `9f18a1d`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/9f18a1db79fe48518b1e9d37c7e8a1d138ee4fa1...6e9b798ef389ac93d5ed6998be2153932ac771a3
- Included upstream commits:
  - `3d97413` fix: add dialout group to Docker image
  - `6e9b798` Merge pull request #296 from yellowcooln/fix/docker-dialout-group

## 1.0.35

- Track upstream `DEV` commit `9f18a1d` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `de129c1`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/de129c1c1503e1f251a9ceb8eff38dbd50f9154a...9f18a1db79fe48518b1e9d37c7e8a1d138ee4fa1
- Included upstream commits:
  - `b659aa0` Update Femtofox radio settings, remove gpiod requirement and set 1w as 22db (boosts to 30db anyway on hardware)
  - `40c7933` Merge branch 'dev' of https://github.com/theshaun/openhop_repeater into dev
  - `b9c82b5` Resolve gpio_chip + use_gpiod_backend not being set during setup
  - `8b948e1` dont be silly shaun
  - `9f18a1d` Merge pull request #295 from theshaun/dev

## 1.0.34

- Track upstream `DEV` commit `de129c1` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `9459dd5`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/9459dd5bba4cb32edb84b9c0a28a03d16d4eb342...de129c1c1503e1f251a9ceb8eff38dbd50f9154a
- Included upstream commits:
  - `23078de` Enhance contact import logic to respect max_contacts limit and trim excess entries. Update tests to validate trimming behavior and ensure correct handling of favourites during import.
  - `dcaa4ac` Refactor contact trimming logic for improved readability by consolidating function calls into single lines. Update related test cases for consistency.
  - `de129c1` Merge pull request #293 from agessaman/fix/companion-contact-import

## 1.0.33

- Track upstream `DEV` commit `9459dd5` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `291c1a6`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/291c1a6ed9a6aab575eb89b13917a0eede89cb60...9459dd5bba4cb32edb84b9c0a28a03d16d4eb342
- Included upstream commits:
  - `7968473` initial support for station g3
  - `9459dd5` Merge pull request #292 from recrof/dev

## 1.0.32

- Track upstream `DEV` commit `291c1a6` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `99a0429`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/99a04295da33790d0bdd876a7acbe5367017cd8f...291c1a6ed9a6aab575eb89b13917a0eede89cb60
- Included upstream commits:
  - `063c8ee` Fix companion identity OpenAPI contract
  - `aeea4bb` Format OpenAPI identity test
  - `291c1a6` fix:update statics for companion ui fix

## 1.0.31

- Track upstream `DEV` commit `99a0429` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `1f9be5a`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/1f9be5a02430b41ef65f539a35105c0ad8afdceb...99a04295da33790d0bdd876a7acbe5367017cd8f
- Included upstream commits:
  - `1836502` feat(config): add optional KISS CSMA tuning parameters
  - `0b4571c` Stop tracking policy.yaml and add it to .gitignore
  - `99a0429` Merge pull request #287 from agessaman/kiss/tuning-options

## 1.0.30

- Track upstream `DEV` commit `1f9be5a` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `2b7b2b5`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/2b7b2b5b4e7250c94d9c335a2bd32ea0de1d7243...1f9be5a02430b41ef65f539a35105c0ad8afdceb
- Included upstream commits:
  - `524359d` Made requested changed to docker setup
  - `8882003` Delete .env.example
  - `7b85cfc` Delete docker-compose.yml
  - `10b64bc` added current docker compose and env
  - `1f9be5a` Merge pull request #284 from MSmithDev/main

## 1.0.29

- Track upstream `DEV` commit `2b7b2b5` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `00682e8`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/00682e80864b0bfe82a9cf38dd041e4e01369b03...2b7b2b5b4e7250c94d9c335a2bd32ea0de1d7243
- Included upstream commits:
  - `5dfa98c` Rewrite README with expanded docs and images
  - `a308ddc` docker: add gpio and spi groups
  - `9e8c152` docker: tolerate read-only config during merge
  - `b5df705` docs: clarify docker setup config steps
  - `7015e0e` docs: document docker gpio gids
  - `d333deb` docker: clarify compose env setup
  - `ca50656` docs: remove fork image from env example
  - `77480c6` docker: use named volumes by default

## 1.0.28

- Track upstream `DEV` commit `00682e8` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `af603d7`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/af603d78d0f3e37a6855a67e2fb113a887885446...00682e80864b0bfe82a9cf38dd041e4e01369b03
- Included upstream commits:
  - `7d57b34` feat(companion): enhance contact capacity management and bridge settings
  - `499f871` Merge upstream/dev into companion/advanced-settings
  - `7fe1b19` fix: update packet injector to include origin hash for companion bridge
  - `dac6044` feat(companion): implement contact trimming and retention policies
  - `ea6e660` refactor(api_endpoints): improve sqlite_handler retrieval logic
  - `f3146eb` fix(companion): clean up ruff errors
  - `00682e8` Merge pull request #282 from agessaman/companion/advanced-settings

## 1.0.27

- Track upstream `DEV` commit `af603d7` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `225feda`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/225feda19572d72508ea034047c1c55d8e708cba...af603d78d0f3e37a6855a67e2fb113a887885446
- Included upstream commits:
  - `4abc497` MeshSmith: Change tx_power from 22 to 18
  - `e9a9f21` feat: update preamble_length to 32 for radio configurations
  - `b5b2c60` Update MQTT host and audience to meshmapper.net
  - `8926b3d` Fix URL in test_get_preset_meshmapper_is_single_broker_mc2mqtt
  - `767c070` Update broker host and audience in tests
  - `da95c67` fix: improve error logging for invalid policy entries and adjust test configuration
  - `b3119f9` Merge branch 'pr-281' into dev
  - `879aac1` Merge branch 'pr-280' into dev

## 1.0.26

- Track upstream `DEV` commit `225feda` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `cd7058b`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/cd7058be990f7c635cd2e094058ea5afb0a6eb86...225feda19572d72508ea034047c1c55d8e708cba
- Included upstream commits:
  - `14b4804` feat: Enhance logging system and introduce policy management endpoints
  - `225feda` feat:ui for policy and logging update

## 1.0.25

- Track upstream `DEV` commit `cd7058b` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `416310b`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/416310befd838118a1f64fd24cecdc66c35a972a...cd7058be990f7c635cd2e094058ea5afb0a6eb86
- Included upstream commits:
  - `cd7058b` fix: update packet router debugs for less noise and policy prep for advanced filters works

## 1.0.24

- Track upstream `DEV` commit `416310b` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `d7e74e0`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/d7e74e0a898650fb77ce52cd869a651a4ca2d4a5...416310befd838118a1f64fd24cecdc66c35a972a
- Included upstream commits:
  - `9e26068` feat: enhance installation process to align web/OTA updates with manage.sh defaults
  - `416310b` refactor: improve code readability

## 1.0.23

- Track upstream `DEV` commit `d7e74e0` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `2cacb7c`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/2cacb7cfc02024cc65dc30df7533c4c6e2668735...d7e74e0a898650fb77ce52cd869a651a4ca2d4a5
- Included upstream commits:
  - `2d5353a` fix(companion): improve transmission handling in RepeaterHandler
  - `5fcb625` feat: enhance login handler with anonymous request support and region name formatting
  - `778adb6` feat: implement randomized response jitter in DiscoveryHelper to prevent packet collisions
  - `5a9e1c8` Merge branch 'fix/companion-message-send' into feat/pre-1160-compatibility-sendfix
  - `ee92f5b` test: expect True from deferred local TX mock after companion send fix
  - `e24cdca` feat(companion): echo injected TX to companion clients as raw RX (0x88)
  - `d7e74e0` Merge pull request #278 from agessaman/feat/pre-1160-compatibility-sendfix

## 1.0.22

- Track upstream `DEV` commit `2cacb7c` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `730eaa9`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/730eaa97f79d3e10d5dda129b0bb63194169711b...2cacb7cfc02024cc65dc30df7533c4c6e2668735
- Included upstream commits:
  - `0f6a7dc` feat: support 64-byte identity keys in identity validation and tests
  - `d1dc57c` feat: add OpenAPI contract check script and integrate into pre-commit hooks
  - `caf048f` refactor: clean up code formatting in check_openapi_contract.py
  - `9e1dabd` feat: add PUT endpoint for updating transport keys in OpenAPI specification
  - `2cacb7c` Merge pull request #276 from openhop-dev/feat-open-api

## 1.0.21

- Track upstream `DEV` commit `730eaa9` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `5df8b16`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/5df8b160e5f554f2eee6e3a3e1db1f75bdc0a69e...730eaa97f79d3e10d5dda129b0bb63194169711b
- Included upstream commits:
  - `6295f0f` feat: add utility function to restore bytes from JSON and enhance prefs handling in RepeaterCompanionBridge
  - `730eaa9` Merge pull request #275 from agessaman/fix/binary-persist-1150

## 1.0.20

- Track upstream `DEV` commit `5df8b16` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `723e912`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/723e912d486dd1b1c240f4a9c8be75d88a21c64e...5df8b160e5f554f2eee6e3a3e1db1f75bdc0a69e
- Included upstream commits:
  - `f44d225` Add support for Nebra Duo Hat, E22P radio only.
  - `b921160` Merge pull request #270 from bplein/nebra-duo-hat
  - `7b224e2` Updated settings for Nebra Hat Duo E22P 1W
  - `5df8b16` Merge pull request #271 from bplein/nebra-duo-hat

## 1.0.19

- Track upstream `DEV` commit `723e912` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `8eaf24a`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/8eaf24ab35dd51d394199ccf24c5daae2cd07cfa...723e912d486dd1b1c240f4a9c8be75d88a21c64e
- Included upstream commits:
  - `62f35c4` fix: update transport key generation to use 16-byte length and add corresponding test
  - `456e97a` refactor: update pre-commit configuration and dependencies for improved Python 3.9 support
  - `faa3296` refactor: remove unused imports from test files for cleaner code
  - `45a44eb` Refactor test cases and base code for consistency and readability
  - `0c33483` refactor: clean up import statements and whitespace in local_cli, base, and update_endpoints modules
  - `5f25d3b` refactor: update bandit arguments and change pytest entry to use a script
  - `a5355f1` feat: add PR checks workflow for pre-commit validation
  - `60ca184` refactor: enhance security comments and error handling across multiple modules

## 1.0.18

- Track upstream `DEV` commit `8eaf24a` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `36aa8ec`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/36aa8ecf0d5a33256c2651a71b999aa1aec7fee2...8eaf24ab35dd51d394199ccf24c5daae2cd07cfa
- Included upstream commits:
  - `7db6535` fix: Python 3.10 compat for datetime.UTC in api_endpoints
  - `9fe0142` fix: replace datetime.UTC with timezone.utc for Python 3.10 compat
  - `a1c6610` fix: remove datetime.UTC from mqtt_handler and add 3.10 compat test
  - `d597ab2` fix: replace datetime.UTC attribute access in repeater_cli
  - `8eaf24a` Merge pull request #266 from zindello/fix/python310-datetime-utc

## 1.0.17

- Track upstream `DEV` commit `36aa8ec` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `31edaa9`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/31edaa9c7651a059d3b27b28cc43a915c8b27af8...36aa8ecf0d5a33256c2651a71b999aa1aec7fee2
- Included upstream commits:
  - `9da8317` docker: install rrdtool for runtime python
  - `36aa8ec` Merge pull request #265 from yellowcooln/dev

## 1.0.16

- Track upstream `DEV` commit `31edaa9` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `dc317b6`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/dc317b6568f14d1a9b97d0c942eccb693e0ad796...31edaa9c7651a059d3b27b28cc43a915c8b27af8
- Included upstream commits:
  - `37ee0e8` Add more unit tests for handler helpers, identity manager, CLI, key generation, and main functionality
  - `7b86716` Add unit tests for HTTP server, main daemon, service utilities, SQLite handler, and update endpoints
  - `31edaa9` fix: update installation scripts to use the correct branch name

## 1.0.15

- Track upstream `DEV` commit `dc317b6` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `ab55748`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/ab55748f3f7856db207e093a00dbbc5e8bdd69aa...dc317b6568f14d1a9b97d0c942eccb693e0ad796
- Included upstream commits:
  - `e17d113` Merge pull request #259 from openhop-dev/dev
  - `e20eaa7` feat: add LAFVIN UPS Module 3S sensor plugin (lafvin_ups_3s)
  - `dc317b6` Merge pull request #261 from CarlsonCustoms/feat/lafvin-ups-3s-sensor

## 1.0.14

- Track upstream `DEV` commit `ab55748` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `85f2823`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/85f282357ca6cd6516d961eb8650ecc2a6286f74...ab55748f3f7856db207e093a00dbbc5e8bdd69aa
- Included upstream commits:
  - `ab55748` fix: prevent advert echos in the packet table

## 1.0.13

- Track upstream `DEV` commit `85f2823` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `a48b298`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/a48b29837acab532f576c5486b6aeae6ee458ed3...85f282357ca6cd6516d961eb8650ecc2a6286f74
- Included upstream commits:
  - `85f2823` feat: expand allowed sections for configuration imports to include additional radio types

## 1.0.12

- Track upstream `DEV` commit `a48b298` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `4cf04f8`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/4cf04f87d1b2fa6c4ddcbd8a8bc9591077ca2295...a48b29837acab532f576c5486b6aeae6ee458ed3
- Included upstream commits:
  - `5c68707` feat: add endpoint to discover available serial/USB modem device paths
  - `3244f7b` feat: add validation for TX power settings and update API endpoint for serial ports
  - `2a031b7` feat: add validate_config endpoint to check config.yaml syntax and required settings
  - `78648f2` feat: add site_info endpoint to return site identification name without authentication
  - `a48b298` feat: pre-restart config validation and site identification

## 1.0.11

- Track upstream `DEV` commit `4cf04f8` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `8f3477d`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/8f3477ddd6fa879368dad99e18b258770bdeb380...4cf04f87d1b2fa6c4ddcbd8a8bc9591077ca2295
- Included upstream commits:
  - `d25e97a` feat: implement setup status check and reject subsequent setups after completion
  - `5b93d10` fix: update loop detection thresholds and improve path hash handling in API endpoints
  - `b464fa8` docs: update example configuration for Waveshare UPS D and E Hats
  - `22b39e5` fix: update maintainer information in changelog, control, and build scripts
  - `4cf04f8` test: sensor tests with mock implementations and additional assertions

## 1.0.10

- Track upstream `DEV` commit `8f3477d` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `22adbd1`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/22adbd1a84b48bf2143065dca03504b0c3dbcaaa...8f3477ddd6fa879368dad99e18b258770bdeb380
- Included upstream commits:
  - `6e89272` Add Waveshare UPS HAT (E) sensor plug-in
  - `8f3477d` Merge pull request #256 from CarlsonCustoms/add-waveshare-ups-hat-e

## 1.0.9

- Track upstream `DEV` commit `22adbd1` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `6aab7ec`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/6aab7ec67632cb00ff29cb4e8dab2404cf788339...22adbd1a84b48bf2143065dca03504b0c3dbcaaa
- Included upstream commits:
  - `22adbd1` feat: add setup usb/tcp details on setup

## 1.0.8

- Track upstream `DEV` commit `6aab7ec` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `cbfcb69`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/cbfcb69c07adc893a5f4eaac8f3aa1cb47afb970...6aab7ec67632cb00ff29cb4e8dab2404cf788339
- Included upstream commits:
  - `7d54859` Add example configurations for SHTC3 and Waveshare UPS Hat sensors
  - `6aab7ec` fix:update-restart-functions

## 1.0.7

- Track upstream `DEV` commit `cbfcb69` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `13ea672`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/13ea67259711913c498081071fe5b86eb6b283f0...cbfcb69c07adc893a5f4eaac8f3aa1cb47afb970
- Included upstream commits:
  - `9c1661f` Add SHTC3 and Waveshare UPS HAT (D) sensor plug-ins
  - `8b0607a` Add NMEA GPS sensor plug-in
  - `f88d3c5` Revert "Add NMEA GPS sensor plug-in"
  - `cbfcb69` Merge pull request #255 from CarlsonCustoms/add-shtc3-waveshare-sensors

## 1.0.6

- Track upstream `DEV` commit `13ea672` from `openhopdev/openhop-repeater:dev`
- Previous tracked commit: `193b428`
- Upstream diff: https://github.com/openhop-dev/openhop_repeater/compare/193b428cc2949695f3c3434ef3349d32ee3a207d...13ea67259711913c498081071fe5b86eb6b283f0
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
- Run the add-on wrapper as root so startup can manage `/etc/openhop_repeater`

## 1.0.2

- Handle rootless upstream image builds in the add-on Dockerfiles
- Run the add-on wrapper as root so startup can manage `/etc/openhop_repeater`

## 1.0.1

- Enable host networking so companion nodes can bind dynamic host ports

## 1.0.0

- Initial release of the Home Assistant add-on repository
- Add separate `dev` and `main` channel add-ons with aligned behavior
- Track upstream `openhopdev/openhop-repeater:dev` in `openhop_repeater_dev`
