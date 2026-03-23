## 1. Configuration
- [x] 1.1 Add `LoggingConfig` dataclass to `app/config.py` with fields: `level`, `file_path`, `output` (stdout, file, both)
- [x] 1.2 Wire `[logging]` TOML section into `AppConfig` and `load_config()`
- [x] 1.3 Add `APP_LOG_*` environment variable overrides (`APP_LOG_LEVEL`, `APP_LOG_FILE_PATH`, `APP_LOG_OUTPUT`)
- [x] 1.4 Update `config.toml.example` with the new `[logging]` section and comments

## 2. Logging module
- [x] 2.1 Add `structlog` dependency to `pyproject.toml`
- [x] 2.2 Create `app/logging.py` with `configure_logging(config, cli_mode=False)` that sets up structlog processors and stdlib integration
- [x] 2.3 In web mode (`cli_mode=False`): configure stdout and/or file handler based on `output` config; create log directory if needed
- [x] 2.4 In CLI mode (`cli_mode=True`): configure stdout handler only, ignore file config
- [x] 2.5 Expose `get_logger(name)` convenience function that returns a bound structlog logger

## 3. Gitignore and defaults
- [x] 3.1 Add `logs/` to `.gitignore`

## 4. Tests
- [x] 4.1 Unit tests for `LoggingConfig` defaults and env var overrides
- [x] 4.2 Unit tests for `configure_logging()` in both web and CLI modes
- [x] 4.3 Test that log directory is created when it does not exist
