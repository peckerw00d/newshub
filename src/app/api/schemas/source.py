import datetime
from pydantic import BaseModel, ConfigDict


class SourceAdminBase(BaseModel):
    name: str
    url: str
    type: str
    poll_interval: float


class SourceAdminCreate(SourceAdminBase):
    pass


class SourceAdminResponse(SourceAdminBase):
    id: int
    is_active: bool
    last_updated: datetime.datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)
