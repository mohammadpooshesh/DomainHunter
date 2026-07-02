from __future__ import annotations

from typing import Any

from config import Config
from core.cache import Cache
from core.logger import Logger
from core.threads import ThreadManager


class Scanner:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.log = Logger.get(verbose=config.verbose)
        self.cache = Cache(cache_dir=config.cache_dir, ttl=config.cache_ttl) if config.cache else None
        self.threads = ThreadManager(max_workers=config.threads)
        self.results: dict[str, Any] = {}

    def run_module(self, name: str, module: Any, domain: str) -> None:
        cache_key = f"{name}:{domain}" if self.cache else None
        if self.cache and cache_key:
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.log.debug(f"[{name}] loaded from cache")
                self.results[name] = cached
                return

        self.log.debug(f"[{name}] running...")
        try:
            result = module.run(domain, self.config)
            self.results[name] = result
            if self.cache and cache_key:
                self.cache.set(cache_key, result)
            if result and result.get("error"):
                self.log.fail(f"[{name}] {result['error']}")
            else:
                self.log.success(f"[{name}] completed")
        except Exception as e:
            self.log.fail(f"[{name}] failed: {e}")
            self.results[name] = {"error": str(e)}

    def scan(self, domain: str, modules: list[tuple[str, Any]]) -> dict[str, Any]:
        self.log.section(f"Scanning: {domain}")
        self.results = {}
        for name, module in modules:
            self.run_module(name, module, domain)
        return self.results
