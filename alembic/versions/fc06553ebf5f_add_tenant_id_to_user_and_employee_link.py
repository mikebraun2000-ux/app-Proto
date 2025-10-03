"""add tenant id to user and employee link

Revision ID: fc06553ebf5f
Revises: 2c04f4b61831
Create Date: 2025-10-02 00:52:40.237240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc06553ebf5f'
down_revision: Union[str, Sequence[str], None] = '2c04f4b61831'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Add tenant_id to user
    user_columns = {col["name"] for col in inspector.get_columns("user")}
    if "tenant_id" not in user_columns:
        op.add_column(
            "user",
            sa.Column("tenant_id", sa.Integer(), nullable=False, server_default="1"),
        )
        op.execute("UPDATE user SET tenant_id = 1 WHERE tenant_id IS NULL")
        op.execute("PRAGMA table_info('user')")
        try:
            op.execute(sa.text("ALTER TABLE user ALTER COLUMN tenant_id DROP DEFAULT"))
        except Exception:
            pass
        op.create_index("ix_user_tenant_id", "user", ["tenant_id"], unique=False)

    # Add user_id to employee
    employee_columns = {col["name"] for col in inspector.get_columns("employee")}
    if "user_id" not in employee_columns:
        op.add_column(
            "employee",
            sa.Column("user_id", sa.Integer(), nullable=True),
        )

        # attempt mapping by email or full_name
        employees = bind.execute(sa.text("SELECT id, email, full_name FROM employee")).fetchall()
        for emp in employees:
            user_id = None
            if emp[1]:
                user_id = bind.execute(
                    sa.text("SELECT id FROM user WHERE email = :email"), {"email": emp[1]}
                ).scalar()
            if user_id is None:
                user_id = bind.execute(
                    sa.text("SELECT id FROM user WHERE full_name = :name"), {"name": emp[2]}
                ).scalar()
            if user_id:
                bind.execute(
                    sa.text("UPDATE employee SET user_id = :uid WHERE id = :eid"),
                    {"uid": user_id, "eid": emp[0]},
                )

        # Fallback: assign to default admin
        admin_id = bind.execute(
            sa.text("SELECT id FROM user WHERE role = 'admin' ORDER BY id LIMIT 1")
        ).scalar()
        if admin_id:
            bind.execute(
                sa.text("UPDATE employee SET user_id = :uid WHERE user_id IS NULL"),
                {"uid": admin_id},
            )

        op.execute("UPDATE employee SET user_id = 1 WHERE user_id IS NULL")
        op.create_index("ix_employee_user_id", "employee", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    pass
