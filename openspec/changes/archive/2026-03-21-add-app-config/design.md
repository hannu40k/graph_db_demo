# Design: Application Config

## Config File Structure

```toml
# config.toml
[database]
username = "graphuser"
password = "graphpass"
name = "graphdb"
host = "localhost"
port = 5432
```

## Config Object

```python
# app/config.py
@dataclass
class DatabaseConfig:
    username: str
    password: str
    name: str
    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class AppConfig:
    database: DatabaseConfig
```

## Resolution Order

1. Load `config.toml` from project root (or path in `APP_CONFIG_PATH` env var)
2. Override any value with matching env var: `APP_DB_USERNAME`, `APP_DB_PASSWORD`, `APP_DB_NAME`, `APP_DB_HOST`, `APP_DB_PORT`
3. If `config.toml` is missing and env vars are not set, raise a clear error

Env vars take precedence over file values. This supports: local dev (use `config.toml`), CI/CD (use env vars), containers (use env vars).

## Integration Points

### `app/db.py`
```python
from app.config import get_config

def get_engine() -> Engine:
    config = get_config()
    return create_engine(config.database.url)
```

### `alembic/env.py`
```python
from app.config import get_config

def get_url() -> str:
    return get_config().database.url
```

### Tests
Tests can either:
- Use a `config.test.toml` file
- Override via `APP_DB_NAME=graphdb_test` env var
- Override config in `conftest.py` directly

## Extensibility

Adding new config sections is straightforward:
```toml
[database]
username = "graphuser"
# ...

[server]
host = "0.0.0.0"
port = 8000
```

```python
@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000

@dataclass
class AppConfig:
    database: DatabaseConfig
    server: ServerConfig
```
