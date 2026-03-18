from typing import Optional
from sqlalchemy import Boolean, BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TelegramConfigModel(Base):
    __tablename__ = "tg_config"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    bot_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class TelegramSubscriberModel(Base):
    __tablename__ = "tg_subscribers"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_events: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_timeouts: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_services: Mapped[bool] = mapped_column(Boolean, default=True)
