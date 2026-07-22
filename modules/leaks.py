from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class LeaksModule:
    name = "leaks"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "leak_sources": [],
            "exposed_data": [],
            "note": "Checking public breach sources. This module checks only publicly available breach databases.",
        }
        client = Utils.create_client(config.timeout)
        try:
            leak_check_urls = [
                "https://haveibeenpwned.com/domain/" + domain,
                "https://breachdirectory.org/search?domain=" + domain,
            ]
            for url in leak_check_urls:
                response = Utils.safe_get(client, url)
                if response:
                    result["leak_sources"].append({
                        "url": url,
                        "status": response.status_code,
                    })

            github_response = Utils.safe_get(
                client,
                "https://api.github.com/search/code",
                headers={"Accept": "application/vnd.github.v3+json"},
                params={"q": domain + " password", "per_page": 5},
            )
            if github_response and github_response.status_code == 200:
                data = github_response.json()
                for item in data.get("items", [])[:5]:
                    result["exposed_data"].append({
                        "type": "github",
                        "repository": item.get("repository", {}).get("full_name", ""),
                        "path": item.get("path", ""),
                        "url": item.get("html_url", ""),
                    })

            pastebin_response = Utils.safe_get(
                client,
                "https://psbdmp.ws/api/search/" + domain,
            )
            if pastebin_response and pastebin_response.status_code == 200:
                try:
                    paste_data = pastebin_response.json()
                    for entry in (paste_data if isinstance(paste_data, list) else [])[:10]:
                        result["exposed_data"].append({
                            "type": "paste",
                            "id": entry.get("id", ""),
                            "title": entry.get("title", ""),
                            "date": entry.get("date", ""),
                        })
                except (ValueError, TypeError):
                    pass
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
