from dataclasses import dataclass

import time

from google import genai
from google.genai import types

from pr_agent import config


@dataclass
class PatchResult:
    diff: str
    raw_output: str


def build_prompt(task: str) -> str:
    return (
        "You are a coding agent. Generate a unified diff patch only.\n"
        "Wrap the patch between PATCH_BEGIN and PATCH_END.\n\n"
        f"Task:\n{task}\n"
    )


def _should_fallback(error: Exception) -> bool:
    code = getattr(error, "code", None) or getattr(error, "status_code", None)
    if code in {429, 500, 502, 503, 504}:
        return True
    text = str(error).lower()
    return (
        "rate limit" in text
        or "429" in text
        or "deadline" in text
        or "timeout" in text
        or "temporarily unavailable" in text
        or "server error" in text
    )


def _model_sequence() -> list[str]:
    return [
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]


def run_cli_patch(task: str, repo_path: str) -> PatchResult:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("Missing required env var: GEMINI_API_KEY")
    prompt = build_prompt(task)
    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=config.GEMINI_TIMEOUT_MS),
    )
    models = _model_sequence()
    output = ""
    while True:
        for index, model in enumerate(models):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                output = response.text or ""
                return _extract_diff(output)
            except Exception as exc:
                is_last = index == len(models) - 1
                if _should_fallback(exc):
                    if is_last:
                        time.sleep(config.GEMINI_RATE_LIMIT_WAIT_SECONDS)
                        break
                    continue
                raise
    raise RuntimeError("Model response missing PATCH markers.")


def _extract_diff(output: str) -> PatchResult:
    start = output.find("PATCH_BEGIN")
    end = output.find("PATCH_END")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Model response missing PATCH markers.")
    diff = output[start + len("PATCH_BEGIN"):end].strip()
    return PatchResult(diff=diff, raw_output=output)
