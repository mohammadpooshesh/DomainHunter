from config import APIConfig, Config


def test_defaults():
    cfg = Config()
    assert cfg.timeout == 10
    assert cfg.threads == 30
    assert cfg.cache is True
    assert isinstance(cfg.api, APIConfig)


def test_from_env_reads_variables(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "gh-token")
    monkeypatch.setenv("SHODAN_API_KEY", "shodan-key")
    api = APIConfig.from_env()
    assert api.github_token == "gh-token"
    assert api.shodan == "shodan-key"


def test_load_overlays_yaml_file(tmp_path, monkeypatch):
    monkeypatch.delenv("SHODAN_API_KEY", raising=False)
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "timeout: 25\nthreads: 5\nverbose: true\napi:\n  shodan: yaml-key\n",
        encoding="utf-8",
    )
    cfg = Config.load(str(cfg_file))
    assert cfg.timeout == 25
    assert cfg.threads == 5
    assert cfg.verbose is True
    assert cfg.api.shodan == "yaml-key"


def test_load_without_path_returns_defaults():
    cfg = Config.load(None)
    assert cfg.timeout == 10
    assert cfg.threads == 30
