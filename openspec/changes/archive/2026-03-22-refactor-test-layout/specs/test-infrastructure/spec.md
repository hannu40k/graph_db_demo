## ADDED Requirements

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

