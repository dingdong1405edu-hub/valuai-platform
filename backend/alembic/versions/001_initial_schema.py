"""Initial schema — create users, reports, documents tables.

Revision ID: 001
Revises:
Create Date: 2026-05-07 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

job_status_enum = postgresql.ENUM(
    "PENDING",
    "PARSING",
    "RUNNING_AGENTS",
    "AGGREGATING",
    "BUILDING_PDF",
    "DONE",
    "FAILED",
    name="jobstatus",
    create_type=True,
)

document_type_enum = postgresql.ENUM(
    "financial_report",
    "website_fanpage",
    "catalogue_brochure",
    "company_profile",
    "business_plan",
    "ceo_cv",
    "crm_export",
    "accounting_export",
    "erp_export",
    "other",
    name="documenttype",
    create_type=True,
)


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


def upgrade() -> None:
    # Create enum types first
    job_status_enum.create(op.get_bind(), checkfirst=True)
    document_type_enum.create(op.get_bind(), checkfirst=True)

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()::text"),
        ),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── reports ───────────────────────────────────────────────────────────────
    op.create_table(
        "reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()::text"),
        ),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("company_name", sa.String(500), nullable=False),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("job_id", sa.String(255), nullable=False),
        sa.Column("pdf_url", sa.String(2048), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_reports_user_id", "reports", ["user_id"])
    op.create_index("ix_reports_status", "reports", ["status"])
    op.create_index("ix_reports_job_id", "reports", ["job_id"], unique=True)

    # ── documents ─────────────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()::text"),
        ),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=False),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column(
            "doc_type",
            sa.String(50),
            nullable=False,
            server_default="other",
        ),
        sa.Column("storage_path", sa.String(2048), nullable=False),
        sa.Column("extracted_text", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_documents_report_id", "documents", ["report_id"])

    # Trigger to auto-update reports.updated_at
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )
    op.execute(
        """
        CREATE TRIGGER reports_updated_at_trigger
        BEFORE UPDATE ON reports
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
        """
    )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS reports_updated_at_trigger ON reports;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    op.drop_index("ix_documents_report_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_reports_job_id", table_name="reports")
    op.drop_index("ix_reports_status", table_name="reports")
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_table("reports")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    document_type_enum.drop(op.get_bind(), checkfirst=True)
    job_status_enum.drop(op.get_bind(), checkfirst=True)
