from __future__ import annotations

from core.utils import Utils


class TestUtils:
    def test_parse_domain(self):
        parsed = Utils.parse_domain("www.example.com")
        assert parsed.domain_name == "example"
        assert parsed.suffix == "com"
        assert parsed.subdomain == "www"

    def test_parse_domain_from_url(self):
        parsed = Utils.parse_domain("https://www.example.com/path")
        assert parsed.fqdn == "www.example.com"

    def test_is_valid_domain(self):
        assert Utils.is_valid_domain("example.com")
        assert Utils.is_valid_domain("www.example.co.uk")
        assert not Utils.is_valid_domain("not a domain")
        assert not Utils.is_valid_domain("")
        assert not Utils.is_valid_domain("http://example.com")

    def test_clean_domain(self):
        assert Utils.clean_domain("https://www.example.com/a") == "www.example.com"
        assert Utils.clean_domain("example.com/") == "example.com"
        assert Utils.clean_domain("EXAMPLE.COM.") == "example.com"

    def test_normalize_url(self):
        assert Utils.normalize_url("example.com") == "https://example.com"
        assert Utils.normalize_url("http://example.com") == "http://example.com"
        assert Utils.normalize_url("https://example.com/") == "https://example.com"

    def test_extract_emails(self):
        text = "Contact us at user@example.com or admin@test.org"
        emails = Utils.extract_emails(text)
        assert "user@example.com" in emails
        assert "admin@test.org" in emails

    def test_sanitize_filename(self):
        assert Utils.sanitize_filename("test/file:name") == "test_file_name"

    def test_extract_emails_none(self):
        assert Utils.extract_emails("no emails here") == []
