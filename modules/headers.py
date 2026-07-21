from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class HeadersModule:
    name = "headers"

    SECURITY_HEADERS = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy",
        "X-XSS-Protection",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy",
        "Cross-Origin-Resource-Policy",
    ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(client, "https://" + domain)
            if response is None:
                response = Utils.safe_get(client, "http://" + domain)

            if response:
                headers = dict(response.headers)
                result["all_headers"] = headers
                security: dict[str, Any] = {}
                for header in self.SECURITY_HEADERS:
                    lc = header.lower().replace("-", "").replace("_", "")
                    found = False
                    for key, value in headers.items():
                        if key.lower().replace("-", "").replace("_", "") == lc:
                            security[header] = value
                            found = True
                            break
                    if not found:
                        security[header] = None
                result["security_headers"] = security
                result["security_score"] = self._calculate_score(security)

                cookies = response.headers.get_list("Set-Cookie") if hasattr(response.headers, "get_list") else []
                if not cookies and "set-cookie" in {k.lower() for k in headers}:
                    raw_cookies = response.headers.get("Set-Cookie", "")
                    cookies = [c.strip() for c in raw_cookies.split("\n") if c.strip()]
                if not cookies:
                    sc = headers.get("Set-Cookie", "")
                    cookies = [sc] if sc else []
                result["cookies"] = cookies
                cookie_flags: dict[str, Any] = {"secure": False, "httponly": False, "samesite": False}
                for cookie in cookies:
                    upper = cookie.upper()
                    if "SECURE" in upper:
                        cookie_flags["secure"] = True
                    if "HTTPONLY" in upper:
                        cookie_flags["httponly"] = True
                    if "SAMESITE" in upper:
                        cookie_flags["samesite"] = True
                result["cookie_flags"] = cookie_flags

                waf_headers = [
                    "X-Sucuri-ID", "X-CDN", "CF-RAY", "X-WAF-Enabled",
                    "X-Firewall", "X-Protected-By", "Server",
                ]
                detected_wafs: list[str] = []
                for wh in waf_headers:
                    for key in headers:
                        if key.lower() == wh.lower():
                            detected_wafs.append(wh + ": " + str(headers[key]))
                cdn_signatures = {
                    "cloudflare": ["CF-RAY", "cf-cache-status", "CF-Cache-Status"],
                    "akamai": ["X-Akamai-Transformed"],
                    "cloudfront": ["X-Amz-Cf-Id", "X-Amz-Cf-Pop"],
                    "fastly": ["X-Served-By", "X-Cache", "X-Cache-Hits"],
                    "incapsula": ["X-Iinfo"],
                }
                detected_cdns: list[str] = []
                for cdn_name, sigs in cdn_signatures.items():
                    for sig in sigs:
                        for key in headers:
                            if key.lower() == sig.lower():
                                detected_cdns.append(cdn_name)
                                break
                result["waf_detected"] = list(set(detected_wafs))
                result["cdn_detected"] = list(set(detected_cdns))
            else:
                result["error"] = "Could not connect"
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result

    def _calculate_score(self, security: dict[str, Any]) -> dict[str, Any]:
        score = 0
        max_score = len(self.SECURITY_HEADERS)
        details: list[dict[str, Any]] = []
        for header, value in security.items():
            present = value is not None
            if present:
                score += 1
            details.append({"header": header, "present": present, "value": value})
        grade = "A"
        percentage = (score / max_score * 100) if max_score > 0 else 0
        if percentage < 20:
            grade = "F"
        elif percentage < 40:
            grade = "D"
        elif percentage < 60:
            grade = "C"
        elif percentage < 80:
            grade = "B"
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round(percentage, 1),
            "grade": grade,
            "details": details,
        }
