from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import typer

from config import Config
from core.logger import Logger
from core.report import ReportGenerator
from core.scanner import Scanner
from modules.dns import DNSModule
from modules.whois import WhoisModule
from modules.ssl import SSLModule
from modules.certtransparency import CertTransparencyModule
from modules.web import WebModule
from modules.headers import HeadersModule
from modules.favicon import FaviconModule
from modules.technologies import TechnologiesModule
from modules.subdomains import SubdomainsModule
from modules.wayback import WaybackModule
from modules.reverseip import ReverseIPModule
from modules.ipinfo import IPInfoModule
from modules.github import GitHubModule
from modules.google import GoogleModule
from modules.securitytrails import SecurityTrailsModule
from modules.virustotal import VirusTotalModule
from modules.shodan import ShodanModule
from modules.censys import CensysModule
from modules.email import EmailModule
from modules.leaks import LeaksModule
from modules.portscan import PortScanModule
from modules.screenshots import ScreenshotsModule


app = typer.Typer(
    name="domainhunter",
    help="Professional Domain OSINT Framework",
    add_completion=False,
)


def _get_modules(include_scan: bool = False) -> list[tuple[str, object]]:
    modules: list[tuple[str, object]] = [
        ("whois", WhoisModule()),
        ("dns", DNSModule()),
        ("ssl", SSLModule()),
        ("certificate_transparency", CertTransparencyModule()),
        ("web", WebModule()),
        ("headers", HeadersModule()),
        ("technologies", TechnologiesModule()),
        ("favicon", FaviconModule()),
        ("subdomains", SubdomainsModule()),
        ("wayback", WaybackModule()),
        ("ip_info", IPInfoModule()),
        ("reverse_ip", ReverseIPModule()),
        ("email", EmailModule()),
        ("leaks", LeaksModule()),
        ("github", GitHubModule()),
        ("google", GoogleModule()),
        ("securitytrails", SecurityTrailsModule()),
        ("virustotal", VirusTotalModule()),
        ("shodan", ShodanModule()),
        ("censys", CensysModule()),
    ]
    if include_scan:
        modules.append(("portscan", PortScanModule()))
    modules.append(("screenshots", ScreenshotsModule()))
    return modules


def _version_callback(value: bool) -> None:
    if value:
        from importlib.metadata import version
        try:
            ver = version("domainhunter")
        except Exception:
            ver = "0.1.0"
        print(f"DomainHunter v{ver}")
        raise typer.Exit()


@app.callback()
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-V",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    pass


@app.command()
def scan(
    domain: str = typer.Argument(..., help="Domain to scan"),
    html: bool = typer.Option(False, "--html", help="Generate HTML report"),
    json: bool = typer.Option(False, "--json", help="Generate JSON report"),
    pdf: bool = typer.Option(False, "--pdf", help="Generate PDF report (requires weasyprint)"),
    scan_ports: bool = typer.Option(False, "--scan", help="Enable port scanning"),
    threads: int = typer.Option(30, "--threads", help="Number of worker threads"),
    timeout: int = typer.Option(10, "--timeout", help="Request timeout in seconds"),
    cache_enabled: bool = typer.Option(True, "--cache/--no-cache", help="Enable/disable caching"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    api_config: Optional[Path] = typer.Option(
        None, "--api-config", help="Path to API configuration file",
    ),
) -> None:
    config_obj = Config.load(str(api_config) if api_config else None)
    config_obj.threads = threads
    config_obj.timeout = timeout
    config_obj.cache = cache_enabled
    config_obj.verbose = verbose

    log = Logger.get(verbose=verbose)

    log.info(f"Starting DomainHunter scan for: {domain}")
    start_time = time.time()

    scanner = Scanner(config_obj)
    modules = _get_modules(include_scan=scan_ports)
    results = scanner.scan(domain, modules)

    duration = time.time() - start_time
    log.success(f"Scan completed in {duration:.2f}s")

    report = ReportGenerator(domain, results, duration)

    formats: list[str] = []
    if html:
        formats.append("html")
    if json:
        formats.append("json")
    if pdf:
        formats.append("pdf")
    if not formats:
        formats = ["json", "html", "md"]

    saved = report.save(output_dir=config_obj.output_dir, formats=formats)

    if pdf:
        pdf_path = Path(config_obj.output_dir) / f"{domain}_report.pdf"
        try:
            import weasyprint
            html_content = report.to_html()
            weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
            saved["pdf"] = str(pdf_path)
            log.success(f"PDF report saved to {pdf_path}")
        except ImportError:
            log.warning("PDF generation requires weasyprint: pip install weasyprint")
        except Exception as e:
            log.warning(f"PDF generation failed: {e}")

    log.section("Reports Generated")
    for fmt, path in saved.items():
        log.success(f"[{fmt.upper()}] {path}")

    log.console.print(f"\n[bold]Scan Results Summary:[/]")
    for name, data in results.items():
        if data and isinstance(data, dict) and data.get("error"):
            log.fail(f"  {name}: {data['error']}")
        else:
            ok_msg = "completed"
            if name == "dns" and isinstance(data, dict):
                a_count = len(data.get("a", []))
                ok_msg = f"{a_count} A records"
            elif name == "subdomains" and isinstance(data, dict):
                sd_count = data.get("total", 0)
                ok_msg = f"{sd_count} subdomains"
            elif name == "email" and isinstance(data, dict):
                e_count = data.get("total", 0)
                ok_msg = f"{e_count} emails"
            log.success(f"  {name}: {ok_msg}")


@app.command()
def list_apis() -> None:
    log = Logger.get()
    log.print_table(
        "API Configuration Status",
        ["Service", "Status"],
        [
            ["GitHub", "env: GITHUB_TOKEN"],
            ["VirusTotal", "env: VIRUSTOTAL_API_KEY"],
            ["Shodan", "env: SHODAN_API_KEY"],
            ["SecurityTrails", "env: SECURITYTRAILS_API_KEY"],
            ["Censys", "env: CENSYS_API_ID + CENSYS_API_SECRET"],
        ],
    )


if __name__ == "__main__":
    app()
