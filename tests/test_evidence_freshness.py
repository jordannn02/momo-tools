import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "plugin" / "scripts" / "momo-tools"
AS_OF = "2026-07-10T12:00:00+00:00"


class EvidenceFreshnessCliTests(unittest.TestCase):
    def run_cli(self, command, evidence, strict=False):
        args = [
            sys.executable,
            str(CLI),
            command,
            "--as-of",
            AS_OF,
            "--evidence",
            str(evidence),
        ]
        if strict:
            args.append("--strict")
        return subprocess.run(args, cwd=REPO, text=True, capture_output=True, check=False)

    def write_evidence(self, records):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        evidence = Path(temp_dir.name) / "evidence.jsonl"
        evidence.write_text(
            "\n".join(json.dumps(record) for record in records) + "\n",
            encoding="utf-8",
        )
        return evidence

    def test_freshness_keeps_only_current_aware_verified_working_evidence(self):
        evidence = self.write_evidence(
            [
                {
                    "capability": "synthetic-check",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-10T10:00:00+00:00",
                    "valid_until": "2026-07-10T13:00:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                }
            ]
        )

        result = self.run_cli("freshness", evidence)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["effective_levels"], {"verified-working": 1})
        self.assertEqual(report["freshness"], {"fresh": 1})
        self.assertEqual(report["records"][0]["raw_level"], "verified-working")
        self.assertEqual(report["records"][0]["effective_level"], "verified-working")

    def test_freshness_degrades_expired_naive_and_malformed_verified_working_evidence(self):
        evidence = self.write_evidence(
            [
                {
                    "capability": "expired-check",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-10T10:00:00+00:00",
                    "valid_until": "2026-07-10T11:00:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                },
                {
                    "capability": "naive-check",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-10T10:00:00",
                    "valid_until": "2026-07-10T13:00:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                },
                {
                    "capability": "malformed-check",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "not-a-timestamp",
                    "valid_until": "2026-07-10T13:00:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                },
            ]
        )

        result = self.run_cli("freshness", evidence)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["levels"], {"verified-working": 3})
        self.assertEqual(report["effective_levels"], {"degraded": 3})
        self.assertEqual(report["freshness"], {"expired": 1, "invalid": 2})
        self.assertEqual(
            [record["effective_level"] for record in report["records"]],
            ["degraded", "degraded", "degraded"],
        )

        strict_result = self.run_cli("freshness", evidence, strict=True)
        self.assertEqual(strict_result.returncode, 1, strict_result.stderr)
        self.assertFalse(json.loads(strict_result.stdout)["ok"])

    def test_freshness_degrades_evidence_checked_after_as_of(self):
        evidence = self.write_evidence(
            [
                {
                    "capability": "future-check",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-10T12:30:00+00:00",
                    "valid_until": "2026-07-10T13:30:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                }
            ]
        )

        result = self.run_cli("freshness", evidence)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["freshness"], {"invalid": 1})
        self.assertEqual(report["records"][0]["raw_level"], "verified-working")
        self.assertEqual(report["records"][0]["effective_level"], "degraded")

        strict_result = self.run_cli("freshness", evidence, strict=True)
        self.assertEqual(strict_result.returncode, 1, strict_result.stderr)

    def test_fresh_verified_working_evidence_with_failed_status_is_invalid(self):
        evidence = self.write_evidence(
            [
                {
                    "capability": "failed-check",
                    "level": "verified-working",
                    "status": "failed",
                    "checked_at": "2026-07-10T10:00:00+00:00",
                    "valid_until": "2026-07-10T13:00:00+00:00",
                    "command": "synthetic failing fixture",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                }
            ]
        )

        result = self.run_cli("freshness", evidence)

        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual({"invalid": 1}, report["freshness"])
        self.assertEqual({"degraded": 1}, report["effective_levels"])
        self.assertIn("status", report["records"][0]["errors"][0])

        strict_result = self.run_cli("freshness", evidence, strict=True)
        self.assertEqual(1, strict_result.returncode, strict_result.stderr)

    def test_evidence_reports_the_same_freshness_summary_and_only_strict_fails(self):
        evidence = self.write_evidence(
            [
                {
                    "capability": "invalid-window",
                    "level": "verified-working",
                    "status": "passed",
                    "checked_at": "2026-07-10T12:00:00+00:00",
                    "valid_until": "2026-07-10T12:00:00+00:00",
                    "command": "python3 -m unittest",
                    "evidence_ref": "tests/test_evidence_freshness.py",
                    "risk_boundary": ["synthetic only"],
                }
            ]
        )

        result = self.run_cli("evidence", evidence)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["freshness"], {"invalid": 1})
        self.assertEqual(report["records"][0]["raw_level"], "verified-working")
        self.assertEqual(report["records"][0]["effective_level"], "degraded")

        strict_result = self.run_cli("evidence", evidence, strict=True)
        self.assertEqual(strict_result.returncode, 1, strict_result.stderr)


if __name__ == "__main__":
    unittest.main()
