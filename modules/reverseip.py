from __future__ import annotations

from typing import Any

import dns.resolver
from dns.exception import DNSException

from config import Config


class ReverseIPModule:
    name = "reverse_ip"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ip_addresses": [],
            "domains_on_same_ip": [],
        }
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=10)
            ips = [str(r) for r in answers]
            result["ip_addresses"] = ips

            for ip in ips:
                domains = self._reverse_dns_lookup(ip)
                if domains:
                    result["domains_on_same_ip"].extend(domains)

            result["total_ips"] = len(ips)
            result["total_domains_shared"] = len(result["domains_on_same_ip"])
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException) as e:
            result["error"] = str(e)
        return result

    def _reverse_dns_lookup(self, ip: str) -> list[str]:
        domains: list[str] = []
        try:
            answers = dns.resolver.resolve_address(ip, lifetime=10)
            for rdata in answers:
                domain = str(rdata).strip().rstrip(".")
                if domain:
                    domains.append(domain)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return domains
