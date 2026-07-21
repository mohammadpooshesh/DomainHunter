import types

import dns.resolver

from modules.email import EmailModule


def test_extract_soa_email_converts_rname(monkeypatch):
    fake = [types.SimpleNamespace(rname="admin.example.com.")]
    monkeypatch.setattr(dns.resolver, "resolve", lambda *a, **k: fake)
    emails = EmailModule()._extract_soa_email("example.com")
    assert emails == ["admin@example.com"]


def test_extract_soa_email_handles_failure(monkeypatch):
    def _raise(*a, **k):
        raise RuntimeError("dns down")

    monkeypatch.setattr(dns.resolver, "resolve", _raise)
    assert EmailModule()._extract_soa_email("example.com") == []
