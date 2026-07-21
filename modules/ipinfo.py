from __future__ import annotations

from typing import Any, Optional

import dns.resolver
from dns.exception import DNSException
from ipwhois import IPWhois
from ipwhois.exceptions import BaseIpwhoisException

from config import Config
from core.utils import Utils


class IPInfoModule:
    name = "ip_info"

    CLOUD_PROVIDERS: dict[str, list[str]] = {
        "AWS": ["amazonaws", "aws", "ec2"],
        "Google Cloud": ["googleusercontent", "gce", "goog"],
        "Azure": ["azure", "microsoft"],
        "DigitalOcean": ["digitalocean"],
        "Linode": ["linode"],
        "Vultr": ["vultr"],
        "Hetzner": ["hetzner"],
        "OVH": ["ovh"],
        "Cloudflare": ["cloudflare"],
    }

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        ips = self._get_ips(domain)
        if not ips:
            result["error"] = "Could not resolve IP"
            return result

        result["ip_addresses"] = ips
        ip_data: list[dict[str, Any]] = []
        for ip in ips:
            info = self._get_ip_info(ip, config)
            if info:
                ip_data.append(info)
        result["ip_details"] = ip_data
        if ip_data:
            result["asn"] = ip_data[0].get("asn")
            result["asn_description"] = ip_data[0].get("asn_description")
            result["organization"] = ip_data[0].get("organization")
            result["country"] = ip_data[0].get("country")
            result["region"] = ip_data[0].get("region")
            result["city"] = ip_data[0].get("city")
            result["cloud_provider"] = ip_data[0].get("cloud_provider")
            result["abuse_contact"] = ip_data[0].get("abuse_contact")
        return result

    def _get_ips(self, domain: str) -> list[str]:
        ips: list[str] = []
        try:
            answers = dns.resolver.resolve(domain, "A", lifetime=10)
            ips = [str(r) for r in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return ips

    def _get_ip_info(self, ip: str, config: Config) -> Optional[dict[str, Any]]:
        info: dict[str, Any] = {"ip": ip}
        try:
            obj = IPWhois(ip)
            results = obj.lookup_rdap(depth=1)
            if results:
                info["asn"] = results.get("asn")
                info["asn_description"] = results.get("asn_description")
                info["asn_country_code"] = results.get("asn_country_code")
                network = results.get("network", {})
                info["organization"] = network.get("name", "")
                info["cidr"] = network.get("cidr", "")
                entities = results.get("entities", {})
                info["country"] = network.get("country", "")
                info["region"] = ""
                info["city"] = ""
                info["abuse_contact"] = ""
                entities_dict = entities if isinstance(entities, dict) else {}
                for entity_data in entities_dict.values():
                    vcard_array = entity_data.get("vcardArray", []) if isinstance(entity_data, dict) else []
                    for item in vcard_array:
                        if isinstance(item, list):
                            for entry in item:
                                if isinstance(entry, list) and len(entry) >= 3:
                                    if entry[0] == "adr":
                                        adr_details = entry[1].get("label", "") if isinstance(entry[1], dict) else str(entry[1])
                                        info["region"] = adr_details
                                    if entry[0] == "email" and not info["abuse_contact"]:
                                        info["abuse_contact"] = entry[1] if isinstance(entry[1], str) else (
                                            entry[1].get("value", "") if isinstance(entry[1], dict) else ""
                                        )
                org_name = (str(info.get("organization", "") or "") + " " + str(results.get("asn_description") or "")).lower()
                for provider, keywords in self.CLOUD_PROVIDERS.items():
                    if any(kw in org_name for kw in keywords):
                        info["cloud_provider"] = provider
                        break
        except (BaseIpwhoisException, ValueError, KeyError, IndexError):
            try:
                fallback: Optional[dict[str, Any]] = None
                client = Utils.create_client(config.timeout)
                try:
                    response = Utils.safe_get(client, f"https://ipinfo.io/{ip}/json")
                    if response and response.status_code == 200:
                        fallback = response.json()
                finally:
                    client.close()
                if fallback:
                    info["organization"] = fallback.get("org", "")
                    info["country"] = fallback.get("country", "")
                    info["region"] = fallback.get("region", "")
                    info["city"] = fallback.get("city", "")
                    info["asn"] = fallback.get("asn", "")
                    info["hosting_company"] = fallback.get("org", "")
                    org_name = fallback.get("org", "").lower()
                    for provider, keywords in self.CLOUD_PROVIDERS.items():
                        if any(kw in org_name for kw in keywords):
                            info["cloud_provider"] = provider
                            break
            except Exception:
                pass
        return info
