"""
AgriMind: Prediction Agent
Buys and analyzes sensor data to predict irrigation needs, weather patterns,
pest outbreaks, and harvest timing using simple ML models and rules.

Features:
- Data purchasing from sensor agents
- Simple ML models for predictions
- Rule-based fallback for degraded mode
- Prediction sharing with other agents
"""

import asyncio
import random
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle
import pandas as pd

from .base_agent import BaseAgent, AgentType, MessageType, Message
from data_loaders import load_weather_data, DataSourceInfo


@dataclass
class Prediction:
    """Represents a prediction made by the agent"""
    prediction_type: str
    value: float
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    valid_until: datetime
    metadata: Dict[str, Any]
    source_data: List[str]  # IDs of data sources used


class PredictionAgent(BaseAgent):
    """
    Prediction Agent that purchases sensor data and generates predictions
    for irrigation, weather, pest outbreaks, and harvest timing
    """
    
    def __init__(
        self, 
        agent_id: str,
        crop_type: str = "tomatoes",
        prediction_config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id, AgentType.PREDICTION)
        
        self.crop_type = crop_type
        self.prediction_config = prediction_config or self._default_prediction_config()
        
        # Data storage
        self.purchased_data: Dict[str, List[Dict[str, Any]]] = {}
        self.predictions: Dict[str, List[Prediction]] = {}
        
        # ML models (simple ones for demo)
        self.models = {}
        self.scalers = {}
        
        # Pricing for predictions
        self.prediction_prices = {
            "irrigation_need": 2.0,
            "weather_forecast": 1.5,
            "pest_risk": 3.0,
            "harvest_timing": 5.0
        }
        
        # Subscribe to messages
        self.subscribe(MessageType.DATA_OFFER, self._handle_data_offer)
        self.subscribe(MessageType.DATA_RESPONSE, self._handle_data_response)
        self.subscribe(MessageType.PREDICTION, self._handle_prediction_request)
        
        self.logger.info(f"Prediction agent initialized for crop: {crop_type}")

    async def _load_weather_from_dataset(self, location: str = None) -> Tuple[Optional[pd.DataFrame], DataSourceInfo]:
        """Load weather data from official dataset as fallback for degraded mode"""
        try:
            weather_df, source_info = load_weather_data(
                location_filter=location,
                days_back=30  # Last 30 days for historical patterns
            )
            
            if not weather_df.empty and source_info.source_type == "dataset":
                self.logger.info(f"🌤️ Loaded weather dataset: {source_info.source_name} ({len(weather_df)} records)")
                return weather_df, source_info
            else:
                self.logger.warning(f"Weather dataset load failed: {source_info.source_type}")
                return None, source_info
                
        except Exception as e:
            self.logger.error(f"Error loading weather dataset: {e}")
            error_source = DataSourceInfo(
                source_type="error",
                source_name="weather_dataset_error",
                timestamp=datetime.now(),
                record_count=0,
                confidence=0.0
            )
            return None, error_source

    def _default_prediction_config(self) -> Dict[str, Any]:
        """Default prediction configuration"""
        return {
            "irrigation_need": {
                "enabled": True,
                "update_interval": 1800,  # 30 minutes
                "data_sources": ["soil_moisture", "temperature", "humidity"],
                "min_data_points": 5,
                "confidence_threshold": 0.6
            },
            "weather_forecast": {
                "enabled": True,
                "update_interval": 3600,  # 1 hour
                "data_sources": ["temperature", "humidity"],
                "forecast_hours": 24,
                "confidence_threshold": 0.5
            },
            "pest_risk": {
                "enabled": True,
                "update_interval": 7200,  # 2 hours
                "data_sources": ["temperature", "humidity", "pest_detection"],
                "risk_factors": ["aphids", "spider_mites", "whiteflies"],
                "confidence_threshold": 0.7
            },
            "harvest_timing": {
                "enabled": True,
                "update_interval": 86400,  # 24 hours
                "data_sources": ["temperature", "soil_moisture"],
                "crop_cycle_days": 90,
                "confidence_threshold": 0.8
            }
        }

    async def purchase_data(self, sensor_type: str, count: int = 5) -> bool:
        """Purchase data from sensor agents"""
        try:
            # Send data request to all sensor agents (broadcast)
            request_data = {
                "sensor_type": sensor_type,
                "count": count,
                "max_price_per_unit": self._get_max_price_for_data(sensor_type)
            }
            
            await self.send_message(
                receiver_id="broadcast",
                message_type=MessageType.DATA_REQUEST,
                data=request_data
            )
            
            self.logger.info(f"Requested {count} {sensor_type} readings")
            return True
            
        except Exception as e:
            self.logger.error(f"Error purchasing {sensor_type} data: {e}")
            return False

    def _get_max_price_for_data(self, sensor_type: str) -> float:
        """Get maximum price willing to pay for sensor data"""
        price_limits = {
            "soil_moisture": 0.60,
            "temperature": 0.40,
            "humidity": 0.40,
            "pest_detection": 1.50
        }
        return price_limits.get(sensor_type, 1.0)

    async def _handle_data_offer(self, message: Message):
        """Handle data offers from sensor agents"""
        offer_data = message.data
        sensor_type = offer_data.get("sensor_type")
        price = offer_data.get("price_per_reading")
        max_price = self._get_max_price_for_data(sensor_type)
        
        # Check if we need this type of data
        needed = self._data_needed_for_predictions(sensor_type)
        
        if needed and price <= max_price:
            # Purchase the data
            await self.purchase_data(sensor_type, count=3)

    async def _handle_data_response(self, message: Message):
        """Handle data purchase responses"""
        response_data = message.data
        
        if response_data.get("status") == "approved":
            sensor_data = response_data.get("data", [])
            transaction_id = response_data.get("transaction_id")
            
            # Process and store the purchased data
            for reading in sensor_data:
                sensor_type = reading["sensor_type"]
                
                if sensor_type not in self.purchased_data:
                    self.purchased_data[sensor_type] = []
                
                self.purchased_data[sensor_type].append({
                    "value": reading["value"],
                    "timestamp": datetime.fromisoformat(reading["timestamp"]),
                    "quality": reading["quality"],
                    "source": reading["source"],
                    "transaction_id": transaction_id
                })
            
            # Complete the transaction
            await self.complete_transaction(transaction_id)
            
            # Cache the data for degraded mode
            await self.cache_data(f"purchased_{sensor_type}", sensor_data)
            
            self.logger.info(
                f"Purchased {len(sensor_data)} readings for ${response_data.get('total_price', 0):.2f}"
            )
            
            # Update predictions with new data
            await self.update_predictions()

    def _data_needed_for_predictions(self, sensor_type: str) -> bool:
        """Check if we need more data of this type for predictions"""
        for pred_type, config in self.prediction_config.items():
            if not config.get("enabled", True):
                continue
                
            if sensor_type in config.get("data_sources", []):
                # Check if we have enough recent data
                recent_data = self._get_recent_data(sensor_type, hours=2)
                min_points = config.get("min_data_points", 3)
                
                if len(recent_data) < min_points:
                    return True
        
        return False

    def _get_recent_data(self, sensor_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent data for a sensor type"""
        if sensor_type not in self.purchased_data:
            return []
        
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            data for data in self.purchased_data[sensor_type]
            if data["timestamp"] > cutoff
        ]

    async def update_predictions(self):
        """Update all enabled predictions with available data"""
        for pred_type, config in self.prediction_config.items():
            if not config.get("enabled", True):
                continue
            
            try:
                prediction = await self._generate_prediction(pred_type, config)
                if prediction:
                    # Store prediction
                    if pred_type not in self.predictions:
                        self.predictions[pred_type] = []
                    
                    self.predictions[pred_type].append(prediction)
                    
                    # Keep only recent predictions
                    cutoff = datetime.now() - timedelta(hours=48)
                    self.predictions[pred_type] = [
                        p for p in self.predictions[pred_type]
                        if p.timestamp > cutoff
                    ]
                    
                    # Cache prediction for degraded mode
                    await self.cache_data(f"prediction_{pred_type}", prediction)
                    
                    self.logger.info(
                        f"Generated {pred_type} prediction: {prediction.value:.2f} "
                        f"(confidence: {prediction.confidence:.2f})"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error generating {pred_type} prediction: {e}")

    async def _generate_prediction(self, pred_type: str, config: Dict[str, Any]) -> Optional[Prediction]:
        """Generate a specific type of prediction"""
        if not self.online:
            return await self._generate_degraded_prediction(pred_type, config)
        
        data_sources = config.get("data_sources", [])
        
        # Collect data from all sources
        feature_data = []
        timestamps = []
        
        for sensor_type in data_sources:
            recent_data = self._get_recent_data(sensor_type, hours=24)
            if not recent_data:
                continue
                
            for data_point in recent_data:
                feature_data.append([
                    data_point["value"],
                    data_point["quality"],
                    data_point["timestamp"].hour,  # Time of day feature
                    data_point["timestamp"].weekday()  # Day of week feature
                ])
                timestamps.append(data_point["timestamp"])
        
        if len(feature_data) < config.get("min_data_points", 3):
            self.logger.warning(f"Insufficient data for {pred_type} prediction")
            return await self._generate_rule_based_prediction(pred_type, config)
        
        # Generate prediction based on type
        if pred_type == "irrigation_need":
            return await self._predict_irrigation_need(feature_data, timestamps, config)
        elif pred_type == "weather_forecast":
            return await self._predict_weather(feature_data, timestamps, config)
        elif pred_type == "pest_risk":
            return await self._predict_pest_risk(feature_data, timestamps, config)
        elif pred_type == "harvest_timing":
            return await self._predict_harvest_timing(feature_data, timestamps, config)
        
        return None

    async def _predict_irrigation_need(self, feature_data: List[List[float]], 
                                     timestamps: List[datetime], 
                                     config: Dict[str, Any]) -> Prediction:
        """Predict irrigation needs based on soil moisture and weather data from multiple API sources"""
        try:
            if not feature_data:
                raise ValueError("No feature data available")
            
            # Get latest data from various API sources
            soil_moisture_data = self._get_recent_data("soil_moisture", hours=2)
            temperature_data = self._get_recent_data("temperature", hours=2)
            humidity_data = self._get_recent_data("humidity", hours=2)
            
            # Analyze data source quality and adjust confidence
            data_source_quality = self._analyze_data_source_quality([
                soil_moisture_data, temperature_data, humidity_data
            ])
            
            if not soil_moisture_data:
                # Use rule-based fallback
                irrigation_need = 0.7
                confidence = 0.3
                reasoning = "No soil moisture data - using conservative estimate"
            else:
                latest_moisture = soil_moisture_data[-1]["value"]
                soil_source = soil_moisture_data[-1].get("source", "unknown")
                
                # Enhanced irrigation logic based on data source
                base_confidence = self._get_source_confidence(soil_source)
                
                if latest_moisture < 0.25:
                    irrigation_need = 0.95  # Critical need
                    confidence = base_confidence * 0.9
                    reasoning = f"Critical soil moisture ({latest_moisture:.2f}) from {soil_source}"
                elif latest_moisture < 0.35:
                    irrigation_need = 0.8   # High need
                    confidence = base_confidence * 0.85
                    reasoning = f"Low soil moisture ({latest_moisture:.2f}) from {soil_source}"
                elif latest_moisture < 0.5:
                    irrigation_need = 0.55  # Medium need
                    confidence = base_confidence * 0.8
                    reasoning = f"Moderate soil moisture ({latest_moisture:.2f}) from {soil_source}"
                else:
                    irrigation_need = 0.25  # Low need
                    confidence = base_confidence * 0.75
                    reasoning = f"Adequate soil moisture ({latest_moisture:.2f}) from {soil_source}"
                
                # Temperature adjustment with source tracking
                if temperature_data:
                    latest_temp = temperature_data[-1]["value"]
                    temp_source = temperature_data[-1].get("source", "unknown")
                    
                    if latest_temp > 32:  # Very hot
                        irrigation_need = min(1.0, irrigation_need + 0.25)
                        reasoning += f", very hot ({latest_temp:.1f}°C from {temp_source})"
                    elif latest_temp > 28:  # Hot
                        irrigation_need = min(1.0, irrigation_need + 0.15)
                        reasoning += f", hot ({latest_temp:.1f}°C from {temp_source})"
                    
                    # Adjust confidence based on weather data source
                    temp_confidence = self._get_source_confidence(temp_source)
                    confidence = (confidence + temp_confidence) / 2
                
                # Humidity factor
                if humidity_data:
                    latest_humidity = humidity_data[-1]["value"]
                    humidity_source = humidity_data[-1].get("source", "unknown")
                    
                    if latest_humidity < 40:  # Low humidity increases evaporation
                        irrigation_need = min(1.0, irrigation_need + 0.1)
                        reasoning += f", low humidity ({latest_humidity:.0f}% from {humidity_source})"
            
            return Prediction(
                prediction_type="irrigation_need",
                value=irrigation_need,
                confidence=min(1.0, confidence * data_source_quality),
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=6),
                metadata={
                    "crop_type": self.crop_type,
                    "reasoning": reasoning,
                    "data_sources_used": self._get_data_sources_summary([soil_moisture_data, temperature_data, humidity_data]),
                    "source_quality_score": data_source_quality,
                    "soil_moisture_threshold": 0.25
                },
                source_data=[d.get("transaction_id", "") for d in (soil_moisture_data + temperature_data)[-5:] if d.get("transaction_id")]
            )
            
        except Exception as e:
            self.logger.error(f"Error in irrigation prediction: {e}")
            return await self._generate_rule_based_prediction("irrigation_need", config)

    async def _predict_weather(self, feature_data: List[List[float]], 
                              timestamps: List[datetime], 
                              config: Dict[str, Any]) -> Prediction:
        """Predict weather patterns"""
        try:
            # Simple weather prediction based on recent trends
            temp_data = self._get_recent_data("temperature", hours=12)
            humidity_data = self._get_recent_data("humidity", hours=12)
            
            if len(temp_data) < 2:
                # Fallback to average
                predicted_temp = 22.0
                confidence = 0.4
            else:
                # Simple trend analysis
                temps = [d["value"] for d in temp_data[-5:]]
                trend = (temps[-1] - temps[0]) / len(temps)
                predicted_temp = temps[-1] + trend * 6  # Predict 6 hours ahead
                confidence = 0.6
            
            return Prediction(
                prediction_type="weather_forecast",
                value=predicted_temp,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=config.get("forecast_hours", 24)),
                metadata={
                    "forecast_type": "temperature",
                    "trend_analysis": "simple_linear",
                    "forecast_hours": config.get("forecast_hours", 24)
                },
                source_data=[d.get("transaction_id", "") for d in temp_data[-3:]]
            )
            
        except Exception as e:
            self.logger.error(f"Error in weather prediction: {e}")
            return await self._generate_rule_based_prediction("weather_forecast", config)

    async def _predict_pest_risk(self, feature_data: List[List[float]], 
                                timestamps: List[datetime], 
                                config: Dict[str, Any]) -> Prediction:
        """Predict pest outbreak risk"""
        try:
            # Get pest detection and environmental data
            pest_data = self._get_recent_data("pest_detection", hours=24)
            temp_data = self._get_recent_data("temperature", hours=24)
            humidity_data = self._get_recent_data("humidity", hours=24)
            
            risk_score = 0.0
            confidence = 0.5
            
            # Factor 1: Direct pest detections
            if pest_data:
                recent_detections = [d["value"] for d in pest_data]
                avg_detection = sum(recent_detections) / len(recent_detections)
                risk_score += avg_detection * 0.6
                confidence += 0.2
            
            # Factor 2: Environmental conditions favorable for pests
            if temp_data and humidity_data:
                avg_temp = sum(d["value"] for d in temp_data[-5:]) / min(5, len(temp_data))
                avg_humidity = sum(d["value"] for d in humidity_data[-5:]) / min(5, len(humidity_data))
                
                # Conditions favorable for many common pests
                if 20 <= avg_temp <= 30 and avg_humidity > 60:
                    risk_score += 0.3
                    confidence += 0.1
            
            risk_score = min(1.0, risk_score)
            confidence = min(1.0, confidence)
            
            return Prediction(
                prediction_type="pest_risk",
                value=risk_score,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=12),
                metadata={
                    "risk_factors": config.get("risk_factors", []),
                    "environmental_factors": "temperature_humidity",
                    "detection_weight": 0.6
                },
                source_data=list(set(
                    [d.get("transaction_id", "") for d in pest_data[-3:]] +
                    [d.get("transaction_id", "") for d in temp_data[-3:]]
                ))
            )
            
        except Exception as e:
            self.logger.error(f"Error in pest risk prediction: {e}")
            return await self._generate_rule_based_prediction("pest_risk", config)

    async def _predict_harvest_timing(self, feature_data: List[List[float]], 
                                     timestamps: List[datetime], 
                                     config: Dict[str, Any]) -> Prediction:
        """Predict optimal harvest timing"""
        try:
            # Simple growing degree day (GDD) calculation
            temp_data = self._get_recent_data("temperature", hours=168)  # 7 days
            
            if not temp_data:
                # Use default crop cycle
                days_to_harvest = config.get("crop_cycle_days", 90)
                confidence = 0.3
            else:
                # Calculate GDD accumulation rate
                avg_temp = sum(d["value"] for d in temp_data) / len(temp_data)
                base_temp = 10  # Base temperature for most crops
                
                if avg_temp > base_temp:
                    gdd_per_day = avg_temp - base_temp
                    target_gdd = 1500  # Target GDD for tomatoes
                    days_to_harvest = max(10, target_gdd / gdd_per_day)
                    confidence = 0.7
                else:
                    days_to_harvest = config.get("crop_cycle_days", 90)
                    confidence = 0.4
            
            return Prediction(
                prediction_type="harvest_timing",
                value=days_to_harvest,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(days=7),
                metadata={
                    "crop_type": self.crop_type,
                    "method": "growing_degree_days",
                    "base_temperature": 10,
                    "target_gdd": 1500
                },
                source_data=[d.get("transaction_id", "") for d in temp_data[-7:]]
            )
            
        except Exception as e:
            self.logger.error(f"Error in harvest timing prediction: {e}")
            return await self._generate_rule_based_prediction("harvest_timing", config)

    async def _generate_rule_based_prediction(self, pred_type: str, 
                                            config: Dict[str, Any]) -> Prediction:
        """Generate simple rule-based predictions as fallback"""
        self.logger.info(f"Using rule-based fallback for {pred_type}")
        
        if pred_type == "irrigation_need":
            # Conservative irrigation recommendation
            return Prediction(
                prediction_type="irrigation_need",
                value=0.6,
                confidence=0.4,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=4),
                metadata={"method": "rule_based", "note": "check_soil_manually"},
                source_data=[]
            )
        elif pred_type == "weather_forecast":
            # Use seasonal average
            return Prediction(
                prediction_type="weather_forecast",
                value=20.0,
                confidence=0.3,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=12),
                metadata={"method": "seasonal_average"},
                source_data=[]
            )
        elif pred_type == "pest_risk":
            # Low risk unless evidence suggests otherwise
            return Prediction(
                prediction_type="pest_risk",
                value=0.3,
                confidence=0.5,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=8),
                metadata={"method": "conservative_estimate"},
                source_data=[]
            )
        elif pred_type == "harvest_timing":
            # Use crop cycle default
            return Prediction(
                prediction_type="harvest_timing",
                value=config.get("crop_cycle_days", 90),
                confidence=0.4,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(days=7),
                metadata={"method": "crop_cycle_default"},
                source_data=[]
            )
        
        return None

    async def _generate_degraded_prediction(self, pred_type: str, 
                                          config: Dict[str, Any]) -> Optional[Prediction]:
        """Generate predictions in degraded mode using weather dataset and cached data"""
        data_sources_used = []
        
        # Try to get cached prediction first
        cached_prediction = await self.get_cached_data(f"prediction_{pred_type}", max_age_hours=6)
        if cached_prediction:
            cached_prediction.confidence *= 0.7  # Reduce confidence for cached data
            cached_prediction.timestamp = datetime.now()
            data_sources_used.append("cached prediction")
        
        # Try to use weather dataset for weather-related predictions
        weather_df, weather_source = None, None
        if pred_type in ["weather_forecast", "irrigation_need", "pest_risk"]:
            weather_df, weather_source = await self._load_weather_from_dataset()
            if weather_df is not None and not weather_df.empty:
                data_sources_used.append(f"weather dataset ({weather_source.source_name})")
                
                try:
                    # Use weather dataset for enhanced degraded predictions
                    if pred_type == "weather_forecast":
                        return await self._predict_weather_from_dataset(weather_df, config, weather_source)
                    elif pred_type == "irrigation_need":
                        return await self._predict_irrigation_from_dataset(weather_df, config, weather_source)
                    elif pred_type == "pest_risk":
                        return await self._predict_pest_risk_from_dataset(weather_df, config, weather_source)
                        
                except Exception as e:
                    self.logger.error(f"Error using weather dataset for {pred_type}: {e}")
        
        # Log data sources used in degraded mode
        if data_sources_used:
            self.logger.info(f"🔄 PredictionAgent degraded mode for {pred_type} using: {', '.join(data_sources_used)}")
        
        # Return cached prediction if available
        if cached_prediction:
            return cached_prediction
        
        # Fall back to rule-based prediction
        rule_prediction = await self._generate_rule_based_prediction(pred_type, config)
        if rule_prediction:
            self.logger.info(f"🔄 PredictionAgent using rule-based fallback for {pred_type}")
        return rule_prediction

    async def _predict_weather_from_dataset(self, weather_df: pd.DataFrame, 
                                          config: Dict[str, Any], 
                                          source_info: DataSourceInfo) -> Prediction:
        """Predict weather using historical dataset patterns"""
        try:
            # Use recent weather patterns to forecast
            latest_records = weather_df.tail(7)  # Last week's data
            
            if 'temperature' in weather_df.columns:
                avg_temp = latest_records['temperature'].mean()
                temp_trend = latest_records['temperature'].diff().mean()
                forecast_temp = avg_temp + (temp_trend * 2)  # 2-day trend extrapolation
            else:
                forecast_temp = 20.0  # Default
            
            confidence = min(0.8, source_info.confidence * 0.9)  # Slightly lower for forecasting
            
            return Prediction(
                prediction_type="weather_forecast",
                value=forecast_temp,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=12),
                metadata={
                    "method": "dataset_trend_analysis",
                    "dataset_source": source_info.source_name,
                    "dataset_records": len(latest_records),
                    "reasoning": f"Trend-based forecast from {len(latest_records)} historical records"
                },
                source_data=[f"dataset_{source_info.source_name}"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in dataset weather prediction: {e}")
            return await self._generate_rule_based_prediction("weather_forecast", config)

    async def _predict_irrigation_from_dataset(self, weather_df: pd.DataFrame, 
                                             config: Dict[str, Any], 
                                             source_info: DataSourceInfo) -> Prediction:
        """Predict irrigation needs using weather dataset"""
        try:
            # Analyze recent weather patterns for irrigation needs
            recent_data = weather_df.tail(5)  # Last 5 records
            
            # Temperature factor
            if 'temperature' in weather_df.columns:
                avg_temp = recent_data['temperature'].mean()
                if avg_temp > 30:
                    temp_factor = 0.4  # High irrigation need
                elif avg_temp > 25:
                    temp_factor = 0.25
                elif avg_temp > 20:
                    temp_factor = 0.15
                else:
                    temp_factor = 0.05
            else:
                temp_factor = 0.2
            
            # Humidity factor
            if 'humidity' in weather_df.columns:
                avg_humidity = recent_data['humidity'].mean()
                if avg_humidity < 40:
                    humidity_factor = 0.3  # Low humidity increases need
                elif avg_humidity < 60:
                    humidity_factor = 0.15
                else:
                    humidity_factor = 0.05
            else:
                humidity_factor = 0.1
            
            # Precipitation factor (if available)
            precip_factor = 0.0
            if 'precipitation' in weather_df.columns:
                recent_precip = recent_data['precipitation'].sum()
                if recent_precip < 5:  # Less than 5mm in recent period
                    precip_factor = 0.25
                elif recent_precip < 15:
                    precip_factor = 0.1
            
            # Combine factors
            irrigation_need = min(1.0, temp_factor + humidity_factor + precip_factor + 0.2)  # Base need
            confidence = min(0.85, source_info.confidence * 0.95)
            
            reasoning = f"Dataset analysis: temp={avg_temp:.1f}°C" if 'temperature' in weather_df.columns else "Dataset analysis"
            if 'humidity' in weather_df.columns:
                reasoning += f", humidity={avg_humidity:.0f}%"
            
            return Prediction(
                prediction_type="irrigation_need",
                value=irrigation_need,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=6),
                metadata={
                    "method": "dataset_weather_analysis",
                    "dataset_source": source_info.source_name,
                    "dataset_records": len(recent_data),
                    "reasoning": reasoning,
                    "temperature_factor": temp_factor,
                    "humidity_factor": humidity_factor
                },
                source_data=[f"dataset_{source_info.source_name}"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in dataset irrigation prediction: {e}")
            return await self._generate_rule_based_prediction("irrigation_need", config)

    async def _predict_pest_risk_from_dataset(self, weather_df: pd.DataFrame, 
                                            config: Dict[str, Any], 
                                            source_info: DataSourceInfo) -> Prediction:
        """Predict pest risk using weather dataset patterns"""
        try:
            # Analyze weather conditions favorable to pests
            recent_data = weather_df.tail(7)  # Last week
            
            risk_factors = []
            pest_risk = 0.2  # Base risk
            
            # Temperature-based risk (many pests thrive in warm weather)
            if 'temperature' in weather_df.columns:
                avg_temp = recent_data['temperature'].mean()
                if 25 <= avg_temp <= 35:  # Optimal pest temperature range
                    pest_risk += 0.3
                    risk_factors.append(f"favorable temp ({avg_temp:.1f}°C)")
                elif avg_temp > 35:
                    pest_risk += 0.1  # Too hot for some pests
                    risk_factors.append(f"hot temp ({avg_temp:.1f}°C)")
            
            # Humidity-based risk
            if 'humidity' in weather_df.columns:
                avg_humidity = recent_data['humidity'].mean()
                if avg_humidity > 70:  # High humidity favors many pests
                    pest_risk += 0.25
                    risk_factors.append(f"high humidity ({avg_humidity:.0f}%)")
                elif 50 <= avg_humidity <= 70:
                    pest_risk += 0.1
                    risk_factors.append(f"moderate humidity ({avg_humidity:.0f}%)")
            
            # Seasonal factor (basic)
            current_month = datetime.now().month
            if 6 <= current_month <= 8:  # Summer months
                pest_risk += 0.15
                risk_factors.append("summer season")
            
            pest_risk = min(1.0, pest_risk)
            confidence = min(0.75, source_info.confidence * 0.85)  # Lower confidence for pest prediction
            
            reasoning = "Weather analysis: " + ", ".join(risk_factors) if risk_factors else "Low risk conditions"
            
            return Prediction(
                prediction_type="pest_risk",
                value=pest_risk,
                confidence=confidence,
                timestamp=datetime.now(),
                valid_until=datetime.now() + timedelta(hours=8),
                metadata={
                    "method": "dataset_weather_pest_analysis",
                    "dataset_source": source_info.source_name,
                    "dataset_records": len(recent_data),
                    "reasoning": reasoning,
                    "risk_factors": risk_factors
                },
                source_data=[f"dataset_{source_info.source_name}"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in dataset pest risk prediction: {e}")
            return await self._generate_rule_based_prediction("pest_risk", config)

    async def _handle_prediction_request(self, message: Message):
        """Handle requests for predictions from other agents"""
        request_data = message.data
        pred_type = request_data.get("prediction_type")
        requester_id = message.sender_id
        
        if pred_type not in self.predictions:
            await self.send_message(
                receiver_id=requester_id,
                message_type=MessageType.PREDICTION,
                data={
                    "status": "not_available",
                    "prediction_type": pred_type
                }
            )
            return
        
        recent_predictions = [
            p for p in self.predictions[pred_type]
            if (datetime.now() - p.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        if not recent_predictions:
            await self.send_message(
                receiver_id=requester_id,
                message_type=MessageType.PREDICTION,
                data={
                    "status": "stale",
                    "prediction_type": pred_type
                }
            )
            return
        
        # Get the most recent prediction
        latest_prediction = max(recent_predictions, key=lambda p: p.timestamp)
        
        # Create transaction for prediction
        price = self.prediction_prices.get(pred_type, 2.0)
        transaction_id = await self.create_transaction(
            buyer_id=requester_id,
            seller_id=self.agent_id,
            item_type=f"{pred_type}_prediction",
            quantity=1,
            price=price
        )
        
        # Send prediction
        prediction_dict = asdict(latest_prediction)
        prediction_dict["timestamp"] = latest_prediction.timestamp.isoformat()
        prediction_dict["valid_until"] = latest_prediction.valid_until.isoformat()
        
        await self.send_message(
            receiver_id=requester_id,
            message_type=MessageType.PREDICTION,
            data={
                "status": "success",
                "prediction": prediction_dict,
                "transaction_id": transaction_id,
                "price": price
            }
        )
        
        self.logger.info(f"Shared {pred_type} prediction with {requester_id}")

    async def main_loop(self):
        """Main prediction agent logic"""
        # Update predictions every 30 minutes
        if not hasattr(self, '_last_update') or \
           (datetime.now() - self._last_update).seconds > 1800:
            
            await self.update_predictions()
            self._last_update = datetime.now()
        
        # Purchase data if needed
        await self._check_data_needs()

    async def _check_data_needs(self):
        """Check if we need to purchase more data"""
        for pred_type, config in self.prediction_config.items():
            if not config.get("enabled", True):
                continue
            
            data_sources = config.get("data_sources", [])
            min_points = config.get("min_data_points", 5)
            
            for sensor_type in data_sources:
                recent_data = self._get_recent_data(sensor_type, hours=4)
                if len(recent_data) < min_points:
                    await self.purchase_data(sensor_type, count=min_points)

    def _get_source_confidence(self, source: str) -> float:
        """Get confidence multiplier based on data source quality"""
        source_confidence_map = {
            # Weather API sources (highest to lowest quality)
            "weatherapi_com": 0.95,
            "openweathermap": 0.90,
            "stormglass": 0.88,
            
            # Soil/Agricultural sources
            "agromonitoring_satellite": 0.95,
            "agro_api": 0.90,
            
            # Simulation/fallback sources
            "mock_sensor": 0.75,
            "soil_simulation": 0.70,
            "rule_based": 0.40,
            
            # Cached sources (reduced quality)
            "weatherapi_com_cached": 0.80,
            "openweathermap_cached": 0.75,
            "soil_simulation_cached": 0.60,
        }
        
        return source_confidence_map.get(source.lower(), 0.50)
    
    def _analyze_data_source_quality(self, data_groups: List[List[Dict]]) -> float:
        """Analyze overall data source quality from multiple data types"""
        quality_scores = []
        
        for data_group in data_groups:
            if not data_group:
                continue
                
            # Get most recent data point
            latest_data = data_group[-1]
            source = latest_data.get("source", "unknown")
            data_age_hours = (datetime.now() - latest_data["timestamp"]).total_seconds() / 3600
            
            # Base quality from source
            base_quality = self._get_source_confidence(source)
            
            # Age penalty (data gets less reliable over time)
            if data_age_hours < 1:
                age_factor = 1.0
            elif data_age_hours < 6:
                age_factor = 0.95
            elif data_age_hours < 24:
                age_factor = 0.85
            else:
                age_factor = 0.70
            
            # Data source quality penalty
            if "cached" in source:
                source_factor = 0.8
            elif "simulation" in source or "mock" in source:
                source_factor = 0.7
            elif "rule_based" in source:
                source_factor = 0.4
            else:
                source_factor = 1.0
            
            final_quality = base_quality * age_factor * source_factor
            quality_scores.append(final_quality)
        
        if not quality_scores:
            return 0.3  # Very low confidence with no data
        
        # Return weighted average (more data sources = higher confidence)
        return sum(quality_scores) / len(quality_scores) * min(1.0, len(quality_scores) / 3)
    
    def _get_data_sources_summary(self, data_groups: List[List[Dict]]) -> Dict[str, Any]:
        """Get summary of data sources used in prediction"""
        sources_used = set()
        api_providers = set()
        total_data_points = 0
        
        for data_group in data_groups:
            if not data_group:
                continue
                
            total_data_points += len(data_group)
            
            for data_point in data_group:
                source = data_point.get("source", "unknown")
                sources_used.add(source)
                
                # Extract API provider
                if "weatherapi" in source:
                    api_providers.add("WeatherAPI.com")
                elif "openweather" in source:
                    api_providers.add("OpenWeatherMap")
                elif "stormglass" in source:
                    api_providers.add("StormGlass")
                elif "agromonitoring" in source:
                    api_providers.add("AgroMonitoring")
                elif "simulation" in source or "mock" in source:
                    api_providers.add("Simulation")
                elif "rule_based" in source:
                    api_providers.add("Rule-based")
        
        return {
            "sources": list(sources_used),
            "api_providers": list(api_providers),
            "total_data_points": total_data_points,
            "provider_diversity": len(api_providers)
        }

    def get_prediction_status(self) -> Dict[str, Any]:
        """Get current prediction status with enhanced API source tracking"""
        status = self.get_status()
        
        prediction_summary = {}
        for pred_type, predictions in self.predictions.items():
            if predictions:
                latest = predictions[-1]
                prediction_summary[pred_type] = {
                    "latest_value": latest.value,
                    "confidence": latest.confidence,
                    "timestamp": latest.timestamp.isoformat(),
                    "valid_until": latest.valid_until.isoformat(),
                    "predictions_count": len(predictions),
                    "data_sources": latest.metadata.get("data_sources_used", {}),
                    "reasoning": latest.metadata.get("reasoning", "")
                }
        
        data_summary = {}
        api_provider_usage = {}
        
        for sensor_type, data in self.purchased_data.items():
            if data:
                # Analyze API provider usage
                provider_counts = {}
                for data_point in data:
                    source = data_point.get("source", "unknown")
                    if "weatherapi" in source:
                        provider = "WeatherAPI.com"
                    elif "openweather" in source:
                        provider = "OpenWeatherMap"
                    elif "stormglass" in source:
                        provider = "StormGlass"
                    elif "agromonitoring" in source:
                        provider = "AgroMonitoring"
                    else:
                        provider = "Simulation/Mock"
                    
                    provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
                api_provider_usage[sensor_type] = provider_counts
                
                data_summary[sensor_type] = {
                    "data_points": len(data),
                    "latest_timestamp": max(d["timestamp"] for d in data).isoformat(),
                    "provider_usage": provider_counts
                }
        
        status.update({
            "crop_type": self.crop_type,
            "predictions": prediction_summary,
            "purchased_data": data_summary,
            "api_provider_usage": api_provider_usage,
            "prediction_prices": self.prediction_prices
        })
        
        return status


# Helper function to create prediction agent
def create_prediction_agent(
    agent_id: str,
    crop_type: str = "tomatoes"
) -> PredictionAgent:
    """Factory function to create a prediction agent"""
    return PredictionAgent(agent_id, crop_type)