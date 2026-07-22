# Configuration

## Resolution order

Settings are resolved with increasing precedence:

1. **Built-in defaults** (see `config.py`).
2. **Environment variables** — used for API credentials.
3. **YAML file** — passed with `--api-config path.yaml`, overlaid last.

CLI flags such as `--threads`, `--timeout`, `--cache/--no-cache` and
`--verbose` override the corresponding values after loading.

## Runtime defaults

| Setting | Default | Meaning |
| --- | --- | --- |
| `timeout` | `10` | Per-request timeout (seconds) |
| `threads` | `30` | Worker thread count |
| `cache` | `true` | Enable SQLite result caching |
| `cache_ttl` | `3600` | Cache entry lifetime (seconds) |
| `cache_dir` | `cache` | Cache directory |
| `verbose` | `false` | Verbose logging + subdomain brute force |
| `output_dir` | `output` | Where reports are written |
| `reports_dir` | `reports` | Reserved for future report grouping |

## Environment variables

| Variable | Module |
| --- | --- |
| `GITHUB_TOKEN` | `github` |
| `VIRUSTOTAL_API_KEY` | `virustotal` |
| `SHODAN_API_KEY` | `shodan` |
| `SECURITYTRAILS_API_KEY` | `securitytrails` |
| `CENSYS_API_ID` | `censys` |
| `CENSYS_API_SECRET` | `censys` |

Copy `.env.example` to `.env` and fill in what you have, or export them in your
shell.

## Example YAML config

```yaml
timeout: 15
threads: 40
verbose: true
cache: true
cache_ttl: 7200
output_dir: output

api:
  github_token: ghp_xxx
  virustotal: xxxxxxxx
  shodan: xxxxxxxx
  securitytrails: xxxxxxxx
  censys_id: xxxxxxxx
  censys_secret: xxxxxxxx
```

Top-level API keys (without the `api:` nesting) are also accepted for
convenience.
