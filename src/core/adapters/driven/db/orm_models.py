from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    custom_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notify_events: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_ts: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    active_window_start: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # HH:MM
    active_window_end: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    events: Mapped[list["EventRecordModel"]] = relationship(
        "EventRecordModel",
        back_populates="source",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EventRecordModel(Base):
    __tablename__ = "event_records"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id", ondelete="CASCADE"))
    severity: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    source: Mapped["SourceModel"] = relationship("SourceModel", back_populates="events")


class GlobalSettingsModel(Base):
    __tablename__ = "global_settings"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
