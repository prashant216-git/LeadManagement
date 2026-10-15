
"""Create lead_status table and assign NEW status to existing leads.

Revision ID: 5f126b780990
Revises: f11fe448b65b
"""

from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "5f126b780990"
down_revision = "f11fe448b65b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    # 1. Create lead_status table
    op.create_table(
        "lead_status",
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
            "lead_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("leads.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lead_status_master.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "update_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )

    # 2. Create indexes
    op.create_index(
        "uq_lead_status_lead",
        "lead_status",
        ["lead_id"],
        unique=True,
    )

    op.create_index(
        "ix_lead_status_lead_id",
        "lead_status",
        ["lead_id"],
    )

    op.create_index(
        "ix_lead_status_status_id",
        "lead_status",
        ["status_id"],
    )

    op.create_index(
        "ix_lead_status_update_by",
        "lead_status",
        ["update_by"],
    )

    op.create_index(
        "idx_lead_status_status",
        "lead_status",
        ["status_id"],
    )

    # 3. Assign NEW status to leads that have no status
    rows = connection.execute(
        sa.text("""
            SELECT
                l.id AS lead_id,
                lsm.id AS status_id
            FROM leads l
            JOIN lead_status_master lsm
              ON lsm.user_id = l.user_id
             AND LOWER(lsm.status_name) = 'new'
             AND lsm.is_active = TRUE
            WHERE NOT EXISTS (
                SELECT 1
                FROM lead_status ls
                WHERE ls.lead_id = l.id
            )
        """)
    ).fetchall()

    for row in rows:
        connection.execute(
            sa.text("""
                INSERT INTO lead_status (
                    id,
                    lead_id,
                    status_id
                )
                VALUES (
                    :id,
                    :lead_id,
                    :status_id
                )
                ON CONFLICT (lead_id) DO NOTHING
            """),
            {
                "id": uuid4(),
                "lead_id": row.lead_id,
                "status_id": row.status_id,
            },
        )


def downgrade() -> None:
    op.drop_table("lead_status")

