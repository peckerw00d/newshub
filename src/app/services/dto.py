import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class SourceCreateDTO:
    name: str
    url: str
    type: str
    poll_interval: float
    req_params: Dict[str, Any]
    res_obj: Dict[str, Any]


@dataclass
class SourceResponseDTO(SourceCreateDTO):
    id: int
    last_updated: datetime.datetime
    is_active: bool


@dataclass
class SourceUpdateDTO(SourceCreateDTO):
    is_active: bool


@dataclass
class NewsItemDTO:
    source_id: int
    title: str
    description: str
    url: str
    full_text: str
    published_at: datetime.datetime
    hash: str
