# Proposal: refactor-test-layout

## Summary
Relocate all test files from within the `app/` source tree to a top-level `tests/` directory that mirrors the source structure. This follows standard Python packaging convention, keeps tests out of the shipped application, and allows a single root-level `conftest.py` to be shared across all test modules.

## Motivation
- **Packaging hygiene**: Tests currently live inside `app/`, meaning they would be included in any installed distribution of the package. A top-level `tests/` directory is excluded from wheels by default.
- **Single `conftest.py`**: The shared fixtures in `app/tests/conftest.py` are invisible to `app/cli/tests/`. A root-level `tests/conftest.py` is automatically picked up by every test under `tests/`.
- **Canonical structure**: `pytest` and most Python tooling assume tests live in a top-level `tests/` directory.
- **Correct placement**: `test_graph_service.py` tests `app/services/graph_service.py` and should live in `tests/app/services/`, not `tests/app/`.

## Current Structure
```
app/
  cli/
    tests/
      __init__.py
      test_parse_graph_cli.py
      test_xml_parser.py
  tests/
    conftest.py
    __init__.py
    test_api.py
    test_config.py
    test_graph_service.py   ← wrong location (services/ missing)
    test_logging.py
    test_schemas.py
pyproject.toml  ← testpaths = ["app/tests", "app/cli/tests"]
```

## Target Structure
```
tests/
  conftest.py               ← moved from app/tests/conftest.py
  __init__.py
  app/
    __init__.py
    test_api.py
    test_config.py
    test_logging.py
    test_schemas.py
    cli/
      __init__.py
      test_parse_graph_cli.py
      test_xml_parser.py
    services/
      __init__.py
      test_graph_service.py  ← correct location
pyproject.toml  ← testpaths = ["tests"]
```

## Scope
- Move and rename files; no changes to test logic or fixture code.
- Update `pyproject.toml` `testpaths`.
- Update the `test-infrastructure` spec to reflect the new `conftest.py` location.
- All quality gates (ruff, ty, pytest) must pass after the change.
