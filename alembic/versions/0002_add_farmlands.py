"""add farmlands table

Revision ID: 0002_add_farmlands
Revises: 0001_initial
Create Date: 2026-03-07 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_add_farmlands'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure uuid-ossp extension exists (may not have been created if
    # the initial migration was applied via create_all rather than Alembic)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    op.create_table(
        'farmlands',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('farmer_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('village_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('villages.id', ondelete='SET NULL'), nullable=True),
        sa.Column('land_name', sa.String(length=255), nullable=False),
        sa.Column('total_acres', sa.Float(), nullable=False),
        sa.Column('soil_type', sa.String(length=128), nullable=True),
        sa.Column('irrigation_type', sa.String(length=128), nullable=True),
        sa.Column('crop_type', sa.String(length=128), nullable=True),
        sa.Column('sowing_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('harvest_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('geo_lat', sa.Float(), nullable=True),
        sa.Column('geo_lng', sa.Float(), nullable=True),
        sa.Column('notes', sa.String(length=1024), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=32), nullable=True),
        sa.Column('ai_insight', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True),
    )

    op.create_index('ix_farmlands_farmer_id', 'farmlands', ['farmer_id'])
    op.create_index('ix_farmlands_village_id', 'farmlands', ['village_id'])


def downgrade():
    op.drop_index('ix_farmlands_village_id', table_name='farmlands')
    op.drop_index('ix_farmlands_farmer_id', table_name='farmlands')
    op.drop_table('farmlands')
