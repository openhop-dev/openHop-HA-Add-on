from __future__ import annotations

import importlib.util
import json
import os
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
            "topic\\name",
        ):
            with self.subTest(ref=ref):
                self.assertFalse(branch_state.is_valid_git_ref(ref))


class InstalledRefTests(unittest.TestCase):
    def _write_direct_url(self, root: Path, name: str, revision: str, mtime: int) -> None:
        target = root / f"openhop_repeater-{name}.dist-info" / "direct_url.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "url": "https://github.com/openhop-dev/openhop_repeater.git",
                    "vcs_info": {
                        "vcs": "git",
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


if __name__ == "__main__":
    unittest.main()
