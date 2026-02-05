# PR Agent MVP (CLI Runner)

Hosted background worker that finds issues, makes small changes, and opens PRs.

## Setup

1. Create a GitHub PAT with repo scope.
2. Export env vars (see `.env.example`).
   - `.env` is auto-loaded if present.
3. Install dependencies (uv):
   - `uv sync`

## Run

- Enqueue a job:
  - `uv run pr_agent.enqueue_job --repo owner/name --issue 123`
- Start worker:
  - `uv run pr_agent.worker`
- Run scheduler:
  - `uv run pr_agent.orchestrator --interval 3600`

## Notes

- The default CLI runner is a Claude Code shim:
  - `CLI_RUNNER_CMD=python`
  - `CLI_RUNNER_ARGS=-m pr_agent.claude_shim`
- The shim invokes `CLAUDE_CODE_CMD` and expects a patch between
  `PATCH_BEGIN` and `PATCH_END`.
- For debugging, set `CLAUDE_SHIM_DEBUG=1` to stream CLI output to stderr.
