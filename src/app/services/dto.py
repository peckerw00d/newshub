from dataclasses import dataclass
import datetime


@dataclass
class SourceCreateDTO:
    name: str
    url: str
    type: str
    poll_interval: int
