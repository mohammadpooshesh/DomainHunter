"""Shared helpers: domain parsing, validation, and HTTP client factories."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import httpx
import tldextract

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)
DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
}

_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


@dataclass
class ParsedDomain:
    """Structured representation of a parsed domain name."""

    domain: str
    subdomain: str
    domain_name: str
    suffix: str
    fqdn: str


class Utils:
    """Collection of stateless helper functions used across modules."""

    HTTP_TIMEOUT = 10

    @staticmethod
    def parse_domain(domain: str) -> ParsedDomain:
        """Split a domain into subdomain, registrable name, and suffix."""
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
        """Return True if the string looks like a valid bare domain name."""
        return bool(_DOMAIN_RE.match(domain))

    @staticmethod
    def normalize_url(url: str) -> str:
        """Ensure the URL has an https:// scheme and no trailing slash."""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url.rstrip("/")

    @staticmethod
    def create_client(timeout: int = 10, follow_redirects: bool = True) -> httpx.Client:
        """Create a configured synchronous HTTP client."""
        return httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=follow_redirects,
            headers=dict(DEFAULT_HEADERS),
        )

    @staticmethod
    def create_async_client(timeout: int = 10) -> httpx.AsyncClient:
        """Create a configured asynchronous HTTP client."""
        return httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers=dict(DEFAULT_HEADERS),
        )

    @staticmethod
    def safe_get(client: httpx.Client, url: str, **kwargs) -> Optional[httpx.Response]:
        """GET a URL, returning None on any transport-level error."""
        try:
            return client.get(url, **kwargs)
        except httpx.HTTPError:
            return None

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Replace filesystem-unsafe characters with underscores."""
        return re.sub(r"[^\w\-_. ]", "_", name)

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """Return a sorted, de-duplicated list of e-mail addresses found in text."""
        return sorted(set(_EMAIL_RE.findall(text)))
