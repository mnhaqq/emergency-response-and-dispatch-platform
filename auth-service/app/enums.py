from enum import Enum

class UserRole(str, Enum):
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    POLICE_ADMIN = "POLICE_ADMIN"
    FIRE_ADMIN = "FIRE_ADMIN"