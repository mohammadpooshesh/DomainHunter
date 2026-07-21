"""Shared pytest fixtures and offline HTTP test doubles."""
from __future__ import annotations

import httpx
import pytest


class FakeResponse:
    """Minimal stand-in for httpx.Response used to keep tests offline."""

    def __init__(
        self,
        status_code: int = 200,
        text: str = "",
        json_data=None,
        headers=None,
        url: str = "https://example.com",
        content: bytes | None = None,
    ) -> None:
        self.status_code = status_code
        self.text = text
        self._json_data = json_data
        self.headers = httpx.Headers(headers or {})
        self.url = url
        self.content = content if content is not None else text.encode("utf-8")
        self.history: list = []
        self.encoding = "utf-8"
        self.http_version = "HTTP/1.1"

    def json(self):
        if self._json_data is None:
            raise ValueError("No JSON body")
        return self._json_data


@pytest.fixture
def response_cls():
    """Return the FakeResponse class for building HTTP doubles."""
    return FakeResponse


@pytest.fixture
def fake_config():
    """A Config with caching disabled so tests never touch SQLite."""
    from config import Config

    return Config(cache=False)
