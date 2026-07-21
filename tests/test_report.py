import json as jsonlib

from core.report import ReportGenerator

RESULTS = {
    "dns": {"a": [{"value": "1.2.3.4"}]},
    "web": {"error": "Could not connect"},
}


def test_to_json_is_valid_and_contains_domain():
    report = ReportGenerator("example.com", RESULTS, 1.5)
    parsed = jsonlib.loads(report.to_json())
    assert parsed["domain"] == "example.com"
    assert parsed["duration"] == 1.5
    assert "dns" in parsed["results"]


def test_to_markdown_contains_headers():
    report = ReportGenerator("example.com", RESULTS, 1.5)
    md = report.to_markdown()
    assert "# DomainHunter Report: example.com" in md
    assert "## dns" in md


def test_to_html_contains_domain_and_status():
    report = ReportGenerator("example.com", RESULTS, 1.5)
    html = report.to_html()
    assert "example.com" in html
    assert "ERROR" in html.upper()


def test_summary_stats_counts_success_and_failure():
    report = ReportGenerator("example.com", RESULTS, 1.5)
    stats = {s["label"]: s["value"] for s in report._build_summary_stats()}
    assert stats["Modules Run"] == "2"
    assert stats["Successful"] == "1"
    assert stats["Failed"] == "1"


def test_save_writes_files(tmp_path):
    report = ReportGenerator("example.com", RESULTS, 1.5)
    saved = report.save(output_dir=str(tmp_path), formats=["json", "md"])
    assert (tmp_path / "example.com_report.json").exists()
    assert (tmp_path / "example.com_report.md").exists()
    assert "html" not in saved
