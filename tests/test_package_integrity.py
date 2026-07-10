import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugin"
CLI = PLUGIN / "scripts" / "momo-tools"
EVIDENCE = REPO / "evidence" / "example-verification.jsonl"
AS_OF = "2026-07-10T12:00:00+00:00"


class PublicTrustLifecycleCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )

    def installed_copy(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        install_root = Path(temp_dir.name) / "installed"
        shutil.copytree(PLUGIN, install_root / "plugin")
        return install_root

    def test_integrity_strict_accepts_matching_public_install_and_rejects_corruption(self):
        install_root = self.installed_copy()

        matching = self.run_cli("integrity", "--installed-root", str(install_root), "--strict")

        self.assertEqual(matching.returncode, 0, matching.stderr)
        matching_report = json.loads(matching.stdout)
        self.assertTrue(matching_report["ok"])
        self.assertTrue(matching_report["installed_matches"])
        self.assertEqual(matching_report["missing"], [])
        self.assertEqual(matching_report["mismatched"], [])
        self.assertGreater(len(matching_report["manifest"]), 1)

        target = install_root / "plugin" / "capabilities.example.json"
        target.write_text('{"corrupted": true}\n', encoding="utf-8")
        corrupted = self.run_cli("integrity", "--installed-root", str(install_root), "--strict")

        self.assertEqual(corrupted.returncode, 1, corrupted.stderr)
        corrupted_report = json.loads(corrupted.stdout)
        self.assertFalse(corrupted_report["ok"])
        self.assertIn("capabilities.example.json", corrupted_report["mismatched"])

    def test_strict_integrity_and_slo_require_an_explicit_installed_root(self):
        integrity = self.run_cli("integrity", "--strict")
        slo = self.run_cli(
            "slo",
            "--as-of",
            AS_OF,
            "--evidence",
            str(EVIDENCE),
            "--strict",
        )

        self.assertEqual(integrity.returncode, 1, integrity.stderr)
        integrity_report = json.loads(integrity.stdout)
        self.assertFalse(integrity_report["ok"])
        self.assertIn("installed_root_required", integrity_report["errors"])

        self.assertEqual(slo.returncode, 1, slo.stderr)
        slo_report = json.loads(slo.stdout)
        self.assertFalse(slo_report["ok"])
        self.assertIn("installed_root_required", slo_report["errors"])
        self.assertIn("installed_root_required", slo_report["checks"]["integrity"]["errors"])

    def test_strict_integrity_and_slo_reject_canonical_source_aliases(self):
        for source_alias in ("plugin", "."):
            with self.subTest(source_alias=source_alias):
                integrity = self.run_cli("integrity", "--installed-root", str(source_alias), "--strict")
                slo = self.run_cli(
                    "slo",
                    "--as-of",
                    AS_OF,
                    "--evidence",
                    str(EVIDENCE),
                    "--installed-root",
                    str(source_alias),
                    "--strict",
                )

                integrity_report = json.loads(integrity.stdout)
                slo_report = json.loads(slo.stdout)

                self.assertEqual(integrity.returncode, 1, integrity.stderr)
                self.assertFalse(integrity_report["ok"])
                self.assertIn("installed_root_is_canonical_source", integrity_report["errors"])

                self.assertEqual(slo.returncode, 1, slo.stderr)
                self.assertFalse(slo_report["ok"])
                self.assertIn("installed_root_is_canonical_source", slo_report["errors"])
                self.assertIn(
                    "installed_root_is_canonical_source",
                    slo_report["checks"]["integrity"]["errors"],
                )

    def test_non_strict_integrity_allows_source_only_validation_without_root(self):
        result = self.run_cli("integrity")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertIsNone(report["installed_matches"])
        self.assertFalse(report["installed_copy_checked"])

    def test_recovery_drill_is_temporary_only_and_leaves_source_bytes_unchanged(self):
        source = PLUGIN / "capabilities.example.json"
        source_sha256 = hashlib.sha256(source.read_bytes()).hexdigest()

        result = self.run_cli("recovery-drill", "--strict")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["temporary_only"])
        self.assertTrue(report["source_unchanged"])
        self.assertTrue(report["passed"])
        self.assertEqual(source_sha256, hashlib.sha256(source.read_bytes()).hexdigest())

    def test_slo_strict_aggregates_public_p1_and_p2_checks_without_install_claims(self):
        install_root = self.installed_copy()

        result = self.run_cli(
            "slo",
            "--as-of",
            AS_OF,
            "--evidence",
            str(EVIDENCE),
            "--installed-root",
            str(install_root),
            "--strict",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertTrue(report["public_scope"])
        self.assertIn("real_installation_protected", report["limitations"])
        self.assertFalse(report["limitations"]["real_installation_protected"])
        self.assertEqual(
            set(report["checks"]),
            {"validate", "audit", "benchmark", "pressure", "freshness", "integrity", "recovery_drill"},
        )
        self.assertTrue(all(check["ok"] for check in report["checks"].values()))


if __name__ == "__main__":
    unittest.main()
