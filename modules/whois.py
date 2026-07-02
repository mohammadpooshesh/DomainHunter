from __future__ import annotations

from typing import Any, Optional

import whois as whois_lib

from config import Config


class WhoisModule:
    name = "whois"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        try:
            w = whois_lib.whois(domain)
            result["registrar"] = self._clean(w.registrar)
            result["creation_date"] = self._format_date(w.creation_date)
            result["updated_date"] = self._format_date(w.updated_date)
            result["expiration_date"] = self._format_date(w.expiration_date)
            result["name_servers"] = self._clean_list(w.name_servers)
            result["dnssec"] = self._clean(w.dnssec)
            result["status"] = self._clean_list(w.status)
            result["registrant_name"] = self._clean(w.name)
            result["registrant_organization"] = self._clean(w.org)
            result["registrant_country"] = self._clean(w.country)
            result["emails"] = self._clean_list(w.emails)
            if result.get("registrant_name") == "Privacy Protected" or \
               any("privacy" in str(s).lower() for s in (result.get("status") or [])):
                result["privacy_protected"] = True
            result["raw"] = str(w.text)[:2000] if hasattr(w, "text") and w.text else None
        except Exception as e:
            result["error"] = str(e)
        return result

    @staticmethod
    def _clean(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, list):
            return str(value[0]) if value else None
        return str(value).strip() or None

    @staticmethod
    def _clean_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if v]
        return [str(value).strip()]

    @staticmethod
    def _format_date(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, list):
            value = value[0] if value else None
        if value:
            try:
                return value.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                return str(value)
        return None
