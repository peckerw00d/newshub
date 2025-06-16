from dataclasses import dataclass
import datetime


@dataclass
class SourceCreateDTO:
    name: str
    url: str
    type: str
    poll_interval: float


@dataclass
class SourceResponseDTO(SourceCreateDTO):
    id: int
    last_updated: datetime.datetime
    is_active: bool
