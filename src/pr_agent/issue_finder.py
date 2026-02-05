import requests

from pr_agent import config
from pr_agent.github_client import GitHubClient


def find_issue(github: GitHubClient, query: str | None = None) -> dict | None:
    search_query = query or config.DEFAULT_SEARCH_QUERY
    try:
        data = github.search_issues(search_query, per_page=5)
    except requests.HTTPError:
        return None
    items = data.get("items", [])
    if not items:
        return None
    return items[0]


