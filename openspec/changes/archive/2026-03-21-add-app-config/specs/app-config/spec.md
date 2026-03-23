# Capability: app-config

Provides file-based application configuration with environment variable overrides.

## ADDED Requirements

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
