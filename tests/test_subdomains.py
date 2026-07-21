import types

from core.utils import Utils
from modules.subdomains import SubdomainsModule


def test_subdomains_from_crtsh(monkeypatch, response_cls, fake_config):
    data = [{"name_value": "www.example.com\napi.example.com"}]
    resp = response_cls(status_code=200, json_data=data)
    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: resp)
    result = SubdomainsModule().run("example.com", fake_config)
    assert "www.example.com" in result["found"]
    assert result["total"] >= 2
