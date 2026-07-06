"""
FastAPI app demonstrating the singleflight concurrency pattern.

Two endpoints both call the same expensive async function (simulated DB query
or external API call).  One uses singleflight; the other doesn't.

Hit /with-singleflight and /without-singleflight with concurrent requests to
see the difference: singleflight coalesces N calls into one actual execution.
"""

from __future__ import annotations

import asyncio
import time

import uvicorn
from fastapi import FastAPI

from singleflight import Singleflight

app = FastAPI(title="Singleflight Demo")
sf = Singleflight()

# ── Simulated expensive operation ─────────────────────────────────────────────

_request_counter = 0
_computation_lock = asyncio.Lock()


async def expensive_lookup(user_id: str) -> dict:
    """Pretend this is a slow DB query or remote API call.

    Each *actual* execution increments a counter so the caller can verify
    how many times the work really ran.
    """
    global _request_counter
    async with _computation_lock:
        _request_counter += 1
        n = _request_counter

    await asyncio.sleep(2)  # simulate I/O latency

    return {
        "user_id": user_id,
        "name": f"User-{user_id}",
        "computation_id": n,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────


@app.get("/without-singleflight/{user_id}")
async def without_singleflight(user_id: str):
    """Naive endpoint — every concurrent request calls expensive_lookup again."""
    start = time.perf_counter()
    result = await expensive_lookup(user_id)
    elapsed = time.perf_counter() - start
    return {**result, "elapsed_s": round(elapsed, 2)}


@app.get("/with-singleflight/{user_id}")
async def with_singleflight(user_id: str):
    """Singleflight endpoint — concurrent requests share one execution."""
    start = time.perf_counter()
    result = await sf.execute(user_id, lambda: expensive_lookup(user_id))
    elapsed = time.perf_counter() - start
    return {**result, "elapsed_s": round(elapsed, 2)}

# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)