
"""Create lead status master table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision: str = "d7a91c2e4f60"
down_revision: Union[str, Sequence[str], None] = "abc123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lead_status_master table.
    op.create_table(
        "lead_status_master",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "colour",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Indexes matching the model.
    op.create_index(
        "ix_lead_status_master_user_id",
        "lead_status_master",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_lead_status_master_created_by",
        "lead_status_master",
        ["created_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_status_master_created_by",
        table_name="lead_status_master",
    )

    op.drop_index(
        "ix_lead_status_master_user_id",
        table_name="lead_status_master",
    )

    op.drop_table("lead_status_master")
