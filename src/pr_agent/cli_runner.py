import os
from dataclasses import dataclass

import pexpect

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


def run_cli_patch(task: str, repo_path: str) -> PatchResult:
    prompt = build_prompt(task)
    child = pexpect.spawn(
        config.CLI_RUNNER_CMD,
        config.CLI_RUNNER_ARGS,
        cwd=repo_path,
        encoding="utf-8",
        env=os.environ.copy(),
    )
    child.sendline(prompt)
    child.expect("PATCH_BEGIN", timeout=config.CLI_TIMEOUT_SECONDS)
    child.expect("PATCH_END", timeout=config.CLI_TIMEOUT_SECONDS)
    output = child.before
    diff = output.strip()
    return PatchResult(diff=diff, raw_output=child.before)
