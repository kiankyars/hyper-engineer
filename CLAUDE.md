# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PR Agent MVP is a background worker that autonomously finds GitHub issues, generates code patches using Gemini AI, and opens pull requests. It uses a Redis job queue to manage work.

## Commands

```bash
# Install dependencies
uv sync

# Enqueue a specific job
uv run -m pr_agent.enqueue_job --repo owner/name --issue 123

# Start the worker (processes jobs from queue)
uv run -m pr_agent.worker

# Start the scheduler (enqueues search jobs periodically)
uv run -m pr_agent.orchestrator --interval 3600 --max-page 5
```

## Architecture

The system is a pipeline with three main entry points:

- **orchestrator.py** - Scheduler that enqueues search jobs at intervals
- **enqueue_job.py** - CLI for manual job submission
- **worker.py** - Main job processor that runs the pipeline

### Job Processing Pipeline (worker.py)

1. **Issue Discovery** - `issue_finder.py` searches GitHub for issues matching query
2. **Deduplication** - `job_store.py` tracks claimed issues in Redis (24h TTL)
3. **Repository Setup** - `repo.py` forks, clones, and creates branch
4. **Patch Generation** - `cli_runner.py` calls Gemini with task prompt
5. **Patch Application** - `change_engine.py` applies diff via `git apply`
6. **PR Creation** - `github_client.py` pushes and opens PR

### Key Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Environment configuration (loads from .env) |
| `job_store.py` | Redis job queue operations |
| `github_client.py` | GitHub REST API client |
| `cli_runner.py` | Gemini integration with model fallback chain |
| `change_engine.py` | Patch application and test execution |
| `repo.py` | Git operations (clone, branch, commit, push) |

### Gemini Model Fallback

When generating patches, the system tries models in order:
1. `gemini-3-flash-preview`
2. `gemini-2.5-flash`
3. `gemini-2.5-flash-lite`

Rate limits trigger fallback to next model; exhausting all models waits and retries.

## Environment Variables

Required: `GITHUB_PAT`, `GEMINI_API_KEY`, `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`

See `.env.example` for all options. `.env` is auto-loaded.
