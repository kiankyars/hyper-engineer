import json
import time
from dataclasses import dataclass

import jwt
import requests

from pr_agent import config


@dataclass
class GitHubRepo:
    owner: str
    name: str


class GitHubClient:
    def __init__(self) -> None:
        self.api_url = config.GITHUB_API_URL.rstrip("/")
        self.app_id = config.GITHUB_APP_ID
        self.installation_id = config.GITHUB_INSTALLATION_ID
        self.private_key_path = config.GITHUB_PRIVATE_KEY_PATH
        missing = []
        if not self.app_id:
            missing.append("GITHUB_APP_ID")
        if not self.installation_id:
            missing.append("GITHUB_INSTALLATION_ID")
        if not self.private_key_path:
            missing.append("GITHUB_PRIVATE_KEY_PATH")
        if missing:
            missing_text = ", ".join(missing)
            raise RuntimeError(f"Missing required env vars for GitHub App: {missing_text}")
        self._installation_token: str | None = None
        self._installation_token_expires_at: int = 0

    def _read_private_key(self) -> str:
        with open(self.private_key_path, "r", encoding="utf-8") as handle:
            return handle.read()

    def _app_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 30,
            "exp": now + 540,
            "iss": self.app_id,
        }
        key = self._read_private_key()
        return jwt.encode(payload, key, algorithm="RS256")

    def _app_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._app_jwt()}",
            "Accept": "application/vnd.github+json",
        }

    def _installation_headers(self) -> dict:
        token = self._get_installation_token()
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def _get_installation_token(self) -> str:
        now = int(time.time())
        if self._installation_token and now < self._installation_token_expires_at:
            return self._installation_token

        url = f"{self.api_url}/app/installations/{self.installation_id}/access_tokens"
        response = requests.post(url, headers=self._app_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        token = data["token"]
        expires_at = data["expires_at"]
        self._installation_token = token
        self._installation_token_expires_at = int(
            time.mktime(time.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ"))
        ) - 60
        return token

    def get_installation_account(self) -> str:
        url = f"{self.api_url}/app/installations/{self.installation_id}"
        response = requests.get(url, headers=self._app_headers(), timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["account"]["login"]

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

    def search_issues(self, query: str, per_page: int = 5) -> dict:
        params = {"q": query, "per_page": per_page, "sort": "updated", "order": "desc"}
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
        return self.request("POST", f"/repos/{repo.owner}/{repo.name}/forks")

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
