# Modules reference

Every module lives in `modules/`, exposes a `name` attribute and a
`run(domain, config) -> dict` method, and is designed to fail soft: on any error
it returns a dict containing an `"error"` key instead of raising.

## Passive / no-key modules

### `whois`
Registrar, creation/updated/expiration dates, name servers, DNSSEC, status,
registrant details and a privacy-protection heuristic.

### `dns`
Resolves A, AAAA, MX, NS, TXT, SOA, CAA and SRV records, derives SPF/DMARC from
TXT, performs PTR lookups for resolved A records, and checks whether any name
server permits an AXFR zone transfer.

### `ssl`
Connects on 443 and parses the leaf certificate (subject, issuer, serial, SAN,
validity window, days remaining, chain) and enumerates supported TLS versions.

### `certificate_transparency`
Queries crt.sh for issued certificates and extracts discovered subdomains.

### `web`
Fetches the site and records status code, final URL, server, content type,
title, meta description/keywords, tag counts, forms, redirects, plus `robots.txt`
and sitemap parsing.

### `headers`
Inspects security headers, assigns a graded score, extracts cookie flags, and
flags likely WAF/CDN providers.

### `technologies`
Signature-based fingerprinting of CMSs, frameworks, JS libraries, web servers
and platforms from HTML, headers and cookies.

### `favicon`
Downloads the favicon and computes md5 and mmh3 hashes for infrastructure
pivoting (Shodan-style favicon hashing).

### `subdomains`
Collects subdomains from crt.sh and, when `--verbose` is set, brute-forces a
common-name wordlist.

### `wayback`
Pulls snapshot history from the Wayback Machine (CDX API + timemap).

### `ip_info`
RDAP/WHOIS-based ASN, organization, geo and cloud-provider detection, with an
ipinfo.io fallback.

### `reverse_ip`
Reverse DNS lookups to hint at other domains on the same address.

### `email`
Harvests e-mail addresses from the homepage, common contact pages, MX records
and the SOA `rname`.

### `leaks`
Checks public breach/paste sources and GitHub for exposure hints.

### `google`
Generates ready-to-run Google/Bing/DuckDuckGo dork URLs (no network calls).

### `portscan` (enabled with `--scan`)
TCP-connect scan of common ports with light banner grabbing.

### `screenshots`
Captures full-page screenshots with Playwright (sync or async).

## API-backed modules

These activate only when the relevant credentials are configured; otherwise they
return a friendly `"error"` explaining which key is missing.

| Module | Credentials |
| --- | --- |
| `github` | `GITHUB_TOKEN` (optional — falls back to dork URLs) |
| `securitytrails` | `SECURITYTRAILS_API_KEY` |
| `virustotal` | `VIRUSTOTAL_API_KEY` |
| `shodan` | `SHODAN_API_KEY` |
| `censys` | `CENSYS_API_ID` + `CENSYS_API_SECRET` |

## Writing a new module

```python
from typing import Any
from config import Config
from core.utils import Utils


class MyModule:
    name = "my_module"

    def run(self, domain: str, config: Config) -> dict[str, Any]:
        result: dict[str, Any] = {}
        client = Utils.create_client(config.timeout)
        try:
            # Build URLs with concatenation or params= (never brace f-strings!)
            resp = Utils.safe_get(client, "https://" + domain + "/path")
            if resp and resp.status_code == 200:
                result["ok"] = True
        except Exception as e:  # fail soft
            result["error"] = str(e)
        finally:
            client.close()
        return result
```

Then register it in `main.py::_get_modules` and add an offline test.
