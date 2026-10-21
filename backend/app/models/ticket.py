
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Text

from backend.app.database import Base


# ==================================
# SUPPORT TICKET DATABASE MODEL
# ==================================

class SupportTicket(Base):

    __tablename__ = "support_tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    issue = Column(
        Text,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    # ==================================
    # AI PRIORITY CLASSIFICATION
    # ==================================

    priority = Column(
        String(20),
        default="Medium",
        server_default="Medium",
        nullable=False
    )

    status = Column(
        String(50),
        default="Open",
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
