"""Quick local latency check for the FAQ retriever (no network)."""
from __future__ import annotations

import statistics
import time
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nust_chatbot.retrieve import FaqRetriever  # noqa: E402

QUERIES = [
    "quota seats",
    "NET fee registration",
    "hostel MBBS",
    "ICS engineering chemistry",
    "refund security deposit",
]


def main() -> None:
    r = FaqRetriever(ROOT / "data" / "faq.json")
    times: list[float] = []
    for _ in range(30):
        for q in QUERIES:
            t0 = time.perf_counter()
            r.query(q)
            times.append((time.perf_counter() - t0) * 1000)
    print(f"FAQ entries: {len(r._items)}")
    print(f"Queries measured: {len(times)}")
    print(f"p50 latency: {statistics.median(times):.3f} ms")
    print(f"mean: {statistics.fmean(times):.3f} ms")
    print(f"max: {max(times):.3f} ms")


if __name__ == "__main__":
    main()
