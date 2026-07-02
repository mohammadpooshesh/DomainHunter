from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from config import Config


class TestConfig:
    def test_default_config(self):
        cfg = Config()
        assert cfg.timeout == 10
        assert cfg.threads == 30
        assert cfg.cache is True
        assert cfg.cache_ttl == 3600

    def test_load_from_file(self):
        data = {"timeout": 15, "threads": 50, "cache": False}
        tmp = Path(tempfile.mktemp(suffix=".yaml"))
        try:
            tmp.write_text(yaml.dump(data))
            cfg = Config.load(str(tmp))
            assert cfg.timeout == 15
            assert cfg.threads == 50
            assert cfg.cache is False
        finally:
            if tmp.exists():
                tmp.unlink()

    def test_load_from_env(self):
        os.environ["GITHUB_TOKEN"] = "test_token"
        cfg = Config.load()
        assert cfg.api.github_token == "test_token"
        del os.environ["GITHUB_TOKEN"]

    def test_load_nonexistent_file(self):
        cfg = Config.load("/nonexistent/config.yaml")
        assert cfg.timeout == 10
        assert cfg.threads == 30
