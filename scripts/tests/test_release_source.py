"""Tests for safe release selection and atomic formula staging."""

import hashlib
import io
from pathlib import Path
import sys
import tarfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from release_source import ARCHIVE_BASE, resolve, validate_archive
from stage_formula import stage


def archive(version="0.1.2", name="polaris_code", binary="polaris"):
    content = f'[package]\nname = "{name}"\nversion = "{version}"\n\n[[bin]]\nname = "{binary}"\n'.encode()
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as output:
        member = tarfile.TarInfo("source/crates/polaris_code/Cargo.toml")
        member.size = len(content)
        output.addfile(member, io.BytesIO(content))
    return buffer.getvalue()


def formula(checksum="a" * 64):
    return (
        'class PolarisCode < Formula\n'
        f'  url "{ARCHIVE_BASE}v0.1.1.tar.gz"\n'
        f'  sha256 "{checksum}"\n'
        '  bottle do\n    root_url "https://example.com/old-bottles"\n  end\n'
        '  depends_on "rust" => :build\nend\n'
    )


class ReleaseSourceTests(unittest.TestCase):
    def test_new_release_uses_exact_archive_bytes(self):
        content = archive()
        original = formula()
        source, build = resolve(original, "v0.1.2", fetch=lambda _: content)
        self.assertTrue(build)
        self.assertEqual(source.sha256, hashlib.sha256(content).hexdigest())
        self.assertEqual(source.version, "0.1.2")
        self.assertIn("old-bottles", original)

    def test_tag_must_match_the_crate_version(self):
        with self.assertRaisesRegex(ValueError, "crate version"):
            validate_archive(archive("0.1.3"), "v0.1.2")

    def test_crate_and_executable_are_the_public_contract(self):
        for content in (archive(name="another_crate"), archive(binary="polaris-code")):
            with self.subTest(content=content), self.assertRaises(ValueError):
                validate_archive(content, "v0.1.2")

    def test_duplicate_notification_skips_an_existing_bottle(self):
        content = archive("0.1.1")
        current = formula(hashlib.sha256(content).hexdigest())
        self.assertFalse(resolve(current, "v0.1.1", fetch=lambda _: content)[1])
        self.assertTrue(resolve(current, "v0.1.1", True, fetch=lambda _: content)[1])

    def test_an_existing_tag_cannot_change_its_source(self):
        with self.assertRaisesRegex(ValueError, "checksum changed"):
            resolve(formula(), "v0.1.1", fetch=lambda _: archive("0.1.1"))

    def test_delayed_old_release_cannot_roll_back_the_tap(self):
        def unexpected_fetch(_):
            self.fail("An older version should not be downloaded")
        source, build = resolve(formula(), "v0.1.0", True, fetch=unexpected_fetch)
        self.assertFalse(build)
        self.assertEqual(source.tag, "v0.1.1")

    def test_manual_current_version_rebuild_preserves_the_source(self):
        source, build = resolve(formula(), "")
        self.assertTrue(build)
        self.assertEqual(source.tag, "v0.1.1")

    def test_staged_source_has_no_obsolete_bottles_and_keeps_build_behavior(self):
        original = formula()
        updated = stage(original, ARCHIVE_BASE + "v0.1.2.tar.gz", "b" * 64)
        self.assertIn('v0.1.2.tar.gz', updated)
        self.assertIn('sha256 "' + "b" * 64 + '"', updated)
        self.assertNotIn("bottle do", updated)
        self.assertIn('depends_on "rust" => :build', updated)
        self.assertIn("old-bottles", original)

    def test_unexpected_source_urls_and_checksums_are_refused(self):
        for url, checksum in (("https://example.com/v0.1.2.tar.gz", "b"*64), (ARCHIVE_BASE+"v0.1.2.tar.gz", "invalid")):
            with self.subTest(url=url, checksum=checksum), self.assertRaises(ValueError):
                stage(formula(), url, checksum)


if __name__ == "__main__":
    unittest.main()
