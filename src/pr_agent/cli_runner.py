from dataclasses import dataclass

from google import genai

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


def _select_model() -> str:
    if config.GEMINI_RATE_LIMIT_LEVEL >= 2:
        return config.GEMINI_MODEL_FALLBACK_LITE
    if config.GEMINI_RATE_LIMIT_LEVEL >= 1:
        return config.GEMINI_MODEL_FALLBACK
    return config.GEMINI_MODEL_PRIMARY


def run_cli_patch(task: str, repo_path: str) -> PatchResult:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("Missing required env var: GEMINI_API_KEY")
    prompt = build_prompt(task)
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    model = _select_model()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    output = response.text or ""
    start = output.find("PATCH_BEGIN")
    end = output.find("PATCH_END")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("Model response missing PATCH markers.")
    diff = output[start + len("PATCH_BEGIN"):end].strip()
    return PatchResult(diff=diff, raw_output=output)
