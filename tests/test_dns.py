import dns.exception
import dns.resolver

from config import Config
from modules.dns import DNSModule


def test_run_handles_no_records(monkeypatch):
    def _raise(*args, **kwargs):
        raise dns.exception.DNSException("no dns")

    monkeypatch.setattr(dns.resolver, "resolve", _raise)
    result = DNSModule().run("example.com", Config(cache=False))
    assert result["a"] == []
    assert result["mx"] == []
    assert result["soa"] is None
    assert result["spf"] == []
    assert "axfr" in result
