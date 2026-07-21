from core.cache import Cache


def test_set_and_get_roundtrip(tmp_path):
    cache = Cache(cache_dir=str(tmp_path), ttl=3600)
    cache.set("k", {"a": 1})
    assert cache.get("k") == {"a": 1}


def test_expired_entry_returns_none(tmp_path):
    cache = Cache(cache_dir=str(tmp_path), ttl=3600)
    cache.set("k", "v", ttl=-1)
    assert cache.get("k") is None


def test_delete_and_clear(tmp_path):
    cache = Cache(cache_dir=str(tmp_path), ttl=3600)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.delete("a")
    assert cache.get("a") is None
    assert cache.get("b") == 2
    cache.clear()
    assert cache.get("b") is None


def test_missing_key_returns_none(tmp_path):
    cache = Cache(cache_dir=str(tmp_path), ttl=10)
    assert cache.get("nope") is None
