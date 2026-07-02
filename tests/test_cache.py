from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.cache import Cache


class TestCache:
    @pytest.fixture
    def cache(self):
        tmp_dir = tempfile.mkdtemp()
        c = Cache(cache_dir=tmp_dir, ttl=3600)
        yield c
        import shutil
        try:
            c._init_db()
        except Exception:
            pass
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def test_set_and_get(self, cache):
        cache.set("key1", {"data": "value"})
        assert cache.get("key1") == {"data": "value"}

    def test_get_nonexistent(self, cache):
        assert cache.get("nonexistent") is None

    def test_delete(self, cache):
        cache.set("key1", "value")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_clear(self, cache):
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_ttl_expiry(self, cache):
        cache.set("key1", "value", ttl=0)
        import time
        time.sleep(0.1)
        assert cache.get("key1") is None

    def test_cleanup(self, cache):
        cache.set("key1", "value", ttl=0)
        import time
        time.sleep(0.1)
        cache.cleanup()
        assert cache.get("key1") is None
