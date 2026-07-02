from __future__ import annotations

from typing import Any

import dns.resolver
from dns.exception import DNSException

from config import Config
from core.utils import Utils


class ShodanModule:
    name = "shodan"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        api_key = config.api.shodan
        if not api_key:
            result["error"] = "No Shodan API key configured"
            return result

        ips = self._get_ips(domain)
        if not ips:
            result["error"] = "Could not resolve domain IP"
            return result

        client = Utils.create_client(config.timeout)
        headers = {"Accept": "application/json"}
        try:
            for ip in ips:
                response = Utils.safe_get(
                    client,
                    f"https://api.shodan.io/shodan/host/{ip}?key={api_key}",
                    headers=headers,
                )
                if response and response.status_code == 200:
                    data = response.json()
                    ip_data: dict[str, Any] = {
                        "ip": ip,
                        "ports": data.get("ports", []),
                        "hostnames": data.get("hostnames", []),
                        "org": data.get("org", ""),
                        "isp": data.get("isp", ""),
                        "country": data.get("country_name", ""),
                        "city": data.get("city", ""),
                        "os": data.get("os", ""),
                        "vulns": data.get("vulns", []),
                    }
                    services = []
                    for service_data in data.get("data", []):
                        services.append({
                            "port": service_data.get("port"),
                            "transport": service_data.get("transport"),
                            "product": service_data.get("product", ""),
                            "version": service_data.get("version", ""),
                        })
                    ip_data["services"] = services
                    result[ip] = ip_data
                elif response and response.status_code == 403:
                    result["error"] = "Invalid Shodan API key"
                    break
            if not result.get("error") and not any(k.startswith("1") or k.startswith("2") for k in result):
                result["error"] = "No data found on Shodan"
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result

    def _get_ips(self, domain: str) -> list[str]:
        ips: list[str] = []
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=10)
            ips = [str(r) for r in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return ips
