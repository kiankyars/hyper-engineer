import argparse
import time

from pr_agent import config
from pr_agent.job_store import JobStore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=3600)
    parser.add_argument("--search-query", default=config.DEFAULT_SEARCH_QUERY)
    args = parser.parse_args()

    store = JobStore()
    while True:
        store.enqueue({"search_query": args.search_query})
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
