from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class SecurityTrailsModule:
    name = "securitytrails"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        api_key = config.api.securitytrails
        if not api_key:
            result["error"] = "No SecurityTrails API key configured"
            return result

        headers = {"APIKEY": api_key, "Accept": "application/json"}
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(
                client,
                "https://api.securitytrails.com/v1/domain/" + domain,
                headers=headers,
            )
            if response and response.status_code == 200:
                data = response.json()
                result["current_dns"] = {
                    "a": data.get("current_dns", {}).get("a", {}).get("values", []),
                    "mx": data.get("current_dns", {}).get("mx", {}).get("values", []),
                    "ns": data.get("current_dns", {}).get("ns", {}).get("values", []),
                    "txt": data.get("current_dns", {}).get("txt", {}).get("values", []),
                    "soa": data.get("current_dns", {}).get("soa", {}).get("values", []),
                }
                result["alexa_rank"] = data.get("alexa_rank")
                result["hostname"] = data.get("hostname")
                result["mx"] = data.get("mx", [])
            elif response and response.status_code == 403:
                result["error"] = "Invalid SecurityTrails API key"
            else:
                result["error"] = f"API returned {response.status_code if response else 'no response'}"

            subdomains_response = Utils.safe_get(
                client,
                "https://api.securitytrails.com/v1/domain/" + domain + "/subdomains",
                headers=headers,
            )
            if subdomains_response and subdomains_response.status_code == 200:
                sd_data = subdomains_response.json()
                result["subdomains"] = sd_data.get("subdomains", [])
                result["subdomain_count"] = len(result["subdomains"])
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
