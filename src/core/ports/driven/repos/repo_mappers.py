from datetime import datetime, time, timezone
from typing import Optional


def _naive_utc(dt: datetime) -> datetime:
    """Strip timezone info, treating naive datetimes as UTC already."""
    if dt is None:
        return dt
    return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

from core.domain import EventLogAgg, EventRecord, EventSeverity, TimeWindowVO
from core.adapters.driven.db.orm_models import SourceModel, EventRecordModel


def _parse_time(value: Optional[str]) -> Optional[time]:
    if not value:
        return None
    try:
        parts = value.split(":")
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def _format_time(t: Optional[time]) -> Optional[str]:
    if t is None:
        return None
    return t.strftime("%H:%M")


def source_model_to_domain(model: SourceModel) -> EventLogAgg:
    window = None
    ws = _parse_time(model.active_window_start)
    we = _parse_time(model.active_window_end)
    if ws and we:
        window = TimeWindowVO(start_time=ws, end_time=we)

    events = [
        EventRecord(
            event_id=er.event_id,
            severity=EventSeverity(er.severity),
            title=er.title,
            detail=er.detail,
            timestamp=_naive_utc(er.timestamp),
        )
        for er in (model.events or [])
    ]
    events.sort(key=lambda e: e.timestamp)

    return EventLogAgg(
        id=model.id,
        custom_name=model.custom_name,
        notify_events=model.notify_events,
        is_active=model.is_active,
        started_at=_naive_utc(model.started_at) if model.started_at else None,
        stopped_at=_naive_utc(model.stopped_at) if model.stopped_at else None,
        last_seen_ts=_naive_utc(model.last_seen_ts) if model.last_seen_ts else None,
        active_window=window,
        events=events,
    )


def domain_to_source_model(agg: EventLogAgg, model: Optional[SourceModel] = None) -> SourceModel:
    if model is None:
        model = SourceModel()
    model.id = agg.id
    model.custom_name = agg.custom_name
    model.notify_events = agg.notify_events
    model.is_active = agg.is_active
    model.started_at = _naive_utc(agg.started_at) if agg.started_at else None
    model.stopped_at = _naive_utc(agg.stopped_at) if agg.stopped_at else None
    model.last_seen_ts = _naive_utc(agg.last_seen_ts) if agg.last_seen_ts else None
    if agg.active_window:
        model.active_window_start = _format_time(agg.active_window.start_time)
        model.active_window_end = _format_time(agg.active_window.end_time)
    else:
        model.active_window_start = None
        model.active_window_end = None
    model.events = [
        EventRecordModel(
            event_id=e.event_id,
            source_id=agg.id,
            severity=e.severity.value,
            title=e.title,
            detail=e.detail,
            timestamp=_naive_utc(e.timestamp),
        )
        for e in agg.events
    ]
    return model
