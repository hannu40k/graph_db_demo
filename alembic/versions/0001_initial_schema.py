"""Initial schema: graph, node, edge tables

Revision ID: 0001
Revises:
Create Date: 2026-03-20
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "graph",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "node",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("graph_id", sa.String(32), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id", "graph_id"),
        sa.ForeignKeyConstraint(["graph_id"], ["graph.id"]),
    )
    op.create_index("idx_node_graph_id", "node", ["graph_id"])

    op.create_table(
        "edge",
        sa.Column("id", sa.String(32), nullable=False),
        sa.Column("graph_id", sa.String(32), nullable=False),
        sa.Column("from_node_id", sa.String(32), nullable=False),
        sa.Column("to_node_id", sa.String(32), nullable=False),
        sa.Column("cost", sa.Numeric, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id", "graph_id"),
        sa.ForeignKeyConstraint(["graph_id"], ["graph.id"]),
        sa.ForeignKeyConstraint(
            ["from_node_id", "graph_id"], ["node.id", "node.graph_id"]
        ),
        sa.ForeignKeyConstraint(
            ["to_node_id", "graph_id"], ["node.id", "node.graph_id"]
        ),
    )
    op.create_index("idx_edge_graph_id", "edge", ["graph_id"])


def downgrade() -> None:
    op.drop_index("idx_edge_graph_id", table_name="edge")
    op.drop_table("edge")
    op.drop_index("idx_node_graph_id", table_name="node")
    op.drop_table("node")
    op.drop_table("graph")
