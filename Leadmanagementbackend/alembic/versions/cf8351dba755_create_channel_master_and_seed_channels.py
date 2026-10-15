
"""Create channel master and seed Gmail and WhatsApp."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# Revision identifiers
revision: str = "cf8351dba755"
down_revision: Union[str, Sequence[str], None] = "abc123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # ---------------------------------------------------------
    # 1. CREATE ENUM TYPES
    # ---------------------------------------------------------
    channel_category = postgresql.ENUM(
        "MESSAGING",
        "EMAIL",
        "SOCIAL",
        "SMS",
        "VOICE",
        "WEBSITE",
        name="channelcategory",
    )

    auth_type = postgresql.ENUM(
        "OAUTH",
        "API_KEY",
        "INTERNAL",
        name="authtype",
    )

    channel_status = postgresql.ENUM(
        "ACTIVE",
        "INACTIVE",
        name="channelstatus",
    )

    channel_category.create(bind, checkfirst=True)
    auth_type.create(bind, checkfirst=True)
    channel_status.create(bind, checkfirst=True)

    # ---------------------------------------------------------
    # 2. CREATE CHANNEL MASTER TABLE
    # ---------------------------------------------------------
    op.create_table(
        "channel_master",
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
            "code",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "category",
            channel_category,
            nullable=False,
        ),
        sa.Column(
            "auth_type",
            auth_type,
            nullable=False,
        ),
        sa.Column(
            "status",
            channel_status,
            nullable=False,
            server_default=sa.text("'ACTIVE'"),
        ),
        sa.Column(
            "supports_send",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "supports_receive",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "supports_webhook",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "supports_oauth",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "supports_media",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "supports_sync",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "icon",
            sa.String(255),
            nullable=True,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 3. UNIQUE INDEX
    # ---------------------------------------------------------
    op.create_index(
        "ix_channel_master_code",
        "channel_master",
        ["code"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 4. SEED GMAIL AND WHATSAPP
    # ---------------------------------------------------------
    channel_master = sa.table(
        "channel_master",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String(50)),
        sa.column("name", sa.String(100)),
        sa.column("category", channel_category),
        sa.column("auth_type", auth_type),
        sa.column("status", channel_status),
        sa.column("supports_send", sa.Boolean()),
        sa.column("supports_receive", sa.Boolean()),
        sa.column("supports_webhook", sa.Boolean()),
        sa.column("supports_oauth", sa.Boolean()),
        sa.column("supports_media", sa.Boolean()),
        sa.column("supports_sync", sa.Boolean()),
        sa.column("icon", sa.String(255)),
        sa.column("description", sa.Text()),
    )

    op.bulk_insert(
        channel_master,
        [
            {
                "id": uuid4(),
                "code": "gmail",
                "name": "Gmail",
                "category": "EMAIL",
                "auth_type": "OAUTH",
                "status": "ACTIVE",
                "supports_send": True,
                "supports_receive": True,
                "supports_webhook": True,
                "supports_oauth": True,
                "supports_media": True,
                "supports_sync": True,
                "icon": "gmail",
                "description": "Gmail integration",
            },
            {
                "id": uuid4(),
                "code": "whatsapp",
                "name": "WhatsApp",
                "category": "MESSAGING",
                "auth_type": "OAUTH",
                "status": "ACTIVE",
                "supports_send": True,
                "supports_receive": True,
                "supports_webhook": True,
                "supports_oauth": True,
                "supports_media": True,
                "supports_sync": False,
                "icon": "whatsapp",
                "description": "WhatsApp Cloud API integration",
            },
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()

    # Drop the table and its index first.
    op.drop_index(
        "ix_channel_master_code",
        table_name="channel_master",
    )
    op.drop_table("channel_master")

    # Drop enum types only if no other database objects use them.
    postgresql.ENUM(
        name="channelcategory",
    ).drop(bind, checkfirst=True)

    postgresql.ENUM(
        name="authtype",
    ).drop(bind, checkfirst=True)

    postgresql.ENUM(
        name="channelstatus",
    ).drop(bind, checkfirst=True)
