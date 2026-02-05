import os
import shutil
import subprocess
import time
from dataclasses import dataclass

from pr_agent import config
from pr_agent.github_client import GitHubClient, GitHubRepo


@dataclass
class RepoContext:
    repo: GitHubRepo
    fork_owner: str
    fork_url: str
    base_branch: str
    workdir: str


def ensure_workdir(base: str, name: str) -> str:
    workdir = os.path.join(base, name)
    os.makedirs(workdir, exist_ok=True)
    return workdir


def ensure_fork(github: GitHubClient, repo: GitHubRepo) -> str:
    fork_owner = github.get_installation_account()
    _ = github.fork_repo(repo)
    for _ in range(20):
        data = github.get_repo_optional(fork_owner, repo.name)
        if data and data.get("full_name"):
            return fork_owner
        time.sleep(2)
    raise RuntimeError("Fork not available after waiting.")


def clone_fork(context: RepoContext) -> None:
    if os.path.exists(context.workdir):
        shutil.rmtree(context.workdir)
    subprocess.run(
        ["git", "clone", context.fork_url, context.workdir],
        check=True,
    )


def checkout_branch(workdir: str, branch: str, base_branch: str) -> None:
    subprocess.run(["git", "checkout", base_branch], cwd=workdir, check=True)
    subprocess.run(["git", "checkout", "-b", branch], cwd=workdir, check=True)


def push_branch(workdir: str, branch: str) -> None:
    subprocess.run(["git", "push", "origin", branch], cwd=workdir, check=True)


def commit_all(workdir: str, message: str) -> None:
    env = os.environ.copy()
    subprocess.run(["git", "add", "-A"], cwd=workdir, check=True, env=env)
    subprocess.run(
        [
            "git",
            "-c",
            f"user.name={config.GIT_AUTHOR_NAME}",
            "-c",
            f"user.email={config.GIT_AUTHOR_EMAIL}",
            "commit",
            "-m",
            message,
        ],
        cwd=workdir,
        check=True,
        env=env,
    )
