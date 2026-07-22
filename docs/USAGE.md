# Usage guide

DomainHunter exposes a small, focused CLI built with [Typer](https://typer.tiangolo.com/).

## Commands

### `scan`

Run a full OSINT scan against a domain and generate reports.

```bash
python main.py scan DOMAIN [OPTIONS]
```

| Option | Default | Description |
| --- | --- | --- |
| `DOMAIN` | (required) | The domain to scan, e.g. `example.com` |
| `--html` | off | Generate the HTML report |
| `--json` | off | Generate the JSON report |
| `--pdf` | off | Generate a PDF report (requires the `pdf` extra) |
| `--scan` | off | Enable the TCP port-scanning module |
| `--threads N` | 30 | Number of worker threads |
| `--timeout N` | 10 | Per-request timeout in seconds |
| `--cache / --no-cache` | on | Enable/disable SQLite result caching |
| `--verbose`, `-v` | off | Verbose logging (also enables subdomain brute force) |
| `--api-config PATH` | none | Path to a YAML config / API key file |

> If neither `--html` nor `--json` is passed, DomainHunter writes **all three**
> formats (JSON, HTML, Markdown) by default.

### `list-apis`

Show which environment variable configures each API-backed module.

```bash
python main.py list-apis
```

### `--version`

```bash
python main.py --version
```

## Examples

```bash
# Everything, verbose, with port scan
python main.py scan example.com -v --scan

# Only JSON, high concurrency
python main.py scan example.com --json --threads 60

# Fresh run (ignore cache) with a longer timeout
python main.py scan example.com --no-cache --timeout 20

# Load API keys from a YAML file
python main.py scan example.com --api-config config.yaml
```

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Scan completed |
| `1` | Invalid domain supplied |
