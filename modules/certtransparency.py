from __future__ import annotations

from typing import Any

from core.utils import Utils

from config import Config


class CertTransparencyModule:
    name = "certificate_transparency"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"certificates": [], "subdomains": []}
        try:
            client = Utils.create_client(config.timeout)
            response = Utils.safe_get(
                client,
                f"https://crt.sh/?q=%25.{domain}&output=json",
            )
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    seen: set[str] = set()
                    for entry in data:
                        cert: dict[str, Any] = {
                            "id": entry.get("id"),
                            "issuer_ca_id": entry.get("issuer_ca_id"),
                            "issuer_name": entry.get("issuer_name"),
                            "common_name": entry.get("common_name"),
                            "name_value": entry.get("name_value"),
                            "not_before": entry.get("not_before"),
                            "not_after": entry.get("not_after"),
                            "serial_number": entry.get("serial_number"),
                        }
                        result["certificates"].append(cert)
                        names = entry.get("name_value", "").split("\n")
                        for name in names:
                            name = name.strip().lower()
                            if name.endswith(f".{domain}") and name not in seen:
                                seen.add(name)
                                result["subdomains"].append(name)
                except (ValueError, TypeError):
                    pass
            client.close()
        except Exception as e:
            result["error"] = str(e)
        return result
