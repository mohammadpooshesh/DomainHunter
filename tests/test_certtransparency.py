import types

from core.utils import Utils
from modules.certtransparency import CertTransparencyModule


def test_certtransparency_extracts_subdomains(monkeypatch, response_cls, fake_config):
    data = [
        {"id": 1, "name_value": "a.example.com\nb.example.com", "common_name": "a.example.com"},
        {"id": 2, "name_value": "a.example.com", "common_name": "a.example.com"},
    ]
    resp = response_cls(status_code=200, json_data=data)
    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: resp)
    result = CertTransparencyModule().run("example.com", fake_config)
    assert "a.example.com" in result["subdomains"]
    assert "b.example.com" in result["subdomains"]
    assert len(result["certificates"]) == 2
