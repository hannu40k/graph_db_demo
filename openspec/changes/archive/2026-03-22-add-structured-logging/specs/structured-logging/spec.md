## ADDED Requirements
### Requirement: Logging configuration setup
The application MUST provide a `configure_logging()` function that initializes structlog with stdlib logging integration based on the application config.

#### Scenario: Web mode with default config
- **WHEN** `configure_logging(config)` is called without `cli_mode`
- **THEN** structlog is configured with JSON rendering, the log level from config is applied, and handlers are set up according to the `output` config value (stdout, file, or both)

#### Scenario: CLI mode ignores file settings
- **WHEN** `configure_logging(config, cli_mode=True)` is called
- **THEN** structlog is configured with stdout output only, regardless of the `output` and `file_path` config values

#### Scenario: Log directory created automatically
- **WHEN** `configure_logging(config)` is called with a `file_path` whose parent directory does not exist and output includes file
- **THEN** the parent directory is created before the file handler is attached

### Requirement: Logger retrieval
The application MUST provide a `get_logger()` function that returns a bound structlog logger.

#### Scenario: Get a named logger
- **WHEN** `get_logger("app.services.graph")` is called
- **THEN** a structlog bound logger is returned with the logger name bound as context

#### Scenario: Get a logger without a name
- **WHEN** `get_logger()` is called without arguments
- **THEN** a structlog bound logger is returned

### Requirement: Stdlib logging integration
structlog MUST be configured to bridge Python's stdlib `logging` so that log output from third-party libraries (e.g., uvicorn, SQLAlchemy) is processed through structlog's pipeline.

#### Scenario: Uvicorn logs go through structlog
- **WHEN** the web backend is running and uvicorn emits a log message
- **THEN** the message is formatted by structlog's processor chain and sent to the configured handlers

### Requirement: Log output format
Log output MUST be structured JSON by default.

#### Scenario: JSON output contains standard fields
- **WHEN** a log message is emitted
- **THEN** the output contains at least `event`, `level`, `timestamp`, and `source` fields in JSON format, where `source` is the file path of the calling module

### Requirement: Log level configuration
The configured log level MUST control which messages are emitted.

#### Scenario: Messages below configured level are suppressed
- **WHEN** the log level is set to `warning`
- **THEN** `info` and `debug` messages are not emitted, but `warning`, `error`, and `critical` messages are
