"""
Comprehensive Energy Analysis and Summary Service.

Computes multi-dimensional energy consumption summaries from daily datasets:
- Period & counts
- Overall statistics & extremes
- Monthly breakdown
- Weekday vs Weekend patterns
- Day-of-week patterns
- Recent periods (7-day, 30-day)
- Deterministic trend calculations (7-day rolling, linear slope, period comparison)
- Cost statistics (clearly labeled as estimated)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Union, Optional


def generate_energy_summary(daily_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates a structured, deterministic summary dictionary from the daily energy DataFrame.
    
    Expected DataFrame columns:
    - date (YYYY-MM-DD)
    - daily_consumption_kwh (float)
    - estimated_cost_pence (optional float)
    - record_count (optional int)
    """
    if daily_df.empty:
        raise ValueError("Daily DataFrame is empty. Cannot generate summary.")

    df = daily_df.copy()
    df["date_dt"] = pd.to_datetime(df["date"])
    df = df.sort_values("date_dt").reset_index(drop=True)

    # 1. PERIOD
    start_date = str(df["date"].iloc[0])
    end_date = str(df["date"].iloc[-1])
    total_days = len(df)
    
    # Check for complete days
    if "is_complete_day" in df.columns:
        complete_days = int(df["is_complete_day"].sum())
        partial_days_list = df[~df["is_complete_day"]][["date", "record_count"]].to_dict(orient="records")
    else:
        complete_days = total_days
        partial_days_list = []

    period_info = {
        "start_date": start_date,
        "end_date": end_date,
        "description": f"{start_date} to {end_date} ({total_days} calendar days)",
        "duration_days": total_days
    }

    # 2. DATASET COUNTS
    counts_info = {
        "daily_records_count": total_days,
        "complete_days_count": complete_days,
        "partial_days": partial_days_list,
        "coverage_ratio": round(complete_days / total_days, 4) if total_days > 0 else 0.0
    }

    # 3. OVERALL STATISTICS & EXTREMES
    # Daily statistics (calculated on complete days for true daily representation if partial exists)
    analysis_df = df[df["is_complete_day"]] if "is_complete_day" in df.columns and complete_days > 0 else df
    
    total_consumption = round(float(df["daily_consumption_kwh"].sum()), 2)
    avg_daily_consumption = round(float(analysis_df["daily_consumption_kwh"].mean()), 2)
    median_daily_consumption = round(float(analysis_df["daily_consumption_kwh"].median()), 2)
    std_daily_consumption = round(float(analysis_df["daily_consumption_kwh"].std()), 2)

    # Extremes (from full complete days to prevent partial day distorting min daily consumption)
    max_row = analysis_df.loc[analysis_df["daily_consumption_kwh"].idxmax()]
    min_row = analysis_df.loc[analysis_df["daily_consumption_kwh"].idxmin()]

    overall_stats = {
        "total_consumption_kwh": total_consumption,
        "average_daily_consumption_kwh": avg_daily_consumption,
        "median_daily_consumption_kwh": median_daily_consumption,
        "std_daily_consumption_kwh": std_daily_consumption,
        "unit": "kWh/day"
    }

    extremes_info = {
        "maximum_day": {
            "date": str(max_row["date"]),
            "consumption_kwh": round(float(max_row["daily_consumption_kwh"]), 2),
            "day_of_week": max_row["date_dt"].strftime("%A")
        },
        "minimum_day": {
            "date": str(min_row["date"]),
            "consumption_kwh": round(float(min_row["daily_consumption_kwh"]), 2),
            "day_of_week": min_row["date_dt"].strftime("%A")
        }
    }

    # 4. MONTHLY STATISTICS
    df["year_month"] = df["date_dt"].dt.strftime("%Y-%m")
    monthly_groups = df.groupby("year_month")

    monthly_stats = {}
    for ym, m_group in monthly_groups:
        m_complete = m_group[m_group["is_complete_day"]] if "is_complete_day" in m_group.columns else m_group
        m_total = round(float(m_group["daily_consumption_kwh"].sum()), 2)
        m_avg = round(float(m_complete["daily_consumption_kwh"].mean()), 2) if len(m_complete) > 0 else 0.0
        monthly_stats[ym] = {
            "month": ym,
            "total_consumption_kwh": m_total,
            "average_daily_consumption_kwh": m_avg,
            "days_count": len(m_group),
            "complete_days_count": len(m_complete)
        }

    # Identify highest / lowest month metrics
    highest_total_month = max(monthly_stats.values(), key=lambda x: x["total_consumption_kwh"])
    highest_avg_month = max(monthly_stats.values(), key=lambda x: x["average_daily_consumption_kwh"])
    lowest_avg_month = min(monthly_stats.values(), key=lambda x: x["average_daily_consumption_kwh"])

    monthly_summary = {
        "monthly_breakdown": monthly_stats,
        "highest_total_month": {
            "month": highest_total_month["month"],
            "total_consumption_kwh": highest_total_month["total_consumption_kwh"]
        },
        "highest_average_month": {
            "month": highest_avg_month["month"],
            "average_daily_consumption_kwh": highest_avg_month["average_daily_consumption_kwh"]
        },
        "lowest_average_month": {
            "month": lowest_avg_month["month"],
            "average_daily_consumption_kwh": lowest_avg_month["average_daily_consumption_kwh"]
        }
    }

    # 5. WEEKDAY VS WEEKEND
    analysis_df_copy = analysis_df.copy()
    analysis_df_copy["is_weekend"] = analysis_df_copy["date_dt"].dt.dayofweek >= 5
    weekday_data = analysis_df_copy[~analysis_df_copy["is_weekend"]]["daily_consumption_kwh"]
    weekend_data = analysis_df_copy[analysis_df_copy["is_weekend"]]["daily_consumption_kwh"]

    weekday_avg = round(float(weekday_data.mean()), 2) if len(weekday_data) > 0 else 0.0
    weekend_avg = round(float(weekend_data.mean()), 2) if len(weekend_data) > 0 else 0.0
    abs_diff = round(weekend_avg - weekday_avg, 2)
    pct_diff = round(((weekend_avg - weekday_avg) / weekday_avg) * 100.0, 1) if weekday_avg > 0 else 0.0

    weekday_weekend_info = {
        "weekday_average_kwh": weekday_avg,
        "weekend_average_kwh": weekend_avg,
        "absolute_difference_kwh": abs_diff,
        "percentage_difference": pct_diff,
        "pattern_description": (
            f"Weekend consumption is {abs(pct_diff)}% "
            f"{'higher' if pct_diff > 0 else 'lower' if pct_diff < 0 else 'equal'} than weekdays"
        )
    }

    # 6. DAY-OF-WEEK PATTERNS
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    analysis_df_copy["day_name"] = analysis_df_copy["date_dt"].dt.day_name()
    dow_group = analysis_df_copy.groupby("day_name")["daily_consumption_kwh"].mean()

    day_of_week_averages = {d: round(float(dow_group.get(d, 0.0)), 2) for d in day_names}
    highest_dow = max(day_of_week_averages.items(), key=lambda x: x[1])
    lowest_dow = min(day_of_week_averages.items(), key=lambda x: x[1])

    dow_summary = {
        "day_of_week_averages_kwh": day_of_week_averages,
        "highest_consumption_day": {"day": highest_dow[0], "average_kwh": highest_dow[1]},
        "lowest_consumption_day": {"day": lowest_dow[0], "average_kwh": lowest_dow[1]}
    }

    # 7. RECENT PERIODS (Recent 7-day, Recent 30-day)
    # Using the last available complete days for consistent daily comparisons
    recent_7_df = analysis_df.tail(7)
    recent_30_df = analysis_df.tail(30)

    recent_7_count = len(recent_7_df)
    recent_7_total = round(float(recent_7_df["daily_consumption_kwh"].sum()), 2)
    recent_7_avg = round(float(recent_7_df["daily_consumption_kwh"].mean()), 2) if recent_7_count > 0 else 0.0
    diff_7_vs_overall = round(recent_7_avg - avg_daily_consumption, 2)
    pct_7_vs_overall = round(((recent_7_avg - avg_daily_consumption) / avg_daily_consumption) * 100.0, 1) if avg_daily_consumption > 0 else 0.0

    recent_30_count = len(recent_30_df)
    recent_30_total = round(float(recent_30_df["daily_consumption_kwh"].sum()), 2)
    recent_30_avg = round(float(recent_30_df["daily_consumption_kwh"].mean()), 2) if recent_30_count > 0 else 0.0
    diff_30_vs_overall = round(recent_30_avg - avg_daily_consumption, 2)
    pct_30_vs_overall = round(((recent_30_avg - avg_daily_consumption) / avg_daily_consumption) * 100.0, 1) if avg_daily_consumption > 0 else 0.0

    recent_periods_info = {
        "recent_7_days": {
            "period": f"{recent_7_df['date'].iloc[0]} to {recent_7_df['date'].iloc[-1]}",
            "days_evaluated": recent_7_count,
            "total_kwh": recent_7_total,
            "average_daily_kwh": recent_7_avg,
            "difference_vs_overall_avg_kwh": diff_7_vs_overall,
            "percentage_vs_overall_avg": pct_7_vs_overall
        },
        "recent_30_days": {
            "period": f"{recent_30_df['date'].iloc[0]} to {recent_30_df['date'].iloc[-1]}",
            "days_evaluated": recent_30_count,
            "total_kwh": recent_30_total,
            "average_daily_kwh": recent_30_avg,
            "difference_vs_overall_avg_kwh": diff_30_vs_overall,
            "percentage_vs_overall_avg": pct_30_vs_overall
        }
    }

    # 8. TREND ANALYSIS
    # (1) Primary: 7-day rolling average comparison (last 7 days vs previous 7 days)
    # (2) Secondary: Linear regression slope on daily consumption over the period
    # (3) Supporting: Recent 30 days vs preceding 30 days
    threshold_pct = 5.0  # +/- 5% threshold to declare increasing / decreasing vs stable
    
    # 7-day rolling comparison
    if len(analysis_df) >= 14:
        last_7_avg = float(analysis_df["daily_consumption_kwh"].iloc[-7:].mean())
        prev_7_avg = float(analysis_df["daily_consumption_kwh"].iloc[-14:-7].mean())
        short_term_change_pct = round(((last_7_avg - prev_7_avg) / prev_7_avg) * 100.0, 1) if prev_7_avg > 0 else 0.0
    else:
        short_term_change_pct = 0.0

    # Linear slope
    x = np.arange(len(analysis_df))
    y = analysis_df["daily_consumption_kwh"].values
    if len(x) > 1:
        slope, intercept = np.polyfit(x, y, 1)
        slope_kwh_per_day = round(float(slope), 4)
    else:
        slope_kwh_per_day = 0.0

    # Long-term comparison: First 30 days vs Last 30 days
    if len(analysis_df) >= 60:
        first_30_avg = float(analysis_df["daily_consumption_kwh"].iloc[:30].mean())
        last_30_avg = float(analysis_df["daily_consumption_kwh"].iloc[-30:].mean())
        long_term_change_pct = round(((last_30_avg - first_30_avg) / first_30_avg) * 100.0, 1) if first_30_avg > 0 else 0.0
    else:
        long_term_change_pct = 0.0

    # Trend Direction determination
    if short_term_change_pct > threshold_pct:
        short_term_direction = "increasing"
    elif short_term_change_pct < -threshold_pct:
        short_term_direction = "decreasing"
    else:
        short_term_direction = "stable"

    if long_term_change_pct > threshold_pct:
        overall_direction = "increasing"
    elif long_term_change_pct < -threshold_pct:
        overall_direction = "decreasing"
    else:
        overall_direction = "stable"

    trend_info = {
        "short_term_trend": {
            "direction": short_term_direction,
            "percentage_change": short_term_change_pct,
            "comparison": "Last 7 days vs Previous 7 days",
            "method": "7-day rolling window comparison"
        },
        "overall_trend": {
            "direction": overall_direction,
            "linear_slope_kwh_per_day": slope_kwh_per_day,
            "long_term_change_percentage": long_term_change_pct,
            "comparison": "Last 30 days vs First 30 days",
            "method": "Linear regression and 30-day boundary comparison"
        },
        "threshold_applied": f"±{threshold_pct}% for significant trend classification"
    }

    # 9. COST STATISTICS (clearly labeled as estimated cost)
    if "estimated_cost_pence" in df.columns:
        total_cost_pence = round(float(df["estimated_cost_pence"].sum()), 2)
        total_cost_pounds = round(total_cost_pence / 100.0, 2)
        avg_daily_cost_pence = round(float(analysis_df["estimated_cost_pence"].mean()), 2)
        avg_daily_cost_pounds = round(avg_daily_cost_pence / 100.0, 2)

        cost_info = {
            "total_estimated_cost_gbp": total_cost_pounds,
            "total_estimated_cost_pence": total_cost_pence,
            "average_daily_estimated_cost_gbp": avg_daily_cost_pounds,
            "average_daily_estimated_cost_pence": avg_daily_cost_pence,
            "currency": "GBP (£) / Pence (p)",
            "disclaimer": "Cost values are estimated calculations based on unit rate data and do not represent confirmed final utility bills."
        }
    else:
        cost_info = None

    # Assemble structured summary JSON
    summary_output = {
        "period": period_info,
        "counts": counts_info,
        "overall": overall_stats,
        "extremes": extremes_info,
        "monthly": monthly_summary,
        "weekday_weekend": weekday_weekend_info,
        "day_of_week": dow_summary,
        "recent": recent_periods_info,
        "trend": trend_info,
        "cost": cost_info
    }

    return summary_output
