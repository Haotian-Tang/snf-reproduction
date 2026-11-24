"""Failure-path checks for immutable inputs and label-invariant validation."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from fetch_data import download, extract_member, inputs, verify
from validate_results import partition_hash


class IntegrityTests(unittest.TestCase):
    def test_existing_corrupt_input_is_rejected_without_overwriting(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "input.zip"
            target.write_bytes(b"corrupt")
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                download("https://example.invalid/input.zip", target, "0" * 64)
            self.assertEqual(target.read_bytes(), b"corrupt")

    def test_corrupt_download_is_not_promoted_to_original(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "input.zip"
            with patch("urllib.request.urlopen", return_value=io.BytesIO(b"truncated")):
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    download("https://example.invalid/input.zip", target, "0" * 64)
            self.assertFalse(target.exists())
            self.assertFalse(target.with_suffix(".zip.partial").exists())

    def test_only_the_named_archive_member_is_extracted_and_protected(self):
        with tempfile.TemporaryDirectory() as d:
            archive_path = Path(d) / "source.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("Breast/expected.txt", b"checked data")
                archive.writestr("../../unexpected.txt", b"do not extract")
            target = Path(d) / "raw/expected.txt"
            digest = hashlib.sha256(b"checked data").hexdigest()
            with zipfile.ZipFile(archive_path) as archive:
                extract_member(archive, "Breast/expected.txt", target, digest)
                extract_member(archive, "Breast/expected.txt", target, digest)
            verify(target, digest)
            self.assertEqual(target.stat().st_mode & 0o222, 0)
            self.assertEqual(sorted(p.name for p in target.parent.iterdir()), ["expected.txt"])

    def test_manifest_cannot_escape_the_raw_directory(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "metadata").mkdir()
            (root / "metadata/inputs.sha256").write_text("0" * 64 + "  data/raw/../../../outside.txt\n")
            with self.assertRaisesRegex(ValueError, "outside data/raw"):
                inputs(root)

    def test_cluster_label_permutations_pass_but_changed_partitions_do_not(self):
        reference = partition_hash(["1", "1", "2", "3", "3"])
        self.assertEqual(reference, partition_hash(["c", "c", "a", "b", "b"]))
        self.assertNotEqual(reference, partition_hash(["c", "a", "c", "b", "b"]))


if __name__ == "__main__":
    unittest.main()
