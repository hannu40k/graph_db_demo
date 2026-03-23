"""Application configuration: TOML file with environment variable overrides."""

from __future__ import annotations

import enum
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CONFIG_PATH = _PROJECT_ROOT / "config.toml"

# Environment variable names for overriding config values from main config file.
ENV_CONFIG_PATH = "APP_CONFIG_PATH"

ENV_DB_USERNAME = "APP_DB_USERNAME"
ENV_DB_PASSWORD = "APP_DB_PASSWORD"
ENV_DB_NAME = "APP_DB_NAME"
ENV_DB_HOST = "APP_DB_HOST"
ENV_DB_PORT = "APP_DB_PORT"

ENV_LOG_LEVEL = "APP_LOG_LEVEL"
ENV_LOG_FILE_PATH = "APP_LOG_FILE_PATH"
ENV_LOG_OUTPUT = "APP_LOG_OUTPUT"

# Module level singleton. Access is guarded by providing an accessor function and a reset function for usage in tests.
_config: AppConfig | None = None


@dataclass
class DatabaseConfig:
    username: str = ""
    password: str = ""
    name: str = ""
    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> str:
        return (
            f"postgresql://{self.username}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )

class LogLevel(enum.StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogOutput(enum.StrEnum):
    STDOUT = "stdout"
    FILE = "file"
    BOTH = "both"


@dataclass
class LoggingConfig:
    level: LogLevel = LogLevel.INFO
    file_path: str = "logs/app.log"
    output: LogOutput = LogOutput.BOTH


@dataclass
class AppConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def _load_toml(path: Path) -> dict:
    """Load a TOML file and return its contents, or empty dict if missing."""
    if not path.is_file():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def _apply_env_overrides(db: DatabaseConfig) -> None:
    """Override DatabaseConfig fields from APP_DB_* environment variables."""
    env_map = {
        ENV_DB_USERNAME: "username",
        ENV_DB_PASSWORD: "password",
        ENV_DB_NAME: "name",
        ENV_DB_HOST: "host",
        ENV_DB_PORT: "port",
    }
    for env_var, attr in env_map.items():
        value = os.environ.get(env_var)
        if value is not None:
            if attr == "port":
                setattr(db, attr, int(value))
            else:
                setattr(db, attr, value)


def _apply_log_env_overrides(log: LoggingConfig) -> None:
    """Override LoggingConfig fields from APP_LOG_* environment variables."""
    env_map = {
        ENV_LOG_LEVEL: "level",
        ENV_LOG_FILE_PATH: "file_path",
        ENV_LOG_OUTPUT: "output",
    }
    for env_var, attr in env_map.items():
        value = os.environ.get(env_var)
        if value is not None:
            if attr == "level":
                setattr(log, attr, LogLevel(value))
            elif attr == "output":
                setattr(log, attr, LogOutput(value))
            else:
                setattr(log, attr, value)


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load config from TOML file + env var overrides.

    Args:
        config_path: Explicit path to config file. If None, uses
                     APP_CONFIG_PATH env var or falls back to project root.

    Raises:
        ValueError: If required database fields are missing after loading.
    """
    if config_path is None:
        env_path = os.environ.get(ENV_CONFIG_PATH)
        config_path = Path(env_path) if env_path else _DEFAULT_CONFIG_PATH

    config_data = _load_toml(config_path)
    db_data = config_data.get("database", {})

    db = DatabaseConfig(
        username=db_data.get("username", ""),
        password=db_data.get("password", ""),
        name=db_data.get("name", ""),
        host=db_data.get("host", "localhost"),
        port=int(db_data.get("port", 5432)),
    )

    _apply_env_overrides(db)

    log_data = config_data.get("logging", {})
    log = LoggingConfig(
        level=LogLevel(log_data.get("level", "info")),
        file_path=log_data.get("file_path", "logs/app.log"),
        output=LogOutput(log_data.get("output", "both")),
    )
    _apply_log_env_overrides(log)

    missing = [f for f in ("username", "password", "name") if not getattr(db, f)]
    if missing:
        raise ValueError(
            f"Missing required database config: {', '.join(missing)}. "
            f"Set them in {config_path} or via APP_DB_* environment variables."
        )

    return AppConfig(database=db, logging=log)


def get_config() -> AppConfig:
    """Return the cached application config, loading it on first call."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Clear the cached config. Useful for testing."""
    global _config
    _config = None
