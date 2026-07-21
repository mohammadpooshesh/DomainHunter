from core.utils import Utils


def test_is_valid_domain_accepts_real_domains():
    assert Utils.is_valid_domain("example.com")
    assert Utils.is_valid_domain("sub.example.co.uk")


def test_is_valid_domain_rejects_bad_input():
    assert not Utils.is_valid_domain("not a domain")
    assert not Utils.is_valid_domain("http://example.com")
    assert not Utils.is_valid_domain("")


def test_normalize_url_adds_scheme_and_strips_slash():
    assert Utils.normalize_url("example.com") == "https://example.com"
    assert Utils.normalize_url("http://example.com/") == "http://example.com"


def test_parse_domain_extracts_parts():
    parsed = Utils.parse_domain("blog.example.com")
    assert parsed.domain_name == "example"
    assert parsed.suffix == "com"
    assert parsed.subdomain == "blog"


def test_extract_emails_dedupes_and_sorts():
    text = "b@example.com and a@example.com and b@example.com"
    assert Utils.extract_emails(text) == ["a@example.com", "b@example.com"]


def test_sanitize_filename_replaces_unsafe_chars():
    assert Utils.sanitize_filename("a/b:c*d") == "a_b_c_d"
