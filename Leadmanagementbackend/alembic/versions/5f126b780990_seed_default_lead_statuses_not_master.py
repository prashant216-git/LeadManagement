"""assign NEW status to existing leads

Revision ID: 5f126b780990
Revises: f11fe448b65b
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "5f126b780990"
down_revision = "f11fe448b65b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    # ---------------------------------------------------------
    # Add unique constraint
    # One lead can have only one current status
    # ---------------------------------------------------------



    # ---------------------------------------------------------
    # Assign NEW status to leads without a status
    # ---------------------------------------------------------

    rows = connection.execute(
        sa.text(
            """
            SELECT
                l.id AS lead_id,
                l.user_id AS user_id,
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
            """
        )
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
    connection = op.get_bind()

    # ---------------------------------------------------------
    # Remove status mappings assigned to NEW
    # ---------------------------------------------------------

    connection.execute(
        sa.text(
            """
            DELETE FROM lead_status ls
            USING lead_status_master lsm
            WHERE ls.status_id = lsm.id
              AND LOWER(lsm.status_name) = 'new'
            """
        )
    )

    # ---------------------------------------------------------
    # Remove unique constraint
    # ---------------------------------------------------------

