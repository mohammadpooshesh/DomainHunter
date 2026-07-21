from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from config import Config


class GoogleModule:
    name = "google"

    DORK_QUERIES = [
        "site:{domain}",
        '"{domain}"',
        "site:github.com {domain}",
        "site:gitlab.com {domain}",
        "filetype:pdf {domain}",
        "filetype:xlsx {domain}",
        "filetype:doc {domain}",
        "filetype:csv {domain}",
        "filetype:xml {domain}",
        "filetype:sql {domain}",
        "inurl:{domain} intitle:index.of",
        "intitle:{domain} \"confidential\"",
    ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "queries": [],
            "note": "These are search engine queries for manual use. "
                     "DomainHunter generates them for you to run in a browser.",
        }
        for q in self.DORK_QUERIES:
            query = q.format(domain=domain)
            encoded = quote_plus(query)
            result["queries"].append({
                "query": query,
                "google_url": "https://www.google.com/search?q=" + encoded,
                "bing_url": "https://www.bing.com/search?q=" + encoded,
                "duckduckgo_url": "https://duckduckgo.com/?q=" + encoded,
            })
        result["total_queries"] = len(result["queries"])
        return result
