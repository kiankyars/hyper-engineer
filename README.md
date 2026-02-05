# PR Agent MVP (CLI Runner)

Hosted background worker that finds issues, makes small changes, and opens PRs.

## Setup

1. Create a GitHub App and install it on your target repos.
2. Export env vars (see `.env.example`).
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

- The CLI runner expects a Claude Code–like CLI that can emit a patch between
  `PATCH_BEGIN` and `PATCH_END`. Configure with `CLI_RUNNER_CMD` and
  `CLI_RUNNER_ARGS`.
