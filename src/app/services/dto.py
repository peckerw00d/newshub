from dataclasses import dataclass
import datetime
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
