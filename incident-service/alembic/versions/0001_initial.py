"""Initial migration - create incidents table

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
        "incidents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("citizen_name", sa.String(), nullable=False),
        sa.Column(
            "incident_type",
            sa.Enum("MEDICAL", "FIRE", "CRIME", "ACCIDENT", "OTHER", name="incidenttype"),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("assigned_unit_id", sa.String(), nullable=True),
        sa.Column(
            "assigned_unit_type",
            sa.Enum("AMBULANCE", "FIRE_TRUCK", "POLICE", name="respondertype"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum("CREATED", "DISPATCHED", "IN_PROGRESS", "RESOLVED", name="incidentstatus"),
            nullable=False,
            server_default="CREATED",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("incidents")
    op.execute("DROP TYPE IF EXISTS incidenttype")
    op.execute("DROP TYPE IF EXISTS respondertype")
    op.execute("DROP TYPE IF EXISTS incidentstatus")
