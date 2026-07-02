from __future__ import annotations

from typing import Any

from config import Config
from core.utils import Utils


class WaybackModule:
    name = "wayback"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {
            "snapshots": [],
            "total_snapshots": 0,
            "first_seen": None,
            "last_seen": None,
        }
        client = Utils.create_client(config.timeout)
        try:
            response = Utils.safe_get(
                client,
                f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=1000",
            )
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if len(data) > 1:
                        snapshots: list[dict[str, Any]] = []
                        timestamps: list[str] = []
                        for entry in data[1:]:
                            if len(entry) >= 6:
                                snap = {
                                    "timestamp": entry[1] if len(entry) > 1 else "",
                                    "original": entry[2] if len(entry) > 2 else "",
                                    "status_code": entry[4] if len(entry) > 4 else "",
                                    "mime_type": entry[3] if len(entry) > 3 else "",
                                }
                                snapshots.append(snap)
                                timestamps.append(entry[1])
                        result["snapshots"] = snapshots[:100]
                        result["total_snapshots"] = len(snapshots)
                        if timestamps:
                            result["first_seen"] = min(timestamps)
                            result["last_seen"] = max(timestamps)
                except (ValueError, TypeError):
                    pass

            history_response = Utils.safe_get(
                client,
                f"https://web.archive.org/web/timemap/link/{domain}",
            )
            if history_response and history_response.status_code == 200:
                result["timemap"] = history_response.text[:2000]

            for path in ["/robots.txt", "/"]:
                snap_response = Utils.safe_get(
                    client,
                    f"https://web.archive.org/web/2020/{domain}{path}",
                )
                if snap_response and snap_response.status_code == 200:
                    key = "history_homepage" if path == "/" else "history_robots"
                    result[key] = snap_response.text[:3000]
        except Exception as e:
            result["error"] = str(e)
        finally:
            client.close()
        return result
