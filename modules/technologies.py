from __future__ import annotations

import re
from typing import Any

from config import Config
from core.utils import Utils


class TechnologiesModule:
    name = "technologies"

    SIGNATURES: list[dict[str, Any]] = [
        {"name": "WordPress", "type": "cms", "checks": [
            {"type": "html", "pattern": r"wp-content|wp-includes|WordPress"},
        ]},
        {"name": "Drupal", "type": "cms", "checks": [
            {"type": "html", "pattern": r"Drupal|drupal.js|sites/all"},
        ]},
        {"name": "Joomla", "type": "cms", "checks": [
            {"type": "html", "pattern": r"joomla|Joomla"},
        ]},
        {"name": "Django", "type": "framework", "checks": [
            {"type": "header", "pattern": r"^django", "header": "X-Frame-Options"},
        ]},
        {"name": "Flask", "type": "framework", "checks": [
            {"type": "header", "pattern": r"flask", "header": "Server"},
        ]},
        {"name": "Laravel", "type": "framework", "checks": [
            {"type": "cookie", "pattern": r"laravel_session"},
        ]},
        {"name": "Symfony", "type": "framework", "checks": [
            {"type": "cookie", "pattern": r"symfony"},
        ]},
        {"name": "ASP.NET", "type": "framework", "checks": [
            {"type": "header", "pattern": r"asp\.net", "header": "X-Powered-By"},
            {"type": "cookie", "pattern": r"asp\.net_sessionid|\.asp"},
        ]},
        {"name": "Express", "type": "framework", "checks": [
            {"type": "header", "pattern": r"express", "header": "X-Powered-By"},
        ]},
        {"name": "Next.js", "type": "framework", "checks": [
            {"type": "header", "pattern": r"next\.js", "header": "X-Powered-By"},
            {"type": "html", "pattern": r"__NEXT_DATA__|next\.js"},
        ]},
        {"name": "Nuxt.js", "type": "framework", "checks": [
            {"type": "html", "pattern": r"__NUXT__|nuxt\.js"},
        ]},
        {"name": "React", "type": "js_library", "checks": [
            {"type": "html", "pattern": r"react\.js|react\.min\.js|__REACT_"},
        ]},
        {"name": "Vue.js", "type": "js_library", "checks": [
            {"type": "html", "pattern": r"vue\.js|vue\.min\.js|__VUE__"},
        ]},
        {"name": "Angular", "type": "js_library", "checks": [
            {"type": "html", "pattern": r"angular\.js|ng-app|ng-version"},
        ]},
        {"name": "jQuery", "type": "js_library", "checks": [
            {"type": "html", "pattern": r"jquery.*\.js|jQuery"},
        ]},
        {"name": "Bootstrap", "type": "css_framework", "checks": [
            {"type": "html", "pattern": r"bootstrap.*\.css|bootstrap.*\.js"},
        ]},
        {"name": "Tailwind CSS", "type": "css_framework", "checks": [
            {"type": "html", "pattern": r"tailwindcss|@tailwind"},
        ]},
        {"name": "Nginx", "type": "web_server", "checks": [
            {"type": "header", "pattern": r"nginx", "header": "Server"},
        ]},
        {"name": "Apache", "type": "web_server", "checks": [
            {"type": "header", "pattern": r"apache", "header": "Server"},
        ]},
        {"name": "LiteSpeed", "type": "web_server", "checks": [
            {"type": "header", "pattern": r"litespeed", "header": "Server"},
        ]},
        {"name": "IIS", "type": "web_server", "checks": [
            {"type": "header", "pattern": r"iis", "header": "Server"},
        ]},
        {"name": "Node.js", "type": "platform", "checks": [
            {"type": "header", "pattern": r"node\.?js", "header": "X-Powered-By"},
        ]},
        {"name": "PHP", "type": "platform", "checks": [
            {"type": "header", "pattern": r"php", "header": "X-Powered-By"},
            {"type": "cookie", "pattern": r"phpsessid"},
        ]},
        {"name": "Python", "type": "platform", "checks": [
            {"type": "header", "pattern": r"python", "header": "Server"},
        ]},
        {"name": "Ruby", "type": "platform", "checks": [
            {"type": "header", "pattern": r"ruby|puma|passenger", "header": "Server"},
            {"type": "cookie", "pattern": r"_rails_session"},
        ]},
        {"name": "Java", "type": "platform", "checks": [
            {"type": "header", "pattern": r"java|tomcat|jetty", "header": "Server"},
            {"type": "cookie", "pattern": r"jsessionid"},
        ]},
        {"name": "Cloudflare", "type": "cdn", "checks": [
            {"type": "header", "pattern": r"cloudflare", "header": "Server"},
            {"type": "header", "pattern": r".*", "header": "CF-RAY"},
        ]},
    ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"technologies": [], "categories": {}}
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(client, "https://" + domain)
            if response is None:
                response = Utils.safe_get(client, "http://" + domain)

            if response:
                html = response.text
                headers = {k.lower(): v for k, v in dict(response.headers).items()}
                cookies_str = str(response.headers.get("Set-Cookie", "")).lower()
                detected: list[dict[str, Any]] = []

                for sig in self.SIGNATURES:
                    found = False
                    for check in sig["checks"]:
                        ctype = check["type"]
                        pattern = re.compile(check["pattern"], re.IGNORECASE)
                        if ctype == "html" and pattern.search(html):
                            found = True
                            break
                        elif ctype == "header":
                            header_name = check.get("header", "").lower()
                            header_val = headers.get(header_name, "")
                            if pattern.search(header_val):
                                found = True
                                break
                        elif ctype == "cookie" and pattern.search(cookies_str):
                            found = True
                            break
                    if found:
                        detected.append({
                            "name": sig["name"],
                            "type": sig.get("type", "unknown"),
                        })

                result["technologies"] = detected
                categories: dict[str, list[str]] = {}
                for tech in detected:
                    cat = tech["type"]
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(tech["name"])
                result["categories"] = categories
                result["count"] = len(detected)
            else:
                result["error"] = "Could not connect"
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
