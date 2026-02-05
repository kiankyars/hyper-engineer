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
  - `uv run -m pr_agent.enqueue_job --repo owner/name --issue 123`
- Enqueue jobs for top repos:
  - `uv run -m pr_agent.enqueue_job --top-repos 100`
- Start worker:
  - `uv run -m pr_agent.worker`
- Run scheduler:
  - `uv run -m pr_agent.orchestrator --interval 3600 --top-repos 100 --search-query ""`

## Notes

- The agent uses Gemini Flash-3 via `google-genai`.
- Set `GEMINI_API_KEY`. Fallback order is:
  - `gemini-3-flash-preview`
  - `gemini-2.5-flash`
  - `gemini-2.5-flash-lite`
- If the last model hits rate limits, the worker waits and retries.
