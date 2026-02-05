import os

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


REDIS_URL = _get_env("REDIS_URL", "redis://localhost:6379/0")
REDIS_QUEUE_NAME = _get_env("REDIS_QUEUE_NAME", "pr-agent-jobs")
WORKDIR_BASE = _get_env("WORKDIR_BASE", "/tmp/pr-agent")

GITHUB_API_URL = _get_env("GITHUB_API_URL", "https://api.github.com")
GITHUB_PAT = os.getenv("GITHUB_PAT", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_PRIMARY = os.getenv("GEMINI_MODEL_PRIMARY", "gemini-3-flash-preview")
GEMINI_MODEL_FALLBACK = os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash")
GEMINI_MODEL_FALLBACK_LITE = os.getenv("GEMINI_MODEL_FALLBACK_LITE", "gemini-2.5-flash-lite")
GEMINI_RATE_LIMIT_LEVEL = int(os.getenv("GEMINI_RATE_LIMIT_LEVEL", "0"))

GIT_AUTHOR_NAME = _get_env("GIT_AUTHOR_NAME", "pr-agent")
GIT_AUTHOR_EMAIL = _get_env("GIT_AUTHOR_EMAIL", "pr-agent@example.com")

DEFAULT_SEARCH_QUERY = _get_env(
    "DEFAULT_SEARCH_QUERY",
    'is:issue is:open label:"good first issue"',
)
TEST_COMMAND = os.getenv("TEST_COMMAND", "")
