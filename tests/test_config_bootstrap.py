from __future__ import annotations

import importlib.util
import stat
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ADDONS = ("openhop_repeater_dev", "openhop_repeater_main")
HELPER_RELATIVE = Path("rootfs/usr/local/lib/openhop-addon/config_bootstrap.py")


def load_helper(addon: str):
    path = ROOT / addon / HELPER_RELATIVE
    if not path.is_file():
        raise AssertionError(f"missing configuration bootstrap helper: {path}")
    spec = importlib.util.spec_from_file_location(f"config_bootstrap_{addon}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ConfigurationBootstrapTests(unittest.TestCase):
    def test_helpers_are_identical_for_both_channels(self) -> None:
        paths = [ROOT / addon / HELPER_RELATIVE for addon in ADDONS]
        for path in paths:
            self.assertTrue(path.is_file(), f"missing helper: {path}")
        self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())

    def test_first_start_is_atomic_private_and_generates_unique_credentials(self) -> None:
        template_text = (
            "# packaged template comment\n"
            "repeater:\n"
            "  node_name: packaged-node\n"
            "  security:\n"
            '    admin_password: "admin123"\n'
            '    guest_password: "guest123"\n'
            '    jwt_secret: ""\n'
            "radio_type: sx1262\n"
        )
        for addon in ADDONS:
            with self.subTest(addon=addon), tempfile.TemporaryDirectory() as temp_dir:
                helper = load_helper(addon)
                root = Path(temp_dir)
                template = root / "template.yaml"
                config = root / "config" / "config.yaml"
                template.write_text(template_text, encoding="utf-8")

                result = helper.bootstrap_config(template, config)

                self.assertEqual(result, "created")
                generated_text = config.read_text(encoding="utf-8")
                self.assertIn("# packaged template comment", generated_text)
                generated = yaml.safe_load(generated_text)
                security = generated["repeater"]["security"]
                self.assertNotEqual(security["admin_password"], "admin123")
                self.assertNotEqual(security["guest_password"], "guest123")
                self.assertGreaterEqual(len(security["admin_password"]), 24)
                self.assertGreaterEqual(len(security["guest_password"]), 24)
                self.assertEqual(len(security["jwt_secret"]), 64)
                self.assertEqual(stat.S_IMODE(config.stat().st_mode), 0o600)
                self.assertEqual(list(config.parent.glob(".config.yaml.*")), [])

    def test_upgrade_merges_missing_defaults_without_replacing_user_values(self) -> None:
        template = {
            "repeater": {
                "node_name": "packaged-node",
                "cache_ttl": 3600,
                "security": {
                    "admin_password": "admin123",
                    "guest_password": "guest123",
                    "jwt_secret": "",
                    "jwt_expiry_minutes": 60,
                },
            },
            "radio_type": "sx1262",
            "gps": {"enabled": False},
            "mqtt": {"brokers": ["packaged"]},
        }
        existing = {
            "repeater": {
                "node_name": "kept-node",
                "security": {
                    "admin_password": "kept-admin",
                    "guest_password": "kept-guest",
                    "jwt_secret": "a" * 64,
                },
            },
            "radio_type": "kiss",
            "mqtt": {"brokers": ["kept"]},
            "custom": {"preserved": True},
        }
        for addon in ADDONS:
            with self.subTest(addon=addon), tempfile.TemporaryDirectory() as temp_dir:
                helper = load_helper(addon)
                root = Path(temp_dir)
                template_path = root / "template.yaml"
                config_path = root / "config.yaml"
                template_path.write_text(yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
                config_path.write_text(yaml.safe_dump(existing, sort_keys=False), encoding="utf-8")

                result = helper.bootstrap_config(template_path, config_path)

                self.assertEqual(result, "merged")
                merged = yaml.safe_load(config_path.read_text(encoding="utf-8"))
                self.assertEqual(merged["repeater"]["node_name"], "kept-node")
                self.assertEqual(merged["repeater"]["security"]["admin_password"], "kept-admin")
                self.assertEqual(merged["repeater"]["security"]["guest_password"], "kept-guest")
                self.assertEqual(merged["repeater"]["security"]["jwt_secret"], "a" * 64)
                self.assertEqual(merged["repeater"]["cache_ttl"], 3600)
                self.assertEqual(merged["repeater"]["security"]["jwt_expiry_minutes"], 60)
                self.assertEqual(merged["gps"], {"enabled": False})
                self.assertEqual(merged["mqtt"]["brokers"], ["kept"])
                self.assertEqual(merged["custom"], {"preserved": True})
                self.assertEqual(stat.S_IMODE(config_path.stat().st_mode), 0o600)

    def test_both_channels_accept_multi_radio_without_legacy_radio_type(self) -> None:
        template = {
            "repeater": {"node_name": "template", "security": {
                "admin_password": "default", "guest_password": "default", "jwt_secret": "default",
            }},
            "radio_type": "sx1262",
            "gps": {"enabled": False},
        }
        existing = {
            "repeater": {"node_name": "field-node", "security": {
                "admin_password": "kept-admin", "guest_password": "kept-guest",
                "jwt_secret": "kept-secret",
            }},
            "radios": [
                {"id": "south", "radio_type": "modem_tcp", "modem_tcp": {"host": "south.invalid"}},
                {"id": "north", "radio_type": "modem_tcp", "modem_tcp": {"host": "north.invalid"}},
            ],
            "fabric": {"default_radio": "north", "tx_mode": "bridge"},
        }
        for addon in ADDONS:
            with self.subTest(addon=addon), tempfile.TemporaryDirectory() as temp_dir:
                helper = load_helper(addon)
                root = Path(temp_dir)
                template_path, config_path = root / "template.yaml", root / "config.yaml"
                template_path.write_text(yaml.safe_dump(template), encoding="utf-8")
                config_path.write_text(yaml.safe_dump(existing), encoding="utf-8")

                self.assertEqual(helper.bootstrap_config(template_path, config_path), "merged")
                merged = yaml.safe_load(config_path.read_text(encoding="utf-8"))
                self.assertNotIn("radio_type", merged)
                self.assertEqual(merged["radios"], existing["radios"])
                self.assertEqual(merged["fabric"], existing["fabric"])
                self.assertEqual(merged["repeater"]["security"], existing["repeater"]["security"])
                self.assertEqual(merged["gps"], template["gps"])
                self.assertEqual(stat.S_IMODE(config_path.stat().st_mode), 0o600)
                self.assertEqual(helper.bootstrap_config(template_path, config_path), "unchanged")

    def test_both_channels_reject_missing_or_incomplete_radio_configuration(self) -> None:
        template = {"repeater": {"node_name": "template"}, "radio_type": None}
        for addon in ADDONS:
            helper = load_helper(addon)
            for radios in (None, [], [{"id": "one", "radio_type": "modem_tcp"}],
                           [{"id": "one", "radio_type": "modem_tcp"}, {"id": "two"}]):
                with self.subTest(addon=addon, radios=radios), tempfile.TemporaryDirectory() as temp_dir:
                    root = Path(temp_dir)
                    template_path, config_path = root / "template.yaml", root / "config.yaml"
                    template_path.write_text(yaml.safe_dump(template), encoding="utf-8")
                    existing = {"repeater": {"node_name": "node"}}
                    if radios is not None:
                        existing["radios"] = radios
                    original = yaml.safe_dump(existing)
                    config_path.write_text(original, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "radio_type is required"):
                        helper.bootstrap_config(template_path, config_path)
                    self.assertEqual(config_path.read_text(encoding="utf-8"), original)


    def test_upgrade_generates_only_missing_credentials(self) -> None:
        template_text = (
            "repeater:\n"
            "  node_name: packaged-node\n"
            "  security:\n"
            "    admin_password: admin123\n"
            "    guest_password: guest123\n"
            '    jwt_secret: ""\n'
            "radio_type: sx1262\n"
        )
        existing_text = (
            "repeater:\n"
            "  node_name: kept-node\n"
            "  security:\n"
            "    admin_password: kept-admin\n"
            "radio_type: kiss\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = load_helper(ADDONS[0])
            root = Path(temp_dir)
            template_path = root / "template.yaml"
            config_path = root / "config.yaml"
            template_path.write_text(template_text, encoding="utf-8")
            config_path.write_text(existing_text, encoding="utf-8")

            helper.bootstrap_config(template_path, config_path)

            merged = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            security = merged["repeater"]["security"]
            self.assertEqual(security["admin_password"], "kept-admin")
            self.assertNotEqual(security["guest_password"], "guest123")
            self.assertEqual(len(security["jwt_secret"]), 64)

    def test_invalid_existing_config_is_left_unchanged(self) -> None:
        template_text = (
            "repeater:\n"
            "  node_name: packaged-node\n"
            "  security:\n"
            "    admin_password: admin123\n"
            "    guest_password: guest123\n"
            '    jwt_secret: ""\n'
            "radio_type: sx1262\n"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = load_helper(ADDONS[0])
            root = Path(temp_dir)
            template_path = root / "template.yaml"
            config_path = root / "config.yaml"
            template_path.write_text(template_text, encoding="utf-8")
            original = "repeater: [unterminated\n"
            config_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                helper.bootstrap_config(template_path, config_path)

            self.assertEqual(config_path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(root.glob(".config.yaml.*")), [])

    def test_invalid_template_does_not_publish_partial_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = load_helper(ADDONS[0])
            root = Path(temp_dir)
            template_path = root / "template.yaml"
            config_path = root / "config.yaml"
            template_path.write_text("repeater: {}\nradio_type: null\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                helper.bootstrap_config(template_path, config_path)

            self.assertFalse(config_path.exists())
            self.assertEqual(list(root.glob(".config.yaml.*")), [])


if __name__ == "__main__":
    unittest.main()
