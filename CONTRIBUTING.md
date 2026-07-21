# Contributing to DomainHunter

Thanks for your interest in improving DomainHunter! This document explains how
to set up your environment and the standards we expect for contributions.

## Development setup

```bash
git clone https://github.com/mohammadpooshesh/DomainHunter.git
cd DomainHunter
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium   # optional, only for the screenshots module
pre-commit install            # optional, runs lint on commit
```

## Workflow

1. Create a feature branch: `git checkout -b feat/my-change`.
2. Make your change with accompanying tests.
3. Run the full local check suite:
   ```bash
   make lint
   make test
   ```
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `test:`, `chore:` ...).
5. Open a pull request against `master` and fill in the template.

## Coding standards

- Target Python 3.10+ and keep the code type-hinted.
- Lint with `ruff check .` (configured in `pyproject.toml`).
- Every scanner module lives in `modules/`, exposes a `name` attribute and a
  `run(domain, config)` method, and must degrade gracefully (return an
  `{"error": ...}` dict rather than raising).
- **Build URLs with string concatenation or httpx `params=`**, never with
  doubled-brace f-strings. A regression test (`tests/test_regression_urls.py`)
  enforces this.
- New network behaviour must ship with offline, mocked tests.

## Reporting bugs & requesting features

Please use the issue templates under `.github/ISSUE_TEMPLATE/`.
