from collections.abc import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from app.config import get_config


def get_engine() -> Engine:
    config = get_config()
    return create_engine(config.database.url)


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    with Session(engine) as session:
        yield session
