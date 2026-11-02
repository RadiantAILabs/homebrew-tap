#!/usr/bin/env python3
"""Fetch and verify the binary formula published with an application release.

The application's CI builds, tests, and attaches `polaris-code.rb` to each
GitHub release. That formula installs the release's prebuilt archives, so the
tap publishes it as-is after checking that it points only at that release and
that every archive matches its checksum.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import urllib.error
import urllib.request


RELEASE_BASE = "https://github.com/RadiantAILabs/polaris_code/releases/download/"
LEGACY_SOURCE_BASE = "https://github.com/RadiantAILabs/polaris_code/archive/refs/tags/"
FORMULA_ASSET = "polaris-code.rb"
TAG_PATTERN = r"v(\d+)\.(\d+)\.(\d+)"


def version_key(tag: str) -> tuple[int, ...]:
    """Parse the stable release tag format used by the application."""
    match = re.fullmatch(TAG_PATTERN, tag)
    if not match:
        raise ValueError("Expected a stable vMAJOR.MINOR.PATCH release tag")
    return tuple(map(int, match.groups()))


def formula_tag(text: str) -> str:
    """Return the release tag a formula installs, for binary or legacy source formulae."""
    version = re.search(r'^  version "([^"]+)"$', text, re.MULTILINE)
    if version:
        tag = "v" + version.group(1)
    else:
        url = re.search(r'^  url "([^"]+)"$', text, re.MULTILINE)
        if not url or not url.group(1).startswith(LEGACY_SOURCE_BASE):
            raise ValueError("Formula declares neither a version nor a tagged source")
        tag = url.group(1).removeprefix(LEGACY_SOURCE_BASE).removesuffix(".tar.gz")
    version_key(tag)
    return tag


def archives(text: str) -> list[tuple[str, str]]:
    """Return each `(url, sha256)` pair, requiring a checksum right after each URL."""
    pairs = re.findall(r'^ +url "([^"]+)"\n +sha256 "([0-9a-f]{64})"$', text, re.MULTILINE)
    if not pairs or len(pairs) != len(re.findall(r'^ +url ', text, re.MULTILINE)):
        raise ValueError("Every formula URL must be followed by its SHA-256 checksum")
    return pairs


def fetch(url: str) -> bytes:
    """Download a public release asset without forwarding workflow credentials."""
    request = urllib.request.Request(url, headers={"User-Agent": "polaris-homebrew-release"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def verify(text: str, tag: str, fetch=fetch) -> None:
    """Require the formula to install only this release's archives, unmodified."""
    version_key(tag)
    if "class PolarisCode < Formula" not in text:
        raise ValueError("Expected the polaris-code formula")
    if formula_tag(text) != tag:
        raise ValueError(f"Formula version does not match release {tag}")
    if "bottle do" in text:
        raise ValueError("The binary formula must not declare bottles")
    prefix = f"{RELEASE_BASE}{tag}/"
    for url, checksum in archives(text):
        if not url.startswith(prefix) or not url.endswith(".tar.gz"):
            raise ValueError(f"Formula URL is not an archive of release {tag}: {url}")
        published = fetch(url + ".sha256").decode().split()
        if not published or published[0] != checksum:
            raise ValueError(f"Formula checksum differs from the published one for {url}")
        if hashlib.sha256(fetch(url)).hexdigest() != checksum:
            raise ValueError(f"Downloaded archive does not match its checksum: {url}")


def resolve(current: str, tag: str, force: bool = False, fetch=fetch) -> str | None:
    """Return the release formula to publish, or None when there is nothing to do.

    An older release never replaces a newer formula, and an unchanged formula is
    not republished unless forced.
    """
    if version_key(tag) < version_key(formula_tag(current)):
        return None
    text = fetch(f"{RELEASE_BASE}{tag}/{FORMULA_ASSET}").decode()
    verify(text, tag, fetch)
    if text == current and not force:
        return None
    return text


def main() -> None:
    """Check the tap's formula, or stage a release's formula for publication."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("formula", type=Path, help="the tap's Formula/polaris-code.rb")
    parser.add_argument("--check", action="store_true", help="only verify the formula in place")
    args = parser.parse_args()
    current = args.formula.read_text()
    try:
        if args.check:
            tag = formula_tag(current)
            verify(current, tag)
            print(f"Formula installs the verified {tag} release archives")
            return
        tag = os.environ["RELEASE_TAG"]
        staged = resolve(current, tag, os.environ.get("FORCE_REBUILD", "false") == "true")
    except (ValueError, urllib.error.URLError) as error:
        raise SystemExit(str(error)) from None
    if staged is not None:
        args.formula.write_text(staged)
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        output.write(f"publish={str(staged is not None).lower()}\nversion={tag[1:]}\n")
    print(f"Release {tag}: {'staged' if staged is not None else 'already current or superseded'}")


if __name__ == "__main__":
    main()
