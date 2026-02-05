import subprocess

from pr_agent import config
from pr_agent.cli_runner import PatchResult, run_cli_patch


def apply_patch(repo_path: str, diff: str) -> None:
    result = subprocess.run(
        ["git", "apply", "--whitespace=fix", "-"],
        input=diff,
        text=True,
        cwd=repo_path,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git apply failed: {result.stderr.strip()}")


def run_tests(repo_path: str, test_command: str) -> None:
    if not test_command:
        return
    subprocess.run(test_command, shell=True, cwd=repo_path, check=True)


def run_change(task: str, repo_path: str, test_command: str) -> PatchResult:
    patch_result = run_cli_patch(task, repo_path)
    apply_patch(repo_path, patch_result.diff)
    run_tests(repo_path, test_command)
    return patch_result
