"""Add equipments and equipment types for workouts

Revision ID: 171dcd7e5f2b
Revises: 24eb097614e4
Create Date: 2023-03-20 22:50:47.672811

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


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
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('equipment_type_id', sa.Integer(), nullable=True),
        sa.Column('creation_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column(
            'total_distance',
            sa.Numeric(precision=10, scale=3),
            server_default=sa.text('0.0'),
            nullable=True,
        ),
        sa.Column(
            'total_duration',
            sa.Interval(),
            server_default=sa.text("'00:00:00'"),
            nullable=False,
        ),
        sa.Column(
            'total_moving',
            sa.Interval(),
            server_default=sa.text("'00:00:00'"),
            nullable=False,
        ),
        sa.Column(
            'total_workouts',
            sa.Integer(),
            server_default=sa.text('0'),
            nullable=False,
        ),
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
        sa.UniqueConstraint(
            'uuid',
            name='equipments_uuid_key',
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

    op.create_table(
        'users_sports_preferences_equipments',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sport_id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['equipment_id'], ['equipments.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['sport_id'], ['sports.id'], ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'sport_id', 'equipment_id'),
    )


def downgrade():
    op.drop_table('users_sports_preferences_equipments')

    op.drop_table('workout_equipments')
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_equipments_user_id'))

    op.drop_table('equipments')
    op.drop_table('equipment_types')
