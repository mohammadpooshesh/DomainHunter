from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from core.report import ReportGenerator


class TestReport:
    @pytest.fixture
    def report(self):
        results = {
            "dns": {"a": [{"value": "1.2.3.4", "ttl": 3600}]},
            "whois": {"registrar": "Test Registrar", "creation_date": "2020-01-01"},
            "headers": {"security_score": {"grade": "A", "score": 5, "max_score": 10}},
        }
        return ReportGenerator("example.com", results, 1.5)

    def test_to_json(self, report):
        data = json.loads(report.to_json())
        assert data["domain"] == "example.com"
        assert data["duration"] == 1.5
        assert "dns" in data["results"]

    def test_to_html(self, report):
        html = report.to_html()
        assert "<html" in html
        assert "example.com" in html
        assert "DomainHunter Report" in html

    def test_to_markdown(self, report):
        md = report.to_markdown()
        assert "example.com" in md
        assert "DNS" in md or "dns" in md

    def test_save(self, report):
        with tempfile.TemporaryDirectory() as tmpdir:
            saved = report.save(output_dir=tmpdir, formats=["json", "html", "md"])
            assert "json" in saved
            assert "html" in saved
            assert "md" in saved
            for path in saved.values():
                assert Path(path).exists()
