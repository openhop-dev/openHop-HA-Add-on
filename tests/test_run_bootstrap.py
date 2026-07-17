from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "openhop_repeater_main"
RUN_SCRIPT = ADDON / "run.sh"
BRANCH_HELPER = (
    ADDON / "rootfs" / "usr" / "local" / "lib" / "openhop-addon" / "branch_state.py"
)


class BootstrapIntegrationTests(unittest.TestCase):
    def test_clean_exit_restarts_into_persisted_branch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-bootstrap-") as temp_dir:
            root = Path(temp_dir)
            base_site = root / "base-site"
            repeater = base_site / "repeater"
            repeater.mkdir(parents=True)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()

            (base_site / "yaml.py").write_text(
                "def safe_load(text):\n"
                "    return {'repeater': {'node_name': 'test'}, 'radio_type': None}\n",
                encoding="utf-8",
            )
            (repeater / "__init__.py").write_text(
                "BRANCH = 'packaged-main'\n", encoding="utf-8"
            )
            (repeater / "main.py").write_text(
                textwrap.dedent(
                    """
                    from __future__ import annotations

                    import json
                    import os
                    import pathlib
                    import sysconfig


                    def emulate_update() -> None:
                        root = pathlib.Path(os.environ["OPENHOP_TEST_ROOT"])
                        (root / "specific-version-env").write_text(
                            os.environ.get(
                                "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENHOP_REPEATER",
                                "<unset>",
                            ),
                            encoding="utf-8",
                        )
                        site = pathlib.Path(sysconfig.get_paths()["purelib"])
                        package = site / "repeater"
                        package.mkdir(parents=True, exist_ok=True)
                        (package / "__init__.py").write_text(
                            "BRANCH = 'dev'\\n", encoding="utf-8"
                        )
                        (package / "main.py").write_text(
                            "from __future__ import annotations\\n"
                            "import os, pathlib, time\\n"
                            "def main():\\n"
                            "    root = pathlib.Path(os.environ['OPENHOP_TEST_ROOT'])\\n"
                            "    (root / 'dev-active').write_text('yes', encoding='utf-8')\\n"
                            "    while True: time.sleep(1)\\n"
                            "if __name__ == '__main__': main()\\n",
                            encoding="utf-8",
                        )
                        dist_info = site / "openhop_repeater-1.0.0.dist-info"
                        dist_info.mkdir(parents=True, exist_ok=True)
                        (dist_info / "METADATA").write_text(
                            "Metadata-Version: 2.1\\n"
                            "Name: openhop_repeater\\n"
                            "Version: 1.0.0\\n",
                            encoding="utf-8",
                        )
                        (dist_info / "direct_url.json").write_text(
                            json.dumps(
                                {
                                    "url": (
                                        "https://github.com/openhop-dev/"
                                        "openhop_repeater.git"
                                    ),
                                    "vcs_info": {
                                        "vcs": "git",
                                        "requested_revision": "dev",
                                        "commit_id": "deadbeef",
                                    },
                                }
                            ),
                            encoding="utf-8",
                        )
                        (root / "data" / ".update_channel").write_text(
                            "dev\\n", encoding="utf-8"
                        )
                        os._exit(0)


                    if __name__ == "__main__":
                        emulate_update()
                    """
                ).lstrip(),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env.update(
                {
                    "OPENHOP_TEST_ROOT": str(root),
                    "OPENHOP_ADDON_CONFIG_DIR": str(root / "config"),
                    "OPENHOP_ADDON_DATA_DIR": str(root / "data"),
                    "OPENHOP_ADDON_RUNTIME_CONFIG_DIR": str(
                        root / "etc" / "openhop_repeater"
                    ),
                    "OPENHOP_ADDON_FIRMWARE_DATA_DIR": str(
                        root / "var" / "openhop_repeater"
                    ),
                    "OPENHOP_ADDON_UPDATE_VENV_LINK": str(root / "opt" / "venv"),
                    "OPENHOP_ADDON_TEMPLATE_CONFIG": str(
                        ADDON / "config.yaml.example"
                    ),
                    "OPENHOP_ADDON_BRANCH_HELPER": str(BRANCH_HELPER),
                    "OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB": str(base_site),
                    "OPENHOP_ADDON_DEFAULT_BRANCH": "main",
                    "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_OPENHOP_REPEATER": (
                        "1.1.2.dev1"
                    ),
                }
            )

            log_path = root / "run.log"
            with log_path.open("w", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    [str(RUN_SCRIPT)],
                    env=env,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                )

                try:
                    deadline = time.monotonic() + 30
                    while time.monotonic() < deadline:
                        if (root / "dev-active").is_file():
                            break
                        return_code = process.poll()
                        if return_code is not None:
                            self.fail(
                                f"bootstrap exited early with status {return_code}:\n"
                                f"{log_path.read_text(encoding='utf-8')}"
                            )
                        time.sleep(0.1)
                    else:
                        self.fail(
                            "persisted dev branch did not become active:\n"
                            + log_path.read_text(encoding="utf-8")
                        )

                    process.send_signal(signal.SIGTERM)
                    self.assertEqual(process.wait(timeout=10), 0)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=10)

            output = log_path.read_text(encoding="utf-8")
            self.assertIn(
                "repeater requested a restart; rerunning branch bootstrap", output
            )
            self.assertIn("selected branch: dev; active branch: dev", output)
            self.assertIn(str(root / "data" / "venv"), output)
            self.assertEqual(
                (root / "specific-version-env").read_text(encoding="utf-8"),
                "<unset>",
            )


if __name__ == "__main__":
    unittest.main()
