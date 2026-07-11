import hashlib
import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugin"
CLI = PLUGIN / "scripts" / "momo-tools"
EVIDENCE = REPO / "evidence" / "example-verification.jsonl"
AS_OF = "2026-07-10T12:00:00+00:00"
PUBLIC_PACKAGE_ARTIFACTS = (
    ".codex-plugin/plugin.json",
    "capabilities.example.json",
    "capabilities.example.yaml",
    "scripts/momo-tools",
    "skills/momo-tools/SKILL.md",
)


def load_cli_module():
    loader = importlib.machinery.SourceFileLoader(
        "momo_tools_public_integrity", str(CLI)
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class PublicTrustLifecycleCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = load_cli_module()

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

    def installed_artifact_aliases(self, link_kind):
        temp_dir = tempfile.TemporaryDirectory(dir=REPO)
        self.addCleanup(temp_dir.cleanup)
        install_root = Path(temp_dir.name) / "installed"
        for relative_path in PUBLIC_PACKAGE_ARTIFACTS:
            source = PLUGIN / relative_path
            installed = install_root / "plugin" / relative_path
            installed.parent.mkdir(parents=True, exist_ok=True)
            if link_kind == "symlink":
                installed.symlink_to(source)
            else:
                os.link(source, installed)
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

    def test_strict_integrity_rejects_per_artifact_source_aliases(self):
        for link_kind in ("symlink", "hardlink"):
            with self.subTest(link_kind=link_kind):
                install_root = self.installed_artifact_aliases(link_kind)

                result = self.run_cli("integrity", "--installed-root", str(install_root), "--strict")

                self.assertEqual(result.returncode, 1, result.stderr)
                report = json.loads(result.stdout)
                self.assertFalse(report["ok"])
                self.assertEqual(report["source_aliases"], list(PUBLIC_PACKAGE_ARTIFACTS))
                self.assertIn("installed_artifacts_are_canonical_source_aliases", report["errors"])

    def test_integrity_reports_installed_open_errors_without_traceback(self):
        install_root = self.installed_copy()
        failed_relative_path = PUBLIC_PACKAGE_ARTIFACTS[0]
        failed_path = install_root / "plugin" / failed_relative_path
        original_open = os.open

        def fail_one_installed_artifact(path, *args, **kwargs):
            if Path(path) == failed_path:
                raise OSError("fixture installed read failure")
            return original_open(path, *args, **kwargs)

        with mock.patch.object(
            self.cli.os, "open", side_effect=fail_one_installed_artifact
        ):
            report = self.cli.integrity_report(install_root, strict=True)

        self.assertFalse(report["ok"])
        self.assertFalse(report["installed_matches"])
        self.assertEqual(
            report["installed_read_errors"],
            [{"path": failed_relative_path, "error": "OSError"}],
        )
        self.assertIn("installed_artifact_read_error", report["errors"])

    def test_integrity_rejects_fifo_without_blocking(self):
        install_root = self.installed_copy()
        fifo_relative_path = PUBLIC_PACKAGE_ARTIFACTS[1]
        fifo_path = install_root / "plugin" / fifo_relative_path
        fifo_path.unlink()
        os.mkfifo(fifo_path)

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "integrity",
                    "--installed-root",
                    str(install_root),
                    "--strict",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
                timeout=1,
            )
        except subprocess.TimeoutExpired:
            self.fail("strict integrity blocked while opening an installed FIFO")

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertEqual(
            report["installed_read_errors"],
            [{"path": fifo_relative_path, "error": "NonRegularFile"}],
        )
        self.assertIn("installed_artifact_read_error", report["errors"])

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
