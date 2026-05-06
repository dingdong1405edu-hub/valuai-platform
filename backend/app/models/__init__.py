"""
ORM model package.

Importing this package ensures all models are registered on
``Base.metadata`` so that ``init_db()`` and Alembic can discover them.
"""

from app.models.report import Document, Report
from app.models.user import User

__all__ = ["Document", "Report", "User"]
