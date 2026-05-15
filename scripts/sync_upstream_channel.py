#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Unsupported version format: {version}")
    major, minor, patch = map(int, parts)
    return f"{major}.{minor}.{patch + 1}"


def load_compare_data(compare_path: str | None) -> dict:
    if not compare_path:
        return {}
    with open(compare_path, encoding="utf-8") as file:
        return json.load(file)


def build_changelog_entry(
    new_version: str,
    channel: str,
    image_ref: str,
    old_rev: str,
    new_rev: str,
    compare_data: dict,
) -> str:
    compare_url = compare_data.get("html_url") or (
        f"https://github.com/pyMC-dev/pyMC_Repeater/compare/{old_rev}...{new_rev}"
    )
    commits = compare_data.get("commits", [])
    channel_label = channel.upper()
    short_old = old_rev[:7]
    short_new = new_rev[:7]

    lines = [
        f"## {new_version}",
        "",
        f"- Track upstream `{channel_label}` commit `{short_new}` from `{image_ref}`",
        f"- Previous tracked commit: `{short_old}`",
        f"- Upstream diff: {compare_url}",
    ]

    commit_entries = []
    for commit in commits[:8]:
        sha = (commit.get("sha") or "")[:7]
        message = commit.get("commit", {}).get("message", "").strip()
        subject = message.splitlines()[0] if message else ""
        if sha and subject:
            commit_entries.append(f"`{sha}` {subject}")
        elif subject:
            commit_entries.append(subject)

    if commit_entries:
        lines.append("- Included upstream commits:")
        for entry in commit_entries:
            lines.append(f"  - {entry}")

    lines.append("")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    state_path = ROOT / os.environ["STATE_FILE"]
    compare_json_path = os.environ.get("COMPARE_JSON_PATH")
    new_revision = os.environ["NEW_REVISION"].strip()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    addon_dir = ROOT / state["addon_dir"]
    config_path = addon_dir / "config.yaml"
    changelog_path = addon_dir / "CHANGELOG.md"
    image_ref = state["image"]
    old_revision = state["revision"]

    if new_revision == old_revision:
        print("No upstream revision change detected.")
        return

    config_text = config_path.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?\s*$', config_text, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not find version in {config_path}")

    old_version = match.group(1)
    new_version = bump_patch(old_version)
    config_path.write_text(
        re.sub(
            r'^version:\s*"?[0-9]+\.[0-9]+\.[0-9]+"?\s*$',
            f'version: "{new_version}"',
            config_text,
            count=1,
            flags=re.MULTILINE,
        ),
        encoding="utf-8",
    )

    compare_data = load_compare_data(compare_json_path)
    changelog = changelog_path.read_text(encoding="utf-8")
    header = "# Changelog\n\n"
    if not changelog.startswith(header):
        raise ValueError(f"Unexpected changelog format in {changelog_path}")

    new_entry = build_changelog_entry(
        new_version,
        state["channel"],
        image_ref,
        old_revision,
        new_revision,
        compare_data,
    )
    changelog_path.write_text(header + new_entry + changelog[len(header):], encoding="utf-8")

    state["revision"] = new_revision
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(f"Bumped {state['channel']} add-on from {old_version} to {new_version}")
    print(f"Tracked upstream revision {old_revision[:7]} -> {new_revision[:7]}")


if __name__ == "__main__":
    main()
