from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_repository.py"


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_validator_accepts_both_prebuilt_channels(self) -> None:
        self.assertTrue(VALIDATOR.is_file(), f"missing validator: {VALIDATOR}")
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 2 add-ons", result.stdout)
        self.assertIn("openhop_repeater_dev", result.stdout)
        self.assertIn("openhop_repeater_main", result.stdout)


if __name__ == "__main__":
    unittest.main()
