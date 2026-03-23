## ADDED Requirements

### Requirement: Logging config value validation
The application MUST reject invalid values for `LogLevel` and `LogOutput` at config
load time by raising a `ValueError`, rather than silently accepting them.

#### Scenario: Invalid log level raises error
- **WHEN** the config specifies an unrecognised log level (e.g. `"verbose"`)
- **THEN** `load_config` raises a `ValueError` before returning a config object

#### Scenario: Invalid log output raises error
- **WHEN** the config specifies an unrecognised output destination (e.g. `"nowhere"`)
- **THEN** `load_config` raises a `ValueError` before returning a config object

#### Scenario: Valid log level loads successfully
- **WHEN** the config specifies a valid log level (`"debug"`, `"info"`, `"warning"`, `"error"`, or `"critical"`)
- **THEN** `load_config` returns a config object without error

#### Scenario: Valid log output loads successfully
- **WHEN** the config specifies a valid output destination (`"stdout"`, `"file"`, or `"both"`)
- **THEN** `load_config` returns a config object without error
