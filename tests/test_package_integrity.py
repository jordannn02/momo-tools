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

    def test_strict_integrity_rejects_symlink_to_independent_equal_bytes(self):
        install_root = self.installed_copy()
        relative_path = PUBLIC_PACKAGE_ARTIFACTS[0]
        installed_path = install_root / "plugin" / relative_path
        independent_path = install_root / "independent-copy"
        shutil.copy2(installed_path, independent_path)
        installed_path.unlink()
        installed_path.symlink_to(independent_path)

        result = self.run_cli(
            "integrity",
            "--installed-root",
            str(install_root),
            "--strict",
        )

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertEqual(
            report["installed_read_errors"],
            [{"path": relative_path, "error": "NonRegularFile"}],
        )
        self.assertIn("installed_artifact_read_error", report["errors"])

    def test_strict_integrity_rejects_symlinked_installed_root_and_plugin_root(self):
        install_root = self.installed_copy()
        root_alias = install_root.parent / "installed-root-alias"
        root_alias.symlink_to(install_root, target_is_directory=True)

        root_result = self.run_cli(
            "integrity",
            "--installed-root",
            str(root_alias),
            "--strict",
        )

        self.assertEqual(1, root_result.returncode, root_result.stderr)
        root_report = json.loads(root_result.stdout)
        self.assertFalse(root_report["ok"])
        self.assertIn("installed_root_is_symlink", root_report["errors"])

        plugin_container = install_root.parent / "plugin-root-container"
        plugin_container.mkdir()
        (plugin_container / "plugin").symlink_to(
            install_root / "plugin",
            target_is_directory=True,
        )
        plugin_result = self.run_cli(
            "integrity",
            "--installed-root",
            str(plugin_container),
            "--strict",
        )

        self.assertEqual(1, plugin_result.returncode, plugin_result.stderr)
        plugin_report = json.loads(plugin_result.stdout)
        self.assertFalse(plugin_report["ok"])
        self.assertIn("installed_plugin_root_is_symlink", plugin_report["errors"])

        nested_root = self.installed_copy()
        scripts_path = nested_root / "plugin" / "scripts"
        real_scripts = nested_root / "plugin" / "real-scripts"
        scripts_path.rename(real_scripts)
        scripts_path.symlink_to(real_scripts, target_is_directory=True)
        nested_result = self.run_cli(
            "integrity",
            "--installed-root",
            str(nested_root),
            "--strict",
        )

        self.assertEqual(1, nested_result.returncode, nested_result.stderr)
        nested_report = json.loads(nested_result.stdout)
        self.assertFalse(nested_report["ok"])
        self.assertIn(
            {"path": "scripts/momo-tools", "error": "UnsafePathComponent"},
            nested_report["installed_read_errors"],
        )

    def test_artifact_hash_rejects_file_changed_during_read(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "artifact"
        path.write_bytes(b"stable-before-hash\n")
        original_sha256_stream = self.cli.sha256_stream

        def mutate_after_hash(stream):
            digest = original_sha256_stream(stream)
            path.write_bytes(b"changed-after-hash-with-a-different-size\n")
            return digest

        with mock.patch.object(
            self.cli,
            "sha256_stream",
            side_effect=mutate_after_hash,
        ):
            with self.assertRaises(self.cli.UnstableFile):
                self.cli.regular_file_identity_and_sha256(path)

    def test_artifact_hash_rejects_atomic_path_replacement(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name)
        path = root / "artifact"
        replacement = root / "replacement"
        path.write_bytes(b"trusted-before-hash\n")
        replacement.write_bytes(b"replaced-after-hash\n")
        original_sha256_stream = self.cli.sha256_stream

        def replace_path_after_hash(stream):
            digest = original_sha256_stream(stream)
            replacement.replace(path)
            return digest

        with mock.patch.object(
            self.cli,
            "sha256_stream",
            side_effect=replace_path_after_hash,
        ):
            with self.assertRaises(self.cli.UnstableFile):
                self.cli.regular_file_identity_and_sha256(path)

    def test_integrity_rejects_directory_swap_after_precheck(self):
        install_root = self.installed_copy()
        plugin_root = install_root / "plugin"
        scripts_path = plugin_root / "scripts"
        real_scripts = plugin_root / "real-scripts"
        original_safe_directory_chain = self.cli.safe_directory_chain
        swapped = False

        def swap_after_precheck(root, relative_path):
            nonlocal swapped
            result = original_safe_directory_chain(root, relative_path)
            if (
                not swapped
                and Path(root) == plugin_root
                and relative_path == "scripts/momo-tools"
            ):
                scripts_path.rename(real_scripts)
                scripts_path.symlink_to(real_scripts, target_is_directory=True)
                swapped = True
            return result

        with mock.patch.object(
            self.cli,
            "safe_directory_chain",
            side_effect=swap_after_precheck,
        ):
            report = self.cli.integrity_report(install_root, strict=True)

        self.assertTrue(swapped)
        self.assertFalse(report["ok"])
        self.assertIn(
            {"path": "scripts/momo-tools", "error": "UnsafePathComponent"},
            report["installed_read_errors"],
        )

    def test_artifact_hash_rejects_directory_swap_during_descriptor_traversal(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        root = Path(temp_dir.name) / "plugin"
        scripts_path = root / "scripts"
        moved_scripts = root / "moved-scripts"
        scripts_path.mkdir(parents=True)
        (scripts_path / "momo-tools").write_bytes(b"trusted artifact\n")
        original_open = os.open
        swapped = False

        def swap_after_component_open(path, flags, *args, **kwargs):
            nonlocal swapped
            descriptor = original_open(path, flags, *args, **kwargs)
            if (
                not swapped
                and path == "scripts"
                and kwargs.get("dir_fd") is not None
            ):
                scripts_path.rename(moved_scripts)
                scripts_path.symlink_to(moved_scripts, target_is_directory=True)
                swapped = True
            return descriptor

        with mock.patch.object(
            self.cli.os,
            "open",
            side_effect=swap_after_component_open,
        ):
            with self.assertRaises(self.cli.UnsafePathComponent):
                self.cli.regular_file_identity_and_sha256_at(
                    root, "scripts/momo-tools"
                )

        self.assertTrue(swapped)

    def test_integrity_reports_installed_open_errors_without_traceback(self):
        install_root = self.installed_copy()
        failed_relative_path = PUBLIC_PACKAGE_ARTIFACTS[0]
        installed_plugin_root = install_root / "plugin"
        original_read = self.cli.regular_file_identity_and_sha256_at

        def fail_one_installed_artifact(root, relative_path):
            if (
                Path(root) == installed_plugin_root
                and relative_path == failed_relative_path
            ):
                raise OSError("fixture installed read failure")
            return original_read(root, relative_path)

        with mock.patch.object(
            self.cli,
            "regular_file_identity_and_sha256_at",
            side_effect=fail_one_installed_artifact,
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
