"""add preferences for segments creation (for .fit files)

Revision ID: 1648fe51cbd1
Revises: b0ef6ca5ec92
Create Date: 2025-06-15 10:43:41.712789

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from fittrackee.users.models import SEGMENTS_CREATION_EVENTS

# revision identifiers, used by Alembic.
revision = "1648fe51cbd1"
down_revision = "b0ef6ca5ec92"
branch_labels = None
depends_on = None


def upgrade():
    events = postgresql.ENUM(
        *SEGMENTS_CREATION_EVENTS, name="segments_creation_events"
    )
    events.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "segments_creation_event",
                events,
                server_default="only_manual",
                nullable=False,
            )
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("segments_creation_event")
    events = postgresql.ENUM(
        *SEGMENTS_CREATION_EVENTS, name="segments_creation_events"
    )
    events.drop(op.get_bind())
