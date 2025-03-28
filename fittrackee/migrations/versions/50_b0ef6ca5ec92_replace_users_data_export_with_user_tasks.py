"""replace 'users_data_export' table with 'user_tasks' table

Revision ID: b0ef6ca5ec92
Revises: 78a90b587a9b
Create Date: 2025-03-28 12:01:30.310651

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b0ef6ca5ec92"
down_revision = "78a90b587a9b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column(
            "task_type",
            sa.Enum("user_data_export", name="task_types"),
            nullable=False,
        ),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("errored", sa.Boolean(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
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
          (user_id, created_at, updated_at, task_type, progress, errored, file_path, file_size)
        SELECT
          ude.user_id,
          ude.created_at,
          ude.updated_at,
          'user_data_export',
          CASE WHEN ude.completed IS TRUE THEN 100 ELSE 0 END,
          ude.completed IS TRUE AND ude.file_name IS NULL,
          ude.file_name,
          ude.file_size
        FROM users_data_export as ude
        ORDER BY ude.created_at;
    """)

    with op.batch_alter_table("users_data_export", schema=None) as batch_op:
        batch_op.drop_index("ix_users_data_export_user_id")

    op.drop_table("users_data_export")


def downgrade():
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
