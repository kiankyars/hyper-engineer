# PR Agent MVP (CLI Runner)

Hosted background worker that finds issues, makes small changes, and opens PRs.

## Setup

1. Create a GitHub App and install it on your target repos.
2. Export env vars (see `.env.example`).
   - For PAT auth, set `GITHUB_PAT` and leave app vars empty.
3. Install dependencies (uv):
   - `uv venv`
   - `source .venv/bin/activate`
   - `uv pip install -e .`

## Run

- Enqueue a job:
  - `python -m pr_agent.enqueue_job --repo owner/name --issue 123`
- Start worker:
  - `python -m pr_agent.worker`
- Run scheduler:
  - `python -m pr_agent.orchestrator --interval 3600`

## Notes

- The default CLI runner is a Claude Code shim:
  - `CLI_RUNNER_CMD=python`
  - `CLI_RUNNER_ARGS=-m pr_agent.claude_shim`
- The shim invokes `CLAUDE_CODE_CMD` and expects a patch between
  `PATCH_BEGIN` and `PATCH_END`.
