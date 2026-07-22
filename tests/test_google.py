from config import Config
from modules.google import GoogleModule


def test_google_generates_encoded_queries():
    result = GoogleModule().run("example.com", Config(cache=False))
    assert result["total_queries"] == len(result["queries"])
    first = result["queries"][0]
    assert first["google_url"].startswith("https://www.google.com/search?q=")
    assert "bing_url" in first
    assert "duckduckgo_url" in first


def test_google_urls_have_no_literal_braces():
    result = GoogleModule().run("example.com", Config(cache=False))
    for q in result["queries"]:
        assert "{" not in q["google_url"]
        assert "}" not in q["google_url"]
