import types

from core.utils import Utils
from modules.technologies import TechnologiesModule


def test_detects_wordpress_and_nginx(monkeypatch, response_cls, fake_config):
    html = "<html><body>wp-content/themes</body></html>"
    resp = response_cls(status_code=200, text=html, headers={"Server": "nginx/1.18"})
    monkeypatch.setattr(
        Utils, "create_client", lambda *a, **k: types.SimpleNamespace(close=lambda: None)
    )
    monkeypatch.setattr(Utils, "safe_get", lambda *a, **k: resp)
    result = TechnologiesModule().run("example.com", fake_config)
    names = {t["name"] for t in result["technologies"]}
    assert "WordPress" in names
    assert "Nginx" in names
