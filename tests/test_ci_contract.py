import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"
WORKFLOW_EXAMPLE = REPO / "docs" / "github-actions-ci.example.yml"


def workflow_run_block(path, step_name):
    lines = path.read_text(encoding="utf-8").splitlines()
    step = f"      - name: {step_name}"
    step_index = lines.index(step)
    run_index = lines.index("        run: |", step_index + 1)
    block = []
    for line in lines[run_index + 1 :]:
        if line.startswith("          "):
            block.append(line[10:])
        elif not line.strip():
            block.append("")
        else:
            break
    return "\n".join(block).rstrip() + "\n"


class PublicCiContractTests(unittest.TestCase):
    def tracked_repo(self, content):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        repo = Path(temp_dir.name)
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / "fixture.txt").write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "fixture.txt"], cwd=repo, check=True)
        return repo

    def run_block(self, block, cwd):
        return subprocess.run(
            ["bash", "-eu", "-o", "pipefail", "-c", block],
            cwd=cwd,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_private_context_leak_scan_is_synced_and_does_not_match_itself(self):
        workflow_block = workflow_run_block(WORKFLOW, "Private-context leak scan")
        example_block = workflow_run_block(WORKFLOW_EXAMPLE, "Private-context leak scan")

        self.assertEqual(workflow_block, example_block)
        for source, block in ((WORKFLOW, workflow_block), (WORKFLOW_EXAMPLE, example_block)):
            with self.subTest(source=source.relative_to(REPO)):
                result = subprocess.run(
                    ["bash", "-eu", "-o", "pipefail", "-c", block],
                    cwd=REPO,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{source.relative_to(REPO)} leak scan failed:\n{result.stdout}{result.stderr}",
                )

    def test_private_context_leak_scan_distinguishes_clean_leaks_and_scan_errors(self):
        block = workflow_run_block(WORKFLOW, "Private-context leak scan")
        cases = (
            ("clean", "public fixture\n", False, None),
            (
                "private-marker",
                "PRIVATE_" + "COMPANY=super-secret-fixture-value\n",
                True,
                "super-secret-fixture-value",
            ),
            ("home-path", "/" + "Users/example/project\n", True, None),
        )
        for name, content, has_leak, secret_value in cases:
            with self.subTest(name=name):
                result = self.run_block(block, self.tracked_repo(content))
                if has_leak:
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    if secret_value:
                        self.assertNotIn(
                            secret_value,
                            result.stdout + result.stderr,
                            "leak scan echoed matched private content",
                        )
                else:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        with tempfile.TemporaryDirectory() as non_git_dir:
            result = self.run_block(block, non_git_dir)
        self.assertNotEqual(result.returncode, 0, "git grep failure was treated as a clean scan")


if __name__ == "__main__":
    unittest.main()
