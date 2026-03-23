from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from app.config import load_config
from app.db import get_session
from app.logging import configure_logging, get_logger
from app.models import GraphDB
from app.schemas import AnswerItem, QueryRequest, QueryResponse
from app.services.graph_service import GraphService

configure_logging(load_config())
_logger = get_logger(__name__)
_logger.info("starting")

app = FastAPI(title="Graph Query API")


def _execute_queries(
    graph: GraphDB, request: QueryRequest, graph_service: GraphService
) -> list[AnswerItem]:
    _logger.debug("execute_queries", graph_id=graph.id, query_count=len(request.queries))
    answers: list[AnswerItem] = []
    for query_item in request.queries:
        if query_item.paths is not None:
            q = query_item.paths
            _logger.debug("query_paths", start=q.start, end=q.end)
            node_paths = graph_service.get_paths(graph, q.start, q.end)
            answers.append(AnswerItem(paths=node_paths))
        elif query_item.cheapest is not None:
            q = query_item.cheapest
            _logger.debug("query_cheapest", start=q.start, end=q.end)
            cheapest_path = graph_service.get_cheapest_path(graph, q.start, q.end)
            answers.append(AnswerItem(cheapest=cheapest_path))
    return answers


@app.post("/query", response_model=QueryResponse)
def query_latest_graph(
    request: QueryRequest,
    session: Session = Depends(get_session),
) -> QueryResponse:
    """Query the latest inserted graph."""
    _logger.debug("query_latest_graph", query_count=len(request.queries))
    graph_service = GraphService(session)
    graph = graph_service.get_latest_graph()

    if graph is None:
        raise HTTPException(status_code=404, detail="No graphs in database. Insert a graph first")

    return QueryResponse(answers=_execute_queries(graph, request, graph_service))


@app.post("/query/{graph_id}", response_model=QueryResponse)
def query_graph(
    graph_id: str,
    request: QueryRequest,
    session: Session = Depends(get_session),
) -> QueryResponse:
    """Query a graph by graph_id."""
    _logger.debug("query_graph", graph_id=graph_id, query_count=len(request.queries))
    graph_service = GraphService(session)
    graph = graph_service.get_graph(graph_id)

    if graph is None:
        raise HTTPException(status_code=404, detail=f"Graph '{graph_id}' not found")

    return QueryResponse(answers=_execute_queries(graph, request, graph_service))
