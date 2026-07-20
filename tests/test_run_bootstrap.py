from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "openhop_repeater_main"
RUN_SCRIPT = ADDON / "run.sh"
BRANCH_HELPER = (
    ADDON / "rootfs" / "usr" / "local" / "lib" / "openhop-addon" / "branch_state.py"
)
PATH_UTILS_HELPER = (
    ADDON / "rootfs" / "usr" / "local" / "lib" / "openhop-addon" / "path_utils.py"
)
CONFIG_HELPER = (
    ADDON / "rootfs" / "usr" / "local" / "lib" / "openhop-addon" / "config_bootstrap.py"
)
RUNTIME_INFO_HELPER = (
    ADDON / "rootfs" / "usr" / "local" / "lib" / "openhop-addon" / "runtime_info.py"
)
PIP_WRAPPER = ADDON / "rootfs" / "usr" / "local" / "bin" / "openhop-venv-pip"


def assert_process_exited(test_case: unittest.TestCase, pid_file: Path) -> None:
    child_pid = int(pid_file.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    test_case.fail(f"child process {child_pid} survived the app wrapper shutdown")


def create_packaged_runtime(root: Path) -> Path:
    base_runtime = root / "protected-base"
    repeater = base_runtime / "repeater"
    repeater.mkdir(parents=True)
    (repeater / "__init__.py").write_text(
        "__version__ = 'packaged-test'\n", encoding="utf-8"
    )
    (repeater / "main.py").write_text(
        textwrap.dedent(
            """
            import os
            import pathlib
            import time


            def main() -> None:
                root = pathlib.Path(os.environ["OPENHOP_TEST_ROOT"])
                (root / "child-pid").write_text(
                    str(os.getpid()), encoding="utf-8"
                )
                (root / "packaged-active").write_text("yes", encoding="utf-8")
                while True:
                    time.sleep(1)


            if __name__ == "__main__":
                main()
            """
        ).lstrip(),
        encoding="utf-8",
    )
    for name in ("radio-settings.json", "radio-presets.json"):
        (base_runtime / name).write_text("{}\n", encoding="utf-8")
    return base_runtime


def base_bootstrap_env(root: Path, base_runtime: Path, pip_wrapper: Path) -> dict[str, str]:
    yaml_site_packages = Path(yaml.__file__).resolve().parent.parent
    base_image_id = root / "base-image-id"
    base_image_id.write_text("test-base\n", encoding="utf-8")
    env = os.environ.copy()
    env.update(
        {
            "OPENHOP_TEST_ROOT": str(root),
            "OPENHOP_ADDON_CONFIG_DIR": str(root / "config"),
            "OPENHOP_ADDON_DATA_DIR": str(root / "data"),
            "OPENHOP_ADDON_RUNTIME_CONFIG_DIR": str(root / "etc" / "openhop_repeater"),
            "OPENHOP_ADDON_FIRMWARE_DATA_DIR": str(root / "var" / "openhop_repeater"),
            "OPENHOP_ADDON_UPDATE_VENV_LINK": str(root / "opt" / "venv"),
            "OPENHOP_ADDON_TEMPLATE_CONFIG": str(ADDON / "config.yaml.example"),
            "OPENHOP_ADDON_BRANCH_HELPER": str(BRANCH_HELPER),
            "OPENHOP_ADDON_PATH_UTILS_HELPER": str(PATH_UTILS_HELPER),
            "OPENHOP_ADDON_CONFIG_HELPER": str(CONFIG_HELPER),
            "OPENHOP_ADDON_RUNTIME_INFO_HELPER": str(RUNTIME_INFO_HELPER),
            "OPENHOP_ADDON_VENV_PIP_WRAPPER": str(pip_wrapper),
            "OPENHOP_ADDON_TEST_WITHOUT_PIP": "true",
            "OPENHOP_ADDON_SYSTEM_PYTHON": "/usr/bin/python3",
            "OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB": str(yaml_site_packages),
            "OPENHOP_ADDON_BASE_RUNTIME_DIR": str(base_runtime),
            "OPENHOP_ADDON_BASE_IMAGE_ID_FILE": str(base_image_id),
            "OPENHOP_ADDON_BUILD_VERSION": "3.0.0",
            "OPENHOP_ADDON_YQ": str(root / "missing-yq"),
        }
    )
    return env


def run_bootstrap_until_marker(
    test_case: unittest.TestCase, root: Path, env: dict[str, str], marker_name: str
) -> str:
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
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline:
                output = log_path.read_text(encoding="utf-8")
                if (root / marker_name).is_file() and (root / "child-pid").is_file():
                    break
                return_code = process.poll()
                if return_code is not None:
                    test_case.fail(
                        f"bootstrap exited early with status {return_code}:\n{output}"
                    )
                time.sleep(0.1)
            else:
                test_case.fail(
                    f"bootstrap did not create {marker_name}:\n"
                    + log_path.read_text(encoding="utf-8")
                )

            process.send_signal(signal.SIGTERM)
            test_case.assertEqual(process.wait(timeout=15), 0)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=15)

    assert_process_exited(test_case, root / "child-pid")
    return log_path.read_text(encoding="utf-8")


class BootstrapIntegrationTests(unittest.TestCase):

    def test_inherited_stop_request_exits_before_bootstrap(self) -> None:
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("OPENHOP_ADDON_")
        }
        env.update(
            {
                "OPENHOP_ADDON_STOP_REQUESTED": "true",
                "OPENHOP_ADDON_TEMPLATE_CONFIG": "/missing/config.yaml.example",
                "OPENHOP_ADDON_BRANCH_HELPER": "/missing/branch_state.py",
                "OPENHOP_ADDON_PATH_UTILS_HELPER": "/missing/path_utils.py",
                "OPENHOP_ADDON_CONFIG_HELPER": "/missing/config_bootstrap.py",
                "OPENHOP_ADDON_RUNTIME_INFO_HELPER": "/missing/runtime_info.py",
            }
        )
        result = subprocess.run(
            [str(RUN_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_selected_branch_is_installed_and_verified_before_start(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-install-") as temp_dir:
            root = Path(temp_dir)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()
            (root / "config" / "config.yaml").write_text(
                "repeater:\n  node_name: install-test\nradio_type: null\n",
                encoding="utf-8",
            )
            (root / "data" / ".update_channel").write_text("dev\n", encoding="utf-8")
            base_runtime = create_packaged_runtime(root)

            fake_pip = root / "fake-pip"
            fake_pip.write_text(
                textwrap.dedent(
                    r"""
                    #!/usr/bin/python3
                    import json
                    import os
                    import pathlib
                    import sys

                    root = pathlib.Path(os.environ["OPENHOP_TEST_ROOT"])
                    (root / "pip-args.json").write_text(
                        json.dumps(sys.argv[1:]), encoding="utf-8"
                    )
                    site = next(
                        (root / "data" / "venv" / "lib").glob(
                            "python*/site-packages"
                        )
                    )
                    package = site / "repeater"
                    package.mkdir(parents=True, exist_ok=True)
                    (package / "__init__.py").write_text(
                        "__version__ = 'dev-test'\n", encoding="utf-8"
                    )
                    (package / "main.py").write_text(
                        "import os, pathlib, time\n"
                        "def main():\n"
                        "    root = pathlib.Path("
                        "os.environ['OPENHOP_TEST_ROOT'])\n"
                        "    (root / 'child-pid').write_text("
                        "str(os.getpid()), encoding='utf-8')\n"
                        "    (root / 'dev-active').write_text("
                        "'yes', encoding='utf-8')\n"
                        "    while True: time.sleep(1)\n"
                        "if __name__ == '__main__': main()\n",
                        encoding="utf-8",
                    )
                    dist_info = site / "openhop_repeater-1.0.0.dist-info"
                    dist_info.mkdir(parents=True, exist_ok=True)
                    (dist_info / "METADATA").write_text(
                        "Metadata-Version: 2.1\n"
                        "Name: openhop_repeater\n"
                        "Version: 1.0.0\n",
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
                    """
                ).lstrip(),
                encoding="utf-8",
            )
            fake_pip.chmod(0o755)

            output = run_bootstrap_until_marker(
                self,
                root,
                base_bootstrap_env(root, base_runtime, fake_pip),
                "dev-active",
            )

            args = json.loads((root / "pip-args.json").read_text(encoding="utf-8"))
            self.assertEqual(
                args[:-1],
                ["install", "--upgrade", "--force-reinstall", "--no-cache-dir"],
            )
            self.assertEqual(
                args[-1],
                (
                    "openhop_repeater[hardware] @ "
                    "git+https://github.com/openhop-dev/openhop_repeater.git@dev"
                ),
            )
            self.assertFalse((root / "packaged-active").exists())
            self.assertEqual(
                (root / "data" / "venv" / ".openhop-ha-branch").read_text(
                    encoding="utf-8"
                ),
                "dev\n",
            )
            self.assertIn("installed and verified branch 'dev'", output)

    def test_failed_branch_install_rebuilds_clean_packaged_fallback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-fallback-") as temp_dir:
            root = Path(temp_dir)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()
            (root / "config" / "config.yaml").write_text(
                "repeater:\n  node_name: fallback-test\nradio_type: null\n",
                encoding="utf-8",
            )
            (root / "data" / ".update_channel").write_text("dev\n", encoding="utf-8")
            base_runtime = create_packaged_runtime(root)

            fake_pip = root / "failing-pip"
            fake_pip.write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$*\" > \"$OPENHOP_TEST_ROOT/pip-args\"\nexit 1\n",
                encoding="utf-8",
            )
            fake_pip.chmod(0o755)

            output = run_bootstrap_until_marker(
                self,
                root,
                base_bootstrap_env(root, base_runtime, fake_pip),
                "packaged-active",
            )

            self.assertEqual(
                (root / "data" / ".update_channel").read_text(encoding="utf-8"),
                "dev\n",
            )
            self.assertFalse(
                (root / "data" / "venv" / ".openhop-ha-branch").exists()
            )
            self.assertIn("could not install branch 'dev'", output)
            self.assertIn("falling back to the packaged runtime", output)
            self.assertIn("active branch: main (packaged image)", output)

    def test_clean_exit_restarts_into_persisted_branch(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-bootstrap-") as temp_dir:
            root = Path(temp_dir)
            base_site = root / "base-site"
            repeater = base_site / "repeater"
            repeater.mkdir(parents=True)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()
            base_image_id = root / "base-image-id"
            base_image_id.write_text("packaged-code-v2\n", encoding="utf-8")

            # Simulate an app update with an update environment created by an
            # older image. The bootstrap must discard it before executing any
            # code from that environment.
            stale_venv = root / "data" / "venv"
            (stale_venv / "bin").mkdir(parents=True)
            stale_python = stale_venv / "bin" / "python"
            stale_python.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
            stale_python.chmod(0o755)
            (stale_venv / ".openhop-ha-python").write_text(
                "addon=2.9.0;python=stale\n", encoding="utf-8"
            )
            (stale_venv / "stale-image-sentinel").write_text(
                "must be removed\n", encoding="utf-8"
            )

            # An empty file can be left behind by a failed or interrupted
            # first start. It should be initialized rather than treated as a
            # valid user configuration.
            (root / "config" / "config.yaml").touch()

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
                            "site = pathlib.Path(__file__).resolve().parent.parent\\n"
                            "for metadata in site.glob("
                            "'openhop_repeater-*.dist-info/direct_url.json'):\\n"
                            "    metadata.unlink(missing_ok=True)\\n"
                            "def main():\\n"
                            "    root = pathlib.Path(os.environ['OPENHOP_TEST_ROOT'])\\n"
                            "    (root / 'child-pid').write_text("
                            "str(os.getpid()), encoding='utf-8')\\n"
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
                    "OPENHOP_ADDON_PATH_UTILS_HELPER": str(PATH_UTILS_HELPER),
                    "OPENHOP_ADDON_CONFIG_HELPER": str(CONFIG_HELPER),
                    "OPENHOP_ADDON_RUNTIME_INFO_HELPER": str(RUNTIME_INFO_HELPER),
                    "OPENHOP_ADDON_VENV_PIP_WRAPPER": str(PIP_WRAPPER),
                    "OPENHOP_ADDON_TEST_WITHOUT_PIP": "true",
                    "OPENHOP_ADDON_SYSTEM_PYTHON": "/usr/bin/python3",
                    "OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB": str(base_site),
                    "OPENHOP_ADDON_DEFAULT_BRANCH": "main",
                    "OPENHOP_ADDON_BUILD_VERSION": "3.0.0",
                    "OPENHOP_ADDON_BASE_IMAGE_ID_FILE": str(base_image_id),
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
                    deadline = time.monotonic() + 90
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
                    self.assertEqual(process.wait(timeout=15), 0)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=15)

            assert_process_exited(self, root / "child-pid")
            output = log_path.read_text(encoding="utf-8")
            self.assertIn(
                "repeater requested a restart; rerunning branch bootstrap", output
            )
            self.assertIn("selected branch: dev; active branch: dev", output)
            self.assertIn(str(root / "data" / "venv"), output)
            self.assertFalse((stale_venv / "stale-image-sentinel").exists())
            self.assertTrue(
                (stale_venv / ".openhop-ha-python")
                .read_text(encoding="utf-8")
                .startswith("addon=3.0.0;base=packaged-code-v2;python=")
            )
            self.assertEqual(
                (root / "specific-version-env").read_text(encoding="utf-8"),
                "<unset>",
            )
            self.assertEqual(
                (stale_venv / ".openhop-ha-branch").read_text(encoding="utf-8"),
                "dev\n",
            )
            self.assertEqual(
                list(
                    (stale_venv / "lib").glob(
                        "python*/site-packages/"
                        "openhop_repeater-*.dist-info/direct_url.json"
                    )
                ),
                [],
            )

            generated_config = root / "config" / "config.yaml"
            generated_text = generated_config.read_text(encoding="utf-8")
            self.assertNotIn('admin_password: "admin123"', generated_text)
            self.assertNotIn('guest_password: "guest123"', generated_text)
            generated = yaml.safe_load(generated_text)
            self.assertEqual(len(generated["repeater"]["security"]["jwt_secret"]), 64)
            self.assertEqual(generated_config.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list((root / "config").glob("config.yaml.tmp.*")), [])

    def test_existing_config_is_merged_and_protected_base_runtime_starts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-merge-") as temp_dir:
            root = Path(temp_dir)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()

            config_path = root / "config" / "config.yaml"
            config_path.write_text(
                textwrap.dedent(
                    """
                    repeater:
                      node_name: "kept-name"
                      security:
                        admin_password: "kept-admin-password"
                    identities:
                      room_servers:
                        - name: "test-room"
                          settings:
                            admin_password: "room-admin-password"
                            guest_password: "room-guest-password"
                    radio_type: null
                    """
                ).lstrip(),
                encoding="utf-8",
            )

            base_runtime = root / "protected-base"
            repeater = base_runtime / "repeater"
            repeater.mkdir(parents=True)
            (repeater / "__init__.py").write_text(
                "__version__ = 'packaged-test'\n", encoding="utf-8"
            )
            (base_runtime / "radio-settings.json").write_text(
                '{"hardware": {"test": {"name": "Test"}}}\n', encoding="utf-8"
            )
            (base_runtime / "radio-presets.json").write_text(
                '{"config": {"suggested_radio_settings": {"entries": []}}}\n',
                encoding="utf-8",
            )
            (repeater / "main.py").write_text(
                textwrap.dedent(
                    """
                    from __future__ import annotations

                    import os
                    import pathlib
                    import time

                    if __name__ == "__main__":
                        root = pathlib.Path(os.environ["OPENHOP_TEST_ROOT"])
                        (root / "child-pid").write_text(
                            str(os.getpid()), encoding="utf-8"
                        )
                        while True:
                            time.sleep(1)
                    """
                ).lstrip(),
                encoding="utf-8",
            )

            fake_yq = root / "yq"
            fake_yq.write_text(
                textwrap.dedent(
                    f"""\
                    #!{sys.executable}
                    from __future__ import annotations

                    import os
                    import pathlib
                    import sys
                    import yaml


                    def merge(base, override):
                        if isinstance(base, dict) and isinstance(override, dict):
                            result = dict(base)
                            for key, value in override.items():
                                result[key] = merge(result.get(key), value)
                            return result
                        return override


                    args = sys.argv[1:]
                    if args == ["--version"]:
                        print("yq (https://github.com/mikefarah/yq/) version v4.40.5")
                    elif args[0] == "eval" and ('has("' in args[1] or "jwt_secret" in args[1]):
                        data = yaml.safe_load(pathlib.Path(args[-1]).read_text()) or {{}}
                        security = (data.get("repeater") or {{}}).get("security") or {{}}
                        if "admin_password" in args[1]:
                            present = "admin_password" in security
                        elif "guest_password" in args[1]:
                            present = "guest_password" in security
                        else:
                            present = bool(security.get("jwt_secret"))
                        print("true" if present else "false")
                    elif args[0] == "eval" and args[1] == "-i":
                        path = pathlib.Path(args[-1])
                        data = yaml.safe_load(path.read_text()) or {{}}
                        security = data.setdefault("repeater", {{}}).setdefault("security", {{}})
                        if "admin_password" in args[2]:
                            security["admin_password"] = os.environ["OPENHOP_GENERATED_PASSWORD"]
                        elif "guest_password" in args[2]:
                            security["guest_password"] = os.environ["OPENHOP_GENERATED_PASSWORD"]
                        else:
                            security["jwt_secret"] = os.environ["OPENHOP_GENERATED_SECRET"]
                        path.write_text(yaml.safe_dump(data, sort_keys=False))
                    elif args[0] == "eval-all":
                        template = yaml.safe_load(pathlib.Path(args[-2]).read_text()) or {{}}
                        user = yaml.safe_load(pathlib.Path(args[-1]).read_text()) or {{}}
                        sys.stdout.write(yaml.safe_dump(merge(template, user), sort_keys=False))
                    elif args[0] == "eval" and args[1] == '... comments=""':
                        sys.stdout.write(pathlib.Path(args[-1]).read_text())
                    elif args[0] == "eval" and args[1] == ".":
                        yaml.safe_load(pathlib.Path(args[-1]).read_text())
                    else:
                        raise SystemExit(f"unexpected fake yq arguments: {{args!r}}")
                    """
                ),
                encoding="utf-8",
            )
            fake_yq.chmod(0o755)

            base_image_id = root / "base-image-id"
            base_image_id.write_text("protected-base-v1\n", encoding="utf-8")
            yaml_site_packages = Path(yaml.__file__).resolve().parent.parent
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
                    "OPENHOP_ADDON_PATH_UTILS_HELPER": str(PATH_UTILS_HELPER),
                    "OPENHOP_ADDON_CONFIG_HELPER": str(CONFIG_HELPER),
                    "OPENHOP_ADDON_RUNTIME_INFO_HELPER": str(RUNTIME_INFO_HELPER),
                    "OPENHOP_ADDON_VENV_PIP_WRAPPER": str(PIP_WRAPPER),
                    "OPENHOP_ADDON_TEST_WITHOUT_PIP": "true",
                    "OPENHOP_ADDON_SYSTEM_PYTHON": "/usr/bin/python3",
                    "OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB": str(yaml_site_packages),
                    "OPENHOP_ADDON_BASE_RUNTIME_DIR": str(base_runtime),
                    "OPENHOP_ADDON_BASE_IMAGE_ID_FILE": str(base_image_id),
                    "OPENHOP_ADDON_BUILD_VERSION": "3.0.0",
                    "OPENHOP_ADDON_YQ": str(fake_yq),
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
                    deadline = time.monotonic() + 90
                    while time.monotonic() < deadline:
                        output = log_path.read_text(encoding="utf-8")
                        if (
                            "repeater process started" in output
                            and (root / "child-pid").is_file()
                        ):
                            break
                        return_code = process.poll()
                        if return_code is not None:
                            self.fail(
                                f"bootstrap exited early with status {return_code}:\n{output}"
                            )
                        time.sleep(0.1)
                    else:
                        self.fail(
                            "bootstrap did not start the protected packaged runtime:\n"
                            + log_path.read_text(encoding="utf-8")
                        )

                    process.send_signal(signal.SIGTERM)
                    self.assertEqual(process.wait(timeout=15), 0)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=15)

            assert_process_exited(self, root / "child-pid")
            merged = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertEqual(merged["repeater"]["node_name"], "kept-name")
            security = merged["repeater"]["security"]
            self.assertEqual(security["admin_password"], "kept-admin-password")
            self.assertTrue(security["guest_password"])
            self.assertNotEqual(security["guest_password"], "guest123")
            self.assertEqual(len(security["jwt_secret"]), 64)
            self.assertIn("cache_ttl", merged["repeater"])
            self.assertIn("gps", merged)
            room_settings = merged["identities"]["room_servers"][0]["settings"]
            self.assertEqual(room_settings["admin_password"], "room-admin-password")
            self.assertEqual(room_settings["guest_password"], "room-guest-password")
            self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)

            output = log_path.read_text(encoding="utf-8")
            self.assertIn("merged missing settings", output)
            self.assertIn("generated unique credentials", output)
            self.assertIn(str(base_runtime / "repeater"), output)
            self.assertIn("active branch: main (packaged image)", output)

            venv_python = root / "data" / "venv" / "bin" / "python"
            purelib = Path(
                subprocess.check_output(
                    [
                        str(venv_python),
                        "-c",
                        "import sysconfig; print(sysconfig.get_paths()['purelib'])",
                    ],
                    text=True,
                ).strip()
            )
            self.assertEqual(
                (purelib / "radio-settings.json").read_text(encoding="utf-8"),
                (base_runtime / "radio-settings.json").read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (purelib / "radio-presets.json").read_text(encoding="utf-8"),
                (base_runtime / "radio-presets.json").read_text(encoding="utf-8"),
            )

    def test_existing_default_password_is_not_silently_changed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-existing-password-") as temp_dir:
            root = Path(temp_dir)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()

            config_path = root / "config" / "config.yaml"
            config_path.write_text(
                "repeater:\n"
                "  node_name: kept-name\n"
                "  security:\n"
                "    admin_password: admin123\n"
                "    guest_password: guest123\n"
                "radio_type: null\n",
                encoding="utf-8",
            )

            base_runtime = root / "protected-base"
            repeater = base_runtime / "repeater"
            repeater.mkdir(parents=True)
            (repeater / "__init__.py").write_text(
                "__version__ = 'test'\n", encoding="utf-8"
            )
            (repeater / "main.py").write_text(
                "import os, pathlib, time\n"
                "if __name__ == '__main__':\n"
                "    root = pathlib.Path(os.environ['OPENHOP_TEST_ROOT'])\n"
                "    (root / 'child-pid').write_text(str(os.getpid()), encoding='utf-8')\n"
                "    time.sleep(30)\n",
                encoding="utf-8",
            )
            for name in ("radio-settings.json", "radio-presets.json"):
                (base_runtime / name).write_text("{}\n", encoding="utf-8")

            fake_yq = root / "yq"
            fake_yq.write_text(
                textwrap.dedent(
                    f"""\
                    #!{sys.executable}
                    import os, pathlib, sys, yaml

                    def merge(base, override):
                        if isinstance(base, dict) and isinstance(override, dict):
                            result = dict(base)
                            for key, value in override.items():
                                result[key] = merge(result.get(key), value)
                            return result
                        return override

                    args = sys.argv[1:]
                    if args == ["--version"]:
                        print("yq (https://github.com/mikefarah/yq/) version v4.40.5")
                    elif args[0] == "eval" and ('has("' in args[1] or "jwt_secret" in args[1]):
                        data = yaml.safe_load(pathlib.Path(args[-1]).read_text()) or {{}}
                        security = (data.get("repeater") or {{}}).get("security") or {{}}
                        if "admin_password" in args[1]:
                            present = "admin_password" in security
                        elif "guest_password" in args[1]:
                            present = "guest_password" in security
                        else:
                            present = bool(security.get("jwt_secret"))
                        print("true" if present else "false")
                    elif args[0] == "eval" and args[1] == "-i":
                        path = pathlib.Path(args[-1])
                        data = yaml.safe_load(path.read_text()) or {{}}
                        security = data.setdefault("repeater", {{}}).setdefault("security", {{}})
                        if "admin_password" in args[2]:
                            security["admin_password"] = os.environ["OPENHOP_GENERATED_PASSWORD"]
                        elif "guest_password" in args[2]:
                            security["guest_password"] = os.environ["OPENHOP_GENERATED_PASSWORD"]
                        else:
                            security["jwt_secret"] = os.environ["OPENHOP_GENERATED_SECRET"]
                        path.write_text(yaml.safe_dump(data, sort_keys=False))
                    elif args[0] == "eval-all":
                        template = yaml.safe_load(pathlib.Path(args[-2]).read_text()) or {{}}
                        user = yaml.safe_load(pathlib.Path(args[-1]).read_text()) or {{}}
                        sys.stdout.write(yaml.safe_dump(merge(template, user), sort_keys=False))
                    elif args[0] == "eval" and args[1] == '... comments=""':
                        sys.stdout.write(pathlib.Path(args[-1]).read_text())
                    elif args[0] == "eval" and args[1] == ".":
                        yaml.safe_load(pathlib.Path(args[-1]).read_text())
                    else:
                        raise SystemExit(2)
                    """
                ),
                encoding="utf-8",
            )
            fake_yq.chmod(0o755)

            base_image_id = root / "base-image-id"
            base_image_id.write_text("test-base\n", encoding="utf-8")
            yaml_site_packages = Path(yaml.__file__).resolve().parent.parent
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
                    "OPENHOP_ADDON_PATH_UTILS_HELPER": str(PATH_UTILS_HELPER),
                    "OPENHOP_ADDON_CONFIG_HELPER": str(CONFIG_HELPER),
                    "OPENHOP_ADDON_RUNTIME_INFO_HELPER": str(RUNTIME_INFO_HELPER),
                    "OPENHOP_ADDON_VENV_PIP_WRAPPER": str(PIP_WRAPPER),
                    "OPENHOP_ADDON_TEST_WITHOUT_PIP": "true",
                    "OPENHOP_ADDON_SYSTEM_PYTHON": "/usr/bin/python3",
                    "OPENHOP_ADDON_BASE_SITE_PACKAGES_GLOB": str(yaml_site_packages),
                    "OPENHOP_ADDON_BASE_RUNTIME_DIR": str(base_runtime),
                    "OPENHOP_ADDON_BASE_IMAGE_ID_FILE": str(base_image_id),
                    "OPENHOP_ADDON_BUILD_VERSION": "3.0.0",
                    "OPENHOP_ADDON_YQ": str(fake_yq),
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
                    deadline = time.monotonic() + 90
                    while time.monotonic() < deadline:
                        output = log_path.read_text(encoding="utf-8")
                        if (
                            "repeater process started" in output
                            and (root / "child-pid").is_file()
                        ):
                            break
                        return_code = process.poll()
                        if return_code is not None:
                            self.fail(
                                "bootstrap exited early with status "
                                f"{return_code}:\n{output}"
                            )
                        time.sleep(0.1)
                    else:
                        self.fail(
                            "bootstrap did not start the packaged runtime:\n"
                            + log_path.read_text(encoding="utf-8")
                        )

                    process.send_signal(signal.SIGTERM)
                    self.assertEqual(process.wait(timeout=15), 0)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=15)

            assert_process_exited(self, root / "child-pid")
            merged = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            self.assertEqual(
                merged["repeater"]["security"]["admin_password"], "admin123"
            )
            self.assertEqual(
                merged["repeater"]["security"]["guest_password"], "guest123"
            )

    def test_invalid_template_does_not_leave_partial_configuration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="openhop-addon-config-") as temp_dir:
            root = Path(temp_dir)
            for directory in ("config", "data", "etc", "var", "opt"):
                (root / directory).mkdir()

            invalid_template = root / "invalid-template.yaml"
            invalid_template.write_text(
                "repeater: {}\nradio_type: null\n", encoding="utf-8"
            )
            env = os.environ.copy()
            env.update(
                {
                    "OPENHOP_ADDON_CONFIG_DIR": str(root / "config"),
                    "OPENHOP_ADDON_DATA_DIR": str(root / "data"),
                    "OPENHOP_ADDON_RUNTIME_CONFIG_DIR": str(
                        root / "etc" / "openhop_repeater"
                    ),
                    "OPENHOP_ADDON_FIRMWARE_DATA_DIR": str(
                        root / "var" / "openhop_repeater"
                    ),
                    "OPENHOP_ADDON_UPDATE_VENV_LINK": str(root / "opt" / "venv"),
                    "OPENHOP_ADDON_TEMPLATE_CONFIG": str(invalid_template),
                    "OPENHOP_ADDON_BRANCH_HELPER": str(BRANCH_HELPER),
                    "OPENHOP_ADDON_PATH_UTILS_HELPER": str(PATH_UTILS_HELPER),
                    "OPENHOP_ADDON_CONFIG_HELPER": str(CONFIG_HELPER),
                    "OPENHOP_ADDON_RUNTIME_INFO_HELPER": str(RUNTIME_INFO_HELPER),
                    "OPENHOP_ADDON_VENV_PIP_WRAPPER": str(PIP_WRAPPER),
                    "OPENHOP_ADDON_TEST_WITHOUT_PIP": "true",
                    "OPENHOP_ADDON_SYSTEM_PYTHON": "/usr/bin/python3",
                    "OPENHOP_ADDON_BUILD_VERSION": "3.0.0",
                }
            )

            result = subprocess.run(
                [str(RUN_SCRIPT)],
                env=env,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("could not generate unique credentials", result.stderr)
            self.assertFalse((root / "config" / "config.yaml").exists())
            self.assertEqual(list((root / "config").glob("config.yaml.tmp.*")), [])


if __name__ == "__main__":
    unittest.main()
