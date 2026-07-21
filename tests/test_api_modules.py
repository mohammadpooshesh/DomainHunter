import dns.exception
import dns.resolver

from config import Config
from modules.censys import CensysModule
from modules.securitytrails import SecurityTrailsModule
from modules.shodan import ShodanModule
from modules.virustotal import VirusTotalModule


def test_securitytrails_requires_key():
    result = SecurityTrailsModule().run("example.com", Config(cache=False))
    assert "error" in result
    assert "key" in result["error"].lower()


def test_virustotal_requires_key():
    result = VirusTotalModule().run("example.com", Config(cache=False))
    assert "error" in result
    assert "key" in result["error"].lower()


def test_shodan_requires_key():
    result = ShodanModule().run("example.com", Config(cache=False))
    assert "error" in result


def test_censys_requires_credentials():
    result = CensysModule().run("example.com", Config(cache=False))
    assert "error" in result


def test_shodan_reports_unresolvable(monkeypatch):
    cfg = Config(cache=False)
    cfg.api.shodan = "fake-key"

    def _raise(*a, **k):
        raise dns.exception.DNSException("nope")

    monkeypatch.setattr(dns.resolver, "resolve", _raise)
    result = ShodanModule().run("example.com", cfg)
    assert result["error"] == "Could not resolve domain IP"
