from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "openhop_repeater_main"
    / "rootfs"
    / "usr"
    / "local"
    / "lib"
    / "openhop-addon"
    / "branch_state.py"
)
PIP_WRAPPER = (
    ROOT
    / "openhop_repeater_main"
    / "rootfs"
    / "usr"
    / "local"
    / "bin"
    / "openhop-venv-pip"
)
SPEC = importlib.util.spec_from_file_location("branch_state", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
branch_state = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(branch_state)


class GitRefValidationTests(unittest.TestCase):
    def test_accepts_normal_branch_names(self) -> None:
        for ref in (
            "main",
            "dev",
            "fix/all-the-things",
            "release/v1.2.3",
            "user/topic_42",
        ):
            with self.subTest(ref=ref):
                self.assertTrue(branch_state.is_valid_git_ref(ref))

    def test_rejects_unsafe_or_invalid_refs(self) -> None:
        for ref in (
            "",
            "-main",
            ".hidden",
            "feature//topic",
            "feature..topic",
            "feature@{topic",
            "feature topic",
            "feature:topic",
            "feature+topic",
            "feature#topic",
            "topic.lock",
            "topic/",
            "topic.",
            "topic./child",
            "topic\\name",
        ):
            with self.subTest(ref=ref):
                self.assertFalse(branch_state.is_valid_git_ref(ref))


class PipArgumentValidationTests(unittest.TestCase):
    def test_accepts_expected_upstream_branch_installs(self) -> None:
        install_spec = (
            "openhop_repeater[hardware] @ "
            "git+https://github.com/openhop-dev/openhop_repeater.git@dev"
        )
        for options in (
            ["--upgrade", "--no-cache-dir"],
            ["--upgrade", "--force-reinstall", "--no-cache-dir"],
        ):
            with self.subTest(options=options):
                self.assertTrue(
                    branch_state.are_safe_pip_args(
                        ["install", *options, install_spec]
                    )
                )

    def test_rejects_other_repositories_and_unsafe_refs(self) -> None:
        for install_spec in (
            (
                "openhop_repeater[hardware] @ "
                "git+https://example.invalid/openhop_repeater.git@dev"
            ),
            (
                "openhop_repeater[hardware] @ "
                "git+https://github.com/openhop-dev/"
                "openhop_repeater.git@dev#subdirectory=repeater"
            ),
            "openhop_repeater",
        ):
            with self.subTest(install_spec=install_spec):
                self.assertFalse(
                    branch_state.are_safe_pip_args(["install", install_spec])
                )

    def test_rejects_extra_packages_or_changed_options(self) -> None:
        install_spec = (
            "openhop_repeater[hardware] @ "
            "git+https://github.com/openhop-dev/openhop_repeater.git@dev"
        )
        for args in (
            ["install", "--upgrade", "--no-cache-dir", install_spec, "requests"],
            ["install", "--no-cache-dir", "--upgrade", install_spec],
            ["--disable-pip-version-check", "install", install_spec],
            ["install", "--upgrade", "pip", "setuptools", "wheel"],
        ):
            with self.subTest(args=args):
                self.assertFalse(branch_state.are_safe_pip_args(args))

    def test_allows_only_version_checks_outside_branch_installs(self) -> None:
        self.assertTrue(branch_state.are_safe_pip_args(["--version"]))
        self.assertTrue(branch_state.are_safe_pip_args(["-V"]))
        self.assertFalse(branch_state.are_safe_pip_args(["--help"]))
        self.assertFalse(
            branch_state.are_safe_pip_args(["uninstall", "-y", "openhop_repeater"])
        )

    def test_wrapper_rejects_an_unsafe_install_before_invoking_pip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bin_dir = Path(temp_dir) / "venv" / "bin"
            bin_dir.mkdir(parents=True)
            (bin_dir / "python").symlink_to(sys.executable)
            (bin_dir / "pip").symlink_to(PIP_WRAPPER)

            env = os.environ.copy()
            env["OPENHOP_ADDON_BRANCH_HELPER"] = str(MODULE_PATH)
            result = subprocess.run(
                [
                    str(bin_dir / "pip"),
                    "install",
                    "openhop_repeater @ git+https://example.invalid/repo.git@main",
                ],
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Refusing an unsafe", result.stderr)

            version = subprocess.run(
                [str(bin_dir / "pip"), "--version"],
                env=env,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            self.assertEqual(version.returncode, 0, version.stderr)
            self.assertIn("pip", version.stdout.lower())


class InstalledRefTests(unittest.TestCase):
    def _write_direct_url(
        self,
        root: Path,
        name: str,
        revision: str,
        mtime: int,
        *,
        url: str = "https://github.com/openhop-dev/openhop_repeater.git",
        vcs: str = "git",
    ) -> None:
        target = root / f"openhop_repeater-{name}.dist-info" / "direct_url.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "url": url,
                    "vcs_info": {
                        "vcs": vcs,
                        "requested_revision": revision,
                        "commit_id": "0" * 40,
                    },
                }
            ),
            encoding="utf-8",
        )
        os.utime(target, ns=(mtime, mtime))

    def test_returns_newest_distribution_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_direct_url(root, "1.0.0", "main", 1)
            self._write_direct_url(root, "2.0.0", "dev", 2)
            self.assertEqual(branch_state.installed_ref(root), "dev")

    def test_ignores_other_repositories_and_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            invalid = root / "openhop_repeater-3.0.0.dist-info" / "direct_url.json"
            invalid.parent.mkdir(parents=True)
            invalid.write_text("not-json", encoding="utf-8")

            other = root / "openhop_repeater-2.0.0.dist-info" / "direct_url.json"
            other.parent.mkdir(parents=True)
            other.write_text(
                json.dumps(
                    {
                        "url": "https://github.com/example/other.git",
                        "vcs_info": {"requested_revision": "wrong"},
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(branch_state.installed_ref(root), "")

    def test_ignores_spoofed_urls_non_git_metadata_and_invalid_refs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_direct_url(
                root,
                "3.0.0",
                "main",
                3,
                url="https://example.invalid/openhop_repeater.git",
            )
            self._write_direct_url(root, "2.0.0", "dev", 2, vcs="hg")
            self._write_direct_url(root, "1.0.0", "unsafe ref", 1)
            self.assertEqual(branch_state.installed_ref(root), "")


if __name__ == "__main__":
    unittest.main()
