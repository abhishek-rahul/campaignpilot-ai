from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_conversation_messages_campaign_id", "campaign_id"),
        Index("ix_conversation_messages_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(50), ForeignKey("campaigns.id"), nullable=False)
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False, default="text")
    message_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    campaign = relationship("Campaign", back_populates="messages")
