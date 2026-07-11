import hashlib
import importlib.machinery
import importlib.util
import json
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


def load_cli_module():
    loader = importlib.machinery.SourceFileLoader(
        "momo_tools_public_doctor", str(CLI)
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class PublicDoctorCliTests(unittest.TestCase):
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

    def temporary_file(self, name, content):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / name
        path.write_text(content, encoding="utf-8")
        return path

    def installed_copy(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        install_root = Path(temp_dir.name) / "installed"
        shutil.copytree(PLUGIN, install_root / "plugin")
        return install_root

    def test_healthy_doctor_has_stable_read_only_public_contract(self):
        install_root = self.installed_copy()
        result = self.run_cli(
            "doctor",
            "--as-of",
            AS_OF,
            "--evidence",
            str(EVIDENCE),
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            {
                "schema_version",
                "command",
                "read_only",
                "health_status",
                "as_of",
                "public_scope",
                "index_path",
                "installed_root",
                "checks",
                "findings",
                "capability_execution",
                "external_calls",
                "network_calls",
                "browser_calls",
                "connector_calls",
                "write_scope",
                "evidence_boundary",
            },
            set(report),
        )
        self.assertEqual("doctor", report["command"])
        self.assertEqual("ok", report["health_status"])
        self.assertTrue(report["read_only"])
        self.assertTrue(report["public_scope"])
        self.assertEqual(
            {
                "index_validation",
                "routing_regression",
                "evidence_freshness",
                "package_integrity",
            },
            set(report["checks"]),
        )
        self.assertEqual([], report["findings"])
        self.assertFalse(report["capability_execution"])
        self.assertFalse(report["external_calls"])
        self.assertFalse(report["network_calls"])
        self.assertFalse(report["browser_calls"])
        self.assertFalse(report["connector_calls"])
        self.assertEqual("none", report["write_scope"])

    def test_doctor_never_runs_recovery_or_an_indexed_capability(self):
        with mock.patch.object(
            self.cli,
            "recovery_drill_report",
            side_effect=AssertionError("doctor must not run recovery"),
        ):
            report = self.cli.build_doctor_report(as_of=AS_OF)

        self.assertEqual("ok", report["health_status"])
        self.assertFalse(report["capability_execution"])
        self.assertFalse(report["external_calls"])
        self.assertNotIn("recovery_drill", report["checks"])

    def test_non_strict_doctor_is_diagnostic_and_strict_fails_invalid_index(self):
        invalid_index = self.temporary_file("invalid-index.json", '[{"name": "broken"}]\n')

        diagnostic = self.run_cli(
            "--index",
            str(invalid_index),
            "doctor",
            "--as-of",
            AS_OF,
            "--json",
        )
        strict = self.run_cli(
            "--index",
            str(invalid_index),
            "doctor",
            "--as-of",
            AS_OF,
            "--json",
            "--strict",
        )

        self.assertEqual(0, diagnostic.returncode, diagnostic.stderr)
        self.assertEqual(1, strict.returncode, strict.stderr)
        report = json.loads(strict.stdout)
        self.assertEqual("failed", report["health_status"])
        self.assertIn(
            "index-validation",
            {finding["category"] for finding in report["findings"]},
        )

    def test_malformed_index_rows_fail_closed_without_traceback(self):
        install_root = self.installed_copy()
        malformed_index = self.temporary_file("malformed-index.json", "[null]\n")
        commands = (
            (
                "doctor",
                "--as-of",
                AS_OF,
                "--installed-root",
                str(install_root),
                "--json",
                "--strict",
            ),
            (
                "repair-plan",
                "--dry-run",
                "--as-of",
                AS_OF,
                "--installed-root",
                str(install_root),
                "--json",
                "--strict",
            ),
        )
        for command in commands:
            with self.subTest(command=command[0]):
                result = self.run_cli(
                    "--index",
                    str(malformed_index),
                    *command,
                )
                self.assertEqual(1, result.returncode, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                report = json.loads(result.stdout)
                if command[0] == "doctor":
                    self.assertEqual("failed", report["health_status"])
                    self.assertIn(
                        "probe-error",
                        {finding["category"] for finding in report["findings"]},
                    )
                else:
                    self.assertEqual("failed", report["source_health_status"])
                    self.assertGreater(report["action_count"], 0)

    def test_expired_evidence_degrades_doctor_without_extending_timestamp(self):
        install_root = self.installed_copy()
        evidence = self.temporary_file(
            "expired.jsonl",
            json.dumps(
                {
                    "capability": "synthetic-capability",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-01T00:00:00+00:00",
                    "valid_until": "2026-07-02T00:00:00+00:00",
                    "command": "synthetic fixture",
                    "evidence_ref": "synthetic://fixture",
                    "risk_boundary": "synthetic only",
                }
            )
            + "\n",
        )

        result = self.run_cli(
            "doctor",
            "--as-of",
            AS_OF,
            "--evidence",
            str(evidence),
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(1, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("degraded", report["health_status"])
        self.assertEqual(
            ["expired-evidence"],
            [finding["category"] for finding in report["findings"]],
        )
        self.assertEqual(
            "expired",
            report["findings"][0]["details"]["freshness"],
        )

    def test_failed_verified_working_evidence_cannot_be_healthy_or_no_op(self):
        install_root = self.installed_copy()
        evidence = self.temporary_file(
            "failed-status.jsonl",
            json.dumps(
                {
                    "capability": "failed-check",
                    "level": "verified-working",
                    "status": "failed",
                    "checked_at": "2026-07-10T10:00:00+00:00",
                    "valid_until": "2026-07-10T13:00:00+00:00",
                    "command": "synthetic failing fixture",
                    "evidence_ref": "synthetic://failed",
                    "risk_boundary": "synthetic only",
                }
            )
            + "\n",
        )
        common = (
            "--as-of",
            AS_OF,
            "--evidence",
            str(evidence),
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        doctor = self.run_cli("doctor", *common)
        repair = self.run_cli("repair-plan", "--dry-run", *common)

        self.assertEqual(1, doctor.returncode, doctor.stderr)
        doctor_report = json.loads(doctor.stdout)
        self.assertEqual("degraded", doctor_report["health_status"])
        self.assertIn(
            "invalid-evidence",
            {finding["category"] for finding in doctor_report["findings"]},
        )
        self.assertEqual(1, repair.returncode, repair.stderr)
        repair_report = json.loads(repair.stdout)
        self.assertNotEqual("no-op", repair_report["plan_status"])
        self.assertGreater(repair_report["action_count"], 0)

    def test_empty_or_malformed_route_case_collections_fail_closed(self):
        install_root = self.installed_copy()
        fixtures = (
            self.temporary_file("empty-cases.json", "[]\n"),
            self.temporary_file("object-cases.json", "{}\n"),
            self.temporary_file("null-row-cases.json", "[null]\n"),
            self.temporary_file(
                "assertionless-cases.json",
                '[{"id":"no-assertions","prompt":"unrelated words"}]\n',
            ),
            self.temporary_file(
                "blank-expected.json",
                '[{"id":"blank-expected","prompt":"unrelated words","expected":["  "]}]\n',
            ),
            self.temporary_file(
                "blank-forbidden.json",
                '[{"id":"blank-forbidden","prompt":"unrelated words","forbidden":[""]}]\n',
            ),
            self.temporary_file(
                "blank-must-gate.json",
                '[{"id":"blank-must-gate","prompt":"unrelated words","must_gate":["   "]}]\n',
            ),
        )
        for fixture in fixtures:
            for option in ("--cases", "--benchmark-cases"):
                with self.subTest(fixture=fixture.name, option=option):
                    result = self.run_cli(
                        "doctor",
                        "--as-of",
                        AS_OF,
                        "--installed-root",
                        str(install_root),
                        option,
                        str(fixture),
                        "--json",
                        "--strict",
                    )
                    self.assertEqual(1, result.returncode, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    report = json.loads(result.stdout)
                    self.assertEqual("failed", report["health_status"])
                    self.assertIn(
                        "probe-error",
                        {finding["category"] for finding in report["findings"]},
                    )

    def test_doctor_fails_closed_for_missing_probe_input_without_traceback(self):
        install_root = self.installed_copy()
        missing = REPO / "tests" / "fixtures" / "does-not-exist.jsonl"

        result = self.run_cli(
            "doctor",
            "--as-of",
            AS_OF,
            "--evidence",
            str(missing),
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(1, result.returncode, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("failed", report["health_status"])
        finding = next(
            item for item in report["findings"] if item["category"] == "probe-error"
        )
        self.assertEqual("evidence_freshness", finding["subject"])

    def test_strict_doctor_requires_explicit_independent_installed_root(self):
        result = self.run_cli(
            "doctor",
            "--as-of",
            AS_OF,
            "--json",
            "--strict",
        )

        self.assertEqual(1, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("failed", report["health_status"])
        self.assertIn(
            "installed-root-required",
            {finding["category"] for finding in report["findings"]},
        )

    def test_invalid_as_of_is_a_usage_error_without_traceback(self):
        result = self.run_cli(
            "doctor",
            "--as-of",
            "2026-07-10",
            "--json",
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("timezone", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_doctor_surfaces_explicit_installed_copy_mismatch(self):
        install_root = self.installed_copy()
        target = install_root / "plugin" / "capabilities.example.json"
        target.write_text('{"corrupted": true}\n', encoding="utf-8")

        result = self.run_cli(
            "doctor",
            "--as-of",
            AS_OF,
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(1, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("failed", report["health_status"])
        self.assertIn(
            "installed-mismatch",
            {finding["category"] for finding in report["findings"]},
        )


class PublicRepairPlanTests(unittest.TestCase):
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

    def doctor_report(self, findings=None, health_status="ok", installed_root=None):
        return {
            "schema_version": 1,
            "command": "doctor",
            "read_only": True,
            "health_status": health_status,
            "public_scope": True,
            "installed_root": installed_root,
            "findings": list(findings or []),
            "capability_execution": False,
            "external_calls": False,
            "network_calls": False,
            "browser_calls": False,
            "connector_calls": False,
            "write_scope": "none",
        }

    def finding(
        self,
        finding_id,
        category,
        severity="failed",
        subject="fixture",
        details=None,
    ):
        return {
            "id": finding_id,
            "severity": severity,
            "category": category,
            "subject": subject,
            "details": dict(details or {}),
            "repair_code": category,
        }

    def test_repair_plan_requires_explicit_dry_run(self):
        result = self.run_cli("repair-plan", "--json")

        self.assertEqual(2, result.returncode)
        self.assertIn("requires --dry-run", result.stderr)

    def test_healthy_repair_plan_is_stable_read_only_no_op(self):
        install_root = self.installed_copy()
        result = self.run_cli(
            "repair-plan",
            "--dry-run",
            "--as-of",
            AS_OF,
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            {
                "schema_version",
                "command",
                "mode",
                "dry_run",
                "read_only",
                "applied",
                "source_health_status",
                "plan_status",
                "source_finding_count",
                "action_count",
                "blocked_count",
                "actions",
                "write_operations_executed",
                "evidence_boundary",
            },
            set(report),
        )
        self.assertEqual("repair-plan", report["command"])
        self.assertEqual("dry-run", report["mode"])
        self.assertEqual("no-op", report["plan_status"])
        self.assertEqual([], report["actions"])
        self.assertFalse(report["applied"])
        self.assertEqual(0, report["write_operations_executed"])

    def test_every_finding_maps_deterministically_and_unknown_is_blocked(self):
        findings = [
            self.finding("doctor-002", "future-category", subject="future"),
            self.finding(
                "doctor-001",
                "expired-evidence",
                severity="degraded",
                subject="synthetic-capability",
            ),
        ]
        source = self.doctor_report(findings, health_status="failed")

        first = self.cli.build_repair_plan(source, dry_run=True)
        second = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual(first, second)
        self.assertEqual(2, first["source_finding_count"])
        self.assertEqual(2, first["action_count"])
        self.assertEqual(
            {"doctor-001", "doctor-002"},
            {action["finding_id"] for action in first["actions"]},
        )
        unknown = next(
            action for action in first["actions"] if action["finding_id"] == "doctor-002"
        )
        self.assertEqual("blocked-manual-review", unknown["action_type"])
        self.assertEqual("blocked", first["plan_status"])
        self.assertTrue(all(not action["auto_applicable"] for action in first["actions"]))
        self.assertTrue(
            all(action["requires_explicit_authorization"] for action in first["actions"])
        )
        self.assertTrue(
            all(
                set(action)
                == {
                    "id",
                    "finding_id",
                    "priority",
                    "action_type",
                    "target",
                    "reason",
                    "procedure",
                    "verification_commands",
                    "auto_applicable",
                    "requires_explicit_authorization",
                }
                for action in first["actions"]
            )
        )

    def test_inconsistent_failed_doctor_cannot_produce_no_op(self):
        source = self.doctor_report([], health_status="failed")

        report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual("blocked", report["plan_status"])
        self.assertEqual(1, report["action_count"])
        self.assertEqual("blocked-inconsistent-doctor", report["actions"][0]["action_type"])

    def test_malformed_finding_and_external_boundary_claim_fail_closed(self):
        malformed = self.doctor_report([None], health_status="failed")
        external = self.doctor_report([], health_status="ok")
        external["network_calls"] = True

        for source in (malformed, external):
            with self.subTest(source=source):
                report = self.cli.build_repair_plan(source, dry_run=True)
                self.assertEqual("blocked", report["plan_status"])
                self.assertEqual(1, report["action_count"])
                self.assertEqual(
                    "blocked-inconsistent-doctor",
                    report["actions"][0]["action_type"],
                )

    def test_installed_mismatch_requires_explicit_installed_root_and_canonical_hash(self):
        finding = self.finding(
            "doctor-001",
            "installed-mismatch",
            subject="capabilities.example.json",
            details={
                "path": "capabilities.example.json",
                "expected_sha256": "a" * 64,
            },
        )
        source = self.doctor_report([finding], health_status="failed", installed_root=None)

        report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual("blocked", report["plan_status"])
        self.assertEqual("blocked-canonical-unproven", report["actions"][0]["action_type"])

    def test_forged_canonical_hash_is_blocked_even_with_existing_installed_root(self):
        install_root = self.installed_copy()
        target = install_root / "plugin" / "capabilities.example.json"
        target.write_text('{"corrupted": true}\n', encoding="utf-8")
        finding = self.finding(
            "doctor-001",
            "installed-mismatch",
            subject="capabilities.example.json",
            details={
                "path": "capabilities.example.json",
                "expected_sha256": "a" * 64,
            },
        )
        source = self.doctor_report(
            [finding],
            health_status="failed",
            installed_root=str(install_root),
        )

        report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual("blocked", report["plan_status"])
        self.assertEqual("blocked-canonical-unproven", report["actions"][0]["action_type"])

    def test_missing_target_directory_swap_is_blocked(self):
        install_root = self.installed_copy()
        plugin_root = install_root / "plugin"
        relative_path = "scripts/momo-tools"
        target = plugin_root / relative_path
        scripts_path = plugin_root / "scripts"
        moved_scripts = plugin_root / "moved-scripts"
        target.unlink()
        expected_sha256 = hashlib.sha256(
            (PLUGIN / relative_path).read_bytes()
        ).hexdigest()
        finding = self.finding(
            "doctor-001",
            "installed-missing",
            subject=relative_path,
            details={
                "path": relative_path,
                "expected_sha256": expected_sha256,
            },
        )
        source = self.doctor_report(
            [finding],
            health_status="failed",
            installed_root=str(install_root),
        )
        original_safe_directory_chain = self.cli.safe_directory_chain
        swapped = False

        def swap_after_precheck(root, checked_relative_path):
            nonlocal swapped
            result = original_safe_directory_chain(root, checked_relative_path)
            if (
                not swapped
                and Path(root) == plugin_root
                and checked_relative_path == relative_path
            ):
                scripts_path.rename(moved_scripts)
                scripts_path.symlink_to(moved_scripts, target_is_directory=True)
                swapped = True
            return result

        with mock.patch.object(
            self.cli,
            "safe_directory_chain",
            side_effect=swap_after_precheck,
        ):
            report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertTrue(swapped)
        self.assertEqual("blocked", report["plan_status"])
        self.assertEqual(
            "blocked-canonical-unproven",
            report["actions"][0]["action_type"],
        )

    def test_stably_missing_target_has_advisory_plan(self):
        install_root = self.installed_copy()
        relative_path = "scripts/momo-tools"
        (install_root / "plugin" / relative_path).unlink()
        expected_sha256 = hashlib.sha256(
            (PLUGIN / relative_path).read_bytes()
        ).hexdigest()
        finding = self.finding(
            "doctor-001",
            "installed-missing",
            subject=relative_path,
            details={
                "path": relative_path,
                "expected_sha256": expected_sha256,
            },
        )
        source = self.doctor_report(
            [finding],
            health_status="failed",
            installed_root=str(install_root),
        )

        report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual("ready", report["plan_status"])
        self.assertEqual(
            "advisory-reinstall-from-verified-release",
            report["actions"][0]["action_type"],
        )

    def test_missing_target_proof_rechecks_open_directory_chain(self):
        install_root = self.installed_copy()
        plugin_root = install_root / "plugin"
        relative_path = "scripts/momo-tools"
        scripts_path = plugin_root / "scripts"
        moved_scripts = plugin_root / "moved-scripts"
        (plugin_root / relative_path).unlink()
        original_open = self.cli.os.open
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
                self.cli.missing_file_is_stable_at(plugin_root, relative_path)

        self.assertTrue(swapped)

    def test_expired_evidence_only_recommends_bounded_reverification(self):
        finding = self.finding(
            "doctor-001",
            "expired-evidence",
            severity="degraded",
            subject="synthetic-capability",
        )
        source = self.doctor_report([finding], health_status="degraded")

        report = self.cli.build_repair_plan(source, dry_run=True)

        action = report["actions"][0]
        self.assertEqual("rerun-safe-verification", action["action_type"])
        procedure = action["procedure"].lower()
        self.assertNotIn("extend", procedure)
        self.assertNotIn("promote", procedure)
        self.assertNotIn("timestamp", procedure)

    def test_repair_plan_does_not_modify_mismatched_installed_artifact(self):
        install_root = self.installed_copy()
        target = install_root / "plugin" / "capabilities.example.json"
        target.write_text('{"corrupted": true}\n', encoding="utf-8")
        before = target.read_bytes()

        result = self.run_cli(
            "repair-plan",
            "--dry-run",
            "--as-of",
            AS_OF,
            "--installed-root",
            str(install_root),
            "--json",
        )

        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        action = next(
            item
            for item in report["actions"]
            if item["action_type"] == "advisory-reinstall-from-verified-release"
        )
        self.assertEqual("capabilities.example.json", action["target"])
        self.assertFalse(report["applied"])
        self.assertEqual(0, report["write_operations_executed"])
        self.assertEqual(before, target.read_bytes())

    def test_unsafe_artifact_finding_is_always_blocked(self):
        finding = self.finding(
            "doctor-001",
            "installed-unsafe",
            subject="capabilities.example.json",
            details={"path": "capabilities.example.json", "error": "NonRegularFile"},
        )
        source = self.doctor_report(
            [finding],
            health_status="failed",
            installed_root="/explicit/fixture",
        )

        report = self.cli.build_repair_plan(source, dry_run=True)

        self.assertEqual("blocked", report["plan_status"])
        self.assertEqual("blocked-unsafe-artifact", report["actions"][0]["action_type"])

    def test_strict_repair_plan_fails_when_source_health_is_not_ok(self):
        install_root = self.installed_copy()
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        invalid_index = Path(temp_dir.name) / "invalid-index.json"
        invalid_index.write_text('[{"name": "broken"}]\n', encoding="utf-8")

        diagnostic = self.run_cli(
            "--index",
            str(invalid_index),
            "repair-plan",
            "--dry-run",
            "--as-of",
            AS_OF,
            "--installed-root",
            str(install_root),
            "--json",
        )
        strict = self.run_cli(
            "--index",
            str(invalid_index),
            "repair-plan",
            "--dry-run",
            "--as-of",
            AS_OF,
            "--installed-root",
            str(install_root),
            "--json",
            "--strict",
        )

        self.assertEqual(0, diagnostic.returncode, diagnostic.stderr)
        self.assertEqual(1, strict.returncode, strict.stderr)
        report = json.loads(strict.stdout)
        self.assertNotEqual("ok", report["source_health_status"])
        self.assertGreater(report["action_count"], 0)
        self.assertFalse(report["applied"])
        self.assertEqual(0, report["write_operations_executed"])


if __name__ == "__main__":
    unittest.main()
