"""
Data loaders and dataset helpers for AgriMind.
Provides safe fallbacks when dataset files or dependencies (like pandas) are missing.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import pandas as pd  # type: ignore
except Exception:
    pd = None  # Optional dependency

DATASETS_DIR = Path("datasets")


@dataclass
class DataSourceInfo:
    source_type: str  # "dataset" | "cache" | "mock" | "error"
    source_name: str
    timestamp: datetime
    record_count: int
    confidence: float


def _empty_df() -> Any:
    if pd is None:
        return None
    return pd.DataFrame()


def get_dataset_summary() -> Dict[str, str]:
    summary: Dict[str, str] = {}
    expected_files = {
        "farm_sensor_data_tehsil_with_date.json": "sensor_dataset",
        "weather_data_tehsil.csv": "weather_dataset",
        "farm_resources.json": "resources_dataset",
        "market_prices.csv": "market_dataset",
    }
    for filename, label in expected_files.items():
        path = DATASETS_DIR / filename
        summary[label] = "Cached" if path.exists() else "Missing"
    return summary


def clear_dataset_cache() -> int:
    # Remove pickled caches produced by agents in data/ directory
    data_dir = Path("data")
    removed = 0
    if data_dir.exists():
        for p in data_dir.glob("*_cache.pickle"):
            try:
                p.unlink()
                removed += 1
            except Exception:
                pass
    return removed


def load_weather_data(location_filter: Optional[str] = None, days_back: int = 30) -> Tuple[Any, DataSourceInfo]:
    """Load weather data from datasets/weather_data_tehsil.csv if available.
    Returns (DataFrame or None, DataSourceInfo).
    """
    src = DataSourceInfo(
        source_type="error",
        source_name="weather_dataset",
        timestamp=datetime.now(),
        record_count=0,
        confidence=0.0,
    )
    path = DATASETS_DIR / "weather_data_tehsil.csv"
    if not path.exists() or pd is None:
        return _empty_df(), src

    try:
        df = pd.read_csv(path)
        # Normalize common columns if present
        # Expect columns like: date, location, temperature, humidity, precipitation
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            cutoff = pd.Timestamp(datetime.now() - timedelta(days=days_back))
            df = df[df["date"] >= cutoff]
        if location_filter and "location" in df.columns:
            df = df[df["location"].str.contains(location_filter, case=False, na=False)]

        src = DataSourceInfo(
            source_type="dataset",
            source_name=path.name,
            timestamp=datetime.now(),
            record_count=len(df),
            confidence=0.9,
        )
        return df, src
    except Exception:
        return _empty_df(), src


def load_sensor_data(location_filter: Optional[str] = None, date_range: Optional[Tuple[datetime, datetime]] = None) -> Tuple[List[Dict[str, Any]], DataSourceInfo]:
    """Load sensor data list from farm_sensor_data_tehsil_with_date.json if available."""
    path = DATASETS_DIR / "farm_sensor_data_tehsil_with_date.json"
    src = DataSourceInfo(
        source_type="error",
        source_name=path.name,
        timestamp=datetime.now(),
        record_count=0,
        confidence=0.0,
    )
    if not path.exists():
        return [], src

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        readings: List[Dict[str, Any]] = []
        for item in data if isinstance(data, list) else []:
            try:
                dt = datetime.fromisoformat(item.get("date") or item.get("timestamp") or datetime.now().isoformat())
                rec = {
                    "date": dt,
                    "soil_moisture": item.get("soil_moisture"),
                    "temperature": item.get("temperature"),
                    "humidity": item.get("humidity"),
                    "pest_index": item.get("pest_index", 0.0),
                    "location": item.get("location", ""),
                }
                if location_filter and location_filter.lower() not in str(rec["location"]).lower():
                    continue
                if date_range:
                    start, end = date_range
                    if not (start <= rec["date"] <= end):
                        continue
                readings.append(rec)
            except Exception:
                continue

        src = DataSourceInfo(
            source_type="dataset",
            source_name=path.name,
            timestamp=datetime.now(),
            record_count=len(readings),
            confidence=0.9,
        )
        return readings, src
    except Exception:
        return [], src


def load_resources_data() -> Tuple[Dict[str, Any], DataSourceInfo]:
    """Load resources from farm_resources.json; returns a dict keyed by farm id."""
    path = DATASETS_DIR / "farm_resources.json"
    src = DataSourceInfo(
        source_type="error",
        source_name=path.name,
        timestamp=datetime.now(),
        record_count=0,
        confidence=0.0,
    )
    if not path.exists():
        return {}, src

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Expect a dict of farms -> resources; be permissive
        farms = data if isinstance(data, dict) else {}
        src = DataSourceInfo(
            source_type="dataset",
            source_name=path.name,
            timestamp=datetime.now(),
            record_count=len(farms),
            confidence=0.9,
        )
        return farms, src
    except Exception:
        return {}, src


def load_market_data(days_back: int = 60) -> Tuple[Any, DataSourceInfo]:
    """Load market prices from market_prices.csv if available."""
    src = DataSourceInfo(
        source_type="error",
        source_name="market_prices.csv",
        timestamp=datetime.now(),
        record_count=0,
        confidence=0.0,
    )
    path = DATASETS_DIR / "market_prices.csv"
    if not path.exists() or pd is None:
        return _empty_df(), src

    try:
        df = pd.read_csv(path)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            cutoff = pd.Timestamp(datetime.now() - timedelta(days=days_back))
            df = df[df["date"] >= cutoff]
        src = DataSourceInfo(
            source_type="dataset",
            source_name=path.name,
            timestamp=datetime.now(),
            record_count=len(df),
            confidence=0.9,
        )
        return df, src
    except Exception:
        return _empty_df(), src
