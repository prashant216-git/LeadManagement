from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "f11fe448b65b"  # Replace with the actual parent revision, if any
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

def downgrade() -> None:
    # Do not drop the extension: other tables may depend on it.
    pass