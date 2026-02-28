"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create extension for uuid generation (postgres)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.create_table(
        'villages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
    )

    op.create_index('ix_villages_name', 'villages', ['name'])

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('username', sa.String(length=150), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=512), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('role', sa.String(length=32), nullable=True),
        sa.Column('village_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('villages.id', ondelete='CASCADE'), nullable=True),
    )

    op.create_table(
        'weather_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('village_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('villages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('precipitation', sa.Float(), nullable=True),
        sa.Column('humidity', sa.Float(), nullable=True),
    )

    op.create_index('ix_weather_village', 'weather_data', ['village_id'])

    op.create_table(
        'market_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('village_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('villages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('commodity', sa.String(length=128), nullable=False),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_index('ix_market_village', 'market_prices', ['village_id'])

    op.create_table(
        'soil_health',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('village_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('villages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ph', sa.Float(), nullable=True),
        sa.Column('organic_matter', sa.Float(), nullable=True),
        sa.Column('nitrogen', sa.Float(), nullable=True),
    )

    op.create_index('ix_soil_village', 'soil_health', ['village_id'])

    op.create_table(
        'risk_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('village_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('villages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
    )

    op.create_index('ix_risk_village', 'risk_scores', ['village_id'])


def downgrade():
    op.drop_index('ix_risk_village', table_name='risk_scores')
    op.drop_table('risk_scores')
    op.drop_index('ix_soil_village', table_name='soil_health')
    op.drop_table('soil_health')
    op.drop_index('ix_market_village', table_name='market_prices')
    op.drop_table('market_prices')
    op.drop_index('ix_weather_village', table_name='weather_data')
    op.drop_table('weather_data')
    op.drop_table('users')
    op.drop_index('ix_villages_name', table_name='villages')
    op.drop_table('villages')