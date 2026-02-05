from pr_agent import config
from pr_agent.github_client import GitHubClient


def find_issue(github: GitHubClient, query: str | None = None) -> dict:
    search_query = query or config.DEFAULT_SEARCH_QUERY
    data = github.search_issues(search_query, per_page=5)
    items = data.get("items", [])
    if not items:
        raise RuntimeError("No issues found for query.")
    return items[0]
