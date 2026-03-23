from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

# --- Request schemas ---

class PathQuery(BaseModel):
    start: str
    end: str


class CheapestQuery(BaseModel):
    start: str
    end: str


class QueryItem(BaseModel):
    """A single query item — exactly one of 'paths' or 'cheapest' must be set."""

    paths: PathQuery | None = None
    cheapest: CheapestQuery | None = None

    @model_validator(mode="after")
    def exactly_one_query_type(self) -> QueryItem:
        has_paths = self.paths is not None
        has_cheapest = self.cheapest is not None
        if has_paths and has_cheapest:
            raise ValueError("A query item must contain 'paths' or 'cheapest', but not both.")
        if not has_paths and not has_cheapest:
            raise ValueError("A query item must contain exactly one of 'paths' or 'cheapest'.")
        return self


class QueryRequest(BaseModel):
    """The main query request. A single request can contain multiple queries."""
    queries: list[QueryItem]


# --- Response schemas ---

class NodePaths(BaseModel):
    """Response for an all-paths query."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    paths: list[list[str]] | bool


class CheapestPath(BaseModel):
    """Response for a cheapest-path query. `path` is False when no path exists."""

    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    path: list[str] | bool


class AnswerItem(BaseModel):
    """A single answer, mirrors the discriminated QueryItem structure. A single answer item only
    contains paths or cheapest, never both."""

    paths: NodePaths | None = None
    cheapest: CheapestPath | None = None

    @model_serializer(mode="wrap")
    def exclude_none_fields(self, handler: Any) -> dict[str, Any]:
        return {k: v for k, v in handler(self).items() if v is not None}


class QueryResponse(BaseModel):
    answers: list[AnswerItem]
