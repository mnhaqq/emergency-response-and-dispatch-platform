"""Initial migration - create vehicles table

Revision ID: 0001
Revises:
Create Date: 2026-03-01
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vehicles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("registration_number", sa.String(), nullable=False, unique=True),
        sa.Column(
            "vehicle_type",
            sa.Enum("AMBULANCE", "FIRE_TRUCK", "POLICE", name="vehicletype"),
            nullable=False,
        ),
        sa.Column("station_id", sa.String(), nullable=False),
        sa.Column("driver_name", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("AVAILABLE", "ON_DUTY", "OUT_OF_SERVICE", name="vehiclestatus"),
            nullable=False,
            server_default="AVAILABLE",
        ),
        sa.Column("current_incident_id", sa.String(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("vehicles")
    op.execute("DROP TYPE IF EXISTS vehicletype")
    op.execute("DROP TYPE IF EXISTS vehiclestatus")
