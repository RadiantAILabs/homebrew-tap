"""Tests for verifying and selecting the application's binary release formula."""

import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_formula import LEGACY_SOURCE_BASE, RELEASE_BASE, formula_tag, resolve, verify


MAC = b"mac archive bytes"
LINUX = b"linux archive bytes"


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def binary_formula(tag="v0.2.0", mac_sha=None, linux_sha=None, base=RELEASE_BASE):
    version = tag[1:]
    return (
        'class PolarisCode < Formula\n'
        f'  version "{version}"\n'
        '  on_macos do\n    on_arm do\n'
        f'      url "{base}{tag}/polaris-code-{version}-aarch64-apple-darwin.tar.gz"\n'
        f'      sha256 "{mac_sha or digest(MAC)}"\n'
        '    end\n  end\n'
        '  on_linux do\n    on_intel do\n'
        f'      url "{base}{tag}/polaris-code-{version}-x86_64-unknown-linux-gnu.tar.gz"\n'
        f'      sha256 "{linux_sha or digest(LINUX)}"\n'
        '    end\n  end\nend\n'
    )


def legacy_formula(tag="v0.1.1"):
    return (
        'class PolarisCode < Formula\n'
        f'  url "{LEGACY_SOURCE_BASE}{tag}.tar.gz"\n'
        f'  sha256 "{"a" * 64}"\n'
        '  bottle do\n    root_url "https://example.com/bottles"\n  end\nend\n'
    )


def release(tag="v0.2.0", formula=None, mac=MAC, linux=LINUX, published=None):
    """A fake release: its formula asset, archives, and published checksum files."""
    version = tag[1:]
    prefix = f"{RELEASE_BASE}{tag}/"
    mac_url = f"{prefix}polaris-code-{version}-aarch64-apple-darwin.tar.gz"
    linux_url = f"{prefix}polaris-code-{version}-x86_64-unknown-linux-gnu.tar.gz"
    assets = {
        prefix + "polaris-code.rb": (formula or binary_formula(tag)).encode(),
        mac_url: mac,
        linux_url: linux,
        mac_url + ".sha256": f"{digest(MAC)}  mac.tar.gz\n".encode(),
        linux_url + ".sha256": f"{digest(LINUX)}  linux.tar.gz\n".encode(),
    }
    assets.update(published or {})
    return assets.__getitem__


class FormulaTagTests(unittest.TestCase):
    def test_reads_binary_and_legacy_source_formulae(self):
        self.assertEqual(formula_tag(binary_formula("v0.2.0")), "v0.2.0")
        self.assertEqual(formula_tag(legacy_formula("v0.1.1")), "v0.1.1")

    def test_rejects_a_formula_with_no_release(self):
        with self.assertRaises(ValueError):
            formula_tag('class PolarisCode < Formula\n  url "https://example.com/x.tar.gz"\nend\n')


class VerifyTests(unittest.TestCase):
    def test_accepts_matching_archives(self):
        verify(binary_formula(), "v0.2.0", fetch=release())

    def test_rejects_an_archive_whose_bytes_changed(self):
        with self.assertRaisesRegex(ValueError, "does not match its checksum"):
            verify(binary_formula(), "v0.2.0", fetch=release(linux=b"tampered"))

    def test_rejects_a_checksum_that_differs_from_the_published_file(self):
        text = binary_formula(mac_sha="b" * 64)
        with self.assertRaisesRegex(ValueError, "differs from the published"):
            verify(text, "v0.2.0", fetch=release())

    def test_rejects_urls_outside_the_release(self):
        text = binary_formula(base="https://example.com/")
        with self.assertRaisesRegex(ValueError, "not an archive of release"):
            verify(text, "v0.2.0", fetch=release())

    def test_rejects_a_version_that_differs_from_the_tag(self):
        with self.assertRaisesRegex(ValueError, "does not match release"):
            verify(binary_formula("v0.2.1"), "v0.2.0", fetch=release())

    def test_rejects_a_url_without_a_checksum(self):
        text = binary_formula().replace(f'      sha256 "{digest(MAC)}"\n', "", 1)
        with self.assertRaisesRegex(ValueError, "followed by its SHA-256"):
            verify(text, "v0.2.0", fetch=release())

    def test_rejects_bottles(self):
        text = binary_formula().replace("end\n", "  bottle do\n  end\nend\n", 1)
        with self.assertRaisesRegex(ValueError, "bottles"):
            verify(text, "v0.2.0", fetch=release())


class ResolveTests(unittest.TestCase):
    def test_a_newer_release_replaces_the_legacy_source_formula(self):
        staged = resolve(legacy_formula("v0.1.1"), "v0.2.0", fetch=release())
        self.assertEqual(staged, binary_formula("v0.2.0"))

    def test_an_older_release_never_rolls_back_the_formula(self):
        def unreachable(url):
            raise AssertionError(f"fetched {url}")

        self.assertIsNone(resolve(binary_formula("v0.2.0"), "v0.1.9", fetch=unreachable))

    def test_an_unchanged_formula_is_not_republished_unless_forced(self):
        current = binary_formula("v0.2.0")
        self.assertIsNone(resolve(current, "v0.2.0", fetch=release()))
        self.assertEqual(resolve(current, "v0.2.0", force=True, fetch=release()), current)

    def test_a_bad_release_formula_is_refused(self):
        with self.assertRaises(ValueError):
            resolve(legacy_formula(), "v0.2.0", fetch=release(mac=b"tampered"))


if __name__ == "__main__":
    unittest.main()
