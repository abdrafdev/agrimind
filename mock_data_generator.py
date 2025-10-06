#!/usr/bin/env python3
"""
Mock Data Generator for AgriMind Multi-Agent System
Generates realistic farm sensor data, weather records, and market prices
"""
import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List

class MockDataGenerator:
    def __init__(self):
        self.crop_types = ['wheat', 'corn', 'soybeans', 'tomatoes', 'lettuce', 'carrots', 'potatoes']
        self.weather_conditions = ['sunny', 'cloudy', 'rainy', 'partly-cloudy', 'stormy']
        self.pest_types = ['aphids', 'caterpillars', 'beetles', 'fungus', 'weeds']
        
    def generate_sensor_data(self, days: int = 30) -> List[Dict]:
        """Generate realistic sensor data over time"""
        sensor_data = []
        
        for day in range(days):
            timestamp = datetime.now() - timedelta(days=days-day)
            
            # Generate realistic seasonal variations
            base_temp = 20 + (10 * (0.5 - abs(0.5 - (day / 365))))  # Seasonal temperature
            daily_temp_variation = random.uniform(-5, 8)
            
            sensor_reading = {
                'timestamp': timestamp.isoformat(),
                'location': random.choice(['Field A - North', 'Field B - South', 'Field C - East']),
                'soil_moisture': round(random.uniform(25, 80), 1),
                'temperature': round(base_temp + daily_temp_variation, 1),
                'humidity': round(random.uniform(40, 90), 1),
                'ph_level': round(random.uniform(5.5, 8.0), 1),
                'light_intensity': round(random.uniform(200, 800), 0),
                'pest_detection': {
                    'level': random.choice(['low', 'medium', 'high']),
                    'types_detected': random.sample(self.pest_types, k=random.randint(0, 3)),
                    'confidence': round(random.uniform(0.7, 0.98), 2)
                },
                'air_pressure': round(random.uniform(1010, 1030), 1),
                'wind_speed': round(random.uniform(0, 25), 1),
                'uv_index': random.randint(1, 11)
            }
            
            sensor_data.append(sensor_reading)
        
        return sensor_data
    
    def generate_weather_history(self, days: int = 90) -> List[Dict]:
        """Generate historical weather data"""
        weather_history = []
        
        for day in range(days):
            date = datetime.now() - timedelta(days=days-day)
            
            # Create weather patterns with some consistency
            if day > 0:
                prev_temp = weather_history[-1]['temperature_high']
                temp_change = random.uniform(-8, 8)
                new_temp = max(5, min(40, prev_temp + temp_change))
            else:
                new_temp = random.uniform(15, 30)
            
            weather_data = {
                'date': date.strftime('%Y-%m-%d'),
                'temperature_high': round(new_temp, 1),
                'temperature_low': round(new_temp - random.uniform(3, 12), 1),
                'precipitation_mm': round(random.uniform(0, 50) if random.random() > 0.7 else 0, 1),
                'humidity': random.randint(30, 95),
                'wind_speed': round(random.uniform(0, 35), 1),
                'conditions': random.choice(self.weather_conditions),
                'pressure': round(random.uniform(1000, 1040), 1),
                'visibility_km': round(random.uniform(5, 50), 1)
            }
            
            weather_history.append(weather_data)
        
        return weather_history
    
    def generate_market_data(self, days: int = 365) -> Dict[str, List]:
        """Generate market price history for different crops"""
        market_data = {}
        
        base_prices = {
            'wheat': 6.50,
            'corn': 4.20,
            'soybeans': 13.80,
            'tomatoes': 2.40,
            'lettuce': 1.85,
            'carrots': 1.95,
            'potatoes': 0.85
        }
        
        for crop in self.crop_types:
            crop_prices = []
            current_price = base_prices.get(crop, 5.0)
            
            for day in range(days):
                date = datetime.now() - timedelta(days=days-day)
                
                # Add market volatility and seasonal trends
                seasonal_factor = 1 + (0.2 * math.sin((day / 365) * 2 * math.pi))
                volatility = random.uniform(-0.15, 0.15)
                trend = random.uniform(-0.02, 0.03)
                
                price_change = current_price * (volatility + trend) * seasonal_factor
                current_price = max(0.50, current_price + price_change)
                
                price_data = {
                    'date': date.strftime('%Y-%m-%d'),
                    'price_per_kg': round(current_price, 2),
                    'volume_traded': random.randint(1000, 15000),
                    'demand_level': random.choice(['low', 'medium', 'high', 'very_high']),
                    'supply_level': random.choice(['scarce', 'limited', 'adequate', 'abundant']),
                    'quality_grade': random.choice(['A+', 'A', 'B+', 'B', 'C']),
                    'market_sentiment': random.choice(['bullish', 'bearish', 'neutral'])
                }
                
                crop_prices.append(price_data)
            
            market_data[crop] = crop_prices
        
        return market_data
    
    def generate_farm_profiles(self, num_farms: int = 5) -> List[Dict]:
        """Generate profiles for different farms in the network"""
        farms = []
        
        farm_types = ['small_organic', 'medium_conventional', 'large_commercial', 'specialty_crops', 'mixed_farming']
        
        for i in range(num_farms):
            farm_id = f"farm_{i+1:03d}"
            farm_type = random.choice(farm_types)
            
            # Generate realistic farm characteristics
            if 'small' in farm_type:
                acreage = random.uniform(5, 50)
                annual_revenue = random.uniform(50000, 250000)
            elif 'medium' in farm_type:
                acreage = random.uniform(50, 500)
                annual_revenue = random.uniform(250000, 1000000)
            else:
                acreage = random.uniform(500, 5000)
                annual_revenue = random.uniform(1000000, 10000000)
            
            farm_profile = {
                'farm_id': farm_id,
                'name': f"Green Valley Farm {i+1}",
                'type': farm_type,
                'location': {
                    'state': random.choice(['Iowa', 'Nebraska', 'California', 'Texas', 'Illinois']),
                    'coordinates': {
                        'lat': round(random.uniform(25, 48), 4),
                        'lon': round(random.uniform(-125, -70), 4)
                    }
                },
                'characteristics': {
                    'total_acreage': round(acreage, 1),
                    'cultivated_acreage': round(acreage * random.uniform(0.7, 0.95), 1),
                    'annual_revenue': round(annual_revenue, 2),
                    'established_year': random.randint(1950, 2020),
                    'irrigation_type': random.choice(['drip', 'sprinkler', 'flood', 'mixed']),
                    'certification': random.choice(['organic', 'conventional', 'transitioning'])
                },
                'crops_grown': random.sample(self.crop_types, k=random.randint(2, 5)),
                'equipment': {
                    'tractors': random.randint(1, 8),
                    'harvesters': random.randint(0, 3),
                    'irrigation_systems': random.randint(1, 10),
                    'sensors_deployed': random.randint(5, 50)
                },
                'challenges': random.sample([
                    'water_scarcity', 'pest_management', 'market_volatility', 
                    'equipment_costs', 'labor_shortage', 'weather_unpredictability',
                    'soil_degradation', 'regulatory_compliance'
                ], k=random.randint(2, 5))
            }
            
            farms.append(farm_profile)
        
        return farms
    
    def generate_agent_performance_history(self, days: int = 30) -> Dict:
        """Generate historical performance data for agents"""
        agent_types = ['sensor', 'prediction', 'resource_allocation', 'market']
        performance_history = {}
        
        for agent_type in agent_types:
            daily_performance = []
            
            for day in range(days):
                date = datetime.now() - timedelta(days=days-day)
                
                # Different agents have different baseline performance
                if agent_type == 'sensor':
                    base_accuracy = 95
                    base_uptime = 98
                elif agent_type == 'prediction':
                    base_accuracy = 85
                    base_uptime = 94
                elif agent_type == 'resource_allocation':
                    base_accuracy = 88
                    base_uptime = 96
                else:  # market
                    base_accuracy = 78
                    base_uptime = 92
                
                daily_data = {
                    'date': date.strftime('%Y-%m-%d'),
                    'accuracy': round(base_accuracy + random.uniform(-5, 5), 1),
                    'uptime_percentage': round(base_uptime + random.uniform(-3, 3), 1),
                    'response_time_ms': round(random.uniform(50, 300), 0),
                    'successful_transactions': random.randint(10, 100),
                    'failed_transactions': random.randint(0, 10),
                    'data_processed_mb': round(random.uniform(100, 2000), 1),
                    'earnings_usd': round(random.uniform(50, 500), 2)
                }
                
                daily_performance.append(daily_data)
            
            performance_history[agent_type] = daily_performance
        
        return performance_history
    
    def save_all_mock_data(self, filename: str = 'agrimind_mock_data.json'):
        """Generate and save all mock data to a JSON file"""
        print("🔄 Generating comprehensive mock data...")
        
        mock_data = {
            'generated_at': datetime.now().isoformat(),
            'metadata': {
                'description': 'Mock data for AgriMind Multi-Agent System demonstration',
                'version': '1.0',
                'data_types': ['sensor_readings', 'weather_history', 'market_prices', 'farm_profiles', 'agent_performance']
            },
            'sensor_readings': self.generate_sensor_data(30),
            'weather_history': self.generate_weather_history(90),
            'market_prices': self.generate_market_data(365),
            'farm_profiles': self.generate_farm_profiles(5),
            'agent_performance_history': self.generate_agent_performance_history(30)
        }
        
        with open(filename, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        print(f"✅ Mock data saved to {filename}")
        print(f"📊 Generated:")
        print(f"   - {len(mock_data['sensor_readings'])} sensor readings")
        print(f"   - {len(mock_data['weather_history'])} weather records")
        print(f"   - {sum(len(prices) for prices in mock_data['market_prices'].values())} market price points")
        print(f"   - {len(mock_data['farm_profiles'])} farm profiles")
        print(f"   - Performance data for {len(mock_data['agent_performance_history'])} agent types")
        
        return mock_data

if __name__ == "__main__":
    generator = MockDataGenerator()
    mock_data = generator.save_all_mock_data()
    
    print("\n🌾 Mock Data Generation Complete!")
    print("This data demonstrates the real-world scenarios that AgriMind agents handle:")
    print("- Environmental sensor data from multiple farm locations")
    print("- Historical weather patterns for prediction training")
    print("- Market price volatility across different crop types")
    print("- Diverse farm profiles showing the range of users we serve")
    print("- Agent performance metrics proving system effectiveness")