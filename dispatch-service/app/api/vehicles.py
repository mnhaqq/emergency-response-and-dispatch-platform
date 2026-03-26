from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.models.vehicle import Vehicle, VehicleStatus, VehicleType
from app.schemas.vehicle import (
    VehicleRegister, VehicleResponse, LocationResponse,
    LocationUpdate, VehicleStatusUpdate,
)
from app.services.dependencies import get_current_user
from app.services.ws_manager import manager

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.post("/register", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def register_vehicle(
    payload: VehicleRegister,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    existing = db.query(Vehicle).filter(Vehicle.registration_number == payload.registration_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already registered")
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(
    vehicle_type: Optional[VehicleType] = Query(None),
    status: Optional[VehicleStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    q = db.query(Vehicle)
    if vehicle_type:
        q = q.filter(Vehicle.vehicle_type == vehicle_type)
    if status:
        q = q.filter(Vehicle.status == status)
    return q.all()


@router.get("/{vehicle_id}/location", response_model=LocationResponse)
def get_vehicle_location(
    vehicle_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}/location", response_model=LocationResponse)
async def update_vehicle_location(
    vehicle_id: UUID,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """REST endpoint for drivers to push GPS updates (alternative to WebSocket)."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.latitude = payload.latitude
    vehicle.longitude = payload.longitude
    vehicle.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)

    # Broadcast to any WebSocket subscribers
    await manager.broadcast(str(vehicle_id), {
        "vehicle_id": str(vehicle.id),
        "latitude": vehicle.latitude,
        "longitude": vehicle.longitude,
        "status": vehicle.status.value,
        "timestamp": vehicle.last_updated.isoformat(),
    })
    return vehicle


@router.put("/{vehicle_id}/status")
def update_vehicle_status(
    vehicle_id: UUID,
    payload: VehicleStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    vehicle.status = payload.status
    vehicle.current_incident_id = payload.incident_id
    db.commit()
    db.refresh(vehicle)
    return {"message": "Status updated", "vehicle_id": str(vehicle.id), "status": vehicle.status.value}


# ─── WebSocket: real-time tracking ───────────────────────────────────────────

@router.websocket("/{vehicle_id}/ws")
async def vehicle_tracking_ws(vehicle_id: str, websocket: WebSocket):
    """
    Drivers connect here to stream GPS location.
    Admins/clients also connect here to receive live updates.

    Message format (driver sends):
      { "latitude": 5.603, "longitude": -0.187 }

    Broadcast format (clients receive):
      { "vehicle_id": "...", "latitude": 5.603, "longitude": -0.187,
        "status": "on_duty", "timestamp": "..." }
    """
    await manager.connect(vehicle_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            lat = data.get("latitude")
            lon = data.get("longitude")
            if lat is None or lon is None:
                continue

            # Persist to DB
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                if vehicle:
                    vehicle.latitude = lat
                    vehicle.longitude = lon
                    vehicle.last_updated = datetime.utcnow()
                    db.commit()
                    await manager.broadcast(vehicle_id, {
                        "vehicle_id": vehicle_id,
                        "latitude": lat,
                        "longitude": lon,
                        "status": vehicle.status.value,
                        "timestamp": vehicle.last_updated.isoformat(),
                    })
            finally:
                db.close()
    except WebSocketDisconnect:
        manager.disconnect(vehicle_id, websocket)
