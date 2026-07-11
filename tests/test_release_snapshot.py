import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class ReleaseSnapshotContractTests(unittest.TestCase):
    def committed_fixture(self, root, version="9.9.9-test", consumer_versions=None):
        versions = {
            "json": version,
            "yaml": version,
            "release_notes": version,
        }
        versions.update(consumer_versions or {})
        fixture = Path(root) / "repo"
        builder = REPO / "scripts" / "build-release-snapshot.sh"
        (fixture / "scripts").mkdir(parents=True)
        (fixture / "plugin" / ".codex-plugin").mkdir(parents=True)
        shutil.copy2(builder, fixture / "scripts" / builder.name)
        (fixture / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        (fixture / "README.md").write_text("# fixture\n", encoding="utf-8")
        (fixture / "RELEASE_NOTES.md").write_text(
            f"# Release Notes\n\n## v{versions['release_notes']}\n",
            encoding="utf-8",
        )
        (fixture / "plugin" / ".codex-plugin" / "plugin.json").write_text(
            json.dumps({"name": "momo-tools", "version": version}),
            encoding="utf-8",
        )
        (fixture / "plugin" / "capabilities.example.json").write_text(
            json.dumps([{"name": "fixture", "version": versions["json"]}]),
            encoding="utf-8",
        )
        (fixture / "plugin" / "capabilities.example.yaml").write_text(
            f"- name: fixture\n  version: {versions['yaml']}\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "init", "-q"], cwd=fixture, check=True)
        subprocess.run(["git", "add", "."], cwd=fixture, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=MoMo Tools Tests",
                "-c",
                "user.email=tests@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            cwd=fixture,
            check=True,
        )
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=fixture, text=True
        ).strip()
        return fixture, commit, fixture / "scripts" / builder.name

    def test_release_version_is_single_and_consistent(self):
        version_path = REPO / "VERSION"
        self.assertTrue(version_path.is_file(), "VERSION must be the release source of truth")
        version = version_path.read_text(encoding="utf-8").strip()
        self.assertRegex(version, r"^[0-9]+\.[0-9]+\.[0-9]+-public$")

        plugin = json.loads(
            (REPO / "plugin" / ".codex-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        capabilities = json.loads(
            (REPO / "plugin" / "capabilities.example.json").read_text(
                encoding="utf-8"
            )
        )
        yaml_text = (REPO / "plugin" / "capabilities.example.yaml").read_text(
            encoding="utf-8"
        )
        release_notes = (REPO / "RELEASE_NOTES.md").read_text(encoding="utf-8")

        self.assertEqual(version, plugin["version"])
        self.assertEqual(version, capabilities[0]["version"])
        self.assertIn(f"version: {version}", yaml_text)
        self.assertIn(f"## v{version}", release_notes)

    def test_builder_creates_reproducible_snapshot_from_exact_commit(self):
        builder = REPO / "scripts" / "build-release-snapshot.sh"
        self.assertTrue(builder.is_file(), "release snapshot builder is required")

        with tempfile.TemporaryDirectory(prefix="momo-tools-release-fixture-") as tmp:
            fixture, commit, fixture_builder = self.committed_fixture(tmp)

            outputs = []
            for name in ("first", "second"):
                output_dir = fixture / name
                result = subprocess.run(
                    [
                        "bash",
                        str(fixture_builder),
                        "--ref",
                        commit,
                        "--output-dir",
                        str(output_dir),
                    ],
                    cwd=fixture,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    0,
                    result.returncode,
                    f"builder failed:\n{result.stdout}{result.stderr}",
                )
                outputs.append(output_dir)

            archive_name = "momo-tools-v9.9.9-test.tar.gz"
            first_archive = outputs[0] / archive_name
            second_archive = outputs[1] / archive_name
            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())

            digest = hashlib.sha256(first_archive.read_bytes()).hexdigest()
            checksum = (outputs[0] / f"{archive_name}.sha256").read_text(
                encoding="utf-8"
            )
            manifest = json.loads(
                (outputs[0] / "momo-tools-v9.9.9-test.snapshot.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(f"{digest}  {archive_name}\n", checksum)
            self.assertEqual("release-snapshot/v1", manifest["schema"])
            self.assertEqual("9.9.9-test", manifest["version"])
            self.assertEqual("v9.9.9-test", manifest["tag"])
            self.assertEqual(commit, manifest["commit_sha"])
            self.assertEqual(digest, manifest["sha256"])
            self.assertTrue(manifest["reproducible"])

            with tarfile.open(first_archive, "r:gz") as archive:
                members = archive.getnames()
            self.assertTrue(members)
            prefix = "momo-tools-v9.9.9-test"
            self.assertTrue(
                all(name == prefix or name.startswith(f"{prefix}/") for name in members)
            )
            self.assertIn("momo-tools-v9.9.9-test/VERSION", members)
            self.assertNotIn("momo-tools-v9.9.9-test/.git", members)

    def test_builder_rejects_every_committed_version_consumer_mismatch(self):
        for consumer in ("json", "yaml", "release_notes"):
            with self.subTest(consumer=consumer), tempfile.TemporaryDirectory(
                prefix="momo-tools-release-version-drift-"
            ) as tmp:
                fixture, commit, fixture_builder = self.committed_fixture(
                    tmp, consumer_versions={consumer: "9.9.9-drift"}
                )
                output_dir = fixture / "output"

                result = subprocess.run(
                    [
                        "bash",
                        str(fixture_builder),
                        "--ref",
                        commit,
                        "--output-dir",
                        str(output_dir),
                    ],
                    cwd=fixture,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertNotEqual(0, result.returncode)
                self.assertIn("Version mismatch", result.stderr)
                self.assertFalse(list(output_dir.glob("*.tar.gz")))

    def test_ci_builds_twice_compares_and_uploads_the_snapshot(self):
        workflow = (REPO / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("Build reproducible release snapshot", workflow)
        self.assertEqual(2, workflow.count("scripts/build-release-snapshot.sh --ref"))
        self.assertIn('cmp "$first_archive" "$second_archive"', workflow)
        self.assertIn("uses: actions/upload-artifact@v4", workflow)
        self.assertIn("dist/release/", workflow)
        self.assertIn("Smoke-test release snapshot artifact", workflow)

        scan_position = workflow.index("- name: Private-context leak scan")
        build_position = workflow.index("- name: Build reproducible release snapshot")
        smoke_position = workflow.index("- name: Smoke-test release snapshot artifact")
        upload_position = workflow.index("- name: Upload release snapshot")
        self.assertLess(scan_position, build_position)
        self.assertLess(build_position, smoke_position)
        self.assertLess(smoke_position, upload_position)
        self.assertIn('tar -xzf "$first_archive"', workflow)
        self.assertIn('"$snapshot_root/scripts/install-local.sh"', workflow)
        self.assertIn(
            '"$snapshot_root/plugin/scripts/momo-tools" integrity', workflow
        )
        self.assertIn(
            '"$snapshot_root/plugin/scripts/momo-tools" recovery-drill', workflow
        )
        self.assertIn('"$snapshot_root/plugin/scripts/momo-tools" slo', workflow)
        self.assertIn('"$snapshot_root/plugin/scripts/momo-tools" doctor', workflow)
        self.assertIn(
            '"$snapshot_root/plugin/scripts/momo-tools" repair-plan --dry-run',
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
