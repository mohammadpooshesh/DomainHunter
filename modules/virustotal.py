from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class VirusTotalModule:
    name = "virustotal"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        api_key = config.api.virustotal
        if not api_key:
            result["error"] = "No VirusTotal API key configured"
            return result

        headers = {"x-apikey": api_key, "Accept": "application/json"}
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(
                client,
                "https://www.virustotal.com/api/v3/domains/" + domain,
                headers=headers,
            )
            if response and response.status_code == 200:
                data = response.json()
                attributes = data.get("data", {}).get("attributes", {})
                last_analysis = attributes.get("last_analysis_results", {})
                stats = attributes.get("last_analysis_stats", {})
                result["malicious"] = stats.get("malicious", 0)
                result["suspicious"] = stats.get("suspicious", 0)
                result["harmless"] = stats.get("harmless", 0)
                result["undetected"] = stats.get("undetected", 0)
                result["total_votes"] = attributes.get("total_votes", {})
                result["reputation"] = attributes.get("reputation", 0)
                result["categories"] = attributes.get("categories", {})
                resolutions = attributes.get("resolutions", [])
                result["resolutions"] = [
                    {"ip_address": r.get("ip_address"), "date": r.get("date")}
                    for r in resolutions[:20]
                ]
                analysis_results = {}
                for engine, res in last_analysis.items():
                    analysis_results[engine] = {
                        "category": res.get("category"),
                        "result": res.get("result"),
                    }
                result["analysis_results"] = analysis_results
            elif response and response.status_code == 404:
                result["error"] = "Domain not found in VirusTotal"
            elif response:
                result["error"] = f"API returned {response.status_code}"
            else:
                result["error"] = "No response from VirusTotal"
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
