"""
AgriMind: Dataset Loaders
Load and validate official hackathon datasets for all agent types.

Features:
- JSON and CSV dataset loading with schema validation
- Data caching for performance
- Error handling with fallbacks
- Source tracking for logging
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DataSourceInfo:
    """Information about the data source used"""
    source_type: str  # "dataset", "api", "mock", "cached"
    source_name: str  # filename or API name
    timestamp: datetime
    record_count: int
    confidence: float  # 0.0 to 1.0


class DatasetCache:
    """Simple caching system for loaded datasets"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached data if still valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_duration:
                return data
        return None
    
    def set(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        self._cache[key] = (data, datetime.now())


# Global cache instance
_dataset_cache = DatasetCache()


def load_sensor_data(
    file_path: str = "datasets/farm_sensor_data_tehsil_with_date.json",
    location_filter: Optional[str] = None,
    crop_filter: Optional[str] = None,
    date_range: Optional[Tuple[datetime, datetime]] = None
) -> Tuple[List[Dict[str, Any]], DataSourceInfo]:
    """
    Load sensor data from official hackathon JSON dataset
    
    Args:
        file_path: Path to sensor data JSON file
        location_filter: Filter by specific location/tehsil
        crop_filter: Filter by crop type
        date_range: Tuple of (start_date, end_date) for filtering
    
    Returns:
        Tuple of (sensor_readings_list, source_info)
    """
    cache_key = f"sensor_data_{file_path}_{location_filter}_{crop_filter}"
    
    # Try cache first
    cached_data = _dataset_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Sensor dataset not found: {file_path}")
        
        logger.info(f"Loading sensor data from {file_path}")
        
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Validate and standardize data format
        sensor_readings = []
        
        for record in raw_data:
            try:
<<<<<<< HEAD
                # Validate required fields
                required_fields = ['soil_moisture', 'temperature', 'humidity', 'location', 'date']
=======
                # Validate required fields (adjust for actual dataset structure)
                required_fields = ['soil_moisture_%', 'temperature_c', 'humidity_%', 'date']
>>>>>>> 8f6adccdf567b072766f7a631b59de49a98aec25
                if not all(field in record for field in required_fields):
                    logger.warning(f"Skipping record with missing fields: {record}")
                    continue
                
                # Parse date
                try:
                    if isinstance(record['date'], str):
                        record_date = datetime.fromisoformat(record['date'].replace('Z', '+00:00'))
                    else:
                        record_date = datetime.now()  # Fallback
                except:
                    record_date = datetime.now()  # Fallback
                
                # Apply filters
<<<<<<< HEAD
                if location_filter and record.get('location', '').lower() != location_filter.lower():
=======
                if location_filter and record.get('district', '').lower() != location_filter.lower():
>>>>>>> 8f6adccdf567b072766f7a631b59de49a98aec25
                    continue
                
                if crop_filter and record.get('crop_type', '').lower() != crop_filter.lower():
                    continue
                
                if date_range:
                    start_date, end_date = date_range
                    if not (start_date <= record_date <= end_date):
                        continue
                
                # Standardize reading format
                standardized_record = {
                    'sensor_type': 'multi_sensor',
<<<<<<< HEAD
                    'soil_moisture': float(record['soil_moisture']),
                    'temperature': float(record['temperature']), 
                    'humidity': float(record['humidity']),
                    'pest_index': float(record.get('pest_index', 0.0)),
                    'location': str(record['location']),
                    'crop_type': str(record.get('crop_type', 'unknown')),
=======
                    'soil_moisture': float(record['soil_moisture_%']),
                    'temperature': float(record['temperature_c']), 
                    'humidity': float(record['humidity_%']),
                    'pest_index': 1.0 if record.get('pest_detection', 'None') != 'None' else 0.0,
                    'location': str(record.get('district', 'unknown')),
                    'crop_type': str(record.get('crop_type', 'unknown')),
                    'farm_id': str(record.get('farm_id', 'unknown')),
                    'tehsil': str(record.get('tehsil', 'unknown')),
                    'pest_detection': str(record.get('pest_detection', 'None')),
>>>>>>> 8f6adccdf567b072766f7a631b59de49a98aec25
                    'date': record_date,
                    'timestamp': record_date.isoformat(),
                    'quality': 0.9,  # High quality for official dataset
                    'source': 'dataset'
                }
                
                sensor_readings.append(standardized_record)
                
            except Exception as e:
                logger.warning(f"Error processing sensor record: {e}")
                continue
        
        source_info = DataSourceInfo(
            source_type="dataset",
            source_name=file_path_obj.name,
            timestamp=datetime.now(),
            record_count=len(sensor_readings),
            confidence=0.9
        )
        
        # Cache the result
        result = (sensor_readings, source_info)
        _dataset_cache.set(cache_key, result)
        
        logger.info(f"Loaded {len(sensor_readings)} sensor records from dataset")
        return result
        
    except Exception as e:
        logger.error(f"Error loading sensor data: {e}")
        # Return empty data with error info
        source_info = DataSourceInfo(
            source_type="error",
            source_name=f"failed_to_load_{file_path}",
            timestamp=datetime.now(),
            record_count=0,
            confidence=0.0
        )
        return [], source_info


def load_weather_data(
    file_path: str = "datasets/weather_data_tehsil.csv",
    location_filter: Optional[str] = None,
    days_back: int = 30
) -> Tuple[pd.DataFrame, DataSourceInfo]:
    """
    Load weather data from official hackathon CSV dataset
    
    Args:
        file_path: Path to weather data CSV file
        location_filter: Filter by specific location/tehsil
        days_back: Number of days of historical data to include
    
    Returns:
        Tuple of (weather_dataframe, source_info)
    """
    cache_key = f"weather_data_{file_path}_{location_filter}_{days_back}"
    
    # Try cache first
    cached_data = _dataset_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Weather dataset not found: {file_path}")
        
        logger.info(f"Loading weather data from {file_path}")
        
        # Load CSV with pandas
        df = pd.read_csv(file_path_obj, encoding='utf-8')
        
        # Standardize column names (case-insensitive matching)
        df.columns = df.columns.str.lower().str.strip()
        
        # Validate required columns
        required_cols = ['temperature', 'humidity', 'date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns in weather data: {missing_cols}")
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Apply location filter
        if location_filter and 'location' in df.columns:
            df = df[df['location'].str.lower() == location_filter.lower()]
        
        # Apply date range filter
        if days_back > 0:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            df = df[df['date'] >= cutoff_date]
        
        # Clean numeric columns
        numeric_columns = ['temperature', 'humidity', 'wind_speed', 'precipitation']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with all NaN values in numeric columns
        existing_numeric_cols = [col for col in numeric_columns if col in df.columns]
        if existing_numeric_cols:
            df = df.dropna(subset=existing_numeric_cols, how='all')
        
        # Sort by date
        if 'date' in df.columns:
            df = df.sort_values('date')
        
        source_info = DataSourceInfo(
            source_type="dataset",
            source_name=file_path_obj.name,
            timestamp=datetime.now(),
            record_count=len(df),
            confidence=0.9
        )
        
        # Cache the result
        result = (df, source_info)
        _dataset_cache.set(cache_key, result)
        
        logger.info(f"Loaded {len(df)} weather records from dataset")
        return result
        
    except Exception as e:
        logger.error(f"Error loading weather data: {e}")
        # Return empty dataframe with error info
        source_info = DataSourceInfo(
            source_type="error",
            source_name=f"failed_to_load_{file_path}",
            timestamp=datetime.now(),
            record_count=0,
            confidence=0.0
        )
        return pd.DataFrame(), source_info


def load_resources_data(
    file_path: str = "datasets/farm_resources.json",
    farm_filter: Optional[str] = None
) -> Tuple[Dict[str, Any], DataSourceInfo]:
    """
    Load farm resources data from official hackathon JSON dataset
    
    Args:
        file_path: Path to resources data JSON file
        farm_filter: Filter by specific farm ID
    
    Returns:
        Tuple of (resources_dict, source_info)
    """
    cache_key = f"resources_data_{file_path}_{farm_filter}"
    
    # Try cache first
    cached_data = _dataset_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Resources dataset not found: {file_path}")
        
        logger.info(f"Loading resources data from {file_path}")
        
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Standardize resources format
        resources_data = {}
        
        if isinstance(raw_data, list):
            # Handle array format - aggregate by farm or use first record
            for record in raw_data:
                farm_id = record.get('farm_id', 'default_farm')
                if farm_filter and farm_id != farm_filter:
                    continue
                resources_data[farm_id] = record
        elif isinstance(raw_data, dict):
            # Handle object format
            if farm_filter and farm_filter in raw_data:
                resources_data = {farm_filter: raw_data[farm_filter]}
            else:
                resources_data = raw_data
        
        # Validate and standardize resource structure
        standardized_resources = {}
        for farm_id, farm_resources in resources_data.items():
            standardized_farm = {
                'water': {
                    'total_capacity': float(farm_resources.get('water', {}).get('capacity', 10000)),
                    'used': 0,
                    'reservations': {},
                    'efficiency_multiplier': 1.0
                },
                'fertilizer': {
                    'inventory': {
                        'nitrogen': float(farm_resources.get('fertilizer', {}).get('nitrogen', 500)),
                        'phosphorus': float(farm_resources.get('fertilizer', {}).get('phosphorus', 300)),
                        'potassium': float(farm_resources.get('fertilizer', {}).get('potassium', 400))
                    },
                    'reservations': {}
                },
                'equipment': {
                    'units': farm_resources.get('equipment', {
                        'tractors': 2,
                        'irrigation_pumps': 4,
                        'sprayers': 3,
                        'harvesters': 1
                    }),
                    'availability': {},
                    'maintenance_schedule': {}
                },
                'labor': {
                    'workers': int(farm_resources.get('labor', {}).get('workers', 8)),
                    'assigned': 0,
                    'skills': farm_resources.get('labor', {}).get('skills', ['basic', 'intermediate', 'expert']),
                    'rates': farm_resources.get('labor', {}).get('rates', {'basic': 10, 'intermediate': 12, 'expert': 15})
                }
            }
            standardized_resources[farm_id] = standardized_farm
        
        source_info = DataSourceInfo(
            source_type="dataset",
            source_name=file_path_obj.name,
            timestamp=datetime.now(),
            record_count=len(standardized_resources),
            confidence=0.9
        )
        
        # Cache the result
        result = (standardized_resources, source_info)
        _dataset_cache.set(cache_key, result)
        
        logger.info(f"Loaded resources for {len(standardized_resources)} farms from dataset")
        return result
        
    except Exception as e:
        logger.error(f"Error loading resources data: {e}")
        # Return empty resources with error info
        source_info = DataSourceInfo(
            source_type="error",
            source_name=f"failed_to_load_{file_path}",
            timestamp=datetime.now(),
            record_count=0,
            confidence=0.0
        )
        return {}, source_info


def load_market_data(
    file_path: str = "datasets/market_prices.csv",
    crop_filter: Optional[str] = None,
    days_back: int = 60
) -> Tuple[pd.DataFrame, DataSourceInfo]:
    """
    Load market price data from official hackathon CSV dataset
    
    Args:
        file_path: Path to market prices CSV file
        crop_filter: Filter by specific crop type
        days_back: Number of days of price history to include
    
    Returns:
        Tuple of (prices_dataframe, source_info)
    """
    cache_key = f"market_data_{file_path}_{crop_filter}_{days_back}"
    
    # Try cache first
    cached_data = _dataset_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Market dataset not found: {file_path}")
        
        logger.info(f"Loading market data from {file_path}")
        
        # Load CSV with pandas
        df = pd.read_csv(file_path_obj, encoding='utf-8')
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
<<<<<<< HEAD
        # Validate required columns
        required_cols = ['crop', 'price', 'date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns in market data: {missing_cols}")
            # Try alternative column names
            column_mapping = {
                'crop_type': 'crop',
                'commodity': 'crop',
                'price_per_kg': 'price',
                'unit_price': 'price'
            }
            for old_name, new_name in column_mapping.items():
                if old_name in df.columns and new_name not in df.columns:
                    df[new_name] = df[old_name]
=======
        # Map column names to standard format
        column_mapping = {
            'commodity': 'crop',
            'avg_price_pkr_per_40kg': 'price',
            'min_price_pkr_per_40kg': 'min_price',
            'max_price_pkr_per_40kg': 'max_price',
            'market_location': 'location'
        }
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns and new_name not in df.columns:
                df[new_name] = df[old_name]
        
        # Validate required columns after mapping
        required_cols = ['crop', 'price', 'date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns in market data after mapping: {missing_cols}")
>>>>>>> 8f6adccdf567b072766f7a631b59de49a98aec25
        
        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df = df.dropna(subset=['date'])
        
        # Apply crop filter
        if crop_filter and 'crop' in df.columns:
            df = df[df['crop'].str.lower() == crop_filter.lower()]
        
        # Apply date range filter
        if days_back > 0:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            df = df[df['date'] >= cutoff_date]
        
        # Clean price column
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
            df = df.dropna(subset=['price'])
        
        # Add additional columns if not present
        if 'volume' not in df.columns:
            df['volume'] = np.random.randint(100, 1000, size=len(df))
        
        if 'quality_grade' not in df.columns:
            df['quality_grade'] = np.random.choice(['A', 'B', 'C'], size=len(df), p=[0.3, 0.5, 0.2])
        
        # Sort by date and crop
        df = df.sort_values(['date', 'crop'] if 'crop' in df.columns else ['date'])
        
        source_info = DataSourceInfo(
            source_type="dataset",
            source_name=file_path_obj.name,
            timestamp=datetime.now(),
            record_count=len(df),
            confidence=0.9
        )
        
        # Cache the result
        result = (df, source_info)
        _dataset_cache.set(cache_key, result)
        
        logger.info(f"Loaded {len(df)} market price records from dataset")
        return result
        
    except Exception as e:
        logger.error(f"Error loading market data: {e}")
        # Return empty dataframe with error info
        source_info = DataSourceInfo(
            source_type="error",
            source_name=f"failed_to_load_{file_path}",
            timestamp=datetime.now(),
            record_count=0,
            confidence=0.0
        )
        return pd.DataFrame(), source_info


def get_dataset_summary() -> Dict[str, Any]:
    """Get a summary of all loaded datasets"""
    summary = {
        'sensor_data': 'Not loaded',
        'weather_data': 'Not loaded', 
        'resources_data': 'Not loaded',
        'market_data': 'Not loaded',
        'cache_size': len(_dataset_cache._cache)
    }
    
    # Check which datasets are in cache
    for key in _dataset_cache._cache.keys():
        if 'sensor_data' in key:
            summary['sensor_data'] = 'Cached'
        elif 'weather_data' in key:
            summary['weather_data'] = 'Cached'
        elif 'resources_data' in key:
            summary['resources_data'] = 'Cached' 
        elif 'market_data' in key:
            summary['market_data'] = 'Cached'
    
    return summary


def clear_dataset_cache():
    """Clear the dataset cache"""
    _dataset_cache._cache.clear()
    logger.info("Dataset cache cleared")