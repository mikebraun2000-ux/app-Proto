"""add tenant id to core tables

Revision ID: 2c04f4b61831
Revises: d33215865d71
Create Date: 2025-10-02 00:31:49.560457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '2c04f4b61831'
down_revision: Union[str, Sequence[str], None] = 'd33215865d71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()
    inspector = inspect(bind)

    tables = [
        "user",
        "project",
        "report",
        "employee",
        "timeentry",
        "projectimage",
        "materialusage",
        "invoice",
        "offer",
        "reportimage",
        "companylogo",
    ]

    for table in tables:
        columns = {col["name"] for col in inspector.get_columns(table)}
        indexes = {idx["name"] for idx in inspector.get_indexes(table)}
        fks = {fk["name"] for fk in inspector.get_foreign_keys(table)}

        if "tenant_id" not in columns:
            op.add_column(
                table,
                sa.Column(
                    "tenant_id",
                    sa.Integer(),
                    nullable=False,
                    server_default="1",
                ),
            )
            op.execute(f"UPDATE {table} SET tenant_id = 1 WHERE tenant_id IS NULL")

        if f"ix_{table}_tenant_id" not in indexes:
            op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    tables = [
        "companylogo",
        "reportimage",
        "offer",
        "invoice",
        "materialusage",
        "projectimage",
        "timeentry",
        "employee",
        "report",
        "project",
        "user",
    ]

    for table in tables:
        op.drop_index(f"ix_{table}_tenant_id", table_name=table)
        op.drop_column(table, "tenant_id")
