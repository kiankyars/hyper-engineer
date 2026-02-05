import argparse
import time

from pr_agent import config
from pr_agent.github_client import GitHubClient
from pr_agent.issue_finder import repo_issue_query, top_repos
from pr_agent.job_store import JobStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=3600)
    parser.add_argument("--search-query", default=config.DEFAULT_SEARCH_QUERY)
    parser.add_argument("--top-repos", type=int, default=100)
    args = parser.parse_args()

    store = JobStore()
    while True:
        if args.search_query:
            store.enqueue({"search_query": args.search_query})
        else:
            github = GitHubClient()
            for repo_full_name in top_repos(github, count=args.top_repos):
                store.enqueue({"search_query": repo_issue_query(repo_full_name)})
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
