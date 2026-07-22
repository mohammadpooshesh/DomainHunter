from config import Config
from modules.google import GoogleModule


def test_all_modules_have_name_and_run():
    from main import _get_modules

    modules = _get_modules(include_scan=True)
    names = [name for name, _ in modules]
    assert "dns" in names
    assert "web" in names
    assert "portscan" in names
    for name, module in modules:
        assert isinstance(name, str)
        assert hasattr(module, "run")
        assert callable(module.run)


def test_google_module_offline_smoke():
    result = GoogleModule().run("example.com", Config(cache=False))
    assert result["queries"]
