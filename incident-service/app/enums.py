from enum import Enum

class IncidentType(str, Enum):
    CRIME = "crime"
    FIRE = "fire"
    MEDICAL = "medical"