import math
import httpx
from app.config import settings
from app.models.incident import IncidentType, ResponderType


INTERNAL_KEY = "internal-service-key-change-in-production"
INTERNAL_HEADERS = {"x-internal-key": INTERNAL_KEY}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate straight-line distance in km between two GPS coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def incident_type_to_responder(incident_type: IncidentType) -> ResponderType:
    mapping = {
        IncidentType.MEDICAL: ResponderType.AMBULANCE,
        IncidentType.FIRE: ResponderType.FIRE_TRUCK,
        IncidentType.CRIME: ResponderType.POLICE,
        IncidentType.ACCIDENT: ResponderType.AMBULANCE,
        IncidentType.OTHER: ResponderType.POLICE,
    }
    return mapping[incident_type]


def find_nearest_responder(incident_lat: float, incident_lon: float, responder_type: ResponderType) -> dict | None:
    """
    Calls the Dispatch Service to get all available vehicles of the required type,
    then returns the nearest one using the Haversine formula.
    """
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"{settings.DISPATCH_SERVICE_URL}/vehicles",
                params={"vehicle_type": responder_type.value, "status": "AVAILABLE"},
                headers=INTERNAL_HEADERS,
            )
            resp.raise_for_status()
            vehicles = resp.json()
    except Exception as e:
        return None

    if not vehicles:
        return None

    # Filter out vehicles with no GPS location yet
    vehicles_with_location = [
        v for v in vehicles
        if v.get("latitude") is not None and v.get("longitude") is not None
    ]

    if not vehicles_with_location:
        return None

    nearest = min(
        vehicles_with_location,
        key=lambda v: haversine_km(incident_lat, incident_lon, v["latitude"], v["longitude"]),
    )
    return nearest


def notify_analytics(
    incident_id: str,
    event: str,
    incident_type: str = None,
    region: str = None,
    assigned_unit_type: str = None,
    assigned_unit_id: str = None,
):
    """Send incident lifecycle event to the analytics service."""
    payload = {
        "incident_id": incident_id,
        "event": event,
        "incident_type": incident_type,
        "region": region,
        "assigned_unit_type": assigned_unit_type,
        "assigned_unit_id": assigned_unit_id,
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{settings.ANALYTICS_SERVICE_URL}/analytics/events",
                json=payload,
            )
    except Exception as e:
        pass
        # Never block incident operations due to analytics failure