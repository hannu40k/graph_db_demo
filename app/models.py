from datetime import datetime

from sqlalchemy import ForeignKeyConstraint, Index, PrimaryKeyConstraint
from sqlalchemy.sql import func
from sqlmodel import Field, Relationship, SQLModel


class CreatedAtMixin(SQLModel):
    # Note: Will only be None during insert, which will be allowed. DB populates the field.
    created_at: datetime = Field(default=None, sa_column_kwargs={"server_default": func.now()})


class GraphDB(CreatedAtMixin, table=True):
    __tablename__ = "graph"

    id: str = Field(primary_key=True, max_length=32)
    name: str
    nodes: list["NodeDB"] = Relationship(back_populates="graph")
    edges: list["EdgeDB"] = Relationship(back_populates="graph")


class NodeDB(CreatedAtMixin, table=True):
    __tablename__ = "node"

    __table_args__ = (
        # Apparently multiple primary key decalarations on fields to signal composite primary key
        # can sometimes fail, and this is safer to do.
        PrimaryKeyConstraint("id", "graph_id"),
    )

    id: str = Field(max_length=32)
    name: str
    graph_id: str = Field(foreign_key="graph.id", max_length=32, index=True)
    graph: GraphDB = Relationship(back_populates="nodes")


class EdgeDB(CreatedAtMixin, table=True):
    __tablename__ = "edge"

    __table_args__ = (
        ForeignKeyConstraint(
            ["from_node_id", "graph_id"],
            ["node.id", "node.graph_id"],
        ),
        ForeignKeyConstraint(
            ["to_node_id", "graph_id"],
            ["node.id", "node.graph_id"],
        ),
        #
        # Note! For some reason these indexes do not materialize in the database.
        # Initial debugging unfruitful, needs further research.
        #
        Index("ix_edge_from_node", "from_node_id", "graph_id"),
        Index("ix_edge_to_node", "to_node_id", "graph_id"),
    )

    id: str = Field(primary_key=True, max_length=32)
    from_node_id: str = Field(max_length=32, index=True)
    to_node_id: str = Field(max_length=32, index=True)
    cost: float | None = None

    graph_id: str = Field(primary_key=True, foreign_key="graph.id", max_length=32, index=True)
    graph: GraphDB = Relationship(back_populates="edges")
