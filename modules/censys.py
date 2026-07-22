from __future__ import annotations

from typing import Any

import dns.resolver
from dns.exception import DNSException

from config import Config
from core.utils import Utils


class CensysModule:
    name = "censys"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        api_id = config.api.censys_id
        api_secret = config.api.censys_secret
        if not api_id or not api_secret:
            result["error"] = "Censys API credentials not configured"
            return result

        ips = self._get_ips(domain)
        if not ips:
            result["error"] = "Could not resolve domain IP"
            return result

        client = Utils.create_client(config.timeout)
        auth = (api_id, api_secret)
        try:
            for ip in ips:
                response = Utils.safe_get(
                    client,
                    "https://search.censys.io/api/v2/hosts/" + ip,
                    auth=auth,
                )
                if response and response.status_code == 200:
                    data = response.json()
                    res = data.get("result", {})
                    services = []
                    for svc in res.get("services", []):
                        services.append({
                            "port": svc.get("port"),
                            "service_name": svc.get("service_name"),
                            "transport_protocol": svc.get("transport_protocol"),
                        })
                    location = res.get("location", {})
                    ip_data: dict[str, Any] = {
                        "ip": ip,
                        "services": services,
                        "location": {
                            "country": location.get("country", ""),
                            "city": location.get("city", ""),
                            "coordinates": location.get("coordinates", {}),
                        },
                        "autonomous_system": res.get("autonomous_system", {}),
                    }
                    result[ip] = ip_data
                elif response and response.status_code == 403:
                    result["error"] = "Invalid Censys API credentials"
                    break
                elif response and response.status_code == 404:
                    result[ip] = {"ip": ip, "error": "Not found on Censys"}
            if not result.get("error") and not result:
                result["error"] = "No data found"
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
