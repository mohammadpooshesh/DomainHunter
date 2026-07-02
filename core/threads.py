from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterator


class ThreadManager:
    def __init__(self, max_workers: int = 30) -> None:
        self.max_workers = max_workers

    def run_batch(
        self,
        tasks: list[tuple[Callable, list[Any], dict[str, Any]]],
    ) -> list[Any]:
        results: list[Any] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(fn, *args, **kwargs): (fn, args, kwargs)
                for fn, args, kwargs in tasks
            }
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception:
                    results.append(None)
        return results

    def run_batch_simple(
        self,
        func: Callable,
        items: list[Any],
        **kwargs: Any,
    ) -> Iterator[Any]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(func, item, **kwargs): item for item in items}
            for future in as_completed(futures):
                try:
                    yield future.result()
                except Exception:
                    yield None

    def run_map(self, func: Callable, items: list[Any]) -> list[Any]:
        results: list[Any] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for result in executor.map(func, items):
                results.append(result)
        return results
