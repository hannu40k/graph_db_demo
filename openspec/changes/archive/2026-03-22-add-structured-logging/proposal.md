# Change: Add structured logging with structlog

## Why
The application currently has no logging infrastructure. Structured logging via `structlog` will provide consistent, machine-parseable log output across the web backend and CLI tools, making debugging and observability straightforward.

## What Changes
- Add `structlog` as a project dependency
- Add a `[logging]` section to `config.toml` with log level, log file path, and output destination options
- Add environment variable overrides for logging config (`APP_LOG_*`)
- Create a logging module (`app/logging.py`) that configures structlog with stdlib integration
- Web backend logs to stdout and/or file (`logs/app.log` by default); CLI apps log to stdout only
- Provide a `get_logger()` helper for obtaining bound loggers throughout the codebase

## Impact
- Affected specs: `app-config` (new `[logging]` section), new `structured-logging` capability
- Affected code: `app/config.py`, new `app/logging.py`, `config.toml`, `config.toml.example`, `pyproject.toml`
