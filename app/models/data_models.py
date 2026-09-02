"""
Pydantic schemas for daily energy data operations and summaries.
Data unit: (date, value, memo) where value = daily electricity consumption in kWh.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re


class EnergyDataCreate(BaseModel):
    date: str = Field(..., description="Local calendar date in YYYY-MM-DD format", example="2026-09-01")
    value: float = Field(..., ge=0.0, description="Daily electricity consumption in kWh", example=4.52)
    memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Worked from home, AC running")
    estimated_cost_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional estimated daily cost in pence")
    standing_charge_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional standing charge in pence")

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(pattern, v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid calendar date")
        return v


class EnergyDataUpdate(BaseModel):
    value: Optional[float] = Field(default=None, ge=0.0, description="Daily electricity consumption in kWh", example=5.10)
    memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Updated note")
    estimated_cost_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional estimated daily cost in pence")
    standing_charge_pence: Optional[float] = Field(default=None, ge=0.0, description="Optional standing charge in pence")


class EnergyDataResponse(BaseModel):
    id: str = Field(..., description="Unique document ID (local date string YYYY-MM-DD)")
    date: str = Field(..., description="Local calendar date in YYYY-MM-DD format")
    value: float = Field(..., description="Daily electricity consumption in kWh")
    unit: str = Field(default="kWh", description="Energy unit")
    memo: Optional[str] = Field(default=None, description="Optional user note")
    estimated_cost_pence: Optional[float] = Field(default=None, description="Estimated daily cost in pence (not actual bill)")
    estimated_cost_pounds: Optional[float] = Field(default=None, description="Estimated daily cost in GBP (£)")
    standing_charge_pence: Optional[float] = Field(default=None, description="Standing charge in pence")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp when created")
    updated_at: Optional[str] = Field(default=None, description="ISO timestamp when updated")


class EnergyDataListResponse(BaseModel):
    total_count: int = Field(..., description="Total number of daily records in database")
    records: List[EnergyDataResponse] = Field(..., description="List of daily energy records")


class SummaryResponse(BaseModel):
    period: Dict[str, Any] = Field(..., description="Analysis period details")
    counts: Dict[str, Any] = Field(..., description="Dataset coverage and count details")
    overall: Dict[str, Any] = Field(..., description="Overall consumption statistics")
    extremes: Dict[str, Any] = Field(..., description="Highest and lowest consumption days")
    monthly: Dict[str, Any] = Field(..., description="Monthly totals and averages")
    weekday_weekend: Dict[str, Any] = Field(..., description="Weekday vs Weekend comparison")
    day_of_week: Dict[str, Any] = Field(..., description="Day-of-week averages")
    recent: Dict[str, Any] = Field(..., description="Recent 7-day and 30-day metrics")
    trend: Dict[str, Any] = Field(..., description="Short-term and long-term trend analysis")
    cost: Optional[Dict[str, Any]] = Field(default=None, description="Estimated cost statistics")
