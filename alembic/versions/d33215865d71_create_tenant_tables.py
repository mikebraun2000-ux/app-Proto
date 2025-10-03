"""create tenant tables

Revision ID: d33215865d71
Revises: 
Create Date: 2025-10-02 00:28:34.223035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'd33215865d71'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)

    if not inspector.has_table("tenant"):
        tenant_table = op.create_table(
        "tenant",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("subscription_status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(length=120), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=120), nullable=True),
        sa.Column("current_period_end", sa.DateTime(), nullable=True),
        sa.Column("trial_end", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    else:
        tenant_table = sa.Table(
            "tenant",
            sa.MetaData(),
            autoload_with=bind,
        )

    if not inspector.has_table("tenant_settings"):
        settings_table = op.create_table(
        "tenant_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("invoice_prefix", sa.String(length=20), nullable=True, server_default="INV"),
        sa.Column("invoice_next_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("payment_terms_days", sa.Integer(), nullable=False, server_default="14"),
        sa.Column("default_currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("tax_rate_default", sa.Float(), nullable=True),
        sa.Column("branding_primary_color", sa.String(length=20), nullable=True),
        sa.Column("branding_secondary_color", sa.String(length=20), nullable=True),
        sa.Column("footer_text", sa.String(length=500), nullable=True),
        sa.Column("retention_days_time_entries", sa.Integer(), nullable=True),
        sa.Column("retention_days_logs", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id"),
    )

    else:
        settings_table = sa.Table(
            "tenant_settings",
            sa.MetaData(),
            autoload_with=bind,
        )

    if not inspector.has_index("tenant_settings", "ix_tenant_settings_tenant_id"):
        op.create_index("ix_tenant_settings_tenant_id", "tenant_settings", ["tenant_id"], unique=True)

    # Ensure default tenant exists
    result = bind.execute(sa.select(tenant_table.c.id).where(tenant_table.c.id == 1)).fetchone()
    if result is None:
        bind.execute(
            tenant_table.insert().values(
                id=1,
                name="Default Tenant",
                status="active",
                subscription_status="active",
                created_at=sa.func.now(),
                updated_at=sa.func.now(),
            )
        )

    settings_exists = bind.execute(
        sa.select(settings_table.c.id).where(settings_table.c.tenant_id == 1)
    ).fetchone()
    if settings_exists is None:
        bind.execute(
            settings_table.insert().values(
                tenant_id=1,
                invoice_prefix="INV",
                invoice_next_number=1,
                payment_terms_days=14,
                default_currency="EUR",
                created_at=sa.func.now(),
                updated_at=sa.func.now(),
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_tenant_settings_tenant_id", table_name="tenant_settings")
    op.drop_table("tenant_settings")
    op.drop_table("tenant")
