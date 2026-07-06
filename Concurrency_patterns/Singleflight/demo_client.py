#!/usr/bin/env python3
"""
Demo client — fires concurrent requests to both endpoints and compares results.

Usage:
    # Terminal 1 — start the app
    python app.py

    # Terminal 2 — run the demo
    python demo_client.py
"""

from __future__ import annotations

import asyncio
import time

import httpx


async def fire(base_url: str, endpoint: str, user_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{base_url}/{endpoint}/{user_id}")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]


async def main() -> None:
    base = "http://127.0.0.1:8000"

    # ── Without singleflight: 5 concurrent requests for the same user ────
    print("=== WITHOUT singleflight ===")
    start = time.perf_counter()
    results = await asyncio.gather(
        *[fire(base, "without-singleflight", "42") for _ in range(5)]
    )
    elapsed = time.perf_counter() - start

    computation_ids = {r["computation_id"] for r in results}
    for r in results:
        print(
            f"  user={r['user_id']}  "
            f"computation_id={r['computation_id']}  "
            f"took={r['elapsed_s']}s"
        )
    print(f"  --- {len(results)} requests in {elapsed:.2f}s total."
          f"  Unique computations: {len(computation_ids)}"
          f"  (expected: 5 — each request ran its own)")
    print()

    # ── With singleflight: 5 concurrent requests for the same user ───────
    print("=== WITH singleflight ===")
    start = time.perf_counter()
    results = await asyncio.gather(
        *[fire(base, "with-singleflight", "42") for _ in range(5)]
    )
    elapsed = time.perf_counter() - start

    computation_ids = {r["computation_id"] for r in results}
    for r in results:
        print(
            f"  user={r['user_id']}  "
            f"computation_id={r['computation_id']}  "
            f"took={r['elapsed_s']}s"
        )
    print(f"  --- {len(results)} requests in {elapsed:.2f}s total."
          f"  Unique computations: {len(computation_ids)}"
          f"  (expected: 1 — singleflight coalesced them)")
    print()

    # ── Different keys: no coalescing ────────────────────────────────────
    print("=== Singleflight — different keys ===")
    results = await asyncio.gather(
        *[fire(base, "with-singleflight", str(uid)) for uid in range(5)]
    )
    computation_ids = {r["computation_id"] for r in results}
    for r in results:
        print(f"  user={r['user_id']}  computation_id={r['computation_id']}")
    print(f"  Unique computations: {len(computation_ids)}"
          f"  (expected: 5 — different keys, no coalescing)")


if __name__ == "__main__":
    asyncio.run(main())