from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from config import Config
from core.utils import Utils


class WebModule:
    name = "web"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        client = Utils.create_client(config.timeout)
        url = f"https://{domain}"
        try:
            response = Utils.safe_get(client, url)
            if response is None:
                url = f"http://{domain}"
                response = Utils.safe_get(client, url)

            if response:
                result["status_code"] = response.status_code
                result["url"] = str(response.url)
                result["server"] = response.headers.get("Server", "")
                result["content_type"] = response.headers.get("Content-Type", "")
                result["content_length"] = len(response.content)
                result["encoding"] = response.encoding or ""
                result["http_version"] = response.http_version if hasattr(response, "http_version") else ""
                try:
                    soup = BeautifulSoup(response.text, "lxml")
                    result["title"] = soup.title.string.strip() if soup.title and soup.title.string else ""
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        result["description"] = meta_desc["content"].strip()
                    meta_keys = soup.find("meta", attrs={"name": "keywords"})
                    if meta_keys and meta_keys.get("content"):
                        result["keywords"] = meta_keys["content"].strip()
                    result["meta_tags"] = len(soup.find_all("meta"))
                    result["scripts"] = len(soup.find_all("script"))
                    result["links"] = len(soup.find_all("a"))
                    result["images"] = len(soup.find_all("img"))
                    forms = soup.find_all("form")
                    result["forms"] = len(forms)
                    if forms:
                        result["form_details"] = []
                        for form in forms:
                            form_info = {
                                "action": form.get("action", ""),
                                "method": form.get("method", "get").upper(),
                                "inputs": len(form.find_all("input")),
                            }
                            result["form_details"].append(form_info)
                except Exception:
                    pass
                redirects = []
                if hasattr(response, "history") and response.history:
                    for h in response.history:
                        redirects.append(str(h.url))
                result["redirects"] = redirects
                result["redirect_count"] = len(redirects)
            else:
                result["error"] = "Could not connect to domain"
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()

        self._check_robots_txt(domain, config, result)
        self._check_sitemap(domain, config, result)
        return result

    def _check_robots_txt(self, domain: str, config: Config, result: dict[str, Any]) -> None:
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(client, f"https://{domain}/robots.txt")
            if response and response.status_code == 200:
                text = response.text
                result["robots_txt"] = text
                disallowed: list[str] = []
                sitemaps: list[str] = []
                for line in text.splitlines():
                    line = line.strip()
                    if line.lower().startswith("disallow:"):
                        path = line.split(":", 1)[1].strip()
                        if path:
                            disallowed.append(path)
                    if line.lower().startswith("sitemap:"):
                        sm = line.split(":", 1)[1].strip()
                        if sm:
                            sitemaps.append(sm)
                result["robots_disallowed"] = disallowed
                result["robots_sitemaps"] = sitemaps
        except Exception:
            pass
        finally:
            client.close()

    def _check_sitemap(self, domain: str, config: Config, result: dict[str, Any]) -> None:
        client = Utils.create_client(config.timeout)
        try:
            sitemap_urls = result.get("robots_sitemaps", [])
            if not sitemap_urls:
                sitemap_urls = [f"https://{domain}/sitemap.xml"]
            urls: list[str] = []
            for sm_url in sitemap_urls:
                response = Utils.safe_get(client, sm_url)
                if response and response.status_code == 200:
                    try:
                        soup = BeautifulSoup(response.text, "xml")
                        for loc in soup.find_all("loc"):
                            if loc.string:
                                urls.append(loc.string.strip())
                    except Exception:
                        pass
            result["sitemap_urls"] = urls
        except Exception:
            pass
        finally:
            client.close()
