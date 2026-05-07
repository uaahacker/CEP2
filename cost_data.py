"""
cost_data.py – AWS Cost Explorer & Demo Data Module
=====================================================
Handles all cost data fetching.

Real Mode:  Calls AWS Cost Explorer via boto3 GetCostAndUsage.
Demo Mode:  Generates realistic synthetic cost data with a built-in
            anomaly spike so the insights panel always has something
            interesting to show even without AWS credentials.

The public interface is get_cost_data() – call this from app.py.
The DataFrame it returns always has exactly three columns:
    Date  (datetime64)
    Group (str)
    Cost  (float)
"""

from __future__ import annotations

import os
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ── Optional boto3 import (app works without it in Demo Mode) ─────────────────
try:
    import boto3
    from botocore.exceptions import (
        ClientError,
        NoCredentialsError,
        PartialCredentialsError,
    )
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# DEMO DATA CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

_GROUPS_MAP: dict[str, list[str]] = {
    "SERVICE": [
        "Amazon EC2",
        "Amazon S3",
        "Amazon RDS",
        "AWS Lambda",
        "Amazon CloudFront",
        "Amazon DynamoDB",
        "Amazon VPC",
        "Amazon EKS",
    ],
    "REGION": ["us-east-1", "us-west-2", "eu-west-1", "ap-south-1"],
    "LINKED_ACCOUNT": ["Production", "Development", "Testing", "Analytics"],
}

# Approximate daily USD base costs per group
_BASE_COSTS: dict[str, float] = {
    # Services
    "Amazon EC2": 85.0,
    "Amazon S3": 12.0,
    "Amazon RDS": 55.0,
    "AWS Lambda": 4.0,
    "Amazon CloudFront": 9.0,
    "Amazon DynamoDB": 18.0,
    "Amazon VPC": 6.0,
    "Amazon EKS": 35.0,
    # Regions
    "us-east-1": 90.0,
    "us-west-2": 70.0,
    "eu-west-1": 55.0,
    "ap-south-1": 30.0,
    # Accounts
    "Production": 130.0,
    "Development": 50.0,
    "Testing": 25.0,
    "Analytics": 40.0,
}


# ─────────────────────────────────────────────────────────────────────────────
# AWS CREDENTIAL CHECK
# ─────────────────────────────────────────────────────────────────────────────

def check_aws_credentials() -> bool:
    """
    Perform a lightweight AWS Cost Explorer probe to verify that real
    credentials are present and Cost Explorer is accessible.

    Returns True only when a real AWS call succeeds.
    Never raises – always returns a bool.
    """
    if not BOTO3_AVAILABLE:
        return False

    try:
        ce = boto3.client(
            "ce",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
        today = date.today()
        start = (today - timedelta(days=2)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")
        ce.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
        )
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# AWS COST EXPLORER FETCH
# ─────────────────────────────────────────────────────────────────────────────

def fetch_cost_explorer_data(
    start_date: date,
    end_date: date,
    granularity: str,
    metric: str,
    group_by: str,
) -> pd.DataFrame | None:
    """
    Call AWS Cost Explorer GetCostAndUsage and return a clean DataFrame.

    Args:
        start_date:   Inclusive start date.
        end_date:     Inclusive end date (CE end is exclusive, adjusted internally).
        granularity:  "DAILY" or "MONTHLY".
        metric:       "UnblendedCost" or "AmortizedCost".
        group_by:     "SERVICE", "REGION", or "LINKED_ACCOUNT".

    Returns:
        DataFrame with columns [Date, Group, Cost], or None on any error.
        None triggers automatic Demo Mode fallback in the caller.
    """
    if not BOTO3_AVAILABLE:
        return None

    # Cost Explorer end date is EXCLUSIVE → add one day
    ce_end = (end_date + timedelta(days=1)).strftime("%Y-%m-%d")
    ce_start = start_date.strftime("%Y-%m-%d")

    try:
        ce = boto3.client(
            "ce",
            region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
        response = ce.get_cost_and_usage(
            TimePeriod={"Start": ce_start, "End": ce_end},
            Granularity=granularity,
            Metrics=[metric],
            GroupBy=[{"Type": "DIMENSION", "Key": group_by}],
        )
    except (NoCredentialsError, PartialCredentialsError):
        return None
    except ClientError as exc:
        # Cost Explorer not enabled, access denied, or auth failure
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("OptInRequired", "AccessDeniedException", "AuthFailure"):
            return None
        return None
    except Exception:
        return None

    # Parse CE response into flat rows
    rows = []
    for result in response.get("ResultsByTime", []):
        period_start = result["TimePeriod"]["Start"]
        for group in result.get("Groups", []):
            group_name = group["Keys"][0]
            amount = float(group["Metrics"][metric]["Amount"])
            rows.append({
                "Date": pd.to_datetime(period_start),
                "Group": group_name,
                "Cost": amount,
            })

    if not rows:
        return None

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# DEMO / SYNTHETIC DATA GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_demo_data(
    start_date: date,
    end_date: date,
    granularity: str,
    group_by: str,
) -> pd.DataFrame:
    """
    Generate realistic synthetic AWS cost data for Demo Mode.

    Key properties:
    - Gaussian noise (±12 %) on top of realistic base costs
    - A deliberate ×4.5 cost spike injected near the end of the period
      for the first group, so anomaly detection always fires in demos
    - Monthly granularity multiplies daily costs by 30

    Args:
        start_date:  Inclusive start date.
        end_date:    Inclusive end date.
        granularity: "DAILY" or "MONTHLY".
        group_by:    "SERVICE", "REGION", or "LINKED_ACCOUNT".

    Returns:
        DataFrame with columns [Date, Group, Cost].
    """
    np.random.seed(42)

    groups = _GROUPS_MAP[group_by]
    total_days = (end_date - start_date).days + 1

    # Build date spine
    if granularity == "DAILY":
        date_spine = [start_date + timedelta(days=i) for i in range(total_days)]
    else:  # MONTHLY
        date_spine = []
        cursor = date(start_date.year, start_date.month, 1)
        while cursor <= end_date:
            date_spine.append(cursor)
            cursor = (
                date(cursor.year + 1, 1, 1)
                if cursor.month == 12
                else date(cursor.year, cursor.month + 1, 1)
            )

    spike_idx = max(0, len(date_spine) - 5)   # spike near the end of the range
    monthly_multiplier = 30 if granularity == "MONTHLY" else 1

    rows = []
    for g in groups:
        base = _BASE_COSTS.get(g, 20.0) * monthly_multiplier
        for idx, d in enumerate(date_spine):
            noise = np.random.normal(0, base * 0.12)
            cost = max(0.0, base + noise)

            # Inject anomaly spike for the first group only
            if g == groups[0] and idx == spike_idx:
                cost *= 4.5

            rows.append({
                "Date": pd.to_datetime(d),
                "Group": g,
                "Cost": round(cost, 4),
            })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def get_cost_data(
    start_date: date,
    end_date: date,
    granularity: str,
    metric: str,
    group_by: str,
    aws_available: bool,
) -> tuple[pd.DataFrame, bool]:
    """
    Unified data loader.  Tries AWS Cost Explorer first when aws_available
    is True; falls back to Demo Mode automatically on any failure.

    Args:
        start_date:    Inclusive start date.
        end_date:      Inclusive end date.
        granularity:   "DAILY" or "MONTHLY".
        metric:        "UnblendedCost" or "AmortizedCost".
        group_by:      "SERVICE", "REGION", or "LINKED_ACCOUNT".
        aws_available: Pre-checked flag from check_aws_credentials().

    Returns:
        (df, is_real_aws)
            df           – DataFrame[Date, Group, Cost]
            is_real_aws  – True when real AWS data was used, False for Demo Mode
    """
    df: pd.DataFrame | None = None

    if aws_available:
        df = fetch_cost_explorer_data(
            start_date, end_date, granularity, metric, group_by
        )

    if df is None or df.empty:
        df = generate_demo_data(start_date, end_date, granularity, group_by)
        return df, False

    return df, True
