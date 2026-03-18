from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel

from core.domain import EventSeverity


class EventRecordSchema(BaseModel):
    event_id: str
    severity: EventSeverity
    title: str
    detail: Optional[str]
    timestamp: datetime


class SourceCardSchema(BaseModel):
    id: str
    display_name: str
    is_active: bool
    notify_events: bool
    total_events: int
    error_count: int
    last_seen_ts: Optional[datetime]
    started_at: Optional[datetime]


class SourceDetailsSchema(BaseModel):
    id: str
    display_name: str
    custom_name: Optional[str]
    is_active: bool
    notify_events: bool
    started_at: Optional[datetime]
    stopped_at: Optional[datetime]
    uptime_seconds: Optional[int]
    total_events: int
    info_count: int
    warning_count: int
    error_count: int
    critical_count: int
    error_rate: float
    active_window_start: Optional[str]
    active_window_end: Optional[str]
    recent_events: list[EventRecordSchema]


class UpdateSourceSettingsRequestSchema(BaseModel):
    custom_name: Optional[str] = None
    notify_events: bool = True
    active_window_start: Optional[str] = None
    active_window_end: Optional[str] = None


class GlobalSettingsSchema(BaseModel):
    active_window_start: Optional[str]
    active_window_end: Optional[str]
