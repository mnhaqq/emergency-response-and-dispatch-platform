from app.services.distance import calculate_distance
from app.services.responder_mock import RESPONDERS
from app.enums import IncidentType

def find_nearest_responder(lat, lon, incident_type):
    candidates = []

    for r in RESPONDERS:
        if not r["available"]:
            continue

        if incident_type == IncidentType.MEDICAL and r["type"] != "MEDICAL":
            continue
        if incident_type == IncidentType.FIRE and r["type"] != "FIRE":
            continue
        if incident_type == IncidentType.CRIME and r["type"] != "POLICE":
            continue

        dist = calculate_distance(lat, lon, r["latitude"], r["longitude"])
        candidates.append((dist, r))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]