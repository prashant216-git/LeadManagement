"""seed default lead statuses for all users

Revision ID: xxxxx
Revises: previous_revision_id
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f11fe448b65b"
down_revision = "cf8351dba755"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    users = connection.execute(
        sa.text(
            """
            SELECT id
            FROM users
            """
        )
    ).fetchall()

    lead_status_master = sa.table(
        "lead_status_master",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("user_id", postgresql.UUID(as_uuid=True)),
        sa.column("status_name", sa.String()),
        sa.column("is_active", sa.Boolean()),
        sa.column("is_default", sa.Boolean()),
        sa.column("created_by", postgresql.UUID(as_uuid=True)),
    )

    for user in users:
        user_id = user[0]

        op.bulk_insert(
            lead_status_master,
            [
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "status_name": "New",
                    "is_active": True,
                    "is_default": True,
                    "created_by": user_id,
                },
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "status_name": "Contacted",
                    "is_active": True,
                    "is_default": False,
                    "created_by": user_id,
                },
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "status_name": "Converted",
                    "is_active": True,
                    "is_default": False,
                    "created_by": user_id,
                },
                {
                    "id": uuid4(),
                    "user_id": user_id,
                    "status_name": "Not Interested",
                    "is_active": True,
                    "is_default": False,
                    "created_by": user_id,
                },
            ],
        )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM lead_status_master
            WHERE status_name IN (
                'New',
                'Contacted',
                'Converted',
                'Not Interested'
            )
            """
        )
    )