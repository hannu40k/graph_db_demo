"""Unit tests for GraphService path-finding logic (no DB required)."""


from datetime import UTC

from app.models import EdgeDB, GraphDB, NodeDB
from app.schemas import NodePaths
from app.services.graph_service import GraphService


def make_graph(
    graph_id: str,
    nodes: list[tuple[str, str]],
    edges: list[tuple[str, str, str, float]],
) -> GraphDB:
    """Build an in-memory GraphDB (not persisted) for unit testing."""
    graph = GraphDB(id=graph_id, name="Test Graph")
    graph.nodes = [NodeDB(id=nid, graph_id=graph_id, name=name) for nid, name in nodes]
    graph.edges = [
        EdgeDB(id=eid, graph_id=graph_id, from_node_id=f, to_node_id=t, cost=c)
        for eid, f, t, c in edges
    ]
    return graph


# --- Sample graphs for unit testing ---

GRAPH_1 = make_graph(
    "g1",
    nodes=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D"), ("e", "E")],
    edges=[
        ("e1", "a", "e", 42.0),
        ("e2", "a", "b", 50.0),
        ("e3", "b", "e", 4.2),
        ("e4", "c", "d", 0.0),
        ("e5", "a", "a", 0.42),  # self-loop
    ],
)

GRAPH_3 = make_graph(
    "g3",
    nodes=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D"), ("e", "E")],
    edges=[
        ("e1", "a", "b", 1.0),
        ("e2", "b", "c", 1.0),
        ("e3", "c", "d", 1.0),
        ("e4", "d", "e", 1.0),
        ("e5", "a", "c", 2.0),
        ("e6", "a", "d", 3.0),
    ],
)


class TestGetPaths:
    def _service(self):
        return GraphService(session=None)  # type: ignore[arg-type]

    def test_multiple_paths(self):
        result = self._service().get_paths(GRAPH_1, "a", "e")
        assert isinstance(result, NodePaths)
        # Both simple paths should be present (order may vary)
        paths = [tuple(p) for p in result.paths]
        assert ("a", "b", "e") in paths
        assert ("a", "e") in paths

    def test_no_path_between_disconnected_nodes(self):
        result = self._service().get_paths(GRAPH_1, "a", "h")
        assert result.paths is False

    def test_no_path_returns_false(self):
        # c->d only; no path from a to d via that edge since a doesn't connect there
        result = self._service().get_paths(GRAPH_1, "c", "a")
        assert result.paths is False

    def test_self_loop_excluded(self):
        """The a->a self-loop must not appear in path results."""
        result = self._service().get_paths(GRAPH_1, "a", "e")
        for path in result.paths:
            assert path.count("a") == 1, f"Self-loop detected in path: {path}"

    def test_start_equals_end_returns_trivial_path(self):
        """start == end yields the trivial zero-length path [[start]]."""
        result = self._service().get_paths(GRAPH_1, "a", "a")
        assert result.paths == [["a"]]

    def test_from_to_echoed_in_result(self):
        result = self._service().get_paths(GRAPH_1, "a", "e")
        assert result.from_ == "a"
        assert result.to == "e"


class TestGetCheapestPath:
    def _service(self):
        return GraphService(session=None)  # type: ignore[arg-type]

    def test_basic_cheapest(self):
        """a->e (42) is cheaper than a->b->e (50+4.2=54.2)."""
        result = self._service().get_cheapest_path(GRAPH_1, "a", "e")
        assert result.path == ["a", "e"]

    def test_tiebreaker_fewest_nodes(self):
        """graph_3: three paths all cost 4; pick the one with fewest nodes (a->d->e)."""
        result = self._service().get_cheapest_path(GRAPH_3, "a", "e")
        assert result.path == ["a", "d", "e"]

    def test_no_path_returns_false(self):
        result = self._service().get_cheapest_path(GRAPH_1, "a", "h")
        assert result.path is False

    def test_start_equals_end(self):
        result = self._service().get_cheapest_path(GRAPH_1, "a", "a")
        assert result.path == ["a"]

    def test_from_to_echoed_in_result(self):
        result = self._service().get_cheapest_path(GRAPH_1, "a", "e")
        assert result.from_ == "a"
        assert result.to == "e"


class TestGetLatestGraph:
    def test_returns_none_when_no_graphs(self, db_session):
        service = GraphService(session=db_session)
        assert service.get_latest_graph() is None

    def test_returns_single_graph(self, db_session):
        from tests.conftest import make_sample_graph_1

        make_sample_graph_1(db_session)
        service = GraphService(session=db_session)
        result = service.get_latest_graph()
        assert result is not None
        assert result.id == "g1"

    def test_returns_most_recently_inserted_graph(self, db_session):
        """When multiple graphs exist, the one with the latest created_at is returned."""
        from datetime import datetime

        older = GraphDB(
            id="older",
            name="Older Graph",
            created_at=datetime(2020, 1, 1, tzinfo=UTC),
        )
        newer = GraphDB(
            id="newer",
            name="Newer Graph",
            created_at=datetime(2021, 1, 1, tzinfo=UTC),
        )

        db_session.add(older)
        db_session.add(newer)
        db_session.flush()

        service = GraphService(session=db_session)
        result = service.get_latest_graph()

        assert result is not None
        assert result.id == "newer"
