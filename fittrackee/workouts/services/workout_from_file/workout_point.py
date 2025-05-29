from dataclasses import dataclass
from datetime import datetime


@dataclass()
class WorkoutPoint:
    longitude: float
    latitude: float
    time: datetime
