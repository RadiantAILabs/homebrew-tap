#!/usr/bin/env python3
"""Validate Homebrew build metadata and prepare immutable release assets."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from urllib.parse import unquote


artifact_dir = Path(sys.argv[1])
asset_dir = Path(sys.argv[2])
asset_dir.mkdir(parents=True, exist_ok=True)
formula_name = "radiantailabs/tap/polaris-code"
expected_tags = {"arm64_sequoia", "x86_64_linux"}
versions = set()
roots = set()
tags = set()
json_files = sorted(artifact_dir.glob("*.bottle.json"))
if len(json_files) != len(expected_tags):
    raise SystemExit("Expected one bottle manifest for each supported platform")

for manifest in json_files:
    data = json.loads(manifest.read_text())[formula_name]
    formula = data["formula"]
    if formula["tap_git_revision"] != os.environ["GITHUB_SHA"]:
        raise SystemExit("A bottle was built from a different tap commit")
    versions.add(formula["pkg_version"])
    roots.add(data["bottle"]["root_url"])
    for tag, bottle in data["bottle"]["tags"].items():
        if tag in tags:
            raise SystemExit("Duplicate bottle platform")
        tags.add(tag)
        local_name = bottle["local_filename"]
        asset_name = unquote(bottle["filename"])
        if Path(local_name).name != local_name or Path(asset_name).name != asset_name:
            raise SystemExit("Expected flat bottle filenames")
        archive = artifact_dir / local_name
        with archive.open("rb") as source:
            checksum = hashlib.file_digest(source, "sha256").hexdigest()
        if checksum != bottle["sha256"]:
            raise SystemExit("A bottle archive does not match its checksum")
        shutil.copyfile(archive, asset_dir / asset_name)

if tags != expected_tags or len(versions) != 1 or len(roots) != 1:
    raise SystemExit("Bottle platforms or release metadata disagree")
version = versions.pop()
release_tag = f"polaris-code-{version}-bottles-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}"
expected_root = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/releases/download/{release_tag}"
if roots.pop() != expected_root:
    raise SystemExit("Bottle download URL does not match this release")

notes = asset_dir / "release-notes.txt"
notes.write_text(
    f"Homebrew bottles for polaris-code {version}.\n\n"
    f"Built and tested from tap commit {os.environ['GITHUB_SHA']}.\n"
    f"Application source: https://github.com/RadiantAILabs/polaris_code/tree/v{version}\n"
)
with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
    output.write(f"version={version}\nrelease_tag={release_tag}\n")
print(f"Verified bottles for {version}: {', '.join(sorted(tags))}")
