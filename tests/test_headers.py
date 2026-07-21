import types

from core.utils import Utils
from modules.headers import HeadersModule


def test_headers_scores_security(monkeypatch, response_cls, fake_config):
    headers = {
        "Server": "nginx",
        "Strict-Transport-Security": "max-age=63072000",
        "X-Frame-Options": "DENY",
    }
    resp = response_cls(status_code=200, text="ok", headers=headers)
    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: resp)
    result = HeadersModule().run("example.com", fake_config)
    assert result["security_headers"]["Strict-Transport-Security"] == "max-age=63072000"
    assert result["security_score"]["score"] >= 2
    assert result["security_score"]["grade"] in {"A", "B", "C", "D", "F"}


def test_calculate_score_direct():
    module = HeadersModule()
    security = {h: None for h in HeadersModule.SECURITY_HEADERS}
    score = module._calculate_score(security)
    assert score["score"] == 0
    assert score["grade"] == "F"
