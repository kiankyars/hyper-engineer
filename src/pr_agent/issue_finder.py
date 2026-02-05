from pr_agent import config
from pr_agent.github_client import GitHubClient


def find_issue(github: GitHubClient, query: str | None = None) -> dict:
    search_query = query or config.DEFAULT_SEARCH_QUERY
    data = github.search_issues(search_query, per_page=5)
    items = data.get("items", [])
    if not items:
        raise RuntimeError("No issues found for query.")
    return items[0]


def top_repos(github: GitHubClient, count: int = 100) -> list[str]:
    repos: list[str] = []
    page = 1
    while len(repos) < count:
        data = github.search_repositories("stars:>50000 archived:false", per_page=100, page=page)
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            repos.append(item["full_name"])
            if len(repos) >= count:
                break
        page += 1
    return repos[:count]


def repo_issue_query(repo_full_name: str) -> str:
    return f'repo:{repo_full_name} {config.DEFAULT_SEARCH_QUERY}'
