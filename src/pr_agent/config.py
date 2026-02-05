import os

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _normalize_query(value: str) -> str:
    if value.count('"') % 2 == 1:
        return f'{value}"'
    return value


REDIS_URL = _get_env("REDIS_URL", "redis://localhost:6379/0")
REDIS_QUEUE_NAME = _get_env("REDIS_QUEUE_NAME", "pr-agent-jobs")
WORKDIR_BASE = os.path.abspath(os.path.expanduser(_get_env("WORKDIR_BASE", "/tmp/pr-agent")))

GITHUB_API_URL = _get_env("GITHUB_API_URL", "https://api.github.com")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_RATE_LIMIT_WAIT_SECONDS = int(os.getenv("GEMINI_RATE_LIMIT_WAIT_SECONDS", "60"))
GEMINI_TIMEOUT_MS = int(os.getenv("GEMINI_TIMEOUT_MS", "60000"))

GIT_AUTHOR_NAME = _get_env("GIT_AUTHOR_NAME")
GIT_AUTHOR_EMAIL = _get_env("GIT_AUTHOR_EMAIL")

DEFAULT_SEARCH_QUERY = _get_env(
    "DEFAULT_SEARCH_QUERY",
    'is:issue is:open label:"good first issue" stars:>=100',
)
DEFAULT_SEARCH_QUERY = _normalize_query(DEFAULT_SEARCH_QUERY)
SEARCH_MAX_PAGE = int(os.getenv("SEARCH_MAX_PAGE", "5"))
TEST_COMMAND = os.getenv("TEST_COMMAND", "")
