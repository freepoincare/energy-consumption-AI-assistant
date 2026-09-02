"""
Data Service Layer (Business Logic & Firestore Repository).

Encapsulates all Firestore database CRUD interactions for the `data` collection.
Fallback in-memory cache enables continuous testing if Firebase cloud credentials
are absent in local test environments.
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
from app.database.firestore import get_firestore_db, is_firestore_mock


class FirestoreEnergyRepository:
    """
    Repository managing daily electricity consumption documents in Firestore 'data' collection.
    """
    COLLECTION_NAME = "data"

    def __init__(self):
        self._mock_store: Dict[str, Dict[str, Any]] = {}
        self._ensure_initial_dataset_loaded()

    def _ensure_initial_dataset_loaded(self):
        """Loads default daily energy dataset from CSV into mock store or Firestore."""
        processed_csv = Path("data/processed/daily_energy.csv")
        if not processed_csv.exists():
            raw_csv = Path("data/raw/energy_raw.csv")
            if raw_csv.exists():
                process_raw_file(str(raw_csv), str(processed_csv))

        if processed_csv.exists():
            df = pd.read_csv(processed_csv)
            for _, row in df.iterrows():
                date_str = str(row["date"])
                val = float(row["daily_consumption_kwh"])
                cost_p = float(row["estimated_cost_pence"]) if "estimated_cost_pence" in row and not pd.isna(row["estimated_cost_pence"]) else None
                cost_gbp = round(cost_p / 100.0, 4) if cost_p is not None else None
                std_p = float(row["standing_charge_pence"]) if "standing_charge_pence" in row and not pd.isna(row["standing_charge_pence"]) else None
                
                doc_data = {
                    "id": date_str,
                    "date": date_str,
                    "value": val,
                    "unit": "kWh",
                    "memo": None,
                    "estimated_cost_pence": cost_p,
                    "estimated_cost_pounds": cost_gbp,
                    "standing_charge_pence": std_p,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": None
                }
                self._mock_store[date_str] = doc_data

    def get_all(self) -> List[Dict[str, Any]]:
        db = get_firestore_db()
        if db is not None:
            try:
                docs = db.collection(self.COLLECTION_NAME).stream()
                records = []
                for doc in docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    records.append(d)
                if records:
                    return sorted(records, key=lambda x: x.get("date", ""))
            except Exception as e:
                pass  # Fall back to internal memory if connection issue

        return sorted(list(self._mock_store.values()), key=lambda x: x["date"])

    def get_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        db = get_firestore_db()
        if db is not None:
            try:
                doc_ref = db.collection(self.COLLECTION_NAME).document(record_id)
                doc = doc_ref.get()
                if doc.exists:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    return d
                return None
            except Exception:
                pass

        return self._mock_store.get(record_id)

    def create(self, data: EnergyDataCreate) -> Dict[str, Any]:
        record_id = data.date
        now_str = datetime.now(timezone.utc).isoformat()
        cost_pence = data.estimated_cost_pence
        cost_pounds = round(cost_pence / 100.0, 4) if cost_pence is not None else None

        doc_data = {
            "id": record_id,
            "date": data.date,
            "value": round(float(data.value), 4),
            "unit": "kWh",
            "memo": data.memo,
            "estimated_cost_pence": cost_pence,
            "estimated_cost_pounds": cost_pounds,
            "standing_charge_pence": data.standing_charge_pence,
            "created_at": now_str,
            "updated_at": None
        }

        db = get_firestore_db()
        if db is not None:
            try:
                db.collection(self.COLLECTION_NAME).document(record_id).set(doc_data)
            except Exception:
                pass

        self._mock_store[record_id] = doc_data
        return doc_data

    def update(self, record_id: str, data: EnergyDataUpdate) -> Optional[Dict[str, Any]]:
        existing = self.get_by_id(record_id)
        if not existing:
            return None

        update_dict: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if data.value is not None:
            update_dict["value"] = round(float(data.value), 4)
        if data.memo is not None:
            update_dict["memo"] = data.memo
        if data.estimated_cost_pence is not None:
            update_dict["estimated_cost_pence"] = data.estimated_cost_pence
            update_dict["estimated_cost_pounds"] = round(data.estimated_cost_pence / 100.0, 4)
        if data.standing_charge_pence is not None:
            update_dict["standing_charge_pence"] = data.standing_charge_pence

        db = get_firestore_db()
        if db is not None:
            try:
                db.collection(self.COLLECTION_NAME).document(record_id).update(update_dict)
            except Exception:
                pass

        # Update local state
        existing.update(update_dict)
        self._mock_store[record_id] = existing
        return existing

    def delete(self, record_id: str) -> bool:
        found = False
        db = get_firestore_db()
        if db is not None:
            try:
                doc_ref = db.collection(self.COLLECTION_NAME).document(record_id)
                if doc_ref.get().exists:
                    doc_ref.delete()
                    found = True
            except Exception:
                pass

        if record_id in self._mock_store:
            del self._mock_store[record_id]
            found = True

        return found

    def to_dataframe(self) -> pd.DataFrame:
        records = self.get_all()
        if not records:
            return pd.DataFrame(columns=["date", "daily_consumption_kwh", "is_complete_day"])
        df = pd.DataFrame(records)
        df = df.rename(columns={"value": "daily_consumption_kwh"})
        df["is_complete_day"] = True
        return df


# Service instantiation
repository = FirestoreEnergyRepository()


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
