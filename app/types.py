"""Pure Python domain types/models for internal processing needs."""

from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    name: str


class Edge(BaseModel):
    id: str
    from_node: str
    to_node: str
    cost: float = Field(default=0.0, ge=0)


class Graph(BaseModel):
    id: str
    name: str
    nodes: list[Node]
    edges: list[Edge]
