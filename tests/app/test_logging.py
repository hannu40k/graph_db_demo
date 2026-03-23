"""Tests for app.logging: configure_logging() and LoggingConfig behaviour."""

import json
import logging
from pathlib import Path

import pytest

from app.config import AppConfig, DatabaseConfig, LoggingConfig, LogLevel, LogOutput, load_config

# ---------------------------------------------------------------------------
# LoggingConfig defaults and env-var overrides
# ---------------------------------------------------------------------------


def test_logging_config_defaults():
    cfg = LoggingConfig()
    assert cfg.level == "info"
    assert cfg.file_path == "logs/app.log"
    assert cfg.output == "both"


def test_logging_config_from_toml(tmp_path):
    toml = tmp_path / "config.toml"
    toml.write_text(
        "[database]\nusername='u'\npassword='p'\nname='db'\n"
        "[logging]\nlevel='debug'\nfile_path='/tmp/out.log'\noutput='stdout'\n"
    )
    cfg = load_config(toml)
    assert cfg.logging.level == "debug"
    assert cfg.logging.file_path == "/tmp/out.log"
    assert cfg.logging.output == "stdout"


def test_logging_config_toml_missing_section_uses_defaults(tmp_path):
    toml = tmp_path / "config.toml"
    toml.write_text("[database]\nusername='u'\npassword='p'\nname='db'\n")
    cfg = load_config(toml)
    assert cfg.logging.level == "info"
    assert cfg.logging.file_path == "logs/app.log"
    assert cfg.logging.output == "both"


def test_logging_env_var_level_override(tmp_path, monkeypatch):
    toml = tmp_path / "config.toml"
    toml.write_text("[database]\nusername='u'\npassword='p'\nname='db'\n[logging]\nlevel='info'\n")
    monkeypatch.setenv("APP_LOG_LEVEL", "warning")
    cfg = load_config(toml)
    assert cfg.logging.level == "warning"


def test_logging_env_var_file_path_override(tmp_path, monkeypatch):
    toml = tmp_path / "config.toml"
    toml.write_text("[database]\nusername='u'\npassword='p'\nname='db'\n")
    monkeypatch.setenv("APP_LOG_FILE_PATH", "/var/log/custom.log")
    cfg = load_config(toml)
    assert cfg.logging.file_path == "/var/log/custom.log"


def test_logging_env_var_output_override(tmp_path, monkeypatch):
    toml = tmp_path / "config.toml"
    toml.write_text("[database]\nusername='u'\npassword='p'\nname='db'\n")
    monkeypatch.setenv("APP_LOG_OUTPUT", "file")
    cfg = load_config(toml)
    assert cfg.logging.output == "file"


# ---------------------------------------------------------------------------
# configure_logging() — web mode
# ---------------------------------------------------------------------------


@pytest.fixture()
def base_config():
    return AppConfig(
        database=DatabaseConfig(username="u", password="p", name="db"),
        logging=LoggingConfig(level=LogLevel.DEBUG, file_path="", output=LogOutput.STDOUT),
    )


def _make_config(tmp_path: Path, output: LogOutput = LogOutput.STDOUT) -> AppConfig:
    return AppConfig(
        database=DatabaseConfig(username="u", password="p", name="db"),
        logging=LoggingConfig(
            level=LogLevel.DEBUG,
            file_path=str(tmp_path / "logs" / "app.log"),
            output=output,
        ),
    )


def test_configure_logging_web_stdout_only(tmp_path):
    """Note: The test is verifying the config-driven path to stdout, i.e. when output=LogOutput.STDOUT is set in config.

    Using cli_mode=False explicitly tests that the config setting alone is sufficient to route to stdout,
    without relying on the cli_mode override. If it used cli_mode=True instead, it would also produce a StreamHandler,
    but it would be testing the override behavior, not the config behavior"""
    from app.logging import configure_logging

    cfg = _make_config(tmp_path, output=LogOutput.STDOUT)
    configure_logging(cfg, cli_mode=False)

    root = logging.getLogger()
    handler_types = [type(h).__name__ for h in root.handlers]
    assert "StreamHandler" in handler_types
    assert "FileHandler" not in handler_types


def test_configure_logging_web_file_only(tmp_path):
    from app.logging import configure_logging

    cfg = _make_config(tmp_path, output=LogOutput.FILE)
    configure_logging(cfg, cli_mode=False)

    root = logging.getLogger()
    handler_types = [type(h).__name__ for h in root.handlers]
    assert "FileHandler" in handler_types
    assert "StreamHandler" not in handler_types


def test_configure_logging_web_both(tmp_path):
    from app.logging import configure_logging

    cfg = _make_config(tmp_path, output=LogOutput.BOTH)
    configure_logging(cfg, cli_mode=False)

    root = logging.getLogger()
    handler_types = [type(h).__name__ for h in root.handlers]
    assert "StreamHandler" in handler_types
    assert "FileHandler" in handler_types


def test_configure_logging_cli_mode_stdout_only(tmp_path):
    from app.logging import configure_logging

    # Even with output=LogOutput.FILE, CLI mode should only use stdout.
    cfg = _make_config(tmp_path, output=LogOutput.FILE)
    configure_logging(cfg, cli_mode=True)

    root = logging.getLogger()
    handler_types = [type(h).__name__ for h in root.handlers]
    assert "StreamHandler" in handler_types
    assert "FileHandler" not in handler_types


def test_configure_logging_creates_log_directory(tmp_path):
    from app.logging import configure_logging

    log_dir = tmp_path / "new_dir" / "nested"
    cfg = AppConfig(
        database=DatabaseConfig(username="u", password="p", name="db"),
        logging=LoggingConfig(
            level=LogLevel.INFO,
            file_path=str(log_dir / "app.log"),
            output=LogOutput.FILE,
        ),
    )
    assert not log_dir.exists()
    configure_logging(cfg, cli_mode=False)
    assert log_dir.exists()


def test_log_output_json_contains_required_fields(tmp_path, capsys):
    from app.logging import configure_logging, get_logger

    cfg = _make_config(tmp_path, output=LogOutput.STDOUT)
    configure_logging(cfg, cli_mode=False)

    logger = get_logger("test.module")
    logger.info("hello world")

    captured = capsys.readouterr().out.strip()
    # The last non-empty line should be JSON
    line = [ln for ln in captured.splitlines() if ln.strip()][-1]
    data = json.loads(line)
    assert "event" in data
    assert "level" in data
    assert "timestamp" in data
    assert "pathname" in data


def test_configure_logging_respects_level(tmp_path, capsys):
    from app.logging import configure_logging, get_logger

    cfg = AppConfig(
        database=DatabaseConfig(username="u", password="p", name="db"),
        logging=LoggingConfig(level=LogLevel.WARNING, file_path="", output=LogOutput.STDOUT),
    )
    configure_logging(cfg, cli_mode=False)

    logger = get_logger("test.level")
    logger.info("should be suppressed")
    logger.warning("should appear")

    captured = capsys.readouterr().out.strip()
    lines = [ln for ln in captured.splitlines() if ln.strip()]
    events = [json.loads(ln).get("event") for ln in lines]
    assert "should be suppressed" not in events
    assert "should appear" in events
