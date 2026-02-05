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

- The agent uses Gemini Flash-3 via `google-genai`.
- Set `GEMINI_API_KEY`. Fallback models are controlled by:
  - `GEMINI_MODEL_PRIMARY`
  - `GEMINI_MODEL_FALLBACK`
  - `GEMINI_MODEL_FALLBACK_LITE`
  - `GEMINI_RATE_LIMIT_LEVEL` (0=primary, 1=fallback, 2=lite)
