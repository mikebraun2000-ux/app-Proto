"""create tenant invitations table

Revision ID: 502404f3543b
Revises: fc06553ebf5f
Create Date: 2025-10-02 01:04:25.403690

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '502404f3543b'
down_revision: Union[str, Sequence[str], None] = 'fc06553ebf5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("tenant_invitation"):
        op.create_table(
            "tenant_invitation",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(length=150), nullable=False),
            sa.Column("token_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False, server_default="mitarbeiter"),
            sa.Column("invited_by", sa.Integer(), nullable=True),
            sa.Column("accepted_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["invited_by"], ["user.id"], ondelete="SET NULL"),
        )
        op.create_index("ix_tenant_invitation_tenant_id", "tenant_invitation", ["tenant_id"])
        op.create_index("ix_tenant_invitation_email", "tenant_invitation", ["email"])
        op.create_index("ix_tenant_invitation_token_hash", "tenant_invitation", ["token_hash"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_tenant_invitation_token_hash", table_name="tenant_invitation")
    op.drop_index("ix_tenant_invitation_email", table_name="tenant_invitation")
    op.drop_index("ix_tenant_invitation_tenant_id", table_name="tenant_invitation")
    op.drop_table("tenant_invitation")
