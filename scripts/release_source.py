#!/usr/bin/env python3
"""Resolve and validate the tagged application source for a bottle build."""

from dataclasses import dataclass
import hashlib
import io
import os
from pathlib import Path
import re
import tarfile
import tomllib
import urllib.error
import urllib.request


ARCHIVE_BASE = "https://github.com/RadiantAILabs/polaris_code/archive/refs/tags/"
TAG_PATTERN = r"v(\d+)\.(\d+)\.(\d+)"


@dataclass(frozen=True)
class Source:
    """A versioned, checksummed application archive."""

    tag: str
    url: str
    sha256: str

    @property
    def version(self) -> str:
        """Return the crate version represented by this tag."""
        return self.tag[1:]


def version_key(tag: str) -> tuple[int, ...]:
    """Parse the stable release tag format used by the application."""
    match = re.fullmatch(TAG_PATTERN, tag)
    if not match:
        raise ValueError("Expected a stable vMAJOR.MINOR.PATCH release tag")
    return tuple(map(int, match.groups()))


def source_from_formula(text: str) -> Source:
    """Read the existing formula's primary source specification."""
    url = re.search(r'^  url "([^"]+)"$', text, re.MULTILINE)
    checksum = re.search(r'^  sha256 "([0-9a-f]{64})"$', text, re.MULTILINE)
    if not url or not checksum:
        raise ValueError("Formula has no unambiguous primary URL and checksum")
    value = url.group(1)
    if not value.startswith(ARCHIVE_BASE) or not value.endswith(".tar.gz"):
        raise ValueError("Formula must use the public application's tagged source")
    tag = value.removeprefix(ARCHIVE_BASE).removesuffix(".tar.gz")
    version_key(tag)
    return Source(tag, value, checksum.group(1))


def validate_archive(content: bytes, tag: str) -> None:
    """Require the archive's crate version and executable to match the release."""
    version_key(tag)
    with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
        def manifest(relative: str) -> dict:
            matches = [
                entry for entry in archive.getmembers()
                if entry.isfile() and entry.name.partition("/")[2] == relative
            ]
            if len(matches) != 1:
                raise ValueError(f"Archive must contain exactly one {relative}")
            return tomllib.loads(archive.extractfile(matches[0]).read().decode())

        app = manifest("crates/polaris_code/Cargo.toml")
        package = app["package"]
        version = package["version"]
        if isinstance(version, dict) and version.get("workspace"):
            version = manifest("Cargo.toml")["workspace"]["package"]["version"]
        if package["name"] != "polaris_code" or version != tag[1:]:
            raise ValueError("Release tag does not match the application crate version")
        if not any(binary["name"] == "polaris" for binary in app.get("bin", [])):
            raise ValueError("Release must install the polaris executable")


def fetch_archive(url: str) -> bytes:
    """Download public source without forwarding workflow credentials."""
    request = urllib.request.Request(url, headers={"User-Agent": "polaris-homebrew-release"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def resolve(text: str, tag: str, force: bool = False, fetch=fetch_archive) -> tuple[Source, bool]:
    """Select a release without rolling back or rebuilding an existing bottle."""
    current = source_from_formula(text)
    if not tag:
        return current, True
    if version_key(tag) < version_key(current.tag):
        return current, False
    url = ARCHIVE_BASE + tag + ".tar.gz"
    content = fetch(url)
    validate_archive(content, tag)
    source = Source(tag, url, hashlib.sha256(content).hexdigest())
    if tag == current.tag and source.sha256 != current.sha256:
        raise ValueError("An existing release tag's archive checksum changed")
    needs_build = force or tag != current.tag or "  bottle do\n" not in text
    return source, needs_build


def main() -> None:
    """Emit the immutable source inputs used by build and publication jobs."""
    text = Path("Formula/polaris-code.rb").read_text()
    try:
        source, build = resolve(
            text, os.environ.get("RELEASE_TAG", ""),
            os.environ.get("FORCE_REBUILD", "false") == "true",
        )
    except (ValueError, urllib.error.URLError) as error:
        raise SystemExit(str(error)) from None
    outputs = {
        "release_tag": source.tag, "source_url": source.url,
        "source_sha256": source.sha256, "version": source.version,
        "build": str(build).lower(),
    }
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
        for key, value in outputs.items():
            output.write(f"{key}={value}\n")
    print(f"Release {source.tag}: {'build bottles' if build else 'already current or superseded'}")


if __name__ == "__main__":
    main()
