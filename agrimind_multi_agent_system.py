#!/usr/bin/env python3
"""
AgriMind Multi-Agent Swarm System
Addresses the specific problem of small/medium-scale farmers with agent-to-agent economy
"""
import json
import time
import random
import threading
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import math

class AgentType(Enum):
    SENSOR = "sensor"
    PREDICTION = "prediction"
    RESOURCE_ALLOCATION = "resource_allocation"
    MARKET = "market"

class TransactionType(Enum):
    DATA_PURCHASE = "data_purchase"
    SERVICE_REQUEST = "service_request"
    RESOURCE_NEGOTIATION = "resource_negotiation"
    MARKET_RECOMMENDATION = "market_recommendation"

class ConnectivityMode(Enum):
    ONLINE = "online"
    DEGRADED = "degraded"
    OFFLINE = "offline"

@dataclass
class Transaction:
    id: str
    from_agent: str
    to_agent: str
    transaction_type: TransactionType
    amount: float
    data_payload: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"
    reasoning: str = ""

@dataclass
class AgentBalance:
    agent_id: str
    balance: float
    earnings_today: float
    spending_today: float

class BaseAgent:
    def __init__(self, agent_id: str, agent_type: AgentType, farm_id: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.farm_id = farm_id
        self.balance = 1000.0  # Starting virtual currency
        self.earnings_today = 0.0
        self.spending_today = 0.0
        self.transactions = []
        self.cached_data = {}
        self.connectivity_mode = ConnectivityMode.ONLINE
        self.performance_metrics = {
            'success_rate': 95.0,
            'response_time_ms': 150,
            'accuracy': 92.0,
            'uptime_percentage': 98.5
        }
        
    def can_afford(self, amount: float) -> bool:
        return self.balance >= amount
    
    def deduct_balance(self, amount: float, reason: str):
        if self.can_afford(amount):
            self.balance -= amount
            self.spending_today += amount
            print(f"💰 {self.agent_id} spent ${amount:.2f} for {reason}")
    
    def add_earnings(self, amount: float, reason: str):
        self.balance += amount
        self.earnings_today += amount
        print(f"💰 {self.agent_id} earned ${amount:.2f} from {reason}")
    
    def set_connectivity_mode(self, mode: ConnectivityMode):
        self.connectivity_mode = mode
        print(f"📶 {self.agent_id} connectivity: {mode.value}")

class SensorAgent(BaseAgent):
    def __init__(self, agent_id: str, farm_id: str, location: str, sensor_types: List[str]):
        super().__init__(agent_id, AgentType.SENSOR, farm_id)
        self.location = location
        self.sensor_types = sensor_types
        self.data_prices = {
            'soil_moisture': 5.0,
            'temperature': 3.0,
            'humidity': 3.0,
            'pest_detection': 15.0,
            'ph_level': 8.0
        }
        self.current_readings = {}
        self.update_sensor_readings()
    
    def update_sensor_readings(self):
        """Collect fresh environmental data"""
        if self.connectivity_mode == ConnectivityMode.OFFLINE:
            # Use cached/historical data in offline mode
            return self.cached_data
        
        self.current_readings = {
            'soil_moisture': round(random.uniform(25, 80), 1),
            'temperature': round(random.uniform(15, 35), 1),
            'humidity': round(random.uniform(40, 90), 1),
            'pest_detection': random.choice(['low', 'medium', 'high']),
            'ph_level': round(random.uniform(5.5, 8.0), 1),
            'light_intensity': round(random.uniform(200, 800), 0),
            'timestamp': datetime.now().isoformat(),
            'location': self.location
        }
        
        # Cache data for offline mode
        self.cached_data = self.current_readings.copy()
        return self.current_readings
    
    def sell_data(self, buyer_agent: str, data_type: str) -> Transaction:
        """Sell sensor data to other agents"""
        price = self.data_prices.get(data_type, 5.0)
        
        if self.connectivity_mode == ConnectivityMode.DEGRADED:
            price *= 0.8  # Reduced price for degraded quality
        
        transaction = Transaction(
            id=str(uuid.uuid4())[:8],
            from_agent=self.agent_id,
            to_agent=buyer_agent,
            transaction_type=TransactionType.DATA_PURCHASE,
            amount=price,
            data_payload={
                'data_type': data_type,
                'value': self.current_readings.get(data_type),
                'quality_score': 95 if self.connectivity_mode == ConnectivityMode.ONLINE else 75,
                'location': self.location,
                'timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            reasoning=f"Selling {data_type} data from {self.location}"
        )
        
        self.add_earnings(price, f"data sale: {data_type}")
        return transaction

class PredictionAgent(BaseAgent):
    def __init__(self, agent_id: str, farm_id: str, specialization: str):
        super().__init__(agent_id, AgentType.PREDICTION, farm_id)
        self.specialization = specialization  # weather, pest, yield, market
        self.prediction_models = {
            'weather': {'accuracy': 88.5, 'confidence': 0.85},
            'pest': {'accuracy': 92.3, 'confidence': 0.90},
            'yield': {'accuracy': 85.2, 'confidence': 0.82},
            'market': {'accuracy': 79.8, 'confidence': 0.75}
        }
        self.data_requirements = {
            'weather': ['temperature', 'humidity', 'pressure'],
            'pest': ['temperature', 'humidity', 'pest_detection'],
            'yield': ['soil_moisture', 'temperature', 'ph_level'],
            'market': ['weather_forecast', 'supply_data', 'demand_trends']
        }
    
    def purchase_data(self, sensor_agent_id: str, data_types: List[str]) -> List[Transaction]:
        """Purchase data from sensor agents"""
        transactions = []
        
        for data_type in data_types:
            cost = random.uniform(3, 12)  # Variable market pricing
            
            if self.can_afford(cost):
                transaction = Transaction(
                    id=str(uuid.uuid4())[:8],
                    from_agent=sensor_agent_id,
                    to_agent=self.agent_id,
                    transaction_type=TransactionType.DATA_PURCHASE,
                    amount=cost,
                    data_payload={'data_type': data_type, 'requested_at': datetime.now().isoformat()},
                    timestamp=datetime.now(),
                    reasoning=f"Purchasing {data_type} for {self.specialization} prediction"
                )
                
                self.deduct_balance(cost, f"data purchase: {data_type}")
                transactions.append(transaction)
            
        return transactions
    
    def generate_forecast(self, purchased_data: Dict) -> Dict:
        """Generate AI predictions based on purchased data"""
        if self.connectivity_mode == ConnectivityMode.OFFLINE:
            # Use simple rule-based predictions in offline mode
            return self._offline_predictions(purchased_data)
        
        model_info = self.prediction_models.get(self.specialization, {})
        
        forecast = {
            'prediction_type': self.specialization,
            'confidence': model_info.get('confidence', 0.80),
            'accuracy_score': model_info.get('accuracy', 85.0),
            'generated_at': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'reasoning': f"ML model analysis based on {len(purchased_data)} data points"
        }
        
        if self.specialization == 'weather':
            forecast['predictions'] = {
                'precipitation_probability': round(random.uniform(10, 80), 1),
                'temperature_range': [round(random.uniform(15, 20), 1), round(random.uniform(25, 35), 1)],
                'severe_weather_risk': random.choice(['low', 'medium', 'high']),
                'optimal_irrigation_time': datetime.now() + timedelta(hours=random.randint(6, 48))
            }
        elif self.specialization == 'pest':
            forecast['predictions'] = {
                'pest_outbreak_probability': round(random.uniform(15, 75), 1),
                'affected_crops': random.sample(['wheat', 'corn', 'tomatoes', 'soybeans'], k=random.randint(1, 3)),
                'treatment_recommendation': random.choice(['biological', 'chemical', 'integrated']),
                'timing_critical': datetime.now() + timedelta(days=random.randint(1, 7))
            }
        elif self.specialization == 'yield':
            forecast['predictions'] = {
                'expected_yield_percentage': round(random.uniform(80, 120), 1),
                'optimal_harvest_window': [
                    (datetime.now() + timedelta(days=random.randint(30, 60))).isoformat(),
                    (datetime.now() + timedelta(days=random.randint(65, 90))).isoformat()
                ],
                'quality_grade_forecast': random.choice(['A', 'A+', 'B+', 'A-'])
            }
        
        return forecast
    
    def _offline_predictions(self, data: Dict) -> Dict:
        """Simple rule-based predictions for offline mode"""
        return {
            'prediction_type': f"{self.specialization}_offline",
            'confidence': 0.60,  # Lower confidence for offline predictions
            'accuracy_score': 70.0,
            'generated_at': datetime.now().isoformat(),
            'reasoning': "Rule-based offline prediction using cached data",
            'mode': 'degraded_offline'
        }

class ResourceAllocationAgent(BaseAgent):
    def __init__(self, agent_id: str, farm_id: str, managed_resources: List[str]):
        super().__init__(agent_id, AgentType.RESOURCE_ALLOCATION, farm_id)
        self.managed_resources = managed_resources  # water, fertilizer, equipment
        self.resource_capacity = {
            'water': 10000,  # liters per day
            'fertilizer': 500,  # kg per week
            'equipment_hours': 24  # hours per day
        }
        self.current_allocation = {resource: 0 for resource in managed_resources}
        self.negotiation_history = []
    
    def negotiate_resource_sharing(self, requesting_farm: str, resource: str, amount: float, urgency: str) -> Transaction:
        """Negotiate resource allocation with other farms"""
        base_price = {
            'water': 0.05,  # per liter
            'fertilizer': 2.5,  # per kg
            'equipment_hours': 25.0  # per hour
        }.get(resource, 1.0)
        
        # Adjust price based on urgency and availability
        urgency_multiplier = {'low': 0.8, 'medium': 1.0, 'high': 1.3, 'critical': 1.8}.get(urgency, 1.0)
        availability = (self.resource_capacity[resource] - self.current_allocation.get(resource, 0)) / self.resource_capacity[resource]
        scarcity_multiplier = 1.0 if availability > 0.5 else (2.0 - availability)
        
        final_price = base_price * amount * urgency_multiplier * scarcity_multiplier
        
        transaction = Transaction(
            id=str(uuid.uuid4())[:8],
            from_agent=self.agent_id,
            to_agent=f"farm_{requesting_farm}_resource_agent",
            transaction_type=TransactionType.RESOURCE_NEGOTIATION,
            amount=final_price,
            data_payload={
                'resource': resource,
                'amount': amount,
                'urgency': urgency,
                'availability_score': availability,
                'delivery_time_hours': random.randint(1, 24),
                'terms': f"Shared {resource} allocation for {requesting_farm}"
            },
            timestamp=datetime.now(),
            reasoning=f"Resource negotiation: {amount} units of {resource} at {urgency} priority"
        )
        
        # Update allocation if successful
        if availability > 0.1:  # Reserve some capacity
            self.current_allocation[resource] += amount
            self.add_earnings(final_price, f"resource sharing: {resource}")
            transaction.status = "approved"
        else:
            transaction.status = "rejected"
            transaction.reasoning += " - Insufficient capacity"
        
        return transaction
    
    def optimize_irrigation_schedule(self, weather_forecast: Dict, soil_data: Dict) -> Dict:
        """Optimize irrigation based on predictions and sensor data"""
        if self.connectivity_mode == ConnectivityMode.OFFLINE:
            # Simple offline irrigation logic
            return self._offline_irrigation_schedule()
        
        optimization = {
            'agent_id': self.agent_id,
            'schedule_type': 'smart_irrigation',
            'generated_at': datetime.now().isoformat(),
            'water_savings_estimated': round(random.uniform(15, 35), 1),
            'schedule': []
        }
        
        # Generate irrigation schedule for next 7 days
        for day in range(7):
            date = datetime.now() + timedelta(days=day)
            
            # Factor in weather predictions and soil moisture
            rain_probability = weather_forecast.get('precipitation_probability', 30)
            soil_moisture = soil_data.get('soil_moisture', 50)
            
            irrigation_needed = soil_moisture < 40 and rain_probability < 30
            water_amount = random.uniform(200, 800) if irrigation_needed else 0
            
            optimization['schedule'].append({
                'date': date.strftime('%Y-%m-%d'),
                'irrigation_needed': irrigation_needed,
                'water_liters': water_amount,
                'timing': 'early_morning' if irrigation_needed else 'none',
                'reasoning': f"Soil: {soil_moisture}%, Rain: {rain_probability}%"
            })
        
        return optimization
    
    def _offline_irrigation_schedule(self) -> Dict:
        """Basic irrigation schedule for offline mode"""
        return {
            'agent_id': self.agent_id,
            'schedule_type': 'basic_offline',
            'generated_at': datetime.now().isoformat(),
            'reasoning': 'Simple rule-based irrigation (offline mode)',
            'schedule': [
                {
                    'date': (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'irrigation_needed': i % 2 == 0,  # Every other day
                    'water_liters': 400 if i % 2 == 0 else 0,
                    'timing': 'early_morning' if i % 2 == 0 else 'none'
                } for i in range(7)
            ]
        }

class MarketAgent(BaseAgent):
    def __init__(self, agent_id: str, farm_id: str, market_specialization: str):
        super().__init__(agent_id, AgentType.MARKET, farm_id)
        self.market_specialization = market_specialization  # crops, livestock, equipment
        self.price_database = {
            'wheat': {'current': 6.50, 'trend': 'rising'},
            'corn': {'current': 4.20, 'trend': 'stable'},
            'soybeans': {'current': 13.80, 'trend': 'falling'},
            'tomatoes': {'current': 2.40, 'trend': 'rising'},
            'lettuce': {'current': 1.85, 'trend': 'stable'}
        }
        self.buyer_network = []
        self.demand_forecasts = {}
    
    def track_market_prices(self) -> Dict:
        """Track and analyze current market prices"""
        if self.connectivity_mode == ConnectivityMode.OFFLINE:
            return self._offline_price_data()
        
        # Simulate real-time price updates
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'prices': {},
            'market_analysis': {}
        }
        
        for crop, info in self.price_database.items():
            # Simulate price fluctuation
            price_change = random.uniform(-0.10, 0.15)
            new_price = max(0.50, info['current'] + price_change)
            
            market_data['prices'][crop] = {
                'current_price': round(new_price, 2),
                'change_24h': round(price_change, 2),
                'change_percentage': round((price_change / info['current']) * 100, 1),
                'volume_traded': random.randint(1000, 10000),
                'trend': info['trend']
            }
            
            # Update internal database
            self.price_database[crop]['current'] = new_price
        
        return market_data
    
    def recommend_selling_time(self, crop: str, quantity: float, quality: str) -> Transaction:
        """Recommend optimal selling time and connect with buyers"""
        price_info = self.price_database.get(crop, {})
        current_price = price_info.get('current', 5.0)
        trend = price_info.get('trend', 'stable')
        
        # Quality adjustments
        quality_multiplier = {'A+': 1.15, 'A': 1.05, 'B+': 0.95, 'B': 0.85}.get(quality, 1.0)
        adjusted_price = current_price * quality_multiplier
        
        recommendation = {
            'crop': crop,
            'quantity': quantity,
            'quality': quality,
            'current_price': adjusted_price,
            'recommendation': self._generate_timing_recommendation(trend, adjusted_price),
            'potential_buyers': self._find_potential_buyers(crop, quantity),
            'market_conditions': trend,
            'estimated_revenue': quantity * adjusted_price
        }
        
        service_fee = quantity * adjusted_price * 0.02  # 2% service fee
        
        transaction = Transaction(
            id=str(uuid.uuid4())[:8],
            from_agent=self.agent_id,
            to_agent=f"farm_{self.farm_id}_owner",
            transaction_type=TransactionType.MARKET_RECOMMENDATION,
            amount=service_fee,
            data_payload=recommendation,
            timestamp=datetime.now(),
            reasoning=f"Market analysis and selling recommendation for {quantity} units of {crop}"
        )
        
        return transaction
    
    def _generate_timing_recommendation(self, trend: str, price: float) -> str:
        if trend == 'rising':
            return f"Wait 3-7 days - prices trending upward (${price:.2f})"
        elif trend == 'falling':
            return f"Sell immediately - prices declining (${price:.2f})"
        else:
            return f"Neutral timing - stable market (${price:.2f})"
    
    def _find_potential_buyers(self, crop: str, quantity: float) -> List[Dict]:
        """Simulate finding buyers in the network"""
        buyers = [
            {'name': 'FreshMart Co.', 'type': 'retailer', 'capacity': 5000, 'premium': 0.05},
            {'name': 'Organic Foods Ltd.', 'type': 'processor', 'capacity': 10000, 'premium': 0.12},
            {'name': 'Local Farmers Market', 'type': 'direct', 'capacity': 1000, 'premium': 0.08},
            {'name': 'Export Trading Inc.', 'type': 'exporter', 'capacity': 20000, 'premium': 0.03}
        ]
        
        # Filter buyers based on quantity and add random interest
        suitable_buyers = [
            {**buyer, 'interest_level': random.choice(['high', 'medium', 'low'])}
            for buyer in buyers if buyer['capacity'] >= quantity and random.random() > 0.3
        ]
        
        return suitable_buyers[:3]  # Return top 3 matches
    
    def _offline_price_data(self) -> Dict:
        """Cached price data for offline mode"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agent_id': self.agent_id,
            'mode': 'offline_cached',
            'prices': {crop: {'current_price': info['current'], 'trend': 'unknown'} 
                      for crop, info in self.price_database.items()},
            'warning': 'Using cached data - connectivity limited'
        }

class MultiAgentSystem:
    def __init__(self):
        self.agents = {}
        self.transactions = []
        self.system_metrics = {
            'total_transactions': 0,
            'total_volume': 0.0,
            'system_efficiency': 95.0,
            'collaboration_score': 88.5
        }
        self.connectivity_mode = ConnectivityMode.ONLINE
        
        # Initialize agents for demo farm
        self._initialize_demo_agents()
    
    def _initialize_demo_agents(self):
        """Create demo agents for the system"""
        # Sensor Agents
        sensor_1 = SensorAgent("sensor_field_A", "demo_farm_001", "Field A - North", 
                              ["soil_moisture", "temperature", "humidity", "ph_level"])
        sensor_2 = SensorAgent("sensor_field_B", "demo_farm_001", "Field B - South", 
                              ["temperature", "humidity", "pest_detection", "light_intensity"])
        
        # Prediction Agents
        weather_predictor = PredictionAgent("weather_ai_001", "demo_farm_001", "weather")
        pest_predictor = PredictionAgent("pest_ai_001", "demo_farm_001", "pest")
        yield_predictor = PredictionAgent("yield_ai_001", "demo_farm_001", "yield")
        
        # Resource Allocation Agents
        irrigation_manager = ResourceAllocationAgent("irrigation_001", "demo_farm_001", 
                                                   ["water", "fertilizer"])
        equipment_manager = ResourceAllocationAgent("equipment_001", "demo_farm_001", 
                                                   ["equipment_hours"])
        
        # Market Agents
        crop_market = MarketAgent("market_crops_001", "demo_farm_001", "crops")
        
        # Add all agents to system
        agents = [sensor_1, sensor_2, weather_predictor, pest_predictor, yield_predictor,
                 irrigation_manager, equipment_manager, crop_market]
        
        for agent in agents:
            self.agents[agent.agent_id] = agent
    
    def simulate_agent_interactions(self):
        """Simulate realistic agent-to-agent interactions"""
        interactions = []
        
        # Example: Sensor Agent sells data to Prediction Agent
        sensor_agent = self.agents.get("sensor_field_A")
        weather_agent = self.agents.get("weather_ai_001")
        
        if sensor_agent and weather_agent:
            # Weather agent purchases sensor data
            data_transactions = weather_agent.purchase_data("sensor_field_A", 
                                                          ["temperature", "humidity"])
            for tx in data_transactions:
                # Complete the transaction
                sensor_data_tx = sensor_agent.sell_data(weather_agent.agent_id, 
                                                       tx.data_payload['data_type'])
                interactions.append(sensor_data_tx)
                self.transactions.append(sensor_data_tx)
            
            # Generate weather forecast
            forecast = weather_agent.generate_forecast({'temperature': 24.5, 'humidity': 65})
            
            # Resource agent uses forecast for irrigation
            irrigation_agent = self.agents.get("irrigation_001")
            if irrigation_agent:
                irrigation_plan = irrigation_agent.optimize_irrigation_schedule(
                    forecast, {'soil_moisture': 35}
                )
                interactions.append({
                    'type': 'service_delivery',
                    'from': weather_agent.agent_id,
                    'to': irrigation_agent.agent_id,
                    'payload': irrigation_plan,
                    'reasoning': 'Weather forecast used for irrigation optimization'
                })
        
        # Market agent provides selling recommendations
        market_agent = self.agents.get("market_crops_001")
        if market_agent:
            market_data = market_agent.track_market_prices()
            sell_recommendation = market_agent.recommend_selling_time("wheat", 2500, "A")
            interactions.append(sell_recommendation)
            self.transactions.append(sell_recommendation)
        
        return interactions
    
    def set_system_connectivity(self, mode: ConnectivityMode):
        """Set connectivity mode for all agents"""
        self.connectivity_mode = mode
        for agent in self.agents.values():
            agent.set_connectivity_mode(mode)
        print(f"🌐 System connectivity mode: {mode.value}")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        active_agents = len([a for a in self.agents.values() 
                           if a.connectivity_mode != ConnectivityMode.OFFLINE])
        
        total_balance = sum(agent.balance for agent in self.agents.values())
        total_earnings = sum(agent.earnings_today for agent in self.agents.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'connectivity_mode': self.connectivity_mode.value,
            'agents': {
                'total': len(self.agents),
                'active': active_agents,
                'offline': len(self.agents) - active_agents
            },
            'economy': {
                'total_balance': round(total_balance, 2),
                'total_earnings_today': round(total_earnings, 2),
                'total_transactions': len(self.transactions),
                'transaction_volume': round(sum(tx.amount for tx in self.transactions), 2)
            },
            'performance': {
                'system_efficiency': self.system_metrics['system_efficiency'],
                'collaboration_score': self.system_metrics['collaboration_score'],
                'avg_response_time': round(sum(a.performance_metrics['response_time_ms'] 
                                             for a in self.agents.values()) / len(self.agents), 1)
            }
        }
    
    def get_agent_details(self) -> Dict:
        """Get detailed information about all agents"""
        agent_details = {}
        
        for agent_id, agent in self.agents.items():
            agent_details[agent_id] = {
                'id': agent_id,
                'type': agent.agent_type.value,
                'farm_id': agent.farm_id,
                'balance': round(agent.balance, 2),
                'earnings_today': round(agent.earnings_today, 2),
                'spending_today': round(agent.spending_today, 2),
                'connectivity': agent.connectivity_mode.value,
                'performance': agent.performance_metrics,
                'specialization': getattr(agent, 'specialization', 
                                        getattr(agent, 'location', 
                                              getattr(agent, 'managed_resources', 
                                                     getattr(agent, 'market_specialization', 'general')))),
                'current_status': self._get_agent_current_activity(agent)
            }
        
        return agent_details
    
    def _get_agent_current_activity(self, agent) -> str:
        """Determine current activity based on agent type"""
        activities = {
            AgentType.SENSOR: [
                "Collecting soil moisture data", "Monitoring temperature", "Detecting pest activity", 
                "Measuring pH levels", "Calibrating sensors"
            ],
            AgentType.PREDICTION: [
                "Analyzing weather patterns", "Processing sensor data", "Generating forecasts",
                "Training ML models", "Validating predictions"
            ],
            AgentType.RESOURCE_ALLOCATION: [
                "Optimizing irrigation schedule", "Negotiating resource sharing", 
                "Managing equipment allocation", "Calculating water usage", "Planning fertilizer distribution"
            ],
            AgentType.MARKET: [
                "Tracking crop prices", "Analyzing market trends", "Connecting with buyers",
                "Evaluating demand forecasts", "Generating sell recommendations"
            ]
        }
        
        return random.choice(activities.get(agent.agent_type, ["Idle"]))

# Global system instance
agrimind_system = MultiAgentSystem()

def demonstrate_agent_collaboration():
    """Demonstrate agent collaboration flow"""
    print("🌾 AgriMind Multi-Agent System - Collaboration Demo")
    print("=" * 60)
    
    # Normal operation
    print("\n🟢 NORMAL OPERATION MODE")
    agrimind_system.set_system_connectivity(ConnectivityMode.ONLINE)
    interactions = agrimind_system.simulate_agent_interactions()
    print(f"✅ Generated {len(interactions)} agent interactions")
    
    # Degraded mode
    print("\n🟡 DEGRADED CONNECTIVITY MODE")
    agrimind_system.set_system_connectivity(ConnectivityMode.DEGRADED)
    degraded_interactions = agrimind_system.simulate_agent_interactions()
    print(f"⚠️ Generated {len(degraded_interactions)} degraded interactions")
    
    # Offline mode
    print("\n🔴 OFFLINE MODE")
    agrimind_system.set_system_connectivity(ConnectivityMode.OFFLINE)
    offline_interactions = agrimind_system.simulate_agent_interactions()
    print(f"📱 Generated {len(offline_interactions)} offline interactions")
    
    # Reset to online
    agrimind_system.set_system_connectivity(ConnectivityMode.ONLINE)
    
    return {
        'online_interactions': interactions,
        'degraded_interactions': degraded_interactions, 
        'offline_interactions': offline_interactions,
        'system_status': agrimind_system.get_system_status()
    }

if __name__ == "__main__":
    # Run demonstration
    demo_results = demonstrate_agent_collaboration()
    print("\n📊 System Status:")
    print(json.dumps(demo_results['system_status'], indent=2))