#!/usr/bin/env python3
"""Stage a release locally; publish the source and bottle changes together."""

import os
from pathlib import Path
import re
import sys

from release_source import ARCHIVE_BASE, version_key


def stage(text: str, url: str, checksum: str) -> str:
    """Replace the source specification and remove bottles for the prior source."""
    if not url.startswith(ARCHIVE_BASE) or not url.endswith(".tar.gz"):
        raise ValueError("Expected the public application's tagged source URL")
    tag = url.removeprefix(ARCHIVE_BASE).removesuffix(".tar.gz")
    version_key(tag)
    if not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ValueError("Expected a SHA-256 checksum")
    updated, urls = re.subn(r'^  url "[^"]+"$', f'  url "{url}"', text, flags=re.MULTILINE)
    updated, checksums = re.subn(
        r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{checksum}"', updated, flags=re.MULTILINE,
    )
    if urls != 1 or checksums != 1:
        raise ValueError("Formula must have exactly one primary URL and checksum")
    updated = re.sub(r'\n  bottle do\n.*?^  end\n', '', updated, count=1, flags=re.MULTILINE | re.DOTALL)
    return re.sub(r'^  version "[^"]+"$', f'  version "{tag[1:]}"', updated, flags=re.MULTILINE)


def main() -> None:
    """Apply the prepared source only to the runner's formula checkout."""
    path = Path(sys.argv[1])
    path.write_text(stage(path.read_text(), os.environ["SOURCE_URL"], os.environ["SOURCE_SHA256"]))
    print("Staged release source; the published tap remains unchanged until bottles pass")


if __name__ == "__main__":
    main()
