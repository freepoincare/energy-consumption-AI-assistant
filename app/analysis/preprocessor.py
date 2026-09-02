"""
Raw data validation and daily energy preprocessing module.

This module handles:
1. Validating 30-minute interval energy consumption data.
2. Grouping by timezone-aware local date.
3. Summing interval consumption (kWh) without double-multiplying.
4. Aggregating estimated cost (pence) and standing charges (pence).
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple, Optional


def validate_raw_energy_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validates the raw 30-minute energy consumption DataFrame.
    Returns a dictionary report of validation metrics and potential anomalies.
    """
    required_cols = {"consumption_kwh", "estimated_cost_pence", "standing_charge_pence", "start", "end"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns in raw dataset: {missing_cols}")

    total_rows = len(df)
    null_counts = df[list(required_cols)].isnull().sum().to_dict()
    duplicate_count = int(df["start"].duplicated().sum())

    # Convert timestamps
    start_dt = pd.to_datetime(df["start"], format="ISO8601")
    end_dt = pd.to_datetime(df["end"], format="ISO8601")

    # Duration check (each interval should be ~30 min, allowing sub-second end-of-day timestamping e.g. 23:59:59.999)
    duration_min = (end_dt - start_dt).dt.total_seconds() / 60.0
    invalid_durations = int(((duration_min < 29.9) | (duration_min > 30.1)).sum())

    # Start < End check
    invalid_time_relationships = int((start_dt >= end_dt).sum())

    # Negative value checks
    neg_consumption = int((df["consumption_kwh"] < 0).sum())
    neg_cost = int((df["estimated_cost_pence"] < 0).sum())
    neg_standing = int((df["standing_charge_pence"] < 0).sum())

    # Local date extraction
    local_dates = start_dt.dt.date
    daily_counts = local_dates.value_counts().sort_index()

    # Days not having exactly 48 records
    partial_days = daily_counts[daily_counts != 48].to_dict()
    # Format date keys as strings
    partial_days_str = {str(k): int(v) for k, v in partial_days.items()}

    # Check for missing calendar dates in full range
    min_date = local_dates.min()
    max_date = local_dates.max()
    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D").date
    missing_dates = [str(d) for d in set(full_date_range) - set(local_dates.unique())]

    # Continuous step gap check (gap between previous end and current start)
    step_gaps = (start_dt.iloc[1:].values - end_dt.iloc[:-1].values) / np.timedelta64(1, "m")
    unexpected_gaps_count = int((step_gaps != 0).sum())

    return {
        "total_rows": total_rows,
        "columns": list(df.columns),
        "min_timestamp": str(df["start"].iloc[0]).strip(),
        "max_timestamp": str(df["end"].iloc[-1]).strip(),
        "date_range": {"min_date": str(min_date), "max_date": str(max_date)},
        "null_counts": {k: int(v) for k, v in null_counts.items()},
        "duplicate_count": duplicate_count,
        "invalid_numeric_counts": {
            "negative_consumption": neg_consumption,
            "negative_estimated_cost": neg_cost,
            "negative_standing_charge": neg_standing
        },
        "invalid_durations": invalid_durations,
        "invalid_time_relationships": invalid_time_relationships,
        "total_days": len(daily_counts),
        "partial_days": partial_days_str,
        "missing_dates": missing_dates,
        "unexpected_gaps_count": unexpected_gaps_count,
        "is_valid": (
            len(missing_cols) == 0
            and sum(null_counts.values()) == 0
            and duplicate_count == 0
            and invalid_durations == 0
            and invalid_time_relationships == 0
            and neg_consumption == 0
            and neg_cost == 0
            and len(missing_dates) == 0
            and unexpected_gaps_count == 0
        )
    }


def preprocess_daily_energy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses 30-minute interval data into daily aggregated records.
    
    Data semantics:
    - `consumption_kwh` is already interval energy (kWh). Summed across interval records for each local calendar date.
    - `estimated_cost_pence` is summed across intervals. Note: This is an estimated cost and not a confirmed bill.
    - `standing_charge_pence` is aggregated by taking the daily mean (or sum, but note standing charge in raw data is interval rate).
      In raw data, standing charge is ~0.92 - 0.97 pence per 30-min interval.
    """
    df_clean = df.copy()
    
    # Parse timestamp preserving timezone
    start_dt = pd.to_datetime(df_clean["start"], format="ISO8601")
    df_clean["date"] = start_dt.dt.strftime("%Y-%m-%d")

    # Group by local date string
    daily_df = df_clean.groupby("date").agg(
        record_count=("consumption_kwh", "count"),
        daily_consumption_kwh=("consumption_kwh", "sum"),
        estimated_cost_pence=("estimated_cost_pence", "sum"),
        standing_charge_pence=("standing_charge_pence", "sum")
    ).reset_index()

    # Round appropriately
    daily_df["daily_consumption_kwh"] = daily_df["daily_consumption_kwh"].round(4)
    daily_df["estimated_cost_pence"] = daily_df["estimated_cost_pence"].round(2)
    daily_df["standing_charge_pence"] = daily_df["standing_charge_pence"].round(2)
    
    # Estimated cost in pounds (GBP £) for readability
    daily_df["estimated_cost_pounds"] = (daily_df["estimated_cost_pence"] / 100.0).round(4)
    daily_df["is_complete_day"] = daily_df["record_count"] == 48

    return daily_df


def process_raw_file(
    raw_path: str = "data/raw/energy_raw.csv",
    output_path: Optional[str] = "data/processed/daily_energy.csv"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads raw energy CSV, validates it, aggregates to daily dataset, and optionally saves to CSV.
    """
    raw_file = Path(raw_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw energy file not found at: {raw_path}")

    df_raw = pd.read_csv(raw_file)
    validation_report = validate_raw_energy_data(df_raw)
    daily_df = preprocess_daily_energy(df_raw)

    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        daily_df.to_csv(out_file, index=False)

    return daily_df, validation_report
