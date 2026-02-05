import argparse

from pr_agent.job_store import JobStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="owner/name")
    parser.add_argument("--issue", type=int, help="Issue number")
    parser.add_argument("--search-query", help="GitHub search query override")
    parser.add_argument("--search-page", type=int, default=1, help="Search page to use")
    parser.add_argument("--test-command", help="Override test command")
    args = parser.parse_args()

    store = JobStore()

    payload: dict = {}
    if args.repo and args.issue:
        payload["repo"] = args.repo
        payload["issue_number"] = args.issue
    if args.search_query:
        payload["search_query"] = args.search_query
        payload["search_page"] = args.search_page
    if args.test_command:
        payload["test_command"] = args.test_command
    job_id = store.enqueue(payload)
    print(job_id)


if __name__ == "__main__":
    main()
