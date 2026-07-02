from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class APIConfig:
    github_token: Optional[str] = None
    virustotal: Optional[str] = None
    shodan: Optional[str] = None
    securitytrails: Optional[str] = None
    censys_id: Optional[str] = None
    censys_secret: Optional[str] = None


@dataclass
class Config:
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
    def load(cls, path: Optional[str] = None) -> Config:
        cfg = cls()
        if path and Path(path).exists():
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            if "timeout" in data:
                cfg.timeout = int(data["timeout"])
            if "threads" in data:
                cfg.threads = int(data["threads"])
            if "cache" in data:
                cfg.cache = bool(data["cache"])
            if "cache_ttl" in data:
                cfg.cache_ttl = int(data["cache_ttl"])
            if "verbose" in data:
                cfg.verbose = bool(data["verbose"])
            api_data = data.get("api", data)
            cfg.api.github_token = api_data.get("github_token") or os.getenv("GITHUB_TOKEN")
            cfg.api.virustotal = api_data.get("virustotal") or os.getenv("VIRUSTOTAL_API_KEY")
            cfg.api.shodan = api_data.get("shodan") or os.getenv("SHODAN_API_KEY")
            cfg.api.securitytrails = api_data.get("securitytrails") or os.getenv("SECURITYTRAILS_API_KEY")
            cfg.api.censys_id = api_data.get("censys_id") or os.getenv("CENSYS_API_ID")
            cfg.api.censys_secret = api_data.get("censys_secret") or os.getenv("CENSYS_API_SECRET")
        else:
            cfg.api.github_token = os.getenv("GITHUB_TOKEN")
            cfg.api.virustotal = os.getenv("VIRUSTOTAL_API_KEY")
            cfg.api.shodan = os.getenv("SHODAN_API_KEY")
            cfg.api.securitytrails = os.getenv("SECURITYTRAILS_API_KEY")
            cfg.api.censys_id = os.getenv("CENSYS_API_ID")
            cfg.api.censys_secret = os.getenv("CENSYS_API_SECRET")
        return cfg
