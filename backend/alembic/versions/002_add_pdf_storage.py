"""Add pdf_bytes and download_token to reports table.

Revision ID: 002
Revises: 001
Create Date: 2026-05-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("reports", sa.Column("pdf_bytes", sa.LargeBinary(), nullable=True))
    op.add_column("reports", sa.Column("download_token", sa.String(36), nullable=True))


def downgrade() -> None:
    op.drop_column("reports", "download_token")
    op.drop_column("reports", "pdf_bytes")
