from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class SubdomainsModule:
    name = "subdomains"

    COMMON_SUBDOMAINS = [
        "www", "mail", "ftp", "admin", "api", "blog", "cdn", "dev",
        "staging", "test", "webmail", "vpn", "remote", "support",
        "help", "docs", "status", "portal", "beta", "app", "m",
        "shop", "store", "forum", "wiki", "news", "media", "assets",
        "img", "static", "css", "js", "download", "downloads",
        "calendar", "directory", "edu", "gov", "info", "intranet",
        "login", "mail2", "mx", "ns1", "ns2", "ns3", "ns4",
        "pop", "pop3", "smtp", "ssl", "stage", "upload",
        "uploads", "user", "users", "video", "demo",
    ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "found": [],
            "bruteforce_results": [],
            "total": 0,
        }
        ct_subdomains = self._get_crtsh_subdomains(domain, config)
        if ct_subdomains:
            result["found"].extend(ct_subdomains)

        if config.verbose:
            found_brute = self._bruteforce_subdomains(domain, config)
            result["bruteforce_results"] = found_brute
            for sd in found_brute:
                if sd not in result["found"]:
                    result["found"].append(sd)

        result["total"] = len(result["found"])
        return result

    def _get_crtsh_subdomains(self, domain: str, config: Config) -> list[str]:
        subdomains: list[str] = []
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(
                client,
                "https://crt.sh/",
                params={"q": "%." + domain, "output": "json"},
            )
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    seen: set[str] = set()
                    for entry in data:
                        names = entry.get("name_value", "").split("\n")
                        for name in names:
                            name = name.strip().lower()
                            if name.endswith("." + domain) and name not in seen:
                                seen.add(name)
                                subdomains.append(name)
                except (ValueError, TypeError):
                    pass
        except Exception:
            pass
        finally:
            client.close()
        return subdomains

    def _bruteforce_subdomains(self, domain: str, config: Config) -> list[str]:
        found: list[str] = []
        client = Utils.create_client(config.timeout, follow_redirects=False)
        try:
            for sd in self.COMMON_SUBDOMAINS:
                fqdn = sd + "." + domain
                try:
                    response = Utils.safe_get(client, "https://" + fqdn)
                    if response is not None:
                        found.append(fqdn)
                except Exception:
                    pass
        finally:
            client.close()
        return found
