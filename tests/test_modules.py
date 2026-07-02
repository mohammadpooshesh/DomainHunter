from __future__ import annotations

from unittest.mock import patch

import pytest

from config import Config
from modules.dns import DNSModule
from modules.whois import WhoisModule
from modules.google import GoogleModule
from modules.portscan import PortScanModule


class TestModules:
    @pytest.fixture
    def config(self):
        return Config()

    def test_dns_module_init(self):
        module = DNSModule()
        assert module.name == "dns"

    def test_whois_module_init(self):
        module = WhoisModule()
        assert module.name == "whois"

    def test_google_module_generates_queries(self, config):
        module = GoogleModule()
        result = module.run("example.com", config)
        assert "queries" in result
        assert len(result["queries"]) > 0
        assert any("example.com" in q["query"] for q in result["queries"])
        assert result["queries"][0]["google_url"].startswith("https://www.google.com/search")

    @patch("socket.create_connection")
    def test_portscan_no_open_ports(self, mock_socket, config):
        mock_socket.side_effect = ConnectionRefusedError()
        module = PortScanModule()
        result = module.run("1.2.3.4", config)
        assert "open_ports" in result
        assert len(result["open_ports"]) == 0

    def test_whois_clean(self):
        module = WhoisModule()
        assert module._clean(None) is None
        assert module._clean("  test  ") == "test"
        assert module._clean(["a", "b"]) == "a"
        assert module._clean(123) == "123"
