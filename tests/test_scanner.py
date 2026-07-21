from config import Config
from core.scanner import Scanner


class _OkModule:
    name = "ok"

    def run(self, domain, config):
        return {"value": domain}


class _BoomModule:
    name = "boom"

    def run(self, domain, config):
        raise RuntimeError("explode")


def test_scan_collects_module_results():
    scanner = Scanner(Config(cache=False))
    results = scanner.scan("example.com", [("ok", _OkModule())])
    assert results["ok"] == {"value": "example.com"}


def test_scan_captures_module_exceptions():
    scanner = Scanner(Config(cache=False))
    results = scanner.scan("example.com", [("boom", _BoomModule())])
    assert "error" in results["boom"]
    assert "explode" in results["boom"]["error"]
