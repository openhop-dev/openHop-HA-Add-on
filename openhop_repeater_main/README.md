# Home Assistant App: openHop Repeater

Run openHop Repeater as a Home Assistant app with:

- a complete YAML configuration file;
- branch selection from the repeater web interface;
- persistent branch and runtime data;
- verification that the selected branch is the package Python actually imports;
- automatic recovery to a protected packaged runtime when an update fails;
- support for SPI/GPIO radios, USB devices, serial KISS modems, TCP modems, and
  companion services.

The configuration file is created on first start. Later image updates merge
missing packaged defaults without replacing user values. The file is available
on the Home Assistant host at:

```text
/addon_configs/*_openhop_repeater_main/config.yaml
```

See [DOCS.md](DOCS.md) for installation and configuration instructions.
