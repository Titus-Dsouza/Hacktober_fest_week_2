"""Run a small, dependency-free smoke/load check against the local missions API."""

import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

URL = "http://127.0.0.1:8000/api/missions/"
REQUEST_COUNT = 20
WORKER_COUNT = 4


def fetch_missions():
    request = Request(URL, headers={"Accept": "application/json"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected HTTP status: {response.status}")
            payload = json.loads(response.read())
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Local missions API request failed: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("missions"), list):
        raise RuntimeError("Local missions API returned an invalid response shape.")
    return time.perf_counter() - started


def main():
    parsed_url = urlsplit(URL)
    if parsed_url.scheme != "http" or parsed_url.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        raise RuntimeError("This smoke test is restricted to a local HTTP server.")

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=WORKER_COUNT) as executor:
        durations = list(executor.map(lambda _: fetch_missions(), range(REQUEST_COUNT)))

    print(
        f"Passed {len(durations)} local GET requests "
        f"({WORKER_COUNT} concurrent workers); "
        f"avg {statistics.mean(durations) * 1000:.1f} ms, "
        f"max {max(durations) * 1000:.1f} ms, "
        f"wall {time.perf_counter() - started:.2f} s."
    )
    print("This is a lightweight local smoke check, not production load testing.")


if __name__ == "__main__":
    main()
