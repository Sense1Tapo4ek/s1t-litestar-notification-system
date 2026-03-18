from sqlalchemy.ext.asyncio import AsyncSession
from notifications.adapters.driven.db.orm_models import TelegramConfigModel
from notifications.domain import TelegramConfigAgg


_SINGLETON_ID = "telegram"


class SqliteConfigRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> TelegramConfigAgg:
        model = await self._session.get(TelegramConfigModel, _SINGLETON_ID)
        if model is None:
            return TelegramConfigAgg(id=_SINGLETON_ID, bot_token=None)
        return TelegramConfigAgg(id=model.id, bot_token=model.bot_token)

    async def save(self, agg: TelegramConfigAgg) -> None:
        model = TelegramConfigModel(id=agg.id, bot_token=agg.bot_token)
        await self._session.merge(model)
        await self._session.commit()
