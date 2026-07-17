# Changelog

## 3.0.0

- Add branch selection and installation from the openHop Repeater web interface.
- Store the selected branch in Home Assistant's persistent app data.
- Run branch installations from a persistent Python environment.
- Restore the selected branch automatically after container recreation.
- Use the version included in the app image as a runtime fallback.
- Restart openHop Repeater automatically after an in-app update request.
- Include the complete openHop Repeater configuration template.
- Generate unique admin and guest passwords for new configurations.
- Store user configuration in the Home Assistant app configuration directory.
- Add cold-backup support while excluding the generated Python environment.
- Use the current `app_config` mapping and `app_configs` directory naming.
- Use a valid Home Assistant Web UI URL placeholder.
- Point repository metadata at the published GitHub repository.
- Add repository validation, ShellCheck, and branch-state tests.
- Prevent the base image's build-time version override from replacing branch update versions.
- Provide pip for the system Python used by the upstream updater's cleanup commands.
