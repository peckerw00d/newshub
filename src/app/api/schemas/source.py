import datetime
from pydantic import BaseModel


class SourceAdminBase(BaseModel):
    name: str
    url: str
    type: str
    poll_interval: int


class SourceAdminCreate(SourceAdminBase):
    pass


class SourceAdminResponse(SourceAdminBase):
    is_active: bool
    last_updated: datetime.datetime
