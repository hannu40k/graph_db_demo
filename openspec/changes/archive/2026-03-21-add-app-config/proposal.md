# Change: Add Application Config File

## Why
Database credentials are currently hardcoded across `docker-compose.yml`, `app/tests/conftest.py`, and the app itself requires a full `DATABASE_URL` env var to be set manually. There is no single source of truth for configuration, and no structured config object that can grow with the application. A config file provides sensible defaults, a config object enables typed access, and env var overrides support deployment flexibility.

## What Changes
- Add a `config.toml` file at the project root with database parameters: `db_username`, `db_password`, `db_name`, `db_host`, `db_port`
- Create `app/config.py` with a typed config object (Pydantic `BaseSettings` or plain dataclass) that:
  1. Reads defaults from `config.toml` using Python 3.12's built-in `tomllib`
  2. Allows env var overrides (e.g. `APP_DB_USERNAME` overrides `db_username`)
  3. Constructs the `DATABASE_URL` from individual parameters
  4. Is designed as a flat, extensible structure so future settings (e.g. log level, API host/port) can be added without architectural changes
- Update `app/db.py` to use the config object instead of reading `DATABASE_URL` directly from `os.environ`
- Update `alembic/env.py` to use the config object for its database URL
- Update `app/tests/conftest.py` to use config (or its test override) instead of hardcoded credentials
- Add `config.toml` to `.gitignore` and provide a `config.toml.example` with documented defaults

## Design Decisions
- **TOML format**: Already used by the project (`pyproject.toml`), Python 3.12 includes `tomllib` — no new dependency needed.
- **Individual parameters, not a URL**: Storing `db_username`, `db_password`, `db_name`, `db_host`, `db_port` separately is more readable and composable than a single connection URL. The config object constructs the URL internally.
- **Env var prefix `APP_`**: Prevents collisions with system env vars. E.g. `APP_DB_USERNAME`, `APP_DB_PASSWORD`, `APP_DB_NAME`, `APP_DB_HOST`, `APP_DB_PORT`.
- **`db_host` and `db_port` included**: While not explicitly requested, a database connection string requires host and port. Defaults match `docker-compose.yml` (`localhost:5432`).
- **No new dependencies**: Uses `tomllib` (stdlib) + a plain dataclass or Pydantic's `BaseSettings`. Since Pydantic is already a dependency, `BaseSettings` is a natural fit if `pydantic-settings` is acceptable; otherwise a lightweight dataclass + manual env-var loading keeps it zero-dep.

## Impact
- Affected specs: `app-config` (new capability)
- Affected code: `app/config.py` (new), `app/db.py`, `alembic/env.py`, `app/tests/conftest.py`, `config.toml` (new), `config.toml.example` (new), `.gitignore`
