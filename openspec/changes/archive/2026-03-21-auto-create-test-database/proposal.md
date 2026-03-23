# Change: auto-create-test-database

## Why

The test database `graphdb_test` must currently be created manually via
`docker compose exec` before running tests. This adds friction for new
contributors and makes CI setup error-prone. Automating database creation and
teardown inside the `test_engine` fixture removes the manual step entirely and
keeps the test environment self-contained.

## What Changes

**`app/tests/conftest.py` — `test_engine` fixture**

Before the fixture connects to `graphdb_test`, it will:
1. Connect to the PostgreSQL maintenance database (`postgres`) using the same
   host, port, username, and password already available from `_test_config`.
2. Query `pg_database` to check whether `graphdb_test` exists.
3. Create the database if it is absent (`CREATE DATABASE graphdb_test`).

After all tests finish (teardown), the fixture will:
1. Drop all SQLModel tables (existing behaviour).
2. Dispose the main engine (existing behaviour).
3. Connect to the maintenance database again and execute `DROP DATABASE graphdb_test`.

The DDL statements (`CREATE DATABASE`, `DROP DATABASE`) require `AUTOCOMMIT`
isolation level because PostgreSQL disallows them inside a transaction.

No other files change. The `DatabaseConfig.url` property already supplies
everything needed to derive a maintenance-database URL by substituting the
database name with `postgres`.

## Impact

- Affected spec: new `test-infrastructure` capability (added by this change).
- Affected code: `app/tests/conftest.py` only.
- No migrations, no runtime code, no API changes.
