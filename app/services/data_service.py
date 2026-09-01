"""
Data Service Layer (Business Logic).

Currently uses an In-Memory Repository initialized with the processed daily dataset
(data/processed/daily_energy.csv).

In STEP 4, this in-memory repository will be replaced by Firestore Database queries.
"""

import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pathlib import Path
from app.models.data_models import (
    EnergyDataCreate,
    EnergyDataUpdate,
    EnergyDataResponse,
    EnergyDataListResponse,
    SummaryResponse
)
from app.analysis.summary import generate_energy_summary
from app.analysis.preprocessor import process_raw_file


class InMemoryEnergyRepository:
    """
    Temporary in-memory data store for Step 3.
    Pre-populates from data/processed/daily_energy.csv (or generates it if absent).
    """
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._load_initial_data()

    def _load_initial_data(self):
        processed_csv = Path("data/processed/daily_energy.csv")
        if not processed_csv.exists():
            # If not yet created, run preprocessing from raw data
            raw_csv = Path("data/raw/energy_raw.csv")
            if raw_csv.exists():
                process_raw_file(str(raw_csv), str(processed_csv))

        if processed_csv.exists():
            df = pd.read_csv(processed_csv)
            for _, row in df.iterrows():
                date_str = str(row["date"])
                val = float(row["daily_consumption_kwh"])
                self._store[date_str] = {
                    "id": date_str,
                    "date": date_str,
                    "value": val,
                    "unit": "kWh",
                    "memo": None,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "updated_at": None
                }

    def get_all(self) -> List[Dict[str, Any]]:
        # Sort chronologically by date
        return sorted(list(self._store.values()), key=lambda x: x["date"])

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(record_id)

    def create(self, data: EnergyDataCreate) -> Dict[str, Any]:
        record_id = data.date
        now_str = datetime.now(timezone.utc).isoformat()
        record = {
            "id": record_id,
            "date": data.date,
            "value": round(float(data.value), 4),
            "unit": "kWh",
            "memo": data.memo,
            "created_at": now_str,
            "updated_at": None
        }
        self._store[record_id] = record
        return record

    def update(self, record_id: str, data: EnergyDataUpdate) -> Optional[Dict[str, Any]]:
        if record_id not in self._store:
            return None
        
        record = self._store[record_id]
        if data.value is not None:
            record["value"] = round(float(data.value), 4)
        if data.memo is not None:
            record["memo"] = data.memo
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        return record

    def delete(self, record_id: str) -> bool:
        if record_id in self._store:
            del self._store[record_id]
            return True
        return False

    def to_dataframe(self) -> pd.DataFrame:
        records = self.get_all()
        if not records:
            return pd.DataFrame(columns=["date", "daily_consumption_kwh", "is_complete_day"])
        df = pd.DataFrame(records)
        df = df.rename(columns={"value": "daily_consumption_kwh"})
        df["is_complete_day"] = True
        return df


# Singleton instance of repository for Step 3 in-memory store
repository = InMemoryEnergyRepository()


class EnergyDataService:
    @staticmethod
    def list_energy_data() -> EnergyDataListResponse:
        records = repository.get_all()
        return EnergyDataListResponse(
            total_count=len(records),
            records=[EnergyDataResponse(**r) for r in records]
        )

    @staticmethod
    def get_energy_data_by_id(record_id: str) -> Optional[EnergyDataResponse]:
        record = repository.get_by_id(record_id)
        if record:
            return EnergyDataResponse(**record)
        return None

    @staticmethod
    def create_energy_data(data: EnergyDataCreate) -> EnergyDataResponse:
        created = repository.create(data)
        return EnergyDataResponse(**created)

    @staticmethod
    def update_energy_data(record_id: str, data: EnergyDataUpdate) -> Optional[EnergyDataResponse]:
        updated = repository.update(record_id, data)
        if updated:
            return EnergyDataResponse(**updated)
        return None

    @staticmethod
    def delete_energy_data(record_id: str) -> bool:
        return repository.delete(record_id)

    @staticmethod
    def get_summary() -> SummaryResponse:
        daily_df = repository.to_dataframe()
        summary_dict = generate_energy_summary(daily_df)
        return SummaryResponse(**summary_dict)
