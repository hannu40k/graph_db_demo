"""Unit tests for XmlGraphParser — no DB required."""

from unittest.mock import MagicMock

import pytest

from app.services.graph_service import GraphService, GraphXmlParseError, XmlGraphParser
from app.types import Edge, Graph, Node

SAMPLES = "samples"
GOOD = f"{SAMPLES}/good"
INVALID = f"{SAMPLES}/invalid"

parser = XmlGraphParser()


class TestValidGraph:
    def test_sample_graph_1_parses_correctly(self):
        graph = parser.from_xml_file(f"{GOOD}/sample_graph_1.xml")
        assert graph.id == "g1"
        assert graph.name == "Sample Graph 1"
        assert len(graph.nodes) == 5
        assert len(graph.edges) == 5
        node_ids = {n.id for n in graph.nodes}
        assert node_ids == {"a", "b", "c", "d", "e"}
        # e4 has no cost → defaults to 0.0
        e4 = next(e for e in graph.edges if e.id == "e4")
        assert e4.cost == 0.0
        assert e4.from_node == "c"
        assert e4.to_node == "d"
        # e5 is a self-loop (a → a)
        e5 = next(e for e in graph.edges if e.id == "e5")
        assert e5.from_node == "a"
        assert e5.to_node == "a"
        assert e5.cost == 0.42


class TestInvalidGraphs:
    def test_invalid_1_missing_graph_id(self):
        with pytest.raises(GraphXmlParseError, match="id"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_1.xml")

    def test_invalid_2_edges_before_nodes(self):
        with pytest.raises(GraphXmlParseError, match="[Nn]ode"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_2.xml")

    def test_invalid_3_empty_nodes_group(self):
        with pytest.raises(GraphXmlParseError, match="[Nn]ode"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_3.xml")

    def test_invalid_4_duplicate_node_ids(self):
        with pytest.raises(GraphXmlParseError, match="[Dd]uplicate"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_4.xml")

    def test_invalid_5_multiple_from_in_edge(self):
        with pytest.raises(GraphXmlParseError, match="[Ee]dge"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_5.xml")

    def test_invalid_6_multiple_to_in_edge(self):
        with pytest.raises(GraphXmlParseError, match="[Ee]dge"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_6.xml")

    def test_invalid_7_edge_references_undefined_from_node(self):
        with pytest.raises(GraphXmlParseError, match="[Uu]ndefined|[Nn]ode"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_7.xml")

    def test_invalid_8_edge_references_undefined_to_node(self):
        with pytest.raises(GraphXmlParseError, match="[Uu]ndefined|[Nn]ode"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_8.xml")

    def test_invalid_9_negative_edge_cost(self):
        with pytest.raises(GraphXmlParseError, match="[Cc]ost|[Nn]egative"):
            parser.from_xml_file(f"{INVALID}/sample_graph_invalid_9.xml")


class TestInsertGraph:
    """Test GraphService.insert_graph with Graph domain type (mocked session)."""

    def test_insert_graph_converts_domain_to_db_models(self):
        session = MagicMock()
        service = GraphService(session=session)

        graph = Graph(
            id="test1",
            name="Test Graph",
            nodes=[Node(id="a", name="A"), Node(id="b", name="B")],
            edges=[Edge(id="e1", from_node="a", to_node="b", cost=1.5)],
        )

        result = service.insert_graph(graph)
        assert result == "test1"
        # graph + 2 nodes + 1 edge = 4 session.add calls
        assert session.add.call_count == 4
        # flush twice: once after nodes (before edges, for FK ordering), once after edges
        assert session.flush.call_count == 2
        session.commit.assert_not_called()
