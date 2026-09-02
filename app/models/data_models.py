"""
Pydantic schemas for daily energy data operations and summaries.
Data unit: (date, value, memo) where value = daily electricity consumption in kWh.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import re

# 데이터 입력 생성
class EnergyDataCreate(BaseModel):
    date: str = Field(..., description="Local calendar date in YYYY-MM-DD format", example="2026-09-01")
    value: float = Field(..., ge=0.0, description="Daily electricity consumption in kWh", example=4.52)
    memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Worked from home, AC running")

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

# 수정용 모델
class EnergyDataUpdate(BaseModel):
    value: Optional[float] = Field(default=None, ge=0.0, description="Daily electricity consumption in kWh", example=5.10)
    memo: Optional[str] = Field(default=None, max_length=500, description="Optional user note", example="Updated note")

# 단일 조회 응답
class EnergyDataResponse(BaseModel):
    id: str = Field(..., description="Unique record identifier (e.g. date string or UUID)")
    date: str = Field(..., description="Local calendar date in YYYY-MM-DD format")
    value: float = Field(..., description="Daily electricity consumption in kWh")
    unit: str = Field(default="kWh", description="Energy unit")
    memo: Optional[str] = Field(default=None, description="Optional user note")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp when created")
    updated_at: Optional[str] = Field(default=None, description="ISO timestamp when updated")

# 목록 조회 응답 모델
class EnergyDataListResponse(BaseModel):
    total_count: int = Field(..., description="Total number of daily records")
    records: List[EnergyDataResponse] = Field(..., description="List of daily energy records")

# 통계/분석 응답 모델
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
