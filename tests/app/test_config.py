"""Tests for app.config — TOML loading, env var overrides, error handling."""

from pathlib import Path

import pytest

from app.config import DatabaseConfig, get_config, load_config, reset_config


@pytest.fixture(autouse=True)
def _clean_config():
    """Reset cached config before and after each test."""
    reset_config()
    yield
    reset_config()


@pytest.fixture()
def tmp_config(tmp_path):
    """Helper that writes a TOML string to a temp file and returns the path."""
    def _write(content: str) -> Path:
        p = tmp_path / "config.toml"
        p.write_text(content)
        return p
    return _write


class TestDatabaseConfig:
    def test_url_construction(self):
        db = DatabaseConfig(username="u", password="p", name="db", host="h", port=5432)
        assert db.url == "postgresql://u:p@h:5432/db"

    def test_url_with_custom_port(self):
        db = DatabaseConfig(username="u", password="p", name="db", host="h", port=5433)
        assert db.url == "postgresql://u:p@h:5433/db"


class TestLoadConfig:
    def test_load_from_toml(self, tmp_config, monkeypatch):
        monkeypatch.delenv("APP_DB_NAME", raising=False)
        path = tmp_config(
            '[database]\nusername = "alice"\npassword = "secret"\n'
            'name = "mydb"\nhost = "dbhost"\nport = 3306\n'
        )
        cfg = load_config(config_path=path)
        assert cfg.database.username == "alice"
        assert cfg.database.password == "secret"
        assert cfg.database.name == "mydb"
        assert cfg.database.host == "dbhost"
        assert cfg.database.port == 3306

    def test_defaults_for_host_and_port(self, tmp_config):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
        )
        cfg = load_config(config_path=path)
        assert cfg.database.host == "localhost"
        assert cfg.database.port == 5432

    def test_missing_file_and_no_env_raises(self, tmp_path, monkeypatch):
        for var in ("APP_DB_USERNAME", "APP_DB_PASSWORD", "APP_DB_NAME",
                     "APP_DB_HOST", "APP_DB_PORT", "APP_CONFIG_PATH"):
            monkeypatch.delenv(var, raising=False)
        missing = tmp_path / "nonexistent.toml"
        with pytest.raises(ValueError, match="Missing required database config"):
            load_config(config_path=missing)

    def test_env_vars_override_file(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "fileuser"\npassword = "filepass"\n'
            'name = "filedb"\nhost = "filehost"\nport = 5432\n'
        )
        monkeypatch.setenv("APP_DB_USERNAME", "envuser")
        monkeypatch.setenv("APP_DB_NAME", "envdb")
        cfg = load_config(config_path=path)
        assert cfg.database.username == "envuser"
        assert cfg.database.name == "envdb"
        # Non-overridden values stay from file
        assert cfg.database.password == "filepass"
        assert cfg.database.host == "filehost"

    def test_env_vars_without_file(self, tmp_path, monkeypatch):
        monkeypatch.setenv("APP_DB_USERNAME", "eu")
        monkeypatch.setenv("APP_DB_PASSWORD", "ep")
        monkeypatch.setenv("APP_DB_NAME", "edb")
        missing = tmp_path / "nope.toml"
        cfg = load_config(config_path=missing)
        assert cfg.database.username == "eu"
        assert cfg.database.host == "localhost"  # default

    def test_env_port_override(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
        )
        monkeypatch.setenv("APP_DB_PORT", "9999")
        cfg = load_config(config_path=path)
        assert cfg.database.port == 9999

    def test_app_config_path_env(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "x"\npassword = "y"\nname = "z"\n'
        )
        monkeypatch.setenv("APP_CONFIG_PATH", str(path))
        cfg = load_config()
        assert cfg.database.username == "x"


class TestLoggingConfigValidation:
    def test_invalid_log_level_from_toml_raises(self, tmp_config):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
            '[logging]\nlevel = "verbose"\n'
        )
        with pytest.raises(ValueError):
            load_config(config_path=path)

    def test_invalid_log_output_from_toml_raises(self, tmp_config):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
            '[logging]\noutput = "nowhere"\n'
        )
        with pytest.raises(ValueError):
            load_config(config_path=path)

    def test_invalid_log_level_from_env_raises(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
        )
        monkeypatch.setenv("APP_LOG_LEVEL", "spammy")
        with pytest.raises(ValueError):
            load_config(config_path=path)

    def test_invalid_log_output_from_env_raises(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
        )
        monkeypatch.setenv("APP_LOG_OUTPUT", "nowhere")
        with pytest.raises(ValueError):
            load_config(config_path=path)

    def test_valid_log_level_loads(self, tmp_config):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
            '[logging]\nlevel = "debug"\n'
        )
        cfg = load_config(config_path=path)
        assert cfg.logging.level == "debug"

    def test_valid_log_output_loads(self, tmp_config):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
            '[logging]\noutput = "file"\n'
        )
        cfg = load_config(config_path=path)
        assert cfg.logging.output == "file"


class TestGetConfig:
    def test_caching(self, tmp_config, monkeypatch):
        path = tmp_config(
            '[database]\nusername = "u"\npassword = "p"\nname = "db"\n'
        )
        monkeypatch.setenv("APP_CONFIG_PATH", str(path))
        c1 = get_config()
        c2 = get_config()
        assert c1 is c2
