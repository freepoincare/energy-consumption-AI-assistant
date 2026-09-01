"""
FastAPI Router for Daily Energy Data endpoints:
- POST   /api/data        : Create/Add a new daily energy record
- GET    /api/data        : List daily energy records
- GET    /api/data/{id}   : Get a specific daily energy record
- PUT    /api/data/{id}   : Update a daily energy record
- DELETE /api/data/{id}   : Delete a daily energy record
- GET    /api/data/summary: Retrieve statistical summary for context injection & insights
"""

from fastapi import APIRouter, HTTPException, status
from app.models.data_models import (
    EnergyDataCreate,
    EnergyDataUpdate,
    EnergyDataResponse,
    EnergyDataListResponse,
    SummaryResponse
)
from app.services.data_service import EnergyDataService

router = APIRouter(prefix="/api/data", tags=["Energy Data"])


@router.get(
    "/summary",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Energy Consumption Summary",
    description="Returns aggregated statistical summary (period, averages, trends, extremes) used for AI context injection."
)
async def get_energy_summary():
    try:
        return EnergyDataService.get_summary()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate energy summary: {str(e)}"
        )


@router.get(
    "",
    response_model=EnergyDataListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All Daily Energy Records",
    description="Retrieves a list of all daily electricity consumption records sorted chronologically."
)
async def list_energy_data():
    return EnergyDataService.list_energy_data()


@router.post(
    "",
    response_model=EnergyDataResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Daily Energy Record",
    description="Adds a new daily energy record with date (YYYY-MM-DD), value (kWh), and optional memo."
)
async def create_energy_data(payload: EnergyDataCreate):
    # Check if record for this date already exists
    existing = EnergyDataService.get_energy_data_by_id(payload.date)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Energy record for date '{payload.date}' already exists. Use PUT /api/data/{payload.date} to update."
        )
    return EnergyDataService.create_energy_data(payload)


@router.get(
    "/{record_id}",
    response_model=EnergyDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Daily Energy Record by ID",
    description="Retrieves a single daily energy record by its ID / date (e.g. '2026-03-01')."
)
async def get_energy_data(record_id: str):
    record = EnergyDataService.get_energy_data_by_id(record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Energy record with ID '{record_id}' not found."
        )
    return record


@router.put(
    "/{record_id}",
    response_model=EnergyDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Daily Energy Record",
    description="Updates the electricity consumption value (kWh) or memo for a specific record."
)
async def update_energy_data(record_id: str, payload: EnergyDataUpdate):
    updated = EnergyDataService.update_energy_data(record_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Energy record with ID '{record_id}' not found."
        )
    return updated


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Daily Energy Record",
    description="Deletes a daily energy record by its ID / date."
)
async def delete_energy_data(record_id: str):
    deleted = EnergyDataService.delete_energy_data(record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Energy record with ID '{record_id}' not found."
        )
    return {"message": f"Energy record with ID '{record_id}' deleted successfully.", "id": record_id}
