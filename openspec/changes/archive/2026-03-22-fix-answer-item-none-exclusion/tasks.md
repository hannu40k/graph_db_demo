## 1. Schema
- [x] 1.1 Add `model_config = ConfigDict(exclude_none=True)` to `AnswerItem` in `app/schemas.py`
- [x] 1.2 Remove the `# TODO CLAUE FIX` comment at `app/schemas.py:53`

## 2. Tests
- [x] 2.1 Add test in `app/tests/test_schemas.py` verifying that an `AnswerItem` with only `paths` set does not include a `cheapest` key in the JSON output
- [x] 2.2 Add test in `app/tests/test_schemas.py` verifying that an `AnswerItem` with only `cheapest` set does not include a `paths` key in the JSON output
- [x] 2.3 Review existing tests in `app/tests/test_api.py` — ensure no tests assert `cheapest: null` or `paths: null` in answers (fix any that do)
