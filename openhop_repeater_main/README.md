# Home Assistant Add-on: openHop Repeater

Run openHop Repeater as a Home Assistant add-on with:

- a complete YAML configuration file;
- branch selection from the repeater web interface;
- persistent branch and runtime data;
- automatic recovery to the last runnable installation when an update fails;
- support for SPI/GPIO radios, USB devices, serial KISS modems, TCP modems, and
  companion services.

The configuration file is created on first start and is available on the Home
Assistant host at:

```text
app_configs/*_openhop_repeater_main/config.yaml
```

See [DOCS.md](DOCS.md) for installation and configuration instructions.
