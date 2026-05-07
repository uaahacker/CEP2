"""
insights.py – FinOps Insight Calculations
==========================================
All analytical computations are isolated here so app.py stays clean.

Public API:
    calculate_all_insights(df, reduction_pct) -> dict
        Calls every helper below and returns a single insights dict.

Individual helpers (also importable for testing):
    calculate_total_cost(df)              -> float
    calculate_mom_change(df)              -> float | None
    calculate_top3_concentration(df)      -> tuple[float, list[str]]
    detect_anomalies(df)                  -> dict
    calculate_projected_savings(df, pct)  -> tuple[float, float]
"""

from __future__ import annotations

import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# INDIVIDUAL METRIC FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_total_cost(df: pd.DataFrame) -> float:
    """
    Sum all Cost values in the DataFrame.

    Args:
        df: DataFrame with a 'Cost' column.

    Returns:
        Total spend as a float.
    """
    return float(df["Cost"].sum())


def calculate_mom_change(df: pd.DataFrame) -> float | None:
    """
    Estimate period-over-period cost change by splitting the date range
    into two equal halves and comparing their totals.

    A real month-over-month comparison requires at least 2 data points.

    Args:
        df: DataFrame with 'Date' and 'Cost' columns.

    Returns:
        Percentage change as a float (positive = costs increased),
        or None when there is not enough data for a meaningful comparison.
    """
    df_sorted = df.sort_values("Date")
    unique_dates = df_sorted["Date"].unique()
    n = len(unique_dates)

    if n < 2:
        return None

    mid = n // 2
    first_half_cost = df_sorted[df_sorted["Date"].isin(unique_dates[:mid])]["Cost"].sum()
    second_half_cost = df_sorted[df_sorted["Date"].isin(unique_dates[mid:])]["Cost"].sum()

    if first_half_cost <= 0:
        return None

    return round(((second_half_cost - first_half_cost) / first_half_cost) * 100, 2)


def calculate_top3_concentration(df: pd.DataFrame) -> tuple[float, list[str]]:
    """
    Compute what percentage of total spend comes from the top 3 groups.

    Args:
        df: DataFrame with 'Group' and 'Cost' columns.

    Returns:
        (concentration_pct, [top_group_name_1, top_group_name_2, top_group_name_3])
    """
    total = df["Cost"].sum()
    group_totals = df.groupby("Group")["Cost"].sum().sort_values(ascending=False)
    top3 = group_totals.head(3)
    top3_cost = top3.sum()
    concentration = round((top3_cost / total * 100), 1) if total > 0 else 0.0
    return concentration, list(top3.index)


def detect_anomalies(df: pd.DataFrame) -> dict:
    """
    Detect date-level cost spikes using the mean ± 2σ rule.

    A data point is flagged as an anomaly when:
        daily_total > mean(daily_totals) + 2 * std(daily_totals)

    Args:
        df: DataFrame with 'Date' and 'Cost' columns.

    Returns:
        dict with keys:
            count     – number of anomalous dates
            threshold – the computed threshold value (USD)
            dates     – list of [date_str, cost] pairs for anomalous days
    """
    daily = df.groupby("Date")["Cost"].sum().reset_index()
    mean_cost = float(daily["Cost"].mean())
    std_cost = float(daily["Cost"].std(ddof=0))   # population std for robustness
    threshold = mean_cost + 2 * std_cost

    anomalies = daily[daily["Cost"] > threshold].copy()

    date_list = []
    if not anomalies.empty:
        anomalies["Date_str"] = anomalies["Date"].dt.strftime("%Y-%m-%d")
        date_list = anomalies[["Date_str", "Cost"]].values.tolist()

    return {
        "count": int(len(anomalies)),
        "threshold": round(threshold, 2),
        "dates": date_list[:10],   # cap displayed anomalies at 10
    }


def calculate_projected_savings(
    df: pd.DataFrame, reduction_pct: float
) -> tuple[float, float]:
    """
    Estimate savings from a cost-reduction policy applied uniformly.

    Projected Cost   = Total Cost × (1 − reduction_pct / 100)
    Estimated Savings = Total Cost × (reduction_pct / 100)

    Args:
        df:            DataFrame with a 'Cost' column.
        reduction_pct: Target reduction as a percentage (0–30).

    Returns:
        (savings_amount, projected_total_cost)
    """
    total = float(df["Cost"].sum())
    savings = round(total * (reduction_pct / 100), 2)
    projected = round(total - savings, 2)
    return savings, projected


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def calculate_all_insights(df: pd.DataFrame, reduction_pct: float) -> dict:
    """
    Run every insight calculation and return a single dictionary.

    Args:
        df:            DataFrame[Date, Group, Cost].
        reduction_pct: Cost reduction target percentage (0–30).

    Returns:
        dict with keys:
            total_spend         (float)
            mom_change          (float | None)
            top3_concentration  (float)
            top3_names          (list[str])
            anomaly_count       (int)
            anomaly_threshold   (float)
            anomaly_dates       (list[[str, float]])
            projected_savings   (float)
            projected_cost      (float)
    """
    total_spend = calculate_total_cost(df)
    mom_change = calculate_mom_change(df)
    concentration, top3_names = calculate_top3_concentration(df)
    anomaly_info = detect_anomalies(df)
    savings, projected_cost = calculate_projected_savings(df, reduction_pct)

    return {
        "total_spend": total_spend,
        "mom_change": mom_change,
        "top3_concentration": concentration,
        "top3_names": top3_names,
        "anomaly_count": anomaly_info["count"],
        "anomaly_threshold": anomaly_info["threshold"],
        "anomaly_dates": anomaly_info["dates"],
        "projected_savings": savings,
        "projected_cost": projected_cost,
    }
