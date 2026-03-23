# Tasks: refactor-test-layout

## Ordered Work Items

1. **Create top-level `tests/` directory tree**
   - Create `tests/__init__.py`
   - Create `tests/app/__init__.py`
   - Create `tests/app/cli/__init__.py`
   - Create `tests/app/services/__init__.py`
   - Validation: `ls tests/` shows expected directories

2. **Move shared fixtures**
   - Move `app/tests/conftest.py` → `tests/conftest.py`
   - Validation: file exists at new path; no imports broken

3. **Move `app/tests/` test files**
   - Move `app/tests/test_api.py` → `tests/app/test_api.py`
   - Move `app/tests/test_config.py` → `tests/app/test_config.py`
   - Move `app/tests/test_logging.py` → `tests/app/test_logging.py`
   - Move `app/tests/test_schemas.py` → `tests/app/test_schemas.py`
   - Move `app/tests/test_graph_service.py` → `tests/app/services/test_graph_service.py`
   - Validation: old paths gone; new paths present

4. **Move `app/cli/tests/` test files**
   - Move `app/cli/tests/test_parse_graph_cli.py` → `tests/app/cli/test_parse_graph_cli.py`
   - Move `app/cli/tests/test_xml_parser.py` → `tests/app/cli/test_xml_parser.py`
   - Validation: old paths gone; new paths present

5. **Remove now-empty `__init__.py` and test directories from `app/`**
   - Delete `app/tests/__init__.py`, `app/tests/` directory
   - Delete `app/cli/tests/__init__.py`, `app/cli/tests/` directory
   - Validation: `app/` tree contains no `tests/` subdirectories

6. **Update `pyproject.toml`**
   - Change `testpaths = ["app/tests", "app/cli/tests"]` → `testpaths = ["tests"]`
   - Validation: `grep testpaths pyproject.toml` shows `["tests"]`

7. **Update `test-infrastructure` spec**
   - Modify the spec to reference `tests/conftest.py` instead of `app/tests/conftest.py`
   - Validation: `openspec validate refactor-test-layout --strict` passes

8. **Run quality gates**
   - `uv run ruff check app`
   - `uv run ty check app`
   - `uv run pytest`
   - All must pass with zero errors

## Dependencies
- Tasks 1–4 are parallelizable once task 1 is complete.
- Tasks 5–6 depend on tasks 2–4 being fully complete.
- Task 7 is independent of tasks 2–6.
- Task 8 must run last.
