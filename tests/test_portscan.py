import dns.exception
import dns.resolver

from config import Config
from modules.portscan import PortScanModule


def test_portscan_reports_unresolvable(monkeypatch):
    def _raise(*a, **k):
        raise dns.exception.DNSException("nope")

    monkeypatch.setattr(dns.resolver, "resolve", _raise)
    result = PortScanModule().run("example.com", Config(cache=False))
    assert result["error"] == "Could not resolve domain IP"


def test_portscan_no_open_ports(monkeypatch):
    module = PortScanModule()
    monkeypatch.setattr(module, "_get_ips", lambda domain: ["203.0.113.1"])
    monkeypatch.setattr(module, "_check_port", lambda ip, port, timeout: False)
    result = module.run("example.com", Config(cache=False))
    assert result["target_ip"] == "203.0.113.1"
    assert result["total_open"] == 0
    assert result["open_ports"] == []


def test_service_map_known_ports():
    assert PortScanModule.SERVICE_MAP[443] == "HTTPS"
    assert PortScanModule.SERVICE_MAP[22] == "SSH"
