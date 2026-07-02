from __future__ import annotations

from typing import Any, Optional

import dns.resolver
import dns.query
import dns.zone
from dns.exception import DNSException

from config import Config


class DNSModule:
    name = "dns"

    @staticmethod
    def _query_records(domain: str, rtype: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=10)
            for rdata in answers:
                records.append({"value": str(rdata).strip(), "ttl": answers.rrset.ttl if answers.rrset else None})
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, DNSException):
            pass
        return records

    @staticmethod
    def _query_mx(domain: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=10)
            for rdata in answers:
                records.append({
                    "preference": rdata.preference,
                    "exchange": str(rdata.exchange).strip(),
                    "ttl": answers.rrset.ttl if answers.rrset else None,
                })
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return records

    @staticmethod
    def _query_soa(domain: str) -> Optional[dict[str, Any]]:
        try:
            answers = dns.resolver.resolve(domain, "SOA", lifetime=10)
            rdata = answers[0]
            return {
                "mname": str(rdata.mname).strip(),
                "rname": str(rdata.rname).strip(),
                "serial": rdata.serial,
                "refresh": rdata.refresh,
                "retry": rdata.retry,
                "expire": rdata.expire,
                "minimum": rdata.minimum,
                "ttl": answers.rrset.ttl if answers.rrset else None,
            }
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            return None

    @staticmethod
    def _check_axfr(domain: str) -> list[str]:
        results: list[str] = []
        try:
            ns_answers = dns.resolver.resolve(domain, "NS", lifetime=10)
            for ns in ns_answers:
                ns_name = str(ns).strip()
                try:
                    ns_ip = str(dns.resolver.resolve(ns_name, "A", lifetime=5)[0])
                    zones = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, lifetime=5))
                    if zones:
                        results.append(f"AXFR permitted on {ns_name} ({ns_ip})")
                except (DNSException, ConnectionError, TimeoutError):
                    pass
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
            pass
        return results

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "a": self._query_records(domain, "A"),
            "aaaa": self._query_records(domain, "AAAA"),
            "mx": self._query_mx(domain),
            "ns": self._query_records(domain, "NS"),
            "txt": self._query_records(domain, "TXT"),
            "soa": self._query_soa(domain),
        }
        spf_records = []
        dmarc_records = []
        for txt in result["txt"]:
            val = str(txt.get("value", "")).strip()
            if val.upper().startswith("V=SPF"):
                spf_records.append(txt)
            if val.upper().startswith("V=DMARC"):
                dmarc_records.append(txt)
        result["spf"] = spf_records
        result["dmarc"] = dmarc_records
        result["caa"] = self._query_records(domain, "CAA")
        srv_records = self._query_records(f"_sip._tcp.{domain}", "SRV")
        if not srv_records:
            srv_records = self._query_records(f"_autodiscover._tcp.{domain}", "SRV")
        result["srv"] = srv_records
        ptr_records: list[dict[str, Any]] = []
        a_records = result.get("a", [])
        for a in a_records:
            ip = a.get("value", "")
            if ip:
                try:
                    ptr = dns.resolver.resolve_address(ip, lifetime=10)
                    for p in ptr:
                        ptr_records.append({"ip": ip, "ptr": str(p).strip()})
                except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, DNSException):
                    pass
        result["ptr"] = ptr_records
        axfr_results = self._check_axfr(domain)
        result["axfr"] = axfr_results
        return result
