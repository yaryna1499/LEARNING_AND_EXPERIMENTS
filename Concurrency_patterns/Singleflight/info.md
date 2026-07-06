# Request Coalescing (Single-Flight Pattern)

Request Coalescing (often implemented as Single-Flight) prevents duplicate work by ensuring that only one concurrent request performs an expensive operation for a given key, while the others wait and reuse the same result.

It is commonly used to prevent Cache Stampede, but it is also useful for high-traffic endpoints where many identical requests arrive simultaneously, reducing unnecessary database queries, API calls, or other expensive work.

## Definitions

- **Cache Stampede** = the problem (many concurrent cache misses overload the backend).
- **Request Coalescing** = the pattern.
- **Single-Flight** = a common implementation of that pattern (popularized by Go).

## References

- <https://medium.com/@bhagyarana80/7-fastapi-concurrency-patterns-for-sub-50-ms-apis-d86c1b5e0c41>

## In-flight Operations

"In-flight" refers to work that has started but has not completed yet.

Examples:
- **in-flight request**: a request has been sent, but the response has not arrived yet.
- **in-flight operation**: an operation is currently executing.
- **in-flight task**: a task is still running and has not finished.

In Single-Flight implementations, an `inflight` dictionary typically stores ongoing operations (e.g., Future/Task objects) so concurrent callers can wait for the same result instead of starting duplicate work.

## Example 1: Basic Implementation

```python
inflight = {}

async def get_user(user_id):
    key = f"user:{user_id}"

    value = await redis.get(key)
    if value:
        return value

    if key in inflight:
        return await inflight[key]

    future = asyncio.create_task(load_user(user_id))
    inflight[key] = future

    try:
        value = await future
        await redis.set(key, value, ex=300)
        return value
    finally:
        del inflight[key]
```

## Example 2: From Article

```python
import time, asyncio
from collections import defaultdict

CACHE_TTL_MS = 300
_cache: dict[str, tuple[float, dict]] = {}
_inflight: dict[str, asyncio.Future] = defaultdict(asyncio.Future)

async def get_hot(key: str):
    now = time.time() * 1000
    if key in _cache and now - _cache[key][0] < CACHE_TTL_MS:
        return _cache[key][1]

    fut = _inflight.get(key)
    if not fut or fut.done():
        fut = asyncio.get_running_loop().create_future()
        _inflight[key] = fut
        try:
            data = (await client.get(f"https://svc/hot/{key}")).json()
            _cache[key] = (now, data)
            fut.set_result(data)
        except Exception as e:
            fut.set_exception(e)
        finally:
            # Let the future live for late waiters; cleanup happens naturally.
            pass
    return await fut

@app.get("/hot/{key}")
async def hot(key: str):
    return await get_hot(key)
```