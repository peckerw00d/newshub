from dataclasses import dataclass
import datetime


@dataclass
class SourceDTO:
    name: str
    url: str
    type: str
    last_updated: datetime.datetime
    poll_interval: int
    is_active: bool
