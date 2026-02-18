"""update 'users_sports_preferences_equipments' table

Revision ID: 076d33eab04f
Revises: ff53544547cd
Create Date: 2026-02-15 16:36:52.694015

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "076d33eab04f"
down_revision = "ff53544547cd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "users_sports_preferences_equipments", schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column("equipment_type_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "users_sports_preferences_equipments_equipment_types_fkey",
            "equipment_types",
            ["equipment_type_id"],
            ["id"],
            ondelete="CASCADE",
        )

    equipments_helper = sa.Table(
        "equipments",
        sa.MetaData(),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("equipment_type_id", sa.Integer(), nullable=False),
    )

    connection = op.get_bind()
    for equipment in connection.execute(equipments_helper.select()):
        op.execute(f"""
            UPDATE users_sports_preferences_equipments
            SET equipment_type_id = {equipment.equipment_type_id}
            WHERE users_sports_preferences_equipments.equipment_id = {equipment.id}
            """)

    op.alter_column(
        "users_sports_preferences_equipments",
        "equipment_type_id",
        nullable=False,
    )

    op.execute(
        """
        INSERT INTO equipment_types (label, is_active)
        VALUES ('Racket', True), ('Paddle', True);
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM equipment_types
        WHERE label IN ('Racket', 'Paddle');
        """
    )

    with op.batch_alter_table(
        "users_sports_preferences_equipments", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "users_sports_preferences_equipments_equipment_types_fkey",
            type_="foreignkey",
        )
        batch_op.drop_column("equipment_type_id")
