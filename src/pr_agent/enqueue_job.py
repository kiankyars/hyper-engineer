import argparse

from pr_agent.github_client import GitHubClient
from pr_agent.issue_finder import repo_issue_query, top_repos
from pr_agent.job_store import JobStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="owner/name")
    parser.add_argument("--issue", type=int, help="Issue number")
    parser.add_argument("--search-query", help="GitHub search query override")
    parser.add_argument("--test-command", help="Override test command")
    parser.add_argument("--top-repos", type=int, default=0, help="Enqueue jobs for top N repos")
    args = parser.parse_args()

    store = JobStore()
    if args.top_repos > 0:
        github = GitHubClient()
        repos = top_repos(github, count=args.top_repos)
        for repo_full_name in repos:
            payload: dict = {"search_query": repo_issue_query(repo_full_name)}
            if args.test_command:
                payload["test_command"] = args.test_command
            job_id = store.enqueue(payload)
            print(job_id)
        return

    payload: dict = {}
    if args.repo and args.issue:
        payload["repo"] = args.repo
        payload["issue_number"] = args.issue
    if args.search_query:
        payload["search_query"] = args.search_query
    if args.test_command:
        payload["test_command"] = args.test_command
    job_id = store.enqueue(payload)
    print(job_id)


if __name__ == "__main__":
    main()
