from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import httpx
import tldextract


@dataclass
class ParsedDomain:
    domain: str
    subdomain: str
    domain_name: str
    suffix: str
    fqdn: str


class Utils:
    HTTP_TIMEOUT = 10

    @staticmethod
    def parse_domain(domain: str) -> ParsedDomain:
        extracted = tldextract.extract(domain)
        return ParsedDomain(
            domain=domain,
            subdomain=extracted.subdomain,
            domain_name=extracted.domain,
            suffix=extracted.suffix,
            fqdn=extracted.fqdn or domain,
        )

    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        return bool(re.match(pattern, domain))

    @staticmethod
    def normalize_url(url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url.rstrip("/")

    @staticmethod
    def create_client(timeout: int = 10, follow_redirects: bool = True) -> httpx.Client:
        return httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=follow_redirects,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

    @staticmethod
    def create_async_client(timeout: int = 10) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

    @staticmethod
    def safe_get(client: httpx.Client, url: str, **kwargs) -> Optional[httpx.Response]:
        try:
            return client.get(url, **kwargs)
        except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError, httpx.RemoteProtocolError, httpx.HTTPStatusError):
            return None

    @staticmethod
    def sanitize_filename(name: str) -> str:
        return re.sub(r"[^\w\-_. ]", "_", name)

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        return list(set(re.findall(pattern, text)))
