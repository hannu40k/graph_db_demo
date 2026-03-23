# Tasks: auto-create-test-database

## T1 – Implement automatic DB creation and teardown in `test_engine`

- [x] 1.1 Derive a maintenance-database URL from `_test_config` by replacing the
      database name component with `"postgres"`.
- [x] 1.2 In `test_engine` setup: connect to the maintenance DB, query
      `pg_database` for the test DB name, and `CREATE DATABASE` with
      `AUTOCOMMIT` if it does not exist.
- [x] 1.3 In `test_engine` teardown (after `drop_all` and `dispose`): connect to
      the maintenance DB and `DROP DATABASE` with `AUTOCOMMIT`.
- [x] 1.4 Run `uv run ruff check app && uv run ty check app && uv run pytest`
      to confirm all quality gates pass.
