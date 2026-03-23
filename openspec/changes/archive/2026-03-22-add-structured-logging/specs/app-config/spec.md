## MODIFIED Requirements
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

## ADDED Requirements
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
