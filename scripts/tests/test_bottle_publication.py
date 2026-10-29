"""Exercise publication metadata with staged release artifacts."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "prepare-bottles.py"


class BottlePublicationTests(unittest.TestCase):
    def prepare(self, *, revision="prepared-commit", version="0.1.2", corrupt=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifacts = root / "artifacts"
            artifacts.mkdir()
            for tag in ("arm64_sequoia", "x86_64_linux"):
                filename = f"polaris-code-{version}.{tag}.bottle.tar.gz"
                content = f"built binary for {tag}".encode()
                (artifacts / filename).write_bytes(content)
                manifest = {"radiantailabs/tap/polaris-code": {
                    "formula": {"tap_git_revision": revision, "pkg_version": version},
                    "bottle": {
                        "root_url": f"https://github.com/RadiantAILabs/homebrew-tap/releases/download/polaris-code-{version}-bottles-123-1",
                        "tags": {tag: {
                            "filename": filename, "local_filename": filename,
                            "sha256": "0" * 64 if corrupt else hashlib.sha256(content).hexdigest(),
                        }},
                    },
                }}
                (artifacts / f"{tag}.bottle.json").write_text(json.dumps(manifest))
            output = root / "output"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(artifacts), str(root / "assets")],
                env={**os.environ, "GITHUB_SHA": "outdated-event-commit",
                     "BOTTLE_TAP_COMMIT": "prepared-commit", "EXPECTED_VERSION": "0.1.2",
                     "GITHUB_REPOSITORY": "RadiantAILabs/homebrew-tap", "GITHUB_RUN_ID": "123",
                     "GITHUB_RUN_ATTEMPT": "1", "GITHUB_OUTPUT": str(output)},
                capture_output=True, text=True,
            )
            return result, output.read_text() if output.exists() else ""

    def test_queued_event_uses_prepared_commit_and_new_release_version(self):
        result, output = self.prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("version=0.1.2\n", output)
        self.assertIn("release_tag=polaris-code-0.1.2-bottles-123-1\n", output)

    def test_bottle_from_the_outdated_event_is_rejected(self):
        result, output = self.prepare(revision="outdated-event-commit")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different tap commit", result.stderr)
        self.assertEqual(output, "")

    def test_bottle_from_another_application_version_is_rejected(self):
        result, output = self.prepare(version="0.1.1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("prepared application release", result.stderr)
        self.assertEqual(output, "")

    def test_corrupted_binary_is_rejected_before_publication(self):
        result, output = self.prepare(corrupt=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match its checksum", result.stderr)
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()
