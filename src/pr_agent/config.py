import os
import shlex

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

CLI_RUNNER_CMD = _get_env("CLI_RUNNER_CMD", "claude")
CLI_RUNNER_ARGS = shlex.split(os.getenv("CLI_RUNNER_ARGS", ""))
CLI_TIMEOUT_SECONDS = int(_get_env("CLI_TIMEOUT_SECONDS", "900"))

GIT_AUTHOR_NAME = _get_env("GIT_AUTHOR_NAME", "pr-agent")
GIT_AUTHOR_EMAIL = _get_env("GIT_AUTHOR_EMAIL", "pr-agent@example.com")

DEFAULT_SEARCH_QUERY = _get_env(
    "DEFAULT_SEARCH_QUERY",
    'is:issue is:open label:"good first issue"',
)
TEST_COMMAND = os.getenv("TEST_COMMAND", "")
