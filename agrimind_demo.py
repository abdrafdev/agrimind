"""
AgriMind: Collaborative Farm Intelligence Network
Main Demo and Simulation Workflow

This script demonstrates the complete AgriMind system with all agent types
working together in a collaborative farm intelligence network.

Features:
- Complete agent ecosystem simulation
- Real-time agent communication
- Transaction logging and monitoring
- Degraded mode demonstration
- Comprehensive status reporting
"""

import asyncio
import time
import json
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from pathlib import Path

# Import our AgriMind components
from config.config import get_config_manager, validate_environment
from agents.base_agent import message_bus
from agents.sensor_agent import create_sensor_agent
from agents.prediction_agent import create_prediction_agent
from agents.resource_agent import create_resource_agent
from agents.market_agent import create_market_agent
from agents.anomaly_detection_agent import create_anomaly_detection_agent
from agents.advisor_agent import create_advisor_agent
from data_loaders import get_dataset_summary, clear_dataset_cache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agrimind_demo.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AgriMind-Demo")


class AgriMindSimulation:
    """
    Main simulation controller for the AgriMind system with dataset integration
    """
    
    def __init__(self, demo_mode: str = "hybrid"):
        """
        Initialize simulation
        
        Args:
            demo_mode: "hybrid" (datasets + APIs), "offline" (datasets only), "mock" (no datasets)
        """
        self.config_manager = get_config_manager()
        self.agents = {}
        self.running = False
        self.start_time = None
        self.demo_mode = demo_mode
        self.data_sources_summary = {}
        self.demo_stats = {
            "messages_sent": 0,
            "transactions_completed": 0,
            "predictions_made": 0,
            "resource_allocations": 0,
            "market_trades": 0,
            "data_sources_used": set()
        }
    
    async def initialize_system(self):
        """Initialize the complete AgriMind system with dataset integration"""
        logger.info(f"🚀 Initializing AgriMind System in {self.demo_mode.upper()} mode...")
        
        # Set offline mode based on demo mode
        if self.demo_mode == "offline":
            # Force offline mode for dataset-only demo - disable API connectivity
            os.environ['AGRIMIND_FORCE_OFFLINE'] = 'true'
            logger.info("🔒 OFFLINE MODE: API connectivity disabled, datasets only")
        elif self.demo_mode == "mock":
            # Force mock mode - disable datasets and APIs
            os.environ['AGRIMIND_FORCE_MOCK'] = 'true'
            logger.info("🎭 MOCK MODE: Using synthetic data only")
        
        # Display dataset status
        dataset_summary = get_dataset_summary()
        logger.info(f"📊 Dataset Status: {dataset_summary}")
        
        # Validate configuration
        if not validate_environment():
            raise Exception("Configuration validation failed")
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        
        # Get API keys (disabled in offline mode)
        if self.demo_mode == "offline":
            api_keys = {}  # No API keys in offline mode
            logger.info("🔒 Offline mode: APIs disabled, using datasets only")
        else:
            api_keys = self.config_manager.get_api_keys()
            logger.info(f"🔑 API keys loaded: {list(api_keys.keys())}")
        
        # Initialize farms and their agents
        farms_config = self.config_manager.get_all_farms()
        
        for farm_id, farm_config in farms_config.items():
            logger.info(f"🌾 Setting up {farm_id} ({farm_config['crop_type']} farm)")
            
            # Create sensor agent for this farm
            sensor_id = f"sensor_{farm_id}"
            sensor_agent = create_sensor_agent(
                agent_id=sensor_id,
                farm_location=farm_config['location'],
                api_keys=api_keys
            )
            self.agents[sensor_id] = sensor_agent
            message_bus.register_agent(sensor_agent)
            
            # Create prediction agent for this farm
            prediction_id = f"prediction_{farm_id}"
            prediction_agent = create_prediction_agent(
                agent_id=prediction_id,
                crop_type=farm_config['crop_type']
            )
            self.agents[prediction_id] = prediction_agent
            message_bus.register_agent(prediction_agent)
        
        # Create shared resource agent (one per region)
        resource_agent = create_resource_agent(
            agent_id="resource_central",
            region=self.config_manager.get_system_config().region
        )
        self.agents["resource_central"] = resource_agent
        message_bus.register_agent(resource_agent)
        
        # Create market agent (one per region)
        market_agent = create_market_agent(
            agent_id="market_central",
            region=self.config_manager.get_system_config().region
        )
        self.agents["market_central"] = market_agent
        message_bus.register_agent(market_agent)

        # Advanced agents: anomaly monitor and advisor
        anomaly_agent = create_anomaly_detection_agent("anomaly_monitor")
        self.agents["anomaly_monitor"] = anomaly_agent
        message_bus.register_agent(anomaly_agent)

        advisor_agent = create_advisor_agent("advisor_central")
        self.agents["advisor_central"] = advisor_agent
        message_bus.register_agent(advisor_agent)
        
        logger.info(f"✅ Initialized {len(self.agents)} agents")
        logger.info(f"   📊 Sensor Agents: {len([a for a in self.agents if 'sensor' in a])}")
        logger.info(f"   🔮 Prediction Agents: {len([a for a in self.agents if 'prediction' in a])}")
        logger.info(f"   🔄 Resource Agents: {len([a for a in self.agents if 'resource' in a])}")
        logger.info(f"   💰 Market Agents: {len([a for a in self.agents if 'market' in a])}")

    async def run_demo_cycle(self):
        """Run one complete demo cycle showing agent collaboration"""
        logger.info("\n" + "="*60)
        logger.info("🎬 Starting AgriMind Collaboration Demo Cycle")
        logger.info("="*60)
        
        demo_start = time.time()
        
        # Phase 1: Sensor Data Collection
        logger.info("\n📡 Phase 1: Sensor Data Collection")
        sensor_tasks = []
        for agent_id, agent in self.agents.items():
            if 'sensor' in agent_id:
                task = asyncio.create_task(self._demo_sensor_collection(agent))
                sensor_tasks.append(task)
        
        if sensor_tasks:
            await asyncio.gather(*sensor_tasks)
        
        # Wait for data to propagate
        await asyncio.sleep(2)
        
        # Phase 2: Prediction Generation
        logger.info("\n🔮 Phase 2: Prediction Generation")
        prediction_tasks = []
        for agent_id, agent in self.agents.items():
            if 'prediction' in agent_id:
                task = asyncio.create_task(self._demo_prediction_cycle(agent))
                prediction_tasks.append(task)
        
        if prediction_tasks:
            await asyncio.gather(*prediction_tasks)
        
        # Run anomaly scan with advanced agent
        anomaly_agent = self.agents.get("anomaly_monitor")
        if anomaly_agent:
            await anomaly_agent.scan_for_anomalies()
        
        await asyncio.sleep(2)
        
        # Phase 3: Resource Allocation
        logger.info("\n🔄 Phase 3: Resource Allocation")
        resource_agent = self.agents.get("resource_central")
        if resource_agent:
            await self._demo_resource_allocation(resource_agent)
        
        await asyncio.sleep(2)
        
        # Phase 4: Market Operations
        logger.info("\n💰 Phase 4: Market Operations")
        market_agent = self.agents.get("market_central")
        if market_agent:
            await self._demo_market_operations(market_agent)
        
        await asyncio.sleep(2)
        
        # Phase 5: Show Results
        logger.info("\n📈 Phase 5: Collaboration Results")
        await self._show_collaboration_results()
        
        # Phase 6: Data Sources Summary
        logger.info("\n📈 Phase 6: Data Sources Summary")
        await self._show_data_sources_summary()
        
        demo_duration = time.time() - demo_start
        logger.info(f"\n⏱️  Demo cycle completed in {demo_duration:.2f} seconds")

    async def _demo_sensor_collection(self, sensor_agent):
        """Demonstrate sensor data collection with API source information"""
        logger.info(f"   📊 {sensor_agent.agent_id}: Collecting environmental data...")
        
        # Collect sensor data
        readings = await sensor_agent.collect_sensor_data()
        
        if readings:
            logger.info(f"   📊 {sensor_agent.agent_id}: Collected {len(readings)} sensor readings")
            
            # Group readings by API source
            api_sources = {}
            for sensor_type, reading in readings.items():
                source = reading.source
                if source not in api_sources:
                    api_sources[source] = []
                api_sources[source].append((sensor_type, reading))
            
            # Display readings grouped by source
            for source, source_readings in api_sources.items():
                # Get human-readable API provider name
                if "weatherapi" in source:
                    provider_name = "🌦️ WeatherAPI.com"
                elif "openweather" in source:
                    provider_name = "🌦️ OpenWeatherMap"
                elif "stormglass" in source:
                    provider_name = "🌦️ StormGlass"
                elif "agromonitoring" in source:
                    provider_name = "🛰️ AgroMonitoring"
                elif "simulation" in source or "mock" in source:
                    provider_name = "🎯 Simulation"
                else:
                    provider_name = f"🔍 {source}"
                
                logger.info(f"      {provider_name}:")
                for sensor_type, reading in source_readings:
                    logger.info(f"        • {sensor_type}: {reading.value:.2f} {reading.unit} (quality: {reading.quality:.2f})")
            
            # Publish data availability
            await sensor_agent.publish_data_availability()
            logger.info(f"   📊 {sensor_agent.agent_id}: Published data to marketplace")

    async def _demo_prediction_cycle(self, prediction_agent):
        """Demonstrate prediction generation with API source tracking"""
        logger.info(f"   🔮 {prediction_agent.agent_id}: Analyzing data and generating predictions...")
        
        # Try to purchase some data first
        for sensor_type in ["soil_moisture", "temperature", "humidity"]:
            await prediction_agent.purchase_data(sensor_type, count=3)
        
        # Wait a bit for responses
        await asyncio.sleep(1)
        
        # Update predictions
        await prediction_agent.update_predictions()
        
        # Show predictions made with API source information
        prediction_count = sum(len(preds) for preds in prediction_agent.predictions.values())
        if prediction_count > 0:
            logger.info(f"   🔮 {prediction_agent.agent_id}: Generated {prediction_count} predictions")
            
            # Show detailed prediction information
            status = prediction_agent.get_prediction_status()
            
            for pred_type, predictions in prediction_agent.predictions.items():
                if predictions:
                    latest_pred = predictions[-1]
                    
                    # Get API source information
                    pred_status = status["predictions"].get(pred_type, {})
                    api_sources = pred_status.get("data_sources", {}).get("api_providers", [])
                    reasoning = pred_status.get("reasoning", "")
                    
                    sources_str = ", ".join(api_sources) if api_sources else "simulation"
                    
                    logger.info(f"      • {pred_type}: {latest_pred.value:.2f} (confidence: {latest_pred.confidence:.2f})")
                    logger.info(f"        Sources: {sources_str}")
                    if reasoning:
                        logger.info(f"        Reasoning: {reasoning}")
            
            # Show API provider usage summary
            api_usage = status.get("api_provider_usage", {})
            if api_usage:
                logger.info(f"      API Provider Usage:")
                for data_type, providers in api_usage.items():
                    provider_summary = ", ".join([f"{provider}: {count}" for provider, count in providers.items()])
                    logger.info(f"        {data_type}: {provider_summary}")

    async def _demo_resource_allocation(self, resource_agent):
        """Demonstrate resource allocation"""
        logger.info(f"   🔄 {resource_agent.agent_id}: Processing resource requests...")
        
        # Simulate some resource requests
        farm_agents = [agent_id for agent_id in self.agents.keys() if 'sensor' in agent_id]
        
        for i, farm_agent_id in enumerate(farm_agents[:2]):  # Limit to 2 for demo
            # Create mock water request
            request_data = {
                "request_id": f"water_req_{i}_{int(time.time())}",
                "resource_type": "water",
                "quantity": random.randint(500, 2000),
                "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "duration_hours": random.randint(2, 6),
                "priority": "normal",
                "max_price": random.uniform(50, 200),
                "metadata": {"irrigation_type": "drip"}
            }
            
            # Simulate the request
            from agents.base_agent import Message, MessageType
            request_message = Message(
                id=f"req_{i}",
                sender_id=farm_agent_id,
                receiver_id=resource_agent.agent_id,
                message_type=MessageType.RESOURCE_REQUEST,
                timestamp=datetime.now(),
                data=request_data
            )
            
            await resource_agent.receive_message(request_message)
            logger.info(f"      • Processed water request from {farm_agent_id}: {request_data['quantity']}L")
        
        # Show resource status
        status = resource_agent.get_resource_status()
        water_info = status["resource_availability"].get("water", {})
        if water_info:
            utilization = water_info.get("utilization", 0) * 100
            logger.info(f"      • Water system utilization: {utilization:.1f}%")

    async def _demo_market_operations(self, market_agent):
        """Demonstrate market operations"""
        logger.info(f"   💰 {market_agent.agent_id}: Processing market activities...")
        
        # Update market prices
        await market_agent.update_market_prices()
        
        # Show current prices
        status = market_agent.get_market_status()
        current_prices = status.get("current_prices", {})
        
        if current_prices:
            logger.info("      • Current market prices:")
            for crop, price_info in current_prices.items():
                trend_emoji = {
                    "bullish": "📈",
                    "bearish": "📉", 
                    "stable": "➡️",
                    "volatile": "📊"
                }.get(price_info.get("trend", "stable"), "➡️")
                
                logger.info(f"        {crop}: ${price_info['price']:.2f}/kg {trend_emoji}")
        
        # Simulate a sell offer
        farm_ids = [aid for aid in self.agents.keys() if 'sensor' in aid]
        if farm_ids:
            farm_id = farm_ids[0]
            offer_data = {
                "request_type": "sell_offer",
                "crop_type": "tomatoes",
                "quantity": 500,
                "asking_price": 3.25,
                "quality_grade": "B",
                "harvest_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "location": "fresno_ca"
            }
            
            from agents.base_agent import Message, MessageType
            offer_message = Message(
                id="market_offer_demo",
                sender_id=farm_id,
                receiver_id=market_agent.agent_id,
                message_type=MessageType.MARKET_INFO,
                timestamp=datetime.now(),
                data=offer_data
            )
            
            await market_agent.receive_message(offer_message)
            logger.info(f"      • Registered sell offer: 500kg tomatoes at $3.25/kg")

    async def _show_collaboration_results(self):
        """Show the results of agent collaboration"""
        logger.info("   📈 System-wide collaboration results:")
        
        total_transactions = 0
        total_volume = 0
        
        for agent_id, agent in self.agents.items():
            agent_transactions = len(agent.transactions)
            if agent_transactions > 0:
                total_transactions += agent_transactions
                logger.info(f"      • {agent_id}: {agent_transactions} transactions, balance: ${agent.balance:.2f}")
        
        logger.info(f"      • Total system transactions: {total_transactions}")
        
        # Show network effect
        message_count = sum(len(agent.message_queue) for agent in self.agents.values())
        logger.info(f"      • Messages in system: {message_count}")
        
        # Show specialization benefits
        sensor_agents = [a for a in self.agents.values() if 'sensor' in a.agent_id]
        if sensor_agents:
            total_readings = sum(
                len(readings) for agent in sensor_agents 
                for readings in agent.sensor_readings.values()
            )
            logger.info(f"      • Total sensor readings collected: {total_readings}")
        
        prediction_agents = [a for a in self.agents.values() if 'prediction' in a.agent_id]
        if prediction_agents:
            total_predictions = sum(
                len(predictions) for agent in prediction_agents
                for predictions in agent.predictions.values()
            )
        logger.info(f"      • Total predictions generated: {total_predictions}")

    async def _show_data_sources_summary(self):
        """Show summary of data sources used across all agents"""
        logger.info("   📊 Data Sources Usage Report:")
        
        source_counts = {}
        agent_sources = {}
        
        # Collect data source information from all agents
        for agent_id, agent in self.agents.items():
            agent_sources[agent_id] = []
            
            if hasattr(agent, 'sensor_readings') and agent.sensor_readings:
                # Sensor agent data sources
                for sensor_type, readings in agent.sensor_readings.items():
                    if readings:
                        latest_reading = readings[-1]
                        source = latest_reading.source
                        source_counts[source] = source_counts.get(source, 0) + 1
                        agent_sources[agent_id].append(f"{sensor_type}={source}")
            
            elif hasattr(agent, 'predictions') and agent.predictions:
                # Prediction agent data sources 
                for pred_type, predictions in agent.predictions.items():
                    if predictions:
                        latest_prediction = predictions[-1]
                        method = latest_prediction.metadata.get('method', 'unknown')
                        dataset_source = latest_prediction.metadata.get('dataset_source')
                        if dataset_source:
                            source = f"dataset_{method}"
                        else:
                            source = method
                        source_counts[source] = source_counts.get(source, 0) + 1
                        agent_sources[agent_id].append(f"{pred_type}={source}")
            
            elif hasattr(agent, 'available_resources'):
                # Resource agent data sources
                for resource_type, resource_data in agent.available_resources.items():
                    source = resource_data.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                    agent_sources[agent_id].append(f"{resource_type.value}={source}")
            
            elif hasattr(agent, 'price_history'):
                # Market agent data sources
                for crop_type, price_data in agent.price_history.items():
                    if price_data:
                        latest_price = price_data[-1]
                        source = latest_price.source
                        source_counts[source] = source_counts.get(source, 0) + 1
                        agent_sources[agent_id].append(f"{crop_type.value}={source}")
        
        # Display overall source usage
        logger.info("      👀 Overall Data Source Usage:")
        for source, count in sorted(source_counts.items()):
            source_type = "📋 Dataset" if "dataset" in source else "🌐 API" if source in ["weatherapi_com", "openweathermap", "stormglass", "agromonitoring"] else "🤖 Mock/Rule-based"
            logger.info(f"         • {source_type}: {source} ({count} usages)")
        
        # Display agent-specific sources
        logger.info("      🤖 Agent-Specific Data Sources:")
        for agent_id, sources in agent_sources.items():
            if sources:
                logger.info(f"         • {agent_id}: {', '.join(sources)}")
        
        # Show dataset summary
        dataset_summary = get_dataset_summary()
        datasets_loaded = [k for k, v in dataset_summary.items() if v == "Cached"]
        if datasets_loaded:
            logger.info(f"      📋 Active Datasets: {', '.join(datasets_loaded)}")
        
        # Calculate dataset vs API vs mock usage percentages
        total_sources = sum(source_counts.values())
        if total_sources > 0:
            dataset_count = sum(count for source, count in source_counts.items() if "dataset" in source)
            api_count = sum(count for source, count in source_counts.items() if source in ["weatherapi_com", "openweathermap", "stormglass", "agromonitoring"])
            mock_count = total_sources - dataset_count - api_count
            
            dataset_pct = (dataset_count / total_sources) * 100
            api_pct = (api_count / total_sources) * 100
            mock_pct = (mock_count / total_sources) * 100
            
            logger.info(f"      📊 Source Distribution: Dataset {dataset_pct:.1f}%, API {api_pct:.1f}%, Mock/Rule-based {mock_pct:.1f}%")
            
            # Show mode effectiveness
            if self.demo_mode == "offline" and dataset_pct > 70:
                logger.info("      ✅ Offline mode: Successfully using datasets for majority of operations")
            elif self.demo_mode == "hybrid" and dataset_pct > 30 and api_pct > 10:
                logger.info("      ✅ Hybrid mode: Good balance of datasets and live APIs")
            elif mock_pct > 50:
                logger.info("      ⚠️  High reliance on mock data - consider providing dataset files")

    async def simulate_degraded_mode(self):
        """Demonstrate system operation in degraded mode"""
        logger.info("\n" + "="*60)
        logger.info("🔌 Demonstrating Degraded Mode Operation")
        logger.info("="*60)
        
        # Simulate network failure
        logger.info("   ⚠️  Simulating network connectivity loss...")
        
        for agent in self.agents.values():
            agent.online = False
        
        await asyncio.sleep(1)
        
        # Show degraded operations
        sensor_agent = next(iter([a for a in self.agents.values() if 'sensor' in a.agent_id]), None)
        if sensor_agent:
            logger.info("   📡 Sensor agent operating in degraded mode...")
            readings = await sensor_agent.collect_sensor_data()
            
            degraded_readings = [r for r in readings.values() if 'cached' in r.source or 'rule_based' in r.source]
            logger.info(f"      • Using cached/rule-based data: {len(degraded_readings)}/{len(readings)} readings")
        
        prediction_agent = next(iter([a for a in self.agents.values() if 'prediction' in a.agent_id]), None)
        if prediction_agent:
            logger.info("   🔮 Prediction agent operating in degraded mode...")
            await prediction_agent.update_predictions()
            
            degraded_predictions = 0
            for predictions in prediction_agent.predictions.values():
                if predictions:
                    latest = predictions[-1]
                    if latest.confidence < 0.5:  # Lower confidence indicates degraded mode
                        degraded_predictions += 1
            
            if degraded_predictions > 0:
                logger.info(f"      • Generated {degraded_predictions} rule-based predictions")
        
        # Restore network
        logger.info("   ✅ Restoring network connectivity...")
        for agent in self.agents.values():
            agent.online = True
        
        logger.info("   🔄 System recovered and operating normally")

    async def run_simulation(self, duration_minutes: int = 10):
        """Run the complete simulation for specified duration"""
        self.running = True
        self.start_time = datetime.now()
        
        logger.info(f"🎯 Starting {duration_minutes}-minute AgriMind simulation")
        logger.info(f"   Start time: {self.start_time.strftime('%H:%M:%S')}")
        
        # Start all agents
        agent_tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(self._run_agent_loop(agent))
            agent_tasks.append(task)
        
        # Run demo cycles
        demo_task = asyncio.create_task(self._demo_loop(duration_minutes))
        
        try:
            # Run everything concurrently
            await asyncio.wait_for(demo_task, timeout=duration_minutes * 60 + 30)
            
        except asyncio.TimeoutError:
            logger.info("⏰ Simulation timeout reached")
        except KeyboardInterrupt:
            logger.info("🛑 Simulation stopped by user")
        finally:
            self.running = False
            
            # Cancel all agent tasks
            for task in agent_tasks:
                task.cancel()
            
            # Wait for cleanup
            await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Final statistics
        await self._show_final_statistics()

    async def _run_agent_loop(self, agent):
        """Run an individual agent's main loop"""
        try:
            while self.running:
                await agent.main_loop()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in agent {agent.agent_id}: {e}")

    async def _demo_loop(self, duration_minutes: int):
        """Run periodic demo cycles"""
        cycle_interval = max(60, duration_minutes * 60 // 3)  # At least 3 cycles
        next_cycle_time = time.time() + 10  # First cycle after 10 seconds
        
        cycle_count = 0
        
        while self.running and time.time() < (time.time() + duration_minutes * 60):
            current_time = time.time()
            
            if current_time >= next_cycle_time:
                cycle_count += 1
                logger.info(f"\n🔄 Demo Cycle {cycle_count}")
                
                await self.run_demo_cycle()
                
                # Special demo: degraded mode on cycle 2
                if cycle_count == 2:
                    await self.simulate_degraded_mode()
                
                next_cycle_time = current_time + cycle_interval
            
            await asyncio.sleep(5)  # Check every 5 seconds

    async def _show_final_statistics(self):
        """Show final simulation statistics"""
        end_time = datetime.now()
        duration = end_time - self.start_time if self.start_time else timedelta(0)
        
        logger.info("\n" + "="*60)
        logger.info("📊 Final Simulation Statistics")
        logger.info("="*60)
        logger.info(f"   Duration: {duration}")
        logger.info(f"   Agents: {len(self.agents)}")
        
        # Transaction statistics
        total_transactions = sum(len(agent.transactions) for agent in self.agents.values())
        total_balance_change = sum(agent.balance - 1000.0 for agent in self.agents.values())  # Assuming 1000 starting balance
        
        logger.info(f"   Total transactions: {total_transactions}")
        logger.info(f"   Net balance change: ${total_balance_change:.2f}")
        
        # Agent-specific statistics
        for agent_id, agent in self.agents.items():
            if hasattr(agent, 'get_sensor_status') and 'sensor' in agent_id:
                status = agent.get_sensor_status()
                total_readings = sum(data['readings_count'] for data in status['sensors'].values())
                logger.info(f"   {agent_id}: {total_readings} sensor readings")
            
            elif hasattr(agent, 'get_prediction_status') and 'prediction' in agent_id:
                status = agent.get_prediction_status()
                total_predictions = sum(data['predictions_count'] for data in status['predictions'].values())
                logger.info(f"   {agent_id}: {total_predictions} predictions made")
        
        logger.info("\n🎉 AgriMind simulation completed successfully!")


async def main():
    """Main function to run the AgriMind demo with dataset integration"""
    print("🌾 AgriMind: Collaborative Farm Intelligence Network")
    print("   NATIONAL AGENTIC AI HACKATHON Demo with Official Datasets")
    print("="*60)
    
    # Demo mode selection
    import sys
    demo_mode = "hybrid"  # Default to hybrid mode
    
    if len(sys.argv) > 1:
        mode_arg = sys.argv[1].lower()
        if mode_arg in ["hybrid", "offline", "mock"]:
            demo_mode = mode_arg
        else:
            print(f"Unknown mode '{mode_arg}'. Using hybrid mode.")
    
    print(f"🚀 Demo Mode: {demo_mode.upper()}")
    if demo_mode == "hybrid":
        print("   - Uses official datasets + live APIs when available")
    elif demo_mode == "offline":
        print("   - Uses official datasets only (no API calls)")
    elif demo_mode == "mock":
        print("   - Uses mock data only (no datasets or APIs)")
    print()
    
    try:
        # Create and initialize simulation with specified mode
        simulation = AgriMindSimulation(demo_mode=demo_mode)
        await simulation.initialize_system()
        
        # Run a single demo cycle to showcase dataset integration
        await simulation.run_demo_cycle()
        
        # Show degraded mode if in hybrid mode
        if demo_mode == "hybrid":
            await simulation.simulate_degraded_mode()
        
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        raise
    
    print("\n✅ Demo completed! Check the logs for detailed information.")
    print("📁 Logs are saved in: logs/agrimind_demo.log")
    print("💾 Data and caches are saved in: data/")


if __name__ == "__main__":
    # Create directories
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    
    # Run the demo
    asyncio.run(main())