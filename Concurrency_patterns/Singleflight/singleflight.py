"""
Singleflight — coalesce concurrent calls for the same key into one.

When N callers request the same key simultaneously, only one does the work;
the rest share its result.  After completion the key is forgotten (no caching).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class Singleflight:
    """Zero-dependency asyncio singleflight, modelled on Go's sync/singleflight."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._futures: dict[str, asyncio.Future[Any]] = {}

    async def execute(self, key: str, fn: Callable[[], Awaitable[T]]) -> T:
        """Run *fn* once for *key*; concurrent callers share the same result.

        If another caller is already executing for this *key*, wait for their
        result instead of duplicating work.
        """
        async with self._lock:
            if key in self._futures:
                fut: asyncio.Future[Any] = self._futures[key]

        if key in self._futures:
            # Follower path — someone else is already computing
            return await asyncio.shield(fut)

        # Leader path — first caller for this key
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        async with self._lock:
            self._futures[key] = fut

        try:
            result = await fn()
            if not fut.done():
                fut.set_result(result)
            return result  # type: ignore[return-value]
        except BaseException as exc:
            if not fut.done():
                fut.set_exception(exc)
            raise
        finally:
            async with self._lock:
                if self._futures.get(key) is fut:
                    del self._futures[key]