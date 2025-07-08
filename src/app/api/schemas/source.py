import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict


class SourceAdminBase(BaseModel):
    name: str
    url: str
    type: str
    poll_interval: float


class SourceAdminCreate(SourceAdminBase):
    req_params: Dict[str, Any]
    res_obj: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "NewsAPI",
                "url": "https://newsapi.org",
                "type": "newsapi",
                "poll_interval": 60,
                "req_params": {
                    "apiKey": "your_api_key",
                    "country": "us",
                    "pageSize": 20,
                },
                "res_obj": {
                  "title": "results[].headline.main",
                  "description": "results[].abstract",
                  "full_text": "results[].body",
                  "url": "results[].web_url",
                  "published_at": "results[].pub_date"
                }
            }
        }


class SourceAdminUpdate(SourceAdminBase):
    is_active: bool
    req_params: Dict[str, Any]
    res_obj: Dict[str, Any]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "NewsAPI",
                "url": "https://newsapi.org",
                "type": "newsapi",
                "poll_interval": 60,
                "is_active": True,
                "req_params": {
                    "apiKey": "your_api_key",
                    "country": "us",
                    "pageSize": 20,
                },
                "res_obj": {
                  "title": "results[].headline.main",
                  "description": "results[].abstract",
                  "full_text": "results[].body",
                  "url": "results[].web_url",
                  "published_at": "results[].pub_date"
                }
            }
        }


class SourceAdminResponse(SourceAdminBase):
    id: int
    is_active: bool
    last_updated: datetime.datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)
