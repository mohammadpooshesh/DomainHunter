"""Runtime configuration for DomainHunter.

Configuration is sourced from (in increasing order of precedence):
1. Built-in defaults
2. Environment variables (for API credentials)
3. An optional YAML configuration file
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class APIConfig:
    """Optional third-party API credentials."""

    github_token: Optional[str] = None
    virustotal: Optional[str] = None
    shodan: Optional[str] = None
    securitytrails: Optional[str] = None
    censys_id: Optional[str] = None
    censys_secret: Optional[str] = None

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Build an APIConfig from well-known environment variables."""
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            virustotal=os.getenv("VIRUSTOTAL_API_KEY"),
            shodan=os.getenv("SHODAN_API_KEY"),
            securitytrails=os.getenv("SECURITYTRAILS_API_KEY"),
            censys_id=os.getenv("CENSYS_API_ID"),
            censys_secret=os.getenv("CENSYS_API_SECRET"),
        )


@dataclass
class Config:
    """Top-level configuration object passed to every module."""

    timeout: int = 10
    threads: int = 30
    cache: bool = True
    cache_ttl: int = 3600
    cache_dir: str = "cache"
    verbose: bool = False
    api: APIConfig = field(default_factory=APIConfig)
    output_dir: str = "output"
    reports_dir: str = "reports"

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration, overlaying a YAML file on top of env defaults."""
        cfg = cls(api=APIConfig.from_env())
        if path and Path(path).exists():
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            cfg._apply_file(data)
        return cfg

    def _apply_file(self, data: dict[str, Any]) -> None:
        """Overlay values read from a YAML config file onto this instance."""
        for key in ("timeout", "threads", "cache_ttl"):
            if data.get(key) is not None:
                setattr(self, key, int(data[key]))
        for key in ("cache", "verbose"):
            if data.get(key) is not None:
                setattr(self, key, bool(data[key]))
        for key in ("cache_dir", "output_dir", "reports_dir"):
            if data.get(key):
                setattr(self, key, str(data[key]))
        api_data = data.get("api", data)
        for key in (
            "github_token",
            "virustotal",
            "shodan",
            "securitytrails",
            "censys_id",
            "censys_secret",
        ):
            value = api_data.get(key)
            if value:
                setattr(self.api, key, value)
