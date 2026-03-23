# test-infrastructure Specification

## Purpose
TBD - created by archiving change auto-create-test-database. Update Purpose after archive.
## Requirements
### Requirement: Automatic test database creation
The `test_engine` fixture MUST create the test database if it does not already
exist before running any tests.

#### Scenario: Test database absent at session start
Given the test database `graphdb_test` does not exist in PostgreSQL
When the test suite is started
Then the fixture connects to the maintenance database (`postgres`) and executes
  `CREATE DATABASE graphdb_test` with `AUTOCOMMIT` isolation level
And subsequent test setup (table creation, seeding) proceeds without error

#### Scenario: Test database already exists at session start
Given the test database `graphdb_test` already exists in PostgreSQL
When the test suite is started
Then the fixture skips `CREATE DATABASE` and proceeds directly to table creation
And no error is raised

### Requirement: Automatic test database teardown
The `test_engine` fixture MUST drop the test database after all tests in the
session have completed.

#### Scenario: Test database dropped after session
Given the test suite has finished running
When the `test_engine` fixture teardown executes
Then all SQLModel tables are dropped first
Then the engine is disposed
Then the fixture connects to the maintenance database and executes
  `DROP DATABASE graphdb_test` with `AUTOCOMMIT` isolation level
And the database no longer exists in PostgreSQL

### Requirement: AUTOCOMMIT for database-level DDL
All `CREATE DATABASE` and `DROP DATABASE` statements MUST be executed with
the `AUTOCOMMIT` isolation level to comply with PostgreSQL's restriction on
running database DDL inside a transaction.

#### Scenario: AUTOCOMMIT used for CREATE DATABASE
Given a connection to the maintenance database
When `CREATE DATABASE graphdb_test` is issued
Then the connection uses `execution_options(isolation_level="AUTOCOMMIT")`
And the statement succeeds without a transaction error

#### Scenario: AUTOCOMMIT used for DROP DATABASE
Given a connection to the maintenance database after the test session
When `DROP DATABASE graphdb_test` is issued
Then the connection uses `execution_options(isolation_level="AUTOCOMMIT")`
And the statement succeeds without a transaction error

### Requirement: Tests reside in a top-level `tests/` directory
All test files MUST be located under a top-level `tests/` directory that mirrors the source tree under `app/`. No test files SHALL reside inside the `app/` source tree.

#### Scenario: Source module has a corresponding test file
Given a source module at `app/<path>/<module>.py`
When the developer adds or locates its tests
Then the test file is at `tests/app/<path>/test_<module>.py`
And no test file exists at `app/<path>/tests/test_<module>.py` or `app/tests/test_<module>.py`

#### Scenario: `test_graph_service.py` reflects its source module path
Given the service module at `app/services/graph_service.py`
When locating its tests
Then the test file is at `tests/app/services/test_graph_service.py`
And no test file exists at `tests/app/test_graph_service.py`

### Requirement: Single root-level `conftest.py`
The shared test fixtures MUST be defined in `tests/conftest.py`. No `conftest.py` SHALL exist inside `app/`.

#### Scenario: Fixtures available to all test modules
Given `tests/conftest.py` defines the `test_engine` and related fixtures
When any test under `tests/` runs
Then pytest automatically discovers and applies the fixtures from `tests/conftest.py`
And no separate `conftest.py` is required in sub-directories

### Requirement: `pyproject.toml` testpaths set to `tests/`
The `[tool.pytest.ini_options]` `testpaths` setting MUST be `["tests"]`.

#### Scenario: Running `uv run pytest`
Given `testpaths = ["tests"]` in `pyproject.toml`
When `uv run pytest` is executed
Then pytest discovers all tests under `tests/` and runs them
And no test files inside `app/` are collected

