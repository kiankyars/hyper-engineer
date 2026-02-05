import os
import shlex
import sys

import pexpect

from pr_agent import config


def _read_prompt() -> str:
    prompt = sys.stdin.read().strip()
    if not prompt:
        raise RuntimeError("No prompt provided on stdin.")
    return prompt


def _build_instruction(prompt: str) -> str:
    return (
        "You are a coding agent. Generate a unified diff patch only.\n"
        "Wrap the patch between PATCH_BEGIN and PATCH_END.\n\n"
        f"{prompt}\n"
    )


def main() -> None:
    prompt = _read_prompt()
    cmd = os.getenv("CLAUDE_CODE_CMD", "claude")
    args = shlex.split(os.getenv("CLAUDE_CODE_ARGS", ""))
    child = pexpect.spawn(
        cmd,
        args,
        encoding="utf-8",
        env=os.environ.copy(),
    )
    child.sendline(_build_instruction(prompt))
    child.expect("PATCH_BEGIN", timeout=config.CLI_TIMEOUT_SECONDS)
    child.expect("PATCH_END", timeout=config.CLI_TIMEOUT_SECONDS)
    diff = child.before.strip()
    sys.stdout.write(f"PATCH_BEGIN\n{diff}\nPATCH_END\n")


if __name__ == "__main__":
    main()
