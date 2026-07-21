"""Guards against reintroducing the doubled-brace f-string URL bug.

Every scanner module previously built URLs like ``f"{{https://{d}}}"`` which,
after f-string evaluation, produced a literal ``{https://example.com}`` that no
HTTP client could ever fetch. This test greps the real source tree and fails if
the pattern ever comes back.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _source_files():
    files = []
    for sub in ("modules", "core"):
        files.extend(sorted((ROOT / sub).rglob("*.py")))
    for name in ("main.py", "config.py"):
        path = ROOT / name
        if path.exists():
            files.append(path)
    return files


def test_no_literal_brace_url_bug():
    needle = "{" + "{http"
    offenders = []
    for path in _source_files():
        if needle in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"Literal-brace URL bug present in: {offenders}"


def test_source_tree_is_non_empty():
    assert _source_files(), "expected to find Python source files to scan"
