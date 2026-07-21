import types

from core.utils import Utils
from modules.favicon import FaviconModule


def test_favicon_hashes_icon(monkeypatch, response_cls, fake_config):
    icon_bytes = b"\x00\x01\x02\x03icon"

    def fake_get(client, url, **kwargs):
        if url.endswith(".ico"):
            return response_cls(
                status_code=200, content=icon_bytes, headers={"Content-Type": "image/x-icon"}
            )
        return response_cls(status_code=200, text="<html><head></head></html>")

    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )
    monkeypatch.setattr(Utils, "safe_get", fake_get)
    result = FaviconModule().run("example.com", fake_config)
    assert result["url"].endswith("/favicon.ico")
    assert "md5" in result
    assert result["size"] == len(icon_bytes)
