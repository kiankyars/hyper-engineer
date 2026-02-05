import argparse
import random
import time

from pr_agent import config
from pr_agent.job_store import JobStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=3600)
    parser.add_argument("--search-query", default=config.DEFAULT_SEARCH_QUERY)
    parser.add_argument("--max-page", type=int, default=config.SEARCH_MAX_PAGE)
    args = parser.parse_args()

    store = JobStore()
    while True:
        page = random.randint(1, max(1, args.max_page))
        store.enqueue({"search_query": args.search_query, "search_page": page})
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
