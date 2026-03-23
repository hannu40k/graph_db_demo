"""Test fixtures: real PostgreSQL database, session, TestClient with DI override."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.config import load_config, reset_config
from app.db import get_session
from app.main import app
from app.models import EdgeDB, GraphDB, NodeDB

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
# Tests use the application config with APP_DB_NAME defaulting to "graphdb_test".
# Set APP_DB_* env vars or provide a config.toml to customise.

if "APP_DB_NAME" not in os.environ:
    os.environ["APP_DB_NAME"] = "graphdb_test"

# Reload config so the test db name takes effect
reset_config()
_test_config = load_config()
TEST_DATABASE_URL = _test_config.database.url

# Default PostgreSQL maintenance DB.
_MAINTENANCE_DATABASE_URL = _test_config.database.url.rsplit("/", 1)[0] + "/postgres"
_TEST_DB_NAME = _test_config.database.name


def _maintenance_engine():
    return create_engine(_MAINTENANCE_DATABASE_URL, isolation_level="AUTOCOMMIT")


@pytest.fixture(scope="session")
def test_engine():
    """Create engine and schema once per test session, drop after.

    Creates the test database on demand if it does not exist, and drops it
    after the session completes.
    """
    # Create test db if it does not exist.
    maint = _maintenance_engine()
    with maint.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": _TEST_DB_NAME},
        ).fetchone()
        if not exists:
            conn.execute(text(f"CREATE DATABASE {_TEST_DB_NAME}"))
    maint.dispose()

    # Migrate schema from SQLModels.
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()

    # Drop test db..
    maint = _maintenance_engine()
    with maint.connect() as conn:
        conn.execute(text(f"DROP DATABASE {_TEST_DB_NAME}"))
    maint.dispose()


@pytest.fixture()
def db_session(test_engine):
    """Transactional session rolled back after each test for isolation.

    Uses a connection-level transaction so that even session.commit() calls
    in seed helpers are rolled back at teardown.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient with the real test DB session injected."""

    def override_get_session():
        yield db_session

    # Inject fixture db session into the web app.
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample data helpers
# ---------------------------------------------------------------------------


def _insert_graph(session: Session, graph: GraphDB, nodes: list[NodeDB], edges: list[EdgeDB]) -> GraphDB:
    session.add(graph)

    for node in nodes:
        session.add(node)

    # Flush graph + nodes before adding edges so the FK constraint
    # (from_node_id, graph_id) → (node.id, node.graph_id) is satisfied.
    # Using flush (not commit) keeps everything in the test transaction so
    # the db_session fixture can roll back after each test.
    session.flush()

    for edge in edges:
        session.add(edge)

    session.flush()
    session.refresh(graph)

    return graph


def make_sample_graph_1(session: Session) -> GraphDB:
    """Insert sample_graph_1 (g1) and return the GraphDB object."""
    g_id: str = "g1"
    return _insert_graph(
        session,
        GraphDB(id=g_id, name="Sample Graph 1"),
        [
            NodeDB(id="a", graph_id=g_id, name="A name"),
            NodeDB(id="b", graph_id=g_id, name="B name"),
            NodeDB(id="c", graph_id=g_id, name="C name"),
            NodeDB(id="d", graph_id=g_id, name="D name"),
            NodeDB(id="e", graph_id=g_id, name="E name"),
        ],
        [
            EdgeDB(id="e1", graph_id=g_id, from_node_id="a", to_node_id="e", cost=42),
            EdgeDB(id="e2", graph_id=g_id, from_node_id="a", to_node_id="b", cost=50),
            EdgeDB(id="e3", graph_id=g_id, from_node_id="b", to_node_id="e", cost=4.2),
            EdgeDB(id="e4", graph_id=g_id, from_node_id="c", to_node_id="d", cost=0),
            EdgeDB(id="e5", graph_id=g_id, from_node_id="a", to_node_id="a", cost=0.42),
        ],
    )


def make_sample_graph_3(session: Session) -> GraphDB:
    """Insert sample_graph_3 (g3): equal-cost tiebreaker scenario."""
    g_id: str = "g3"
    return _insert_graph(
        session,
        GraphDB(id=g_id, name="Five Node Multi-Path Graph"),
        [
            NodeDB(id="a", graph_id=g_id, name="Node A"),
            NodeDB(id="b", graph_id=g_id, name="Node B"),
            NodeDB(id="c", graph_id=g_id, name="Node C"),
            NodeDB(id="d", graph_id=g_id, name="Node D"),
            NodeDB(id="e", graph_id=g_id, name="Node E"),
        ],
        [
            EdgeDB(id="e1", graph_id=g_id, from_node_id="a", to_node_id="b", cost=1),
            EdgeDB(id="e2", graph_id=g_id, from_node_id="b", to_node_id="c", cost=1),
            EdgeDB(id="e3", graph_id=g_id, from_node_id="c", to_node_id="d", cost=1),
            EdgeDB(id="e4", graph_id=g_id, from_node_id="d", to_node_id="e", cost=1),
            EdgeDB(id="e5", graph_id=g_id, from_node_id="a", to_node_id="c", cost=2),
            EdgeDB(id="e6", graph_id=g_id, from_node_id="a", to_node_id="d", cost=3),
        ],
    )
