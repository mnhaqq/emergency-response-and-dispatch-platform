"""Initial migration - create analytics tables

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
        "incident_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("incident_id", sa.String(), nullable=False, index=True),
        sa.Column(
            "event",
            sa.Enum("INCIDENT_CREATED", "INCIDENT_RESOLVED", name="incidenteventtype"),
            nullable=False,
        ),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "response_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("incident_id", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("incident_type", sa.String(), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("assigned_unit_type", sa.String(), nullable=True),
        sa.Column("assigned_unit_id", sa.String(), nullable=True),
        sa.Column("response_time_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_index("ix_response_records_incident_id", table_name="response_records")
    op.drop_table("response_records")
    op.drop_index("ix_incident_events_incident_id", table_name="incident_events")
    op.drop_table("incident_events")
    op.execute("DROP TYPE IF EXISTS incidenteventtype")
