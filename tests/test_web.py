import types

from core.utils import Utils
from modules.web import WebModule


def _patch_client(monkeypatch):
    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )


def test_web_parses_page(monkeypatch, response_cls, fake_config):
    html = (
        "<html><head><title>Example</title>"
        "<meta name='description' content='desc'></head>"
        "<body><a href='#'>x</a></body></html>"
    )
    resp = response_cls(status_code=200, text=html, headers={"Server": "nginx"})
    _patch_client(monkeypatch)
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: resp)
    result = WebModule().run("example.com", fake_config)
    assert result["status_code"] == 200
    assert result["title"] == "Example"
    assert result["server"] == "nginx"


def test_web_reports_connection_error(monkeypatch, fake_config):
    _patch_client(monkeypatch)
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: None)
    result = WebModule().run("example.com", fake_config)
    assert result["error"] == "Could not connect to domain"
