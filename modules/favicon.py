from __future__ import annotations

import hashlib
from typing import Any

import mmh3
from bs4 import BeautifulSoup

from config import Config
from core.utils import Utils


class FaviconModule:
    name = "favicon"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        client = Utils.create_client(config.timeout)
        favicon_url = None
        try:
            response = Utils.safe_get(client, f"https://{domain}")
            if response:
                soup = BeautifulSoup(response.text, "lxml")
                icon_link = soup.find("link", rel=lambda v: v and ("icon" in v.lower() if v else False))
                if icon_link and icon_link.get("href"):
                    href = icon_link["href"]
                    favicon_url = href if href.startswith("http") else f"https://{domain}{href if href.startswith('/') else '/' + href}"
            if not favicon_url:
                favicon_url = f"https://{domain}/favicon.ico"

            if favicon_url:
                icon_response = Utils.safe_get(client, favicon_url)
                if icon_response and icon_response.status_code == 200:
                    content = icon_response.content
                    result["url"] = favicon_url
                    result["size"] = len(content)
                    result["md5"] = hashlib.md5(content).hexdigest()
                    try:
                        if len(content) >= 4:
                            mmh3_hash = mmh3.hash(content)
                            result["mmh3"] = mmh3_hash
                            result["mmh3_unsigned"] = mmh3_hash & 0xFFFFFFFF
                    except Exception:
                        pass
                    result["content_type"] = icon_response.headers.get("Content-Type", "")
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
