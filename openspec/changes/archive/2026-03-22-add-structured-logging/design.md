## Context
The project has a FastAPI web backend and two CLI tools (`parse-graph`, `detect-cycles`). None of them produce structured logs today. We need a logging foundation that both the web backend and CLI tools can use, with configurable output destinations and levels.

## Goals / Non-Goals
- Goals:
  - Configure structlog to output JSON in production and human-readable output for development
  - Integrate structlog with Python's stdlib `logging` so third-party libraries (uvicorn, SQLAlchemy) also produce structured output
  - Make log level, file path, and output destination configurable via `config.toml` and env vars
  - Create directory for log file automatically if it does not exist
  - CLI apps always log to stdout only (no file logging)
- Non-Goals:
  - Adding log statements throughout the codebase (deferred to a follow-up change)
  - Log rotation or aggregation infrastructure
  - Remote log shipping

## Decisions
- **structlog with stdlib bridging**: structlog will be configured as the primary logging interface. stdlib logging will be bridged so that uvicorn, SQLAlchemy, and other libraries also go through structlog's processing pipeline. This is the standard structlog best practice.
- **JSON renderer for production, console renderer for development**: The default renderer will be JSON (structured). A `render_as` config option or auto-detection (based on TTY) can be added later if needed; for now JSON is the default.
- **Two entry points for setup**: `configure_logging()` will accept parameters for context (web vs CLI) so CLI tools skip file handler setup.
- **Config dataclass pattern**: A `LoggingConfig` dataclass mirrors the existing `DatabaseConfig` pattern in `app/config.py`, with env var overrides using the `APP_LOG_*` prefix.

## Risks / Trade-offs
- Adding structlog as a dependency increases the dependency surface — mitigated by structlog being a well-maintained, widely-used package with no transitive dependencies.
- File logging creates a `logs/` directory — the directory is created on demand with `mkdir -p` semantics and is gitignored.

## Open Questions
- None at this time.
