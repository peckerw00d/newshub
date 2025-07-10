from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.models.logs import UpdateLog
from src.app.db.repositories.base import Repository


class UpdateLogRepository(Repository[UpdateLog, int]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UpdateLog)
