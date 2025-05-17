"""replace 'users_data_export' table with 'user_tasks' table and update following tables:
  - 'app_config'
  - 'users'
  - 'workouts'
  - 'workout_segments'

Revision ID: b0ef6ca5ec92
Revises: 78a90b587a9b
Create Date: 2025-03-28 12:01:30.310651

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b0ef6ca5ec92"
down_revision = "514c727b7feb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "task_type",
            sa.Enum(
                "user_data_export",
                "workouts_archive_upload",
                name="task_types",
            ),
            nullable=False,
        ),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("errored", sa.Boolean(), nullable=False),
        sa.Column("aborted", sa.Boolean(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=255), nullable=True),
        sa.Column(
            "errors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column(
            "data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
        sa.Column("message_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid", name="user_tasks_uuid_key"),
    )
    with op.batch_alter_table("user_tasks", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_user_tasks_task_type"), ["task_type"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_user_tasks_user_id"), ["user_id"], unique=False
        )

    op.execute("""
        INSERT INTO user_tasks
          (uuid, user_id, created_at, updated_at, task_type, progress, errored, aborted, file_path, file_size)
        SELECT
          gen_random_uuid(),
          ude.user_id,
          ude.created_at,
          ude.updated_at,
          'user_data_export',
          CASE WHEN ude.completed IS TRUE THEN 100 ELSE 0 END,
          ude.completed IS TRUE AND ude.file_name IS NULL,
          FALSE,  
          ude.file_name,
          ude.file_size
        FROM users_data_export as ude
        ORDER BY ude.created_at;
    """)

    with op.batch_alter_table("users_data_export", schema=None) as batch_op:
        batch_op.drop_index("ix_users_data_export_user_id")

    op.drop_table("users_data_export")

    with op.batch_alter_table("app_config", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("file_sync_limit_import", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("file_limit_import", sa.Integer(), nullable=True)
        )

    op.execute("""
        UPDATE app_config
        SET file_sync_limit_import = app_config.gpx_limit_import,
            file_limit_import = app_config.gpx_limit_import;
    """)

    with op.batch_alter_table("app_config", schema=None) as batch_op:
        batch_op.alter_column("file_sync_limit_import", nullable=False)
        batch_op.alter_column("file_limit_import", nullable=False)
        batch_op.drop_column("gpx_limit_import")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "hr_visibility",
                sa.Enum(
                    "PUBLIC", "FOLLOWERS", "PRIVATE", name="visibility_levels"
                ),
                server_default="PRIVATE",
                nullable=False,
            )
        )

    with op.batch_alter_table("workout_segments", schema=None) as batch_op:
        batch_op.add_column(sa.Column("max_hr", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("ave_hr", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("max_cadence", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("ave_cadence", sa.Integer(), nullable=True)
        )

    with op.batch_alter_table("workouts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("original_file", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(sa.Column("max_hr", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("ave_hr", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("max_cadence", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("ave_cadence", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("source", sa.String(length=100), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("workouts", schema=None) as batch_op:
        batch_op.drop_column("source")
        batch_op.drop_column("ave_cadence")
        batch_op.drop_column("max_cadence")
        batch_op.drop_column("ave_hr")
        batch_op.drop_column("max_hr")
        batch_op.drop_column("original_file")

    with op.batch_alter_table("workout_segments", schema=None) as batch_op:
        batch_op.drop_column("ave_cadence")
        batch_op.drop_column("max_cadence")
        batch_op.drop_column("ave_hr")
        batch_op.drop_column("max_hr")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("hr_visibility")

    with op.batch_alter_table("app_config", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "gpx_limit_import",
                sa.INTEGER(),
                autoincrement=False,
                nullable=True,
            )
        )

    op.execute("""
               UPDATE app_config
               SET gpx_limit_import = app_config.file_sync_limit_import
               """)

    op.create_table(
        "users_data_export",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "user_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "completed", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "file_name",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "file_size", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="users_data_export_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="users_data_export_pkey"),
    )
    with op.batch_alter_table("users_data_export", schema=None) as batch_op:
        batch_op.create_index(
            "ix_users_data_export_user_id", ["user_id"], unique=True
        )

    op.execute("""
        INSERT INTO users_data_export
          (user_id, created_at, updated_at, completed, file_name, file_size)
        SELECT
          ut.user_id,
          ut.created_at,
          ut.updated_at,
          CASE WHEN ut.progress = 100 THEN TRUE ELSE FALSE END,
          ut.file_path,
          ut.file_size
        FROM user_tasks as ut
        WHERE ut.task_type = 'user_data_export'
        ORDER BY ut.created_at;
    """)

    with op.batch_alter_table("user_tasks", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_tasks_user_id"))
        batch_op.drop_index(batch_op.f("ix_user_tasks_task_type"))

    op.drop_table("user_tasks")
    op.execute("drop type task_types;")

    with op.batch_alter_table("app_config", schema=None) as batch_op:
        batch_op.alter_column("gpx_limit_import", nullable=False)
        batch_op.drop_column("file_limit_import")
        batch_op.drop_column("file_sync_limit_import")
