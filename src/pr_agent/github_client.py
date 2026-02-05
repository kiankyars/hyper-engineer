import json
from dataclasses import dataclass

import requests

from pr_agent import config


@dataclass
class GitHubRepo:
    owner: str
    name: str


class GitHubClient:
    def __init__(self) -> None:
        self.api_url = config.GITHUB_API_URL.rstrip("/")
        self.pat = config.GITHUB_PAT
        if not self.pat:
            raise RuntimeError("Missing required env var: GITHUB_PAT")
        self._installation_token: str | None = None
        self._installation_token_expires_at: int = 0

    def _installation_headers(self) -> dict:
        return {
            "Authorization": f"token {self.pat}",
            "Accept": "application/vnd.github+json",
        }

    def get_installation_account(self) -> str:
        response = requests.get(
            f"{self.api_url}/user",
            headers=self._installation_headers(),
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["login"]

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self.api_url}{path}"
        headers = self._installation_headers()
        response = requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(payload) if payload is not None else None,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def request_raw(self, method: str, path: str, payload: dict | None = None) -> requests.Response:
        url = f"{self.api_url}{path}"
        headers = self._installation_headers()
        return requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(payload) if payload is not None else None,
            timeout=30,
        )

    def search_issues(self, query: str, per_page: int = 5, page: int = 1) -> dict:
        params = {
            "q": query,
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "order": "desc",
        }
        url = f"{self.api_url}/search/issues"
        response = requests.get(
            url,
            headers=self._installation_headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


    def fork_repo(self, repo: GitHubRepo) -> dict:
        try:
            return self.request("POST", f"/repos/{repo.owner}/{repo.name}/forks")
        except requests.HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else None
            if status == 403:
                raise RuntimeError(
                    "Fork forbidden. The repo may be disabled for forking or "
                    "your token lacks access."
                ) from exc
            raise

    def get_repo(self, owner: str, name: str) -> dict:
        return self.request("GET", f"/repos/{owner}/{name}")

    def get_repo_optional(self, owner: str, name: str) -> dict | None:
        response = self.request_raw("GET", f"/repos/{owner}/{name}")
        if response.status_code == 200:
            return response.json()
        return None

    def get_branch(self, owner: str, name: str, branch: str) -> dict:
        return self.request("GET", f"/repos/{owner}/{name}/branches/{branch}")

    def create_branch(self, owner: str, name: str, branch: str, sha: str) -> dict:
        payload = {"ref": f"refs/heads/{branch}", "sha": sha}
        return self.request("POST", f"/repos/{owner}/{name}/git/refs", payload)

    def create_pull_request(
        self,
        owner: str,
        name: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict:
        payload = {"title": title, "body": body, "head": head, "base": base}
        return self.request("POST", f"/repos/{owner}/{name}/pulls", payload)
