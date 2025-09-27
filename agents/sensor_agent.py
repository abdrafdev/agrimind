"""
AgriMind: Sensor Agent
Collects environmental data (soil moisture, temperature, humidity, pest detection)
and shares/sells this data with other agents in the network.

Features:
- Mock data collection with realistic patterns
- API integration for weather services (with fallback)
- Data selling/sharing marketplace
- Degraded mode operation with cached data
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentType, MessageType, Message
from data_loaders import load_sensor_data, DataSourceInfo


@dataclass
class SensorReading:
    """Represents a sensor reading"""
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime
    location: str
    quality: float  # 0.0 to 1.0, indicating data quality
    source: str  # 'api', 'mock', 'cached'


class SensorAgent(BaseAgent):
    """
    Sensor Agent that collects environmental data and makes it available
    to other agents through purchase or subscription
    """
    
    def __init__(
        self, 
        agent_id: str, 
        farm_location: str,
        sensors_config: Optional[Dict[str, Any]] = None,
        api_keys: Optional[Dict[str, str]] = None
    ):
        super().__init__(agent_id, AgentType.SENSOR)
        
        self.farm_location = farm_location
        self.sensors_config = sensors_config or self._default_sensors_config()
        self.api_keys = api_keys or {}
        
        # Data storage
        self.sensor_readings: Dict[str, List[SensorReading]] = {}
        self.data_catalog = {}  # Available data for sale
        
        # Pricing
        self.data_prices = {
            "soil_moisture": 0.50,
            "temperature": 0.30,
            "humidity": 0.30,
            "pest_detection": 1.00,
            "weather_forecast": 0.75
        }
        
        # Subscribe to data requests
        self.subscribe(MessageType.DATA_REQUEST, self._handle_data_request)
        self.subscribe(MessageType.NEGOTIATION, self._handle_negotiation)
        
        self.logger.info(f"Sensor agent initialized for location: {farm_location}")

    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Get the unit for a sensor type"""
        units = {
            "soil_moisture": "percentage",
            "temperature": "celsius",
            "humidity": "percentage",
            "pest_detection": "confidence"
        }
        return units.get(sensor_type, "unknown")

    def _default_sensors_config(self) -> Dict[str, Any]:
        """Default sensor configuration"""
        return {
            "soil_moisture": {
                "enabled": True,
                "update_interval": 300,  # 5 minutes
                "range": [0.1, 0.8],  # Soil moisture range
                "optimal": [0.3, 0.6]
            },
            "temperature": {
                "enabled": True,
                "update_interval": 600,  # 10 minutes
                "range": [5, 45],  # Celsius
                "optimal": [18, 28]
            },
            "humidity": {
                "enabled": True,
                "update_interval": 600,
                "range": [30, 95],  # Percentage
                "optimal": [40, 70]
            },
            "pest_detection": {
                "enabled": True,
                "update_interval": 3600,  # 1 hour
                "confidence_threshold": 0.7
            }
        }

    async def collect_sensor_data(self) -> Dict[str, SensorReading]:
        """Collect data from all enabled sensors with priority: Dataset -> API -> Mock"""
        readings = {}
        data_sources_used = []
        
        # First try to load from official dataset
        try:
            dataset_readings, source_info = load_sensor_data(
                location_filter=self.farm_location,
                date_range=(datetime.now() - timedelta(hours=24), datetime.now())
            )
            
            if dataset_readings and source_info.source_type == "dataset":
                # Use the most recent reading from dataset
                latest_reading = max(dataset_readings, key=lambda x: x['date'])
                
                # Convert dataset format to SensorReading objects
                for sensor_type in ['soil_moisture', 'temperature', 'humidity']:
                    if sensor_type in latest_reading:
                        reading = SensorReading(
                            sensor_type=sensor_type,
                            value=float(latest_reading[sensor_type]),
                            unit=self._get_sensor_unit(sensor_type),
                            timestamp=latest_reading['date'],
                            location=self.farm_location,
                            quality=0.9,  # High quality for dataset
                            source="dataset"
                        )
                        readings[sensor_type] = reading
                
                # Add pest detection if available
                if 'pest_index' in latest_reading and latest_reading['pest_index'] > 0:
                    pest_reading = SensorReading(
                        sensor_type="pest_detection",
                        value=float(latest_reading['pest_index']),
                        unit="index",
                        timestamp=latest_reading['date'],
                        location=self.farm_location,
                        quality=0.9,
                        source="dataset"
                    )
                    readings["pest_detection"] = pest_reading
                
                data_sources_used.append(f"dataset ({source_info.source_name})")
                self.logger.info(f"📊 Using sensor data from dataset: {source_info.source_name} ({source_info.record_count} records)")
            
        except Exception as e:
            self.logger.warning(f"Could not load sensor dataset: {e}")
        
        # For any missing sensors, try API or mock data
        for sensor_type, config in self.sensors_config.items():
            if not config.get("enabled", True) or sensor_type in readings:
                continue
                
            try:
                reading = None
                
                if self.online:
                    # Try to get real data from APIs
                    reading = await self._collect_from_api(sensor_type)
                    if reading:
                        data_sources_used.append(f"API ({reading.source})")
                
                if reading is None:
                    # Fallback to degraded mode or mock data
                    if not self.online:
                        reading = await self._get_degraded_reading(sensor_type, config)
                        if reading:
                            data_sources_used.append(f"cached ({reading.source})")
                    
                    if reading is None:
                        reading = self._generate_mock_reading(sensor_type, config)
                        data_sources_used.append(f"mock")
                
                readings[sensor_type] = reading
                
            except Exception as e:
                self.logger.error(f"Error collecting {sensor_type} data: {e}")
        
        # Store readings and cache for degraded mode
        for sensor_type, reading in readings.items():
            if sensor_type not in self.sensor_readings:
                self.sensor_readings[sensor_type] = []
            self.sensor_readings[sensor_type].append(reading)
            
            # Keep only recent readings (last 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            self.sensor_readings[sensor_type] = [
                r for r in self.sensor_readings[sensor_type] 
                if r.timestamp > cutoff
            ]
            
            # Cache the reading for degraded mode
            await self.cache_data(f"sensor_{sensor_type}", reading)
        
        # Log data sources used
        if data_sources_used:
            sources_summary = ", ".join(set(data_sources_used))
            self.logger.info(f"📊 SensorAgent {self.agent_id} used data sources: {sources_summary}")
                
        return readings

    async def _collect_from_api(self, sensor_type: str) -> Optional[SensorReading]:
        """Collect data from external APIs"""
        if sensor_type in ["temperature", "humidity"] and "weather_api_key" in self.api_keys:
            return await self._get_weather_data(sensor_type)
        elif sensor_type == "soil_moisture" and "agro_api_key" in self.api_keys:
            return await self._get_soil_data()
        
        return None

    async def _get_weather_data(self, sensor_type: str) -> Optional[SensorReading]:
        """Get weather data from multiple providers with fallback chain"""
        # Try providers in order of preference
        providers = [
            {"name": "weatherapi", "func": self._fetch_weatherapi_data},
            {"name": "openweather", "func": self._fetch_openweather_data},
            {"name": "stormglass", "func": self._fetch_stormglass_data}
        ]
        
        for provider in providers:
            try:
                reading = await provider["func"](sensor_type)
                if reading:
                    self.logger.info(f"Weather data from {provider['name']} API")
                    return reading
            except Exception as e:
                self.logger.warning(f"{provider['name']} API failed: {e}")
                continue
        
        self.logger.warning("All weather APIs failed, using fallback")
        return None

    async def _fetch_weatherapi_data(self, sensor_type: str) -> Optional[SensorReading]:
        """Fetch from WeatherAPI.com (primary)"""
        api_key = self.api_keys.get("weather_api_key")
        if not api_key:
            return None
        
        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": self.farm_location,
            "aqi": "no"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data["current"]
            
            if sensor_type == "temperature":
                return SensorReading(
                    sensor_type="temperature",
                    value=current["temp_c"],
                    unit="celsius",
                    timestamp=datetime.now(),
                    location=self.farm_location,
                    quality=0.95,
                    source="weatherapi_com"
                )
            elif sensor_type == "humidity":
                return SensorReading(
                    sensor_type="humidity",
                    value=current["humidity"],
                    unit="percentage",
                    timestamp=datetime.now(),
                    location=self.farm_location,
                    quality=0.95,
                    source="weatherapi_com"
                )
        
        return None

    async def _fetch_openweather_data(self, sensor_type: str) -> Optional[SensorReading]:
        """Fetch from OpenWeatherMap (backup)"""
        api_key = self.api_keys.get("openweather_api_key")
        if not api_key:
            return None
        
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.farm_location,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if sensor_type == "temperature":
                return SensorReading(
                    sensor_type="temperature",
                    value=data["main"]["temp"],
                    unit="celsius",
                    timestamp=datetime.now(),
                    location=self.farm_location,
                    quality=0.90,
                    source="openweathermap"
                )
            elif sensor_type == "humidity":
                return SensorReading(
                    sensor_type="humidity",
                    value=data["main"]["humidity"],
                    unit="percentage",
                    timestamp=datetime.now(),
                    location=self.farm_location,
                    quality=0.90,
                    source="openweathermap"
                )
        
        return None

    async def _fetch_stormglass_data(self, sensor_type: str) -> Optional[SensorReading]:
        """Fetch from StormGlass (backup)"""
        api_key = self.api_keys.get("stormglass_api_key")
        if not api_key:
            return None
        
        # StormGlass requires lat/lng - use coordinates from config
        farm_config = self.config.get('coordinates', [36.7378, -119.7871])  # Default to Fresno
        lat, lng = farm_config[0], farm_config[1]
        
        url = f"https://api.stormglass.io/v2/weather/point"
        params = {
            "lat": lat,
            "lng": lng,
            "params": "airTemperature,humidity"
        }
        headers = {
            "Authorization": api_key
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            hours = data.get("hours", [])
            
            if hours:
                current_hour = hours[0]
                
                if sensor_type == "temperature" and "airTemperature" in current_hour:
                    # StormGlass returns multiple sources, take first available
                    temp_data = current_hour["airTemperature"]
                    temp_value = list(temp_data.values())[0] if temp_data else None
                    
                    if temp_value is not None:
                        return SensorReading(
                            sensor_type="temperature",
                            value=temp_value,
                            unit="celsius",
                            timestamp=datetime.now(),
                            location=self.farm_location,
                            quality=0.88,
                            source="stormglass"
                        )
                
                elif sensor_type == "humidity" and "humidity" in current_hour:
                    humidity_data = current_hour["humidity"]
                    humidity_value = list(humidity_data.values())[0] if humidity_data else None
                    
                    if humidity_value is not None:
                        return SensorReading(
                            sensor_type="humidity",
                            value=humidity_value,
                            unit="percentage",
                            timestamp=datetime.now(),
                            location=self.farm_location,
                            quality=0.88,
                            source="stormglass"
                        )
        
        return None

    async def _get_soil_data(self) -> Optional[SensorReading]:
        """Get soil data from AgroMonitoring API with satellite-based field data"""
        try:
            api_key = self.api_keys.get("agro_api_key")
            if not api_key:
                return None
            
            # For real implementation, polygon would be set up for each farm
            # Using demo polygon ID or create one based on farm coordinates
            polygon_id = self.config.get("agro_polygon_id", "demo_polygon_id")
            
            url = f"http://api.agromonitoring.com/agro/1.0/soil"
            params = {
                "appid": api_key,
                "polyid": polygon_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # AgroMonitoring returns: dt, t10 (temp at 10cm), moisture, t0 (surface temp)
                soil_moisture = data.get("moisture", 0.0)  # m3/m3
                soil_temp_10cm = data.get("t10", 273.15) - 273.15  # Convert Kelvin to Celsius
                surface_temp = data.get("t0", 273.15) - 273.15
                
                self.logger.info(f"AgroMonitoring: moisture={soil_moisture:.3f}, temp_10cm={soil_temp_10cm:.1f}°C")
                
                return SensorReading(
                    sensor_type="soil_moisture",
                    value=soil_moisture,
                    unit="m3/m3",
                    timestamp=datetime.now(),
                    location=self.farm_location,
                    quality=0.95,  # High quality satellite data
                    source="agromonitoring_satellite"
                )
            
            elif response.status_code == 401:
                self.logger.error("AgroMonitoring API: Invalid API key")
            elif response.status_code == 404:
                self.logger.error(f"AgroMonitoring API: Polygon {polygon_id} not found")
            else:
                self.logger.warning(f"AgroMonitoring API returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.logger.warning("AgroMonitoring API timeout")
        except requests.exceptions.ConnectionError:
            self.logger.warning("AgroMonitoring API connection error")
        except Exception as e:
            self.logger.warning(f"AgroMonitoring API error: {e}")
        
        # If real API fails, simulate realistic soil data based on weather and time
        return await self._simulate_soil_data()
    
    async def _simulate_soil_data(self) -> SensorReading:
        """Simulate soil moisture when API is unavailable"""
        # Base simulation on time of day, weather patterns, and irrigation history
        hour = datetime.now().hour
        
        # Base moisture level varies by soil type and recent weather
        base_moisture = 0.35
        
        # Diurnal pattern - moisture decreases during day due to evapotranspiration
        if 6 <= hour <= 18:  # Daylight hours
            diurnal_factor = -0.05 * ((hour - 12) ** 2) / 36  # Peak drying at noon
        else:
            diurnal_factor = 0.02  # Slight recovery at night
        
        # Add some randomness for weather variation
        weather_factor = random.uniform(-0.08, 0.05)
        
        # Simulate recent irrigation effect (would be tracked in real system)
        if hasattr(self, '_last_irrigation_time'):
            hours_since_irrigation = (datetime.now() - self._last_irrigation_time).total_seconds() / 3600
            irrigation_factor = max(0, 0.15 * (1 - hours_since_irrigation / 24))  # Decays over 24 hours
        else:
            irrigation_factor = 0
        
        final_moisture = max(0.1, min(0.8, 
            base_moisture + diurnal_factor + weather_factor + irrigation_factor
        ))
        
        return SensorReading(
            sensor_type="soil_moisture",
            value=final_moisture,
            unit="volumetric",
            timestamp=datetime.now(),
            location=self.farm_location,
            quality=0.75,  # Lower quality for simulated data
            source="soil_simulation"
        )

    def _generate_mock_reading(self, sensor_type: str, config: Dict[str, Any]) -> SensorReading:
        """Generate realistic mock sensor readings"""
        now = datetime.now()
        
        if sensor_type == "soil_moisture":
            # Simulate daily moisture patterns
            base_value = 0.4
            hour_factor = abs(12 - now.hour) / 12  # Drier during midday
            random_factor = random.uniform(-0.1, 0.1)
            value = max(0.1, min(0.8, base_value - hour_factor * 0.2 + random_factor))
            
            return SensorReading(
                sensor_type="soil_moisture",
                value=value,
                unit="volumetric",
                timestamp=now,
                location=self.farm_location,
                quality=0.85,
                source="mock_sensor"
            )
            
        elif sensor_type == "temperature":
            # Simulate daily temperature patterns
            base_temp = 22
            hour_factor = 8 * (1 - abs(14 - now.hour) / 14)  # Peak at 2 PM
            seasonal_factor = random.uniform(-3, 3)
            value = base_temp + hour_factor + seasonal_factor
            
            return SensorReading(
                sensor_type="temperature",
                value=value,
                unit="celsius",
                timestamp=now,
                location=self.farm_location,
                quality=0.85,
                source="mock_sensor"
            )
            
        elif sensor_type == "humidity":
            # Inverse correlation with temperature
            base_humidity = 60
            hour_factor = -10 * (1 - abs(14 - now.hour) / 14)  # Lower at 2 PM
            random_factor = random.uniform(-5, 5)
            value = max(30, min(95, base_humidity + hour_factor + random_factor))
            
            return SensorReading(
                sensor_type="humidity",
                value=value,
                unit="percentage",
                timestamp=now,
                location=self.farm_location,
                quality=0.85,
                source="mock_sensor"
            )
            
        elif sensor_type == "pest_detection":
            # Simulate pest detection with confidence scores
            pest_detected = random.random() < 0.1  # 10% chance of pest detection
            confidence = random.uniform(0.7, 0.95) if pest_detected else random.uniform(0.0, 0.3)
            
            return SensorReading(
                sensor_type="pest_detection",
                value=confidence,
                unit="confidence",
                timestamp=now,
                location=self.farm_location,
                quality=0.80,
                source="mock_ai_vision"
            )
        
        # Default fallback
        return SensorReading(
            sensor_type=sensor_type,
            value=0.0,
            unit="unknown",
            timestamp=now,
            location=self.farm_location,
            quality=0.50,
            source="fallback"
        )

    async def _get_degraded_reading(self, sensor_type: str, config: Dict[str, Any]) -> SensorReading:
        """Get sensor reading in degraded mode using cached data or rules"""
        # Try to get cached data first
        cached_reading = await self.get_cached_data(f"sensor_{sensor_type}", max_age_hours=2)
        if cached_reading:
            # Update timestamp but keep the value
            cached_reading.timestamp = datetime.now()
            cached_reading.source += "_cached"
            cached_reading.quality *= 0.8  # Reduce quality for cached data
            return cached_reading
        
        # Fall back to rule-based generation
        self.logger.warning(f"Using rule-based fallback for {sensor_type}")
        
        if sensor_type == "soil_moisture":
            # Simple rule: if no irrigation in last 12 hours, assume drying
            value = 0.25  # Conservative estimate
        elif sensor_type == "temperature":
            # Use seasonal average
            value = 20.0
        elif sensor_type == "humidity":
            value = 50.0
        else:
            value = 0.0
        
        return SensorReading(
            sensor_type=sensor_type,
            value=value,
            unit="estimated",
            timestamp=datetime.now(),
            location=self.farm_location,
            quality=0.30,
            source="rule_based"
        )

    async def publish_data_availability(self):
        """Publish available data to the marketplace"""
        for sensor_type, readings in self.sensor_readings.items():
            if not readings:
                continue
                
            latest_reading = readings[-1]
            price = self.data_prices.get(sensor_type, 1.0)
            
            # Create data offer
            offer_data = {
                "sensor_type": sensor_type,
                "location": self.farm_location,
                "latest_value": latest_reading.value,
                "quality": latest_reading.quality,
                "price_per_reading": price,
                "readings_available": len(readings),
                "data_age_hours": (datetime.now() - latest_reading.timestamp).total_seconds() / 3600
            }
            
            # Broadcast data offer
            await self.send_message(
                receiver_id="broadcast",
                message_type=MessageType.DATA_OFFER,
                data=offer_data
            )

    async def _handle_data_request(self, message: Message):
        """Handle incoming data requests"""
        request_data = message.data
        sensor_type = request_data.get("sensor_type")
        buyer_id = message.sender_id
        
        if sensor_type not in self.sensor_readings:
            # Send rejection
            await self.send_message(
                receiver_id=buyer_id,
                message_type=MessageType.DATA_RESPONSE,
                data={
                    "status": "rejected",
                    "reason": f"No {sensor_type} data available"
                }
            )
            return
        
        readings = self.sensor_readings[sensor_type]
        if not readings:
            await self.send_message(
                receiver_id=buyer_id,
                message_type=MessageType.DATA_RESPONSE,
                data={
                    "status": "rejected",
                    "reason": f"No recent {sensor_type} readings"
                }
            )
            return
        
        # Calculate price
        requested_count = min(request_data.get("count", 1), len(readings))
        unit_price = self.data_prices.get(sensor_type, 1.0)
        total_price = unit_price * requested_count
        
        # Create transaction
        transaction_id = await self.create_transaction(
            buyer_id=buyer_id,
            seller_id=self.agent_id,
            item_type=f"{sensor_type}_data",
            quantity=requested_count,
            price=total_price
        )
        
        # Prepare data package
        selected_readings = readings[-requested_count:]
        data_package = []
        
        for reading in selected_readings:
            data_package.append({
                "sensor_type": reading.sensor_type,
                "value": reading.value,
                "unit": reading.unit,
                "timestamp": reading.timestamp.isoformat(),
                "quality": reading.quality,
                "source": reading.source
            })
        
        # Send response with data and transaction
        await self.send_message(
            receiver_id=buyer_id,
            message_type=MessageType.DATA_RESPONSE,
            data={
                "status": "approved",
                "transaction_id": transaction_id,
                "total_price": total_price,
                "data": data_package
            }
        )
        
        self.logger.info(
            f"Sold {requested_count} {sensor_type} readings to {buyer_id} "
            f"for ${total_price:.2f}"
        )

    async def _handle_negotiation(self, message: Message):
        """Handle price negotiations"""
        negotiation_data = message.data
        buyer_id = message.sender_id
        
        if negotiation_data.get("action") == "counter_offer":
            sensor_type = negotiation_data.get("sensor_type")
            offered_price = negotiation_data.get("price_per_unit")
            current_price = self.data_prices.get(sensor_type, 1.0)
            
            # Simple negotiation: accept if within 20% of asking price
            if offered_price >= current_price * 0.8:
                # Accept the offer
                self.data_prices[sensor_type] = offered_price
                
                await self.send_message(
                    receiver_id=buyer_id,
                    message_type=MessageType.NEGOTIATION,
                    data={
                        "action": "accept",
                        "sensor_type": sensor_type,
                        "agreed_price": offered_price
                    }
                )
                
                self.logger.info(
                    f"Accepted negotiated price ${offered_price:.2f} for {sensor_type} "
                    f"from {buyer_id}"
                )
            else:
                # Counter with a middle ground
                counter_price = (offered_price + current_price) / 2
                
                await self.send_message(
                    receiver_id=buyer_id,
                    message_type=MessageType.NEGOTIATION,
                    data={
                        "action": "counter_offer",
                        "sensor_type": sensor_type,
                        "price_per_unit": counter_price
                    }
                )

    async def main_loop(self):
        """Main sensor agent logic"""
        # Collect sensor data every minute
        if not hasattr(self, '_last_collection') or \
           (datetime.now() - self._last_collection).seconds > 60:
            
            readings = await self.collect_sensor_data()
            self._last_collection = datetime.now()
            
            if readings:
                self.logger.info(f"Collected {len(readings)} sensor readings")
        
        # Publish data availability every 5 minutes
        if not hasattr(self, '_last_publish') or \
           (datetime.now() - self._last_publish).seconds > 300:
            
            await self.publish_data_availability()
            self._last_publish = datetime.now()

    def get_sensor_status(self) -> Dict[str, Any]:
        """Get current sensor status"""
        status = self.get_status()
        
        sensor_summary = {}
        for sensor_type, readings in self.sensor_readings.items():
            if readings:
                latest = readings[-1]
                sensor_summary[sensor_type] = {
                    "latest_value": latest.value,
                    "latest_timestamp": latest.timestamp.isoformat(),
                    "quality": latest.quality,
                    "source": latest.source,
                    "readings_count": len(readings)
                }
        
        status.update({
            "location": self.farm_location,
            "sensors": sensor_summary,
            "data_prices": self.data_prices
        })
        
        return status


# Helper function to create sensor agent
def create_sensor_agent(
    agent_id: str,
    farm_location: str,
    api_keys: Optional[Dict[str, str]] = None
) -> SensorAgent:
    """Factory function to create a sensor agent"""
    return SensorAgent(agent_id, farm_location, api_keys=api_keys)