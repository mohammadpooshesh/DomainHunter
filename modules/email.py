from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from config import Config
from core.utils import Utils


class EmailModule:
    name = "email"

    CONTACT_PATHS = ["/contact", "/about", "/team", "/support", "/contact-us", "/contactus"]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"emails": [], "sources": {}}
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(client, "https://" + domain)
            if response:
                html_emails = Utils.extract_emails(response.text)
                if html_emails:
                    result["emails"].extend(html_emails)
                    result["sources"]["website"] = html_emails

                soup = BeautifulSoup(response.text, "lxml")
                for tag in soup.find_all(["a", "p", "span", "div"]):
                    text = tag.get_text(strip=True)
                    found = Utils.extract_emails(text)
                    if found:
                        result["emails"].extend(found)

            for path in self.CONTACT_PATHS:
                page_resp = Utils.safe_get(client, "https://" + domain + path)
                if page_resp and page_resp.status_code == 200:
                    page_emails = Utils.extract_emails(page_resp.text)
                    if page_emails:
                        result["emails"].extend(page_emails)
                        result["sources"]["page:" + path] = page_emails

            try:
                import dns.resolver

                mx_answers = dns.resolver.resolve(domain, "MX", lifetime=10)
                for mx in mx_answers:
                    mx_str = str(mx.exchange).strip().rstrip(".")
                    mx_emails = Utils.extract_emails(mx_str)
                    if mx_emails:
                        result["emails"].extend(mx_emails)
                        result["sources"]["dns"] = result["sources"].get("dns", []) + mx_emails
            except Exception:
                pass

            soa_emails = self._extract_soa_email(domain)
            if soa_emails:
                result["emails"].extend(soa_emails)
                result["sources"]["soa"] = soa_emails

            result["emails"] = sorted(set(result["emails"]))
            result["total"] = len(result["emails"])
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result

    def _extract_soa_email(self, domain: str) -> list[str]:
        try:
            import dns.resolver

            answers = dns.resolver.resolve(domain, "SOA", lifetime=10)
            rname = str(answers[0].rname).strip()
            rname = re.sub(r"\.$", "", rname)
            if "@" in rname:
                return [rname]
            at_index = rname.find(".")
            if at_index > 0:
                email = rname[:at_index] + "@" + rname[at_index + 1:]
                if Utils.extract_emails(email):
                    return [email]
        except Exception:
            pass
        return []
