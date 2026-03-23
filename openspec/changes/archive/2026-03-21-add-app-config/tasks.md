# Tasks: add-app-config

## Phase 1: Config foundation
1. [x] Create `config.toml.example` with `[database]` section and documented defaults matching `docker-compose.yml`
2. [x] Add `config.toml` to `.gitignore`
3. [x] Create `app/config.py` with `DatabaseConfig` and `AppConfig` dataclasses
4. [x] Implement TOML file loading with `tomllib` (resolve project root, handle missing file)
5. [x] Implement env var override logic (`APP_DB_USERNAME`, `APP_DB_PASSWORD`, `APP_DB_NAME`, `APP_DB_HOST`, `APP_DB_PORT`)
6. [x] Add `get_config()` function with caching (load once, reuse)

## Phase 2: Integration
7. [x] Update `app/db.py` to use `get_config().database.url` instead of `os.environ["DATABASE_URL"]`
8. [x] Update `alembic/env.py` to use `get_config().database.url`
9. [x] Update `app/tests/conftest.py` to use config (override via env var or test config)
10. [x] Remove hardcoded `DATABASE_URL` references from the codebase

## Phase 3: Validation
11. [x] Write unit tests for config loading (file only, env override, missing file, partial override)
12. [x] Verify existing tests still pass with config-based DB connection
13. [x] Verify alembic migrations work with config-based URL
