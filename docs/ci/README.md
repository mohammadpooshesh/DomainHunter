# CI/CD workflows

These are the finished GitHub Actions workflows for DomainHunter. They live here
because the automation that created this branch is not permitted to write to
`.github/workflows/` directly (that path needs the GitHub `workflows`
permission scope).

**To activate them, copy each file into `.github/workflows/`:**

```bash
mkdir -p .github/workflows
cp docs/ci/ci.yml        .github/workflows/ci.yml
cp docs/ci/docker.yml    .github/workflows/docker.yml
cp docs/ci/codeql.yml    .github/workflows/codeql.yml
cp docs/ci/release.yml   .github/workflows/release.yml
git add .github/workflows
git commit -m "ci: enable GitHub Actions workflows"
git push
```

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `ci.yml` | push / PR to master | Ruff lint, pytest matrix (Ubuntu 3.10-3.13 + macOS + Windows), coverage, mypy |
| `docker.yml` | push / tags / PR | Build & push image to GHCR |
| `codeql.yml` | push / PR / weekly | CodeQL security analysis |
| `release.yml` | `v*` tags | Build sdist/wheel and publish a GitHub release |
