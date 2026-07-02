# DomainHunter

Professional Domain OSINT Framework — collects publicly available intelligence about a domain.

## Features

- WHOIS lookups with privacy protection detection
- DNS enumeration (A, AAAA, MX, NS, TXT, SPF, DMARC, CAA, SOA, SRV, PTR, AXFR test)
- SSL certificate analysis (issuer, SAN, chain, expiry, TLS versions)
- Certificate Transparency via crt.sh
- Web fingerprinting (server, headers, cookies, WAF, CDN)
- Technology detection (30+ signatures: frameworks, CMS, platforms)
- Security headers analysis with scoring (HSTS, CSP, XFO, etc.)
- Subdomain discovery (crt.sh + common subdomain bruteforce)
- Wayback Machine snapshots
- Reverse IP lookups
- IP intelligence (ASN, organization, geolocation, cloud provider)
- GitHub code search (domain references, configs, leaks)
- Search engine dork query generation
- Email discovery (website, DNS, SOA)
- Leak detection (public breach databases, GitHub, pastes)
- Favicon hash calculation (MD5, MurmurHash3)
- Port scanning (26 common ports)
- Screenshots (Playwright-based)
- Optional API integrations: SecurityTrails, VirusTotal, Shodan, Censys
- Beautiful HTML/JSON/Markdown reports
- SQLite caching
- Rich CLI with progress bars

## Installation

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Usage

```bash
python main.py scan example.com
python main.py scan example.com --html --json
python main.py scan example.com --scan --threads 50 --verbose
python main.py scan example.com --api-config config.yaml
python main.py scan example.com --no-cache --timeout 15
```

## API Configuration

Set API keys via environment variables or a YAML config file:

```bash
export GITHUB_TOKEN=ghp_...
export VIRUSTOTAL_API_KEY=...
export SHODAN_API_KEY=...
export SECURITYTRAILS_API_KEY=...
export CENSYS_API_ID=...
export CENSYS_API_SECRET=...
```

Or create `config.yaml`:

```yaml
github_token: ghp_...
virustotal: ...
shodan: ...
securitytrails: ...
censys_id: ...
censys_secret: ...
```

## Reports

Reports are saved to the `output/` directory:
- `example.com_report.json` — structured data
- `example.com_report.html` — styled HTML report
- `example.com_report.md` — Markdown summary

## Ethics

DomainHunter only collects publicly available information. It does not:
- Bypass authentication or authorization
- Scrape search engines directly
- Exploit vulnerabilities
- Perform aggressive scanning
- Fabricate or infer non-public data

Use only for authorized security research and defensive investigations.

## License

MIT
