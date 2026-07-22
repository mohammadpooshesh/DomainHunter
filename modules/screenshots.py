from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from config import Config


class ScreenshotsModule:
    name = "screenshots"

    def _targets(self, domain: str) -> list[tuple[str, str]]:
        base = "https://" + domain
        return [
            (base, "homepage"),
            (base + "/robots.txt", "robots_txt"),
            (base + "/nonexistent-page-404-test", "404_page"),
        ]

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {"screenshots": []}
        try:
            import playwright.sync_api  # noqa: F401

            screenshots = self._capture_sync(domain, config)
            if screenshots:
                result["screenshots"] = screenshots
        except ImportError:
            try:
                screenshots = asyncio.run(self._capture_async(domain, config))
                if screenshots:
                    result["screenshots"] = screenshots
            except Exception as e:
                result["error"] = (
                    f"Playwright not available: {e}. "
                    "Install with: pip install playwright && playwright install"
                )
        except Exception as e:
            result["error"] = str(e)
        return result

    def _capture_sync(self, domain: str, config: Config) -> list[dict[str, Any]]:
        from playwright.sync_api import sync_playwright

        screenshots: list[dict[str, Any]] = []
        output_dir = Path(config.output_dir) / "screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)
        pages_to_capture = self._targets(domain)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            for url, name in pages_to_capture:
                screenshot_path = str(output_dir / (domain + "_" + name + ".png"))
                try:
                    page.goto(url, wait_until="networkidle", timeout=config.timeout * 1000)
                    page.screenshot(path=screenshot_path, full_page=True)
                    screenshots.append({"name": name, "url": url, "path": screenshot_path})
                except Exception:
                    try:
                        page.goto(url, timeout=config.timeout * 1000)
                        page.screenshot(path=screenshot_path)
                        screenshots.append({"name": name, "url": url, "path": screenshot_path})
                    except Exception:
                        pass
            browser.close()
        return screenshots

    async def _capture_async(self, domain: str, config: Config) -> list[dict[str, Any]]:
        from playwright.async_api import async_playwright

        screenshots: list[dict[str, Any]] = []
        output_dir = Path(config.output_dir) / "screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)
        pages_to_capture = self._targets(domain)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            for url, name in pages_to_capture:
                screenshot_path = str(output_dir / (domain + "_" + name + ".png"))
                try:
                    await page.goto(url, wait_until="networkidle", timeout=config.timeout * 1000)
                    await page.screenshot(path=screenshot_path, full_page=True)
                    screenshots.append({"name": name, "url": url, "path": screenshot_path})
                except Exception:
                    try:
                        await page.goto(url, timeout=config.timeout * 1000)
                        await page.screenshot(path=screenshot_path)
                        screenshots.append({"name": name, "url": url, "path": screenshot_path})
                    except Exception:
                        pass
            await browser.close()
        return screenshots
