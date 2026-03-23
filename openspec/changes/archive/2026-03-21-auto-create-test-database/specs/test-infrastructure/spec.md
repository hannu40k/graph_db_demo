# test-infrastructure Specification

## Purpose
Defines requirements for the automated test infrastructure, including
database lifecycle management so tests are self-contained and need no
manual setup steps.

## ADDED Requirements

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
