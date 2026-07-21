# Architecture

DomainHunter is intentionally simple: a thin CLI drives an orchestrator that runs
a list of independent modules and hands their combined results to a report
generator.

```
           +------------------+
           |     main.py      |  Typer CLI (scan, list-apis)
           +--------+---------+
                    |
                    v
           +------------------+        +------------------+
           |  core.scanner    +------->+   core.cache     |  SQLite TTL cache
           |    Scanner       |        +------------------+
           +--------+---------+
                    |  for each (name, module)
                    v
           +------------------+
           |   modules/*.py   |  each: name + run(domain, config) -> dict
           +--------+---------+
                    |  results dict
                    v
           +------------------+
           |  core.report     |  JSON / Markdown / HTML (+ optional PDF)
           +------------------+
```

## Components

### `config.py`
Two dataclasses. `APIConfig` reads API keys from the environment; `Config`
holds runtime settings and overlays an optional YAML file on top of the env
defaults.

### `core/scanner.py`
`Scanner.scan()` iterates over the registered modules, consulting the cache
first (key = `"<module>:<domain>"`), invoking `module.run()`, storing results
and catching any exception so one failing module never aborts the scan.

### `core/threads.py`
`ThreadManager` wraps `concurrent.futures.ThreadPoolExecutor` with `run_batch`,
`run_batch_simple` and `run_map` helpers used by modules that do their own
fan-out (e.g. subdomain brute force).

### `core/cache.py`
A tiny SQLite-backed key/value cache with per-entry TTL and cleanup.

### `core/report.py`
`ReportGenerator` renders the results dict to JSON, Markdown and a
self-contained HTML dashboard (Jinja2 template), and can persist them to disk.

### `core/utils.py`
Stateless helpers: domain parsing/validation, HTTP client factories,
`safe_get` (never raises), filename sanitising and e-mail extraction. **All
modules build request URLs through concatenation or httpx `params=` here** — a
regression test enforces that no doubled-brace f-string URLs return.

### `core/logger.py`
A Rich-based logging singleton providing coloured status output, tables and
progress bars.

## Design principles

- **Isolation** — modules never import each other; they only depend on
  `config` and `core`.
- **Fail soft** — a module returns `{"error": ...}` rather than raising.
- **Testable** — network access goes through `Utils`, which tests monkeypatch
  to stay offline.
