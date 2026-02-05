import os
import time
from urllib.parse import urlparse

from pr_agent import config
from pr_agent.change_engine import run_change
from pr_agent.github_client import GitHubClient, GitHubRepo
from pr_agent.issue_finder import find_issue
from pr_agent.job_store import JobStore
from pr_agent.repo import RepoContext, checkout_branch, clone_fork, commit_all, ensure_fork, push_branch


def _parse_repo(full_name: str) -> GitHubRepo:
    owner, name = full_name.split("/", 1)
    return GitHubRepo(owner=owner, name=name)


def _derive_task(issue: dict) -> str:
    title = issue.get("title", "")
    body = issue.get("body") or ""
    return f"Fix the following issue.\n\nTitle: {title}\n\nBody:\n{body}\n"


def _fork_url(repo_data: dict, fork_owner: str, name: str) -> str:
    clone_url = repo_data["clone_url"]
    parsed = urlparse(clone_url)
    return f"{parsed.scheme}://{fork_owner}@{parsed.netloc}/{fork_owner}/{name}.git"


def process_job(job: dict) -> None:
    store = JobStore()
    job_id = job["id"]
    payload = job["payload"]
    store.update_status(job_id, "running")

    github = GitHubClient()

    if payload.get("repo") and payload.get("issue_number"):
        repo = _parse_repo(payload["repo"])
        issue = github.request("GET", f"/repos/{repo.owner}/{repo.name}/issues/{payload['issue_number']}")
    else:
        issue = find_issue(github, payload.get("search_query"))
        if issue is None:
            store.set_artifact(job_id, "status_message", "No issues found for query.")
            store.update_status(job_id, "skipped")
            return
        repo = _parse_repo(issue["repository_url"].split("/repos/")[-1])

    repo_data = github.get_repo(repo.owner, repo.name)
    base_branch = repo_data["default_branch"]

    fork_owner = ensure_fork(github, repo)
    fork_repo_data = github.get_repo(fork_owner, repo.name)
    fork_url = _fork_url(fork_repo_data, fork_owner, repo.name)

    workdir = os.path.join(config.WORKDIR_BASE, job_id)
    context = RepoContext(
        repo=repo,
        fork_owner=fork_owner,
        fork_url=fork_url,
        base_branch=base_branch,
        workdir=workdir,
    )

    clone_fork(context)
    branch_name = f"pr-agent/{job_id}"
    checkout_branch(context.workdir, branch_name, base_branch)

    task = _derive_task(issue)
    store.set_artifact(job_id, "task", task)
    patch_result = run_change(task, context.workdir, payload.get("test_command", config.TEST_COMMAND))
    store.set_artifact(job_id, "diff", patch_result.diff)
    store.set_artifact(job_id, "cli_output", patch_result.raw_output)

    commit_message = f"PR agent: {issue.get('title', 'update')}"
    commit_all(context.workdir, commit_message)
    push_branch(context.workdir, branch_name)

    pr_title = issue.get("title", "PR agent update")
    pr_body = f"Closes #{issue.get('number')}\n\nAutomated change by PR agent."
    head = f"{fork_owner}:{branch_name}"
    _ = github.create_pull_request(
        owner=repo.owner,
        name=repo.name,
        title=pr_title,
        body=pr_body,
        head=head,
        base=base_branch,
    )

    store.update_status(job_id, "completed")


def main() -> None:
    store = JobStore()
    while True:
        job = store.pop(timeout_seconds=5)
        if job is None:
            time.sleep(1)
            continue
        process_job(job)


if __name__ == "__main__":
    main()
