import networkx as nx
from lxml import etree
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.logging import get_logger
from app.models import EdgeDB, GraphDB, NodeDB
from app.schemas import CheapestPath, NodePaths
from app.types import Edge, Graph, Node

_logger = get_logger(__name__)


class GraphXmlParseError(Exception):
    """Raised when an XML graph file fails validation."""


# Graph paths
_PATH_GRAPH_ID = ["graph", "id"]
_PATH_GRAPH_NAME = ["graph", "name"]
_PATH_GRAPH_NODES = ["graph", "nodes"]

# Node paths
_PATH_GRAPH_NODES_NODE = ["graph", "nodes", "node"]
_PATH_GRAPH_NODES_NODE_ID = ["graph", "nodes", "node", "id"]
_PATH_GRAPH_NODES_NODE_NAME = ["graph", "nodes", "node", "name"]

# Edge paths
_PATH_GRAPH_EDGES = ["graph", "edges"]
_PATH_GRAPH_EDGES_NODE = ["graph", "edges", "node"]
_PATH_GRAPH_EDGES_NODE_ID = ["graph", "edges", "node", "id"]
_PATH_GRAPH_EDGES_NODE_FROM = ["graph", "edges", "node", "from"]
_PATH_GRAPH_EDGES_NODE_TO = ["graph", "edges", "node", "to"]
_PATH_GRAPH_EDGES_NODE_COST = ["graph", "edges", "node", "cost"]


class XmlGraphParser:
    """Parses a directed weighted graph from an XML file into a Graph domain object.

    Uses lxml.etree.iterparse for streaming support (large file compatibility).

    NOTE: iterparse caveats:
    - XML syntactic validation occurs as the XML is traversed.
    - ordering validation (nodes group must come before edges
    group) is enforced inline during iteration, not validated before starting work.
    These are expected trade-offs of streaming XML parsing.
    """

    @staticmethod
    def _validate_and_build_edge(cur_edge: dict[str, list[str]], node_ids: set[str]) -> Edge:
        """Validate a parsed edge buffer and return an Edge domain object.

        Raises:
            GraphXmlParseError: if any validation rule is violated.
        """
        froms = cur_edge["from"]
        tos = cur_edge["to"]

        if len(froms) != 1:
            raise GraphXmlParseError(
                f"Edge must have exactly one <from> element, got {len(froms)}"
            )

        if len(tos) != 1:
            raise GraphXmlParseError(
                f"Edge must have exactly one <to> element, got {len(tos)}"
            )

        from_node = froms[0]
        to_node = tos[0]

        if from_node not in node_ids:
            raise GraphXmlParseError(
                f"Edge references undefined node id: '{from_node}'"
            )

        if to_node not in node_ids:
            raise GraphXmlParseError(
                f"Edge references undefined node id: '{to_node}'"
            )

        cost = 0.0

        if cur_edge["cost"]:
            try:
                cost = float(cur_edge["cost"][0])
            except ValueError as exc:
                raise GraphXmlParseError(
                    f"Invalid cost value: '{cur_edge['cost'][0]}'"
                ) from exc
            if cost < 0:
                raise GraphXmlParseError(
                    f"Edge cost must be non-negative, got {cost}"
                )

        # TODO does it make sense to allow empty edge id ?
        edge_id = cur_edge["id"][0] if cur_edge["id"] else ""

        return Edge(id=edge_id, from_node=from_node, to_node=to_node, cost=cost)

    def from_xml_file(self, file_path: str) -> Graph:
        """Parse an XML graph file and return a Graph domain object.

        Raises:
            GraphXmlParseError: if any validation rule is violated.
        """
        graph_id: str | None = None
        graph_name: str | None = None
        nodes: list[Node] = []
        node_ids: set[str] = set()
        edges: list[Edge] = []
        nodes_group_seen = False

        # Buffers for the element currently being parsed
        cur_node: dict[str, str] = {}
        cur_edge: dict[str, list[str]] = {}

        # Track the element path as a stack so we can distinguish
        # <nodes><node> (graph node) from <edges><node> (edge)
        path: list[str] = []

        try:
            context = etree.iterparse(file_path, events=("start", "end"))
            for event, elem in context:
                tag = elem.tag
                text = (elem.text or "").strip()

                if event == "start":
                    path.append(tag)

                    if path == _PATH_GRAPH_EDGES:
                        # NOTE: iterparse caveat applies here — we can only check
                        # ordering at this point during iteration, not before.
                        if not nodes_group_seen:
                            raise GraphXmlParseError(
                                "Nodes group must appear before edges group in the XML"
                            )
                    elif path == _PATH_GRAPH_NODES_NODE:
                        cur_node = {}
                    elif path == _PATH_GRAPH_EDGES_NODE:
                        cur_edge = {"id": [], "from": [], "to": [], "cost": []}

                elif event == "end":
                    if path == _PATH_GRAPH_ID:
                        graph_id = text
                    elif path == _PATH_GRAPH_NAME:
                        graph_name = text

                    # Graph node completion
                    elif path == _PATH_GRAPH_NODES_NODE_ID:
                        cur_node["id"] = text
                    elif path == _PATH_GRAPH_NODES_NODE_NAME:
                        cur_node["name"] = text
                    elif path == _PATH_GRAPH_NODES_NODE:
                        nid = cur_node.get("id", "")
                        if nid in node_ids:
                            raise GraphXmlParseError(f"Duplicate node id: '{nid}'")
                        node_ids.add(nid)
                        nodes.append(Node(id=nid, name=cur_node.get("name", "")))
                        cur_node = {}

                    # Nodes group completion
                    elif path == _PATH_GRAPH_NODES:
                        nodes_group_seen = True
                        if not nodes:
                            raise GraphXmlParseError(
                                "Nodes group must contain at least one node"
                            )

                    # Edge element completion
                    elif path == _PATH_GRAPH_EDGES_NODE_ID:
                        cur_edge["id"].append(text)
                    elif path == _PATH_GRAPH_EDGES_NODE_FROM:
                        cur_edge["from"].append(text)
                    elif path == _PATH_GRAPH_EDGES_NODE_TO:
                        cur_edge["to"].append(text)
                    elif path == _PATH_GRAPH_EDGES_NODE_COST:
                        cur_edge["cost"].append(text)
                    elif path == _PATH_GRAPH_EDGES_NODE:
                        edges.append(self._validate_and_build_edge(cur_edge, node_ids))
                        cur_edge = {}

                    path.pop()
                    elem.clear()

        except GraphXmlParseError:
            raise
        except Exception as exc:
            raise GraphXmlParseError(f"Failed to parse XML file: {exc}") from exc

        if not graph_id:
            raise GraphXmlParseError("Graph must have an <id> element")
        if not graph_name:
            raise GraphXmlParseError("Graph must have a <name> element")

        return Graph(id=graph_id, name=graph_name, nodes=nodes, edges=edges)


class GraphService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_latest_graph(self) -> GraphDB | None:
        """Fetch the most recently inserted graph with all its nodes and edges."""
        _logger.debug("get_latest_graph")

        statement = (
            select(GraphDB)
            .order_by(GraphDB.created_at.desc())  # type: ignore[union-attr]
            .limit(1)
            .options(
                selectinload(GraphDB.nodes),  # type: ignore[arg-type]
                selectinload(GraphDB.edges),  # type: ignore[arg-type]
            )
        )

        result = self.session.exec(statement).first()

        _logger.debug("get_latest_graph_result", found=result is not None)

        return result

    def get_graph(self, graph_id: str) -> GraphDB | None:
        """Fetch a graph with all its nodes and edges eagerly loaded."""
        _logger.debug("get_graph", graph_id=graph_id)

        statement = (
            select(GraphDB)
            .where(GraphDB.id == graph_id)
            .options(
                selectinload(GraphDB.nodes),  # type: ignore[arg-type]
                selectinload(GraphDB.edges),  # type: ignore[arg-type]
            )
        )

        result = self.session.exec(statement).first()

        _logger.debug("get_graph_result", graph_id=graph_id, found=result is not None)

        return result

    def _build_digraph(self, graph: GraphDB) -> nx.DiGraph:
        """Build a networkx DiGraph (directed graph) from the SQLModel graph, using cost as edge weight."""
        digraph: nx.DiGraph = nx.DiGraph()

        for node in graph.nodes:
            digraph.add_node(node.id)

        for edge in graph.edges:
            cost = float(edge.cost) if edge.cost is not None else 0.0
            digraph.add_edge(edge.from_node_id, edge.to_node_id, cost=cost)

        return digraph

    def get_paths(self, graph: GraphDB, start: str, end: str) -> NodePaths:
        """Return all simple paths from start to end using DFS.

        Self-loops are naturally excluded because all_simple_paths does not revisit nodes.
        If start == end, returns the trivial path [[start]] (zero edges traversed).
        If no path exists, returns False.
        """
        _logger.debug("get_paths", graph_id=graph.id, start=start, end=end)
        digraph = self._build_digraph(graph)

        if start not in digraph or end not in digraph:
            # General note on passing arguments to `model_validate`:
            # `ty` tool generates the Pydantic constructor using alias="from" as the parameter name, and doesn't
            # understand that populate_by_name=True makes from_= valid. Since `from` is a reserved
            # Python keyword, it can never appear as a kwarg, so `ty` reports both a missing and an unknown argument.
            # With more time, could research a proper workaround, but for now it is dictionaries.
            return NodePaths.model_validate({"from": start, "to": end, "paths": False})

        paths = list(nx.all_simple_paths(digraph, source=start, target=end))
        if not paths:
            return NodePaths.model_validate({"from": start, "to": end, "paths": False})

        return NodePaths.model_validate({"from": start, "to": end, "paths": paths})

    def get_cheapest_path(self, graph: GraphDB, start: str, end: str) -> CheapestPath:
        """Return the cheapest path from start to end using Dijkstra's algorithm.

        Tiebreaker: fewest nodes. If still tied, first path found is returned.
        Special cases:
        - start == end → return [start]
        - no path exists → path=False
        """
        _logger.debug("get_cheapest_path", graph_id=graph.id, start=start, end=end)
        if start == end:
            return CheapestPath.model_validate({"from": start, "to": end, "path": [start]})

        digraph = self._build_digraph(graph)
        if start not in digraph or end not in digraph:
            return CheapestPath.model_validate({"from": start, "to": end, "path": False})

        try:
            all_shortest = list(
                nx.all_shortest_paths(digraph, source=start, target=end, weight="cost")
            )
            # Pick the path with fewest nodes; ties broken by first found
            cheapest = min(all_shortest, key=len)
            return CheapestPath.model_validate({"from": start, "to": end, "path": cheapest})
        except nx.NetworkXNoPath:
            return CheapestPath.model_validate({"from": start, "to": end, "path": False})

    def insert_graph(self, graph: Graph) -> str:
        """Convert Graph domain type to DB models, persist all, and return the created graph id.
        Note: Transactions managed by caller.
        """
        _logger.debug("insert_graph", graph_id=graph.id, node_count=len(graph.nodes), edge_count=len(graph.edges))

        graph_db = GraphDB(id=graph.id, name=graph.name)

        node_dbs = [
            NodeDB(id=n.id, graph_id=graph.id, name=n.name) for n in graph.nodes
        ]

        edge_dbs = [
            EdgeDB(id=e.id, graph_id=graph.id, from_node_id=e.from_node, to_node_id=e.to_node, cost=e.cost)
            for e in graph.edges
        ]

        self.session.add(graph_db)

        for node in node_dbs:
            self.session.add(node)

        self.session.flush()

        for edge in edge_dbs:
            self.session.add(edge)

        self.session.flush()

        return graph_db.id
