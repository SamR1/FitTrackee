"""move pace speed display preferences to sports

Revision ID: d8416412506b
Revises: 0bbe0c8372cf
Create Date: 2026-01-01 11:51:21.071755

Note: since the migration will be released in the same version as the previous
migrations introducing pace display preference, updating existing data is not
necessary.
"""

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d8416412506b"
down_revision = "0bbe0c8372cf"
branch_labels = None
depends_on = None

pace_speed_display = postgresql.ENUM(
    "PACE",
    "SPEED",
    "PACE_AND_SPEED",
    name="pace_speed_display",
)


def upgrade():
    pace_speed_display.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table("sports", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "pace_speed_display",
                pace_speed_display,
                server_default="SPEED",
                nullable=False,
            )
        )

    op.execute(
        """
        UPDATE sports
        SET pace_speed_display = 'PACE'
        WHERE label in (
              'Hiking', 'Running', 'Trail', 'Walking'
        );
        """
    )

    with op.batch_alter_table(
        "users_sports_preferences", schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "pace_speed_display",
                pace_speed_display,
                server_default="SPEED",
                nullable=False,
            )
        )

    op.execute(
        """
        UPDATE users_sports_preferences as usp
        SET pace_speed_display = 'PACE'
        FROM (
            SELECT s.id
            FROM sports s
            WHERE s.label in (
                'Hiking', 'Running', 'Trail', 'Walking'
            )
        ) AS s(id)
        WHERE usp.sport_id = s.id;
        """
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("display_speed_with_pace")


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "display_speed_with_pace",
                sa.BOOLEAN(),
                server_default=sa.text("false"),
                autoincrement=False,
                nullable=False,
            )
        )

    with op.batch_alter_table(
        "users_sports_preferences", schema=None
    ) as batch_op:
        batch_op.drop_column("pace_speed_display")

    with op.batch_alter_table("sports", schema=None) as batch_op:
        batch_op.drop_column("pace_speed_display")

    pace_speed_display.drop(op.get_bind())
