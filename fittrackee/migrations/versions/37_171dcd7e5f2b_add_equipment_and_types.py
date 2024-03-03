"""Add equipments and equipment types for workouts

Revision ID: 171dcd7e5f2b
Revises: 24eb097614e4
Create Date: 2023-03-20 22:50:47.672811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '171dcd7e5f2b'
down_revision = '4d51a4ca8001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'equipment_types',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute(
        """
        INSERT INTO equipment_types (label, is_active)
        VALUES 
        ('Shoes', True), ('Bike', True), 
        ('Bike Trainer', True), ('Kayak_Boat', True),
        ('Skis', True), ('Snowshoes', True) 
        """
    )

    op.create_table(
        'equipments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('equipment_type_id', sa.Integer(), nullable=True),
        sa.Column('creation_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ['equipment_type_id'],
            ['equipment_types.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'label',
            'user_id',
            name='equipment_user_label_unique',
        ),
    )
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_equipments_user_id'), ['user_id'], unique=False
        )

    op.create_table(
        'workout_equipments',
        sa.Column('workout_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['workout_id'], ['workouts.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['equipment_id'], ['equipments.id'], ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('workout_id', 'equipment_id'),
    )
    with op.batch_alter_table(
        'users_sports_preferences', schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column('default_equipment_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'users_sports_preferences_default_equipment_id_fkey',
            'equipments',
            ['default_equipment_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade():
    with op.batch_alter_table(
        'users_sports_preferences', schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            'users_sports_preferences_default_equipment_id_fkey',
            type_='foreignkey',
        )
        batch_op.drop_column('default_equipment_id')

    op.drop_table('workout_equipments')
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_equipments_user_id'))

    op.drop_table('equipments')
    op.drop_table('equipment_types')
