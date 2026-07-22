# DomainHunter

[![CI](https://github.com/mohammadpooshesh/DomainHunter/actions/workflows/ci.yml/badge.svg)](https://github.com/mohammadpooshesh/DomainHunter/actions/workflows/ci.yml)
[![CodeQL](https://github.com/mohammadpooshesh/DomainHunter/actions/workflows/codeql.yml/badge.svg)](https://github.com/mohammadpooshesh/DomainHunter/actions/workflows/codeql.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **DomainHunter** is a professional, modular domain OSINT & reconnaissance
> framework. Point it at a domain and it fans out across 20+ independent
> collectors — DNS, WHOIS, TLS, certificate transparency, subdomains,
> technology fingerprinting, web metadata, breach hints, and more — then
> renders a clean JSON, Markdown and HTML report.

---

## Table of contents

- [Features](#features)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Modules](#modules)
- [Output & reports](#output--reports)
- [Architecture](#architecture)
- [Development](#development)
- [Testing](#testing)
- [Docker](#docker)
- [Responsible use](#responsible-use)
- [Contributing](#contributing)
- [License](#license)

## Features

- **20+ pluggable modules** — each is self-contained, fails gracefully, and
  returns structured data.
- **Concurrent engine** with a thread pool and optional SQLite result caching.
- **Three report formats** out of the box (JSON, Markdown, HTML) plus optional
  PDF export.
- **Optional API enrichment** — VirusTotal, Shodan, SecurityTrails, Censys and
  GitHub are used automatically when credentials are present, and skipped
  cleanly when they are not.
- **Zero-config CLI** built with Typer, with a rich terminal UI.
- **Fully tested** offline test suite and strict CI (lint, types, multi-OS
  matrix).

## Quick start

```bash
pip install -r requirements.txt
python main.py scan example.com
```

## Installation

### From source

```bash
git clone https://github.com/mohammadpooshesh/DomainHunter.git
cd DomainHunter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### As a package (editable)

```bash
pip install -e .
domainhunter scan example.com
```

### Optional extras

```bash
pip install -e '.[pdf]'   # PDF reports via weasyprint
pip install -e '.[dev]'   # development + test tooling
playwright install chromium   # only needed for the screenshots module
```

## Usage

```bash
# Basic scan (writes JSON + HTML + Markdown to ./output)
python main.py scan example.com

# Verbose, HTML only, with port scanning enabled
python main.py scan example.com --verbose --html --scan

# Tune concurrency and timeouts
python main.py scan example.com --threads 50 --timeout 15

# Disable caching for a fresh run
python main.py scan example.com --no-cache

# Use a YAML config / API key file
python main.py scan example.com --api-config config.yaml

# Show which env vars back each API module
python main.py list-apis

# Version
python main.py --version
```

See [`docs/USAGE.md`](docs/USAGE.md) for the complete CLI reference.

## Configuration

Configuration is resolved with the following precedence (highest last):

1. Built-in defaults
2. Environment variables (API credentials)
3. An optional YAML config file passed via `--api-config`

Copy [`.env.example`](.env.example) and fill in whichever keys you have:

| Variable | Module |
| --- | --- |
| `GITHUB_TOKEN` | GitHub code/repo search |
| `VIRUSTOTAL_API_KEY` | VirusTotal reputation |
| `SHODAN_API_KEY` | Shodan host data |
| `SECURITYTRAILS_API_KEY` | SecurityTrails DNS/subdomains |
| `CENSYS_API_ID` / `CENSYS_API_SECRET` | Censys host data |

Full details in [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md).

## Modules

| Module | Needs API key | What it collects |
| --- | :---: | --- |
| `whois` | No | Registrar, dates, registrant, name servers |
| `dns` | No | A/AAAA/MX/NS/TXT/SOA/CAA/SRV/PTR, SPF/DMARC, AXFR check |
| `ssl` | No | Certificate details, SAN, chain, supported TLS versions |
| `certificate_transparency` | No | crt.sh certificates and discovered subdomains |
| `web` | No | Status, title, meta, forms, redirects, robots, sitemap |
| `headers` | No | Security headers, scoring, cookies, WAF/CDN hints |
| `technologies` | No | CMS / framework / server fingerprinting |
| `favicon` | No | Favicon hashes (md5 + mmh3 for pivoting) |
| `subdomains` | No | crt.sh + optional brute force |
| `wayback` | No | Wayback Machine snapshots & history |
| `ip_info` | No | ASN, org, geo, cloud-provider detection |
| `reverse_ip` | No | Reverse DNS / shared-host hints |
| `email` | No | E-mails from site, MX and SOA records |
| `leaks` | No | Public breach/paste/GitHub exposure hints |
| `github` | Optional | Code & repository search |
| `google` | No | Ready-to-run search-engine dork URLs |
| `securitytrails` | Yes | DNS history & subdomains |
| `virustotal` | Yes | Domain reputation & analysis |
| `shodan` | Yes | Open ports & service banners |
| `censys` | Yes | Host services & location |
| `portscan` | No (`--scan`) | Common-port TCP scan + banners |
| `screenshots` | No | Playwright page screenshots |

Deep dive in [`docs/MODULES.md`](docs/MODULES.md).

## Output & reports

Reports are written to `./output/` (configurable):

- `<domain>_report.json` — machine-readable results
- `<domain>_report.md` — Markdown summary
- `<domain>_report.html` — self-contained dark-themed HTML dashboard
- `<domain>_report.pdf` — optional, requires the `pdf` extra

## Architecture

```
main.py            # Typer CLI entry point
config.py          # Config + APIConfig dataclasses
core/
  scanner.py       # orchestrates modules, caching, results
  threads.py       # ThreadPool helpers
  cache.py         # SQLite TTL cache
  report.py        # JSON / Markdown / HTML renderers
  logger.py        # Rich-based logging
  utils.py         # domain parsing, HTTP client, validators
modules/           # 22 independent collectors (name + run())
tests/             # offline, mocked test suite
```

More in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Development

```bash
pip install -r requirements-dev.txt
make lint     # ruff
make type     # mypy
make test     # pytest
make check    # all of the above
```

## Testing

The test suite is fully offline — all network and DNS calls are mocked, so
`pytest` is fast and deterministic:

```bash
pytest
pytest --cov=. --cov-report=term-missing
```

A dedicated regression test (`tests/test_regression_urls.py`) fails the build if
any module ever reintroduces the doubled-brace f-string URL bug.

## Docker

```bash
docker build -t domainhunter .
docker run --rm -v "$PWD/output:/app/output" domainhunter scan example.com

# or with docker compose
docker compose run --rm domainhunter scan example.com
```

## Responsible use

DomainHunter is for **authorized** security testing and research only. Only scan
domains you own or are explicitly permitted to assess. See [`SECURITY.md`](SECURITY.md).

## Contributing

Contributions are welcome — please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

Released under the [MIT License](LICENSE).
