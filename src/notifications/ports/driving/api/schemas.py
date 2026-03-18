from pydantic import BaseModel


class SubscriberResponseSchema(BaseModel):
    chat_id: int
    username: str
    is_active: bool
    notify_events: bool
    notify_timeouts: bool
    notify_services: bool


class UpdateTokenRequestSchema(BaseModel):
    token: str


class UpdatePreferenceRequestSchema(BaseModel):
    field: str
    value: bool


class TestResultSchema(BaseModel):
    total: int
    sent: int
    failed: int
    details: list[str]
