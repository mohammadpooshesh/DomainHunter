from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from jinja2 import Template

from core.logger import Logger

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DomainHunter Report - {{ domain }}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }
.container { max-width: 1200px; margin: 0 auto; padding: 20px; }
header { background: linear-gradient(135deg, #1e293b, #0f172a); padding: 30px; border-radius: 12px; margin-bottom: 24px; border: 1px solid #334155; }
header h1 { font-size: 28px; color: #38bdf8; margin-bottom: 8px; }
header .meta { color: #94a3b8; font-size: 14px; }
header .meta span { margin-right: 20px; }
.module { background: #1e293b; border-radius: 8px; margin-bottom: 16px; border: 1px solid #334155; overflow: hidden; }
.module-header { padding: 16px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; user-select: none; }
.module-header:hover { background: #334155; }
.module-header h2 { font-size: 18px; color: #38bdf8; }
.module-header .status { font-size: 12px; padding: 4px 10px; border-radius: 12px; }
.status-ok { background: #166534; color: #86efac; }
.status-error { background: #7f1d1d; color: #fca5a5; }
.module-body { padding: 20px; border-top: 1px solid #334155; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; padding: 8px 12px; background: #0f172a; color: #94a3b8; font-size: 13px; border-bottom: 1px solid #334155; }
.data-table td { padding: 8px 12px; border-bottom: 1px solid #1e293b; font-size: 14px; }
.data-table tr:last-child td { border-bottom: none; }
.data-table td:first-child { font-weight: 600; color: #94a3b8; width: 200px; }
.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin: 2px; }
.tag-green { background: #166534; color: #86efac; }
.tag-red { background: #7f1d1d; color: #fca5a5; }
.tag-yellow { background: #854d0e; color: #fde68a; }
.tag-blue { background: #1e3a5f; color: #93c5fd; }
.score-bar { height: 20px; border-radius: 10px; background: #0f172a; overflow: hidden; margin: 8px 0; }
.score-fill { height: 100%; border-radius: 10px; transition: width 0.5s; }
.score-a { background: linear-gradient(90deg, #22c55e, #86efac); }
.score-b { background: linear-gradient(90deg, #22c55e, #eab308); }
.score-c { background: linear-gradient(90deg, #eab308, #f97316); }
.score-d { background: linear-gradient(90deg, #f97316, #ef4444); }
.score-f { background: linear-gradient(90deg, #ef4444, #dc2626); }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
@media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } }
.stat-card { background: #0f172a; padding: 16px; border-radius: 8px; text-align: center; }
.stat-card .value { font-size: 32px; font-weight: 700; color: #38bdf8; }
.stat-card .label { font-size: 12px; color: #94a3b8; margin-top: 4px; }
pre { background: #0f172a; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 13px; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
footer { text-align: center; padding: 20px; color: #475569; font-size: 13px; }
</style>
</head>
<body>
<div class="container">
<header>
<h1>DomainHunter Report: {{ domain }}</h1>
<div class="meta">
<span>Scan Date: {{ scan_date }}</span>
<span>Duration: {{ duration }}s</span>
{% if modules_count is defined %}<span>Modules: {{ modules_count }}</span>{% endif %}
</div>
</header>

<div class="summary-grid">
{% for stat in summary_stats %}
<div class="stat-card">
<div class="value">{{ stat.value }}</div>
<div class="label">{{ stat.label }}</div>
</div>
{% endfor %}
</div>

{% for module in modules %}
<div class="module">
<div class="module-header">
<h2>{{ module.name }}</h2>
<span class="status status-{{ 'ok' if module.status == 'ok' else 'error' }}">{{ module.status|upper }}</span>
</div>
<div class="module-body">
{% if module.data %}
  {% if module.data is mapping %}
    <table class="data-table">
    {% for key, value in module.data.items() %}
      <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
    {% endfor %}
    </table>
  {% elif module.data is iterable and module.data is not string %}
    {% for item in module.data %}
      {% if item is mapping %}
        <table class="data-table" style="margin-bottom: 12px;">
        {% for key, value in item.items() %}
          <tr><td>{{ key }}</td><td>{{ value }}</td></tr>
        {% endfor %}
        </table>
      {% else %}
        <div>{{ item }}</div>
      {% endif %}
    {% endfor %}
  {% else %}
    <div>{{ module.data }}</div>
  {% endif %}
{% else %}
  <div style="color: #64748b;">No data collected</div>
{% endif %}
</div>
</div>
{% endfor %}
<footer>Generated by DomainHunter on {{ scan_date }}</footer>
</div>
</body>
</html>"""


class ReportGenerator:
    def __init__(self, domain: str, results: dict[str, Any], duration: float) -> None:
        self.domain = domain
        self.results = results
        self.duration = duration
        self.log = Logger.get()

    def _build_module_list(self) -> list[dict[str, Any]]:
        modules: list[dict[str, Any]] = []
        for name, data in self.results.items():
            if data and isinstance(data, dict) and "error" in data and data["error"]:
                modules.append({"name": name, "status": "error", "data": data})
            else:
                modules.append({"name": name, "status": "ok", "data": data})
        return modules

    def _build_summary_stats(self) -> list[dict[str, Any]]:
        total = len(self.results)
        ok_count = sum(
            1 for v in self.results.values()
            if isinstance(v, dict) and ("error" not in v or not v["error"])
        )
        error_count = total - ok_count
        return [
            {"label": "Modules Run", "value": str(total)},
            {"label": "Successful", "value": str(ok_count)},
            {"label": "Failed", "value": str(error_count)},
            {"label": "Duration (s)", "value": f"{self.duration:.1f}"},
        ]

    def _add_summary_counts(self, modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
        counts: dict[str, int] = {}
        for key in self.results:
            parts = key.split("_")
            for part in parts:
                if part not in counts:
                    counts[part] = 0
                counts[part] += 1
        return modules

    def to_json(self) -> str:
        output = {
            "domain": self.domain,
            "scan_date": datetime.now().isoformat(),
            "duration": self.duration,
            "results": self.results,
        }
        return json.dumps(output, indent=2, default=str)

    def to_markdown(self) -> str:
        lines: list[str] = [
            f"# DomainHunter Report: {self.domain}",
            "",
            f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Duration:** {self.duration:.1f}s",
            "---",
            "",
        ]
        for name, data in self.results.items():
            lines.append(f"## {name}")
            lines.append("")
            if isinstance(data, dict):
                for key, value in data.items():
                    lines.append(f"- **{key}:** {value}")
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"- **{k}:** {v}")
                    else:
                        lines.append(f"- {item}")
            else:
                lines.append(f"- {data}")
            lines.append("")
        return "\n".join(lines)

    def to_html(self) -> str:
        modules = self._build_module_list()
        stats = self._build_summary_stats()
        template = Template(HTML_TEMPLATE)
        return template.render(
            domain=self.domain,
            scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duration=f"{self.duration:.1f}",
            modules_count=len(modules),
            modules=modules,
            summary_stats=stats,
        )

    def save(self, output_dir: str = "output", formats: Optional[list[str]] = None) -> dict[str, str]:
        if formats is None:
            formats = ["json", "html", "md"]
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        saved: dict[str, str] = {}

        if "json" in formats:
            path = output_path / f"{self.domain}_report.json"
            path.write_text(self.to_json())
            saved["json"] = str(path)

        if "html" in formats:
            path = output_path / f"{self.domain}_report.html"
            path.write_text(self.to_html(), encoding="utf-8")
            saved["html"] = str(path)

        if "md" in formats:
            path = output_path / f"{self.domain}_report.md"
            path.write_text(self.to_markdown())
            saved["md"] = str(path)

        return saved
