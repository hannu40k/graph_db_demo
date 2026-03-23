# app-config Specification

## Purpose
TBD - created by archiving change add-app-config. Update Purpose after archive.
## Requirements
### Requirement: Config file loading
The application MUST load configuration from a TOML file (`config.toml`) at the project root.

#### Scenario: Config file exists with all database fields
Given a `config.toml` with `[database]` section containing `username`, `password`, `name`, `host`, `port`
When the config is loaded
Then a config object is returned with all values populated from the file

#### Scenario: Config file not found and no env vars
Given no `config.toml` exists and no `APP_DB_*` env vars are set
When the config is loaded
Then a clear error is raised indicating missing configuration

#### Scenario: Config file path override
Given `APP_CONFIG_PATH` env var is set to `/custom/path/config.toml`
When the config is loaded
Then the file at that path is used instead of the default location

#### Scenario: Config file with logging section
Given a `config.toml` with a `[logging]` section containing `level`, `file_path`, and `output`
When the config is loaded
Then a config object is returned with `logging` populated from the file values

#### Scenario: Config file without logging section
Given a `config.toml` with no `[logging]` section
When the config is loaded
Then the `logging` field uses defaults: level `info`, file_path `logs/app.log`, output `both`

### Requirement: Environment variable overrides
Environment variables with the prefix `APP_` MUST override values from the config file.

#### Scenario: Env var overrides file value
Given `config.toml` has `username = "fileuser"` and `APP_DB_USERNAME=envuser` is set
When the config is loaded
Then `config.database.username` equals `"envuser"`

#### Scenario: Partial env var override
Given `config.toml` has all fields and only `APP_DB_NAME=otherdb` is set
When the config is loaded
Then only `config.database.name` is overridden; all other values come from the file

#### Scenario: Env vars without config file
Given no `config.toml` exists but all `APP_DB_*` env vars are set
When the config is loaded
Then a valid config object is returned using env var values with defaults for host/port

### Requirement: Database URL construction
The config object MUST construct a PostgreSQL connection URL from individual parameters.

#### Scenario: URL constructed from config values
Given `username=u`, `password=p`, `name=db`, `host=h`, `port=5432`
When `config.database.url` is accessed
Then it returns `"postgresql://u:p@h:5432/db"`

### Requirement: Integration with database layer
`app/db.py` and `alembic/env.py` MUST use the config object for database connection.

#### Scenario: App uses config for engine creation
Given a valid config
When `get_engine()` is called
Then the engine is created using the URL from the config object, not from a raw `DATABASE_URL` env var

#### Scenario: Alembic uses config for migrations
Given a valid config
When alembic runs migrations
Then the database URL is sourced from the config object

### Requirement: Extensible config structure
The config object MUST be structured to allow adding new top-level sections without modifying existing code.

#### Scenario: New section added
Given a new `[server]` section is added to `config.toml`
When a corresponding dataclass is added to `app/config.py`
Then the new section is loaded alongside `[database]` without changing database config code

### Requirement: Example config and gitignore
A `config.toml.example` MUST be provided and `config.toml` MUST be gitignored.

#### Scenario: Example file documents all fields
Given the project is freshly cloned
When a developer looks at `config.toml.example`
Then all config fields are listed with example values and comments explaining each

### Requirement: Logging config value validation
The application MUST reject invalid values for `LogLevel` and `LogOutput` at config
load time by raising a `ValueError`, rather than silently accepting them.

#### Scenario: Invalid log level raises error
- **WHEN** the config specifies an unrecognised log level (e.g. `"verbose"`)
- **THEN** `load_config` raises a `ValueError` before returning a config object

#### Scenario: Invalid log output raises error
- **WHEN** the config specifies an unrecognised output destination (e.g. `"nowhere"`)
- **THEN** `load_config` raises a `ValueError` before returning a config object

#### Scenario: Valid log level loads successfully
- **WHEN** the config specifies a valid log level (`"debug"`, `"info"`, `"warning"`, `"error"`, or `"critical"`)
- **THEN** `load_config` returns a config object without error

#### Scenario: Valid log output loads successfully
- **WHEN** the config specifies a valid output destination (`"stdout"`, `"file"`, or `"both"`)
- **THEN** `load_config` returns a config object without error

### Requirement: Logging environment variable overrides
Environment variables with the prefix `APP_LOG_` MUST override logging values from the config file.

#### Scenario: APP_LOG_LEVEL overrides file value
Given `config.toml` has `level = "info"` under `[logging]` and `APP_LOG_LEVEL=debug` is set
When the config is loaded
Then `config.logging.level` equals `"debug"`

#### Scenario: APP_LOG_FILE_PATH overrides file value
Given `config.toml` has `file_path = "logs/app.log"` under `[logging]` and `APP_LOG_FILE_PATH=/var/log/app.log` is set
When the config is loaded
Then `config.logging.file_path` equals `"/var/log/app.log"`

#### Scenario: APP_LOG_OUTPUT overrides file value
Given `config.toml` has `output = "both"` under `[logging]` and `APP_LOG_OUTPUT=stdout` is set
When the config is loaded
Then `config.logging.output` equals `"stdout"`

