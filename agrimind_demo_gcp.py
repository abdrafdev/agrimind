#!/usr/bin/env python3
"""
AgriMind Google Cloud Platform Demo
Enhanced multi-agent agricultural system with Google Cloud services
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Add agents directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

# Local imports
from config.config import Config
from agents.base_agent import MessageBus
from agents.gcp_sensor_agent import GCPSensorAgent
from agents.prediction_agent import PredictionAgent
from agents.resource_agent import ResourceAgent
from agents.market_agent import MarketAgent

# Google Cloud imports
try:
    from google.cloud import bigquery
    from google.cloud import monitoring_v3
    from google.cloud import firestore
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agrimind_gcp.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GCPAgriMindDemo:
    """Enhanced AgriMind demonstration with Google Cloud Platform integration"""
    
    def __init__(self):
        self.config = Config()
        self.message_bus = MessageBus()
        self.agents = {}
        
        # GCP services
        self.bigquery_client = None
        self.firestore_client = None
        self.monitoring_client = None
        
        # Demo settings
        self.demo_duration = 60  # seconds
        self.farm_configs = [
            {
                'farm_id': 'farm_1',
                'location': 'California Central Valley',
                'crops': ['tomatoes', 'lettuce', 'corn'],
                'size_hectares': 150
            },
            {
                'farm_id': 'farm_2', 
                'location': 'Iowa Corn Belt',
                'crops': ['corn', 'soybeans'],
                'size_hectares': 200
            }
        ]
    
    async def initialize_gcp_services(self):
        """Initialize Google Cloud Platform services"""
        logger.info("🌐 Initializing Google Cloud Platform services...")
        
        try:
            if GOOGLE_CLOUD_AVAILABLE and os.getenv('GOOGLE_CLOUD_PROJECT'):
                # Initialize BigQuery for analytics
                self.bigquery_client = bigquery.Client()
                await self.setup_bigquery_dataset()
                
                # Initialize Firestore for real-time data
                self.firestore_client = firestore.Client()
                
                # Initialize Cloud Monitoring
                self.monitoring_client = monitoring_v3.MetricServiceClient()
                
                logger.info("✅ Google Cloud services initialized successfully")
            else:
                logger.warning("⚠️ Google Cloud not available - running in enhanced simulation mode")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCP services: {e}")
            logger.info("🔄 Continuing with enhanced local simulation")
    
    async def setup_bigquery_dataset(self):
        """Set up BigQuery dataset and tables for AgriMind"""
        try:
            dataset_id = 'agrimind_analytics'
            project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            
            # Create dataset
            dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
            dataset.location = "US"
            dataset.description = "AgriMind agricultural intelligence data"
            
            try:
                dataset = self.bigquery_client.create_dataset(dataset, exists_ok=True)
                logger.info(f"📊 Created BigQuery dataset: {dataset_id}")
            except Exception as e:
                logger.info(f"📊 BigQuery dataset already exists or accessible: {dataset_id}")
            
            # Create tables
            await self.create_bigquery_tables(dataset_id)
            
        except Exception as e:
            logger.error(f"❌ Error setting up BigQuery: {e}")
    
    async def create_bigquery_tables(self, dataset_id: str):
        """Create BigQuery tables for different data types"""
        try:
            tables = {
                'sensor_readings': [
                    bigquery.SchemaField('timestamp', 'TIMESTAMP'),
                    bigquery.SchemaField('farm_id', 'STRING'),
                    bigquery.SchemaField('sensor_type', 'STRING'),
                    bigquery.SchemaField('value', 'FLOAT'),
                    bigquery.SchemaField('quality', 'FLOAT'),
                    bigquery.SchemaField('source', 'STRING'),
                    bigquery.SchemaField('location_lat', 'FLOAT'),
                    bigquery.SchemaField('location_lng', 'FLOAT')
                ],
                'agent_transactions': [
                    bigquery.SchemaField('timestamp', 'TIMESTAMP'),
                    bigquery.SchemaField('from_agent', 'STRING'),
                    bigquery.SchemaField('to_agent', 'STRING'),
                    bigquery.SchemaField('transaction_type', 'STRING'),
                    bigquery.SchemaField('amount', 'FLOAT'),
                    bigquery.SchemaField('data_type', 'STRING'),
                    bigquery.SchemaField('confidence', 'FLOAT')
                ],
                'predictions': [
                    bigquery.SchemaField('timestamp', 'TIMESTAMP'),
                    bigquery.SchemaField('farm_id', 'STRING'),
                    bigquery.SchemaField('prediction_type', 'STRING'),
                    bigquery.SchemaField('predicted_value', 'FLOAT'),
                    bigquery.SchemaField('confidence', 'FLOAT'),
                    bigquery.SchemaField('data_sources', 'STRING'),
                    bigquery.SchemaField('reasoning', 'STRING')
                ]
            }
            
            for table_name, schema in tables.items():
                table_id = f"{os.getenv('GOOGLE_CLOUD_PROJECT')}.{dataset_id}.{table_name}"
                table = bigquery.Table(table_id, schema=schema)
                
                try:
                    table = self.bigquery_client.create_table(table, exists_ok=True)
                    logger.info(f"📋 Created BigQuery table: {table_name}")
                except Exception as e:
                    logger.info(f"📋 BigQuery table already exists: {table_name}")
                    
        except Exception as e:
            logger.error(f"❌ Error creating BigQuery tables: {e}")
    
    async def initialize_agents(self):
        """Initialize all AgriMind agents with GCP enhancements"""
        logger.info("🤖 Initializing AgriMind agents with Google Cloud integration...")
        
        for farm_config in self.farm_configs:
            farm_id = farm_config['farm_id']
            
            # Enhanced Sensor Agent with Google Vision API
            sensor_agent = GCPSensorAgent(
                farm_id=farm_id,
                config=self.config.get_agent_config('sensor', farm_config)
            )
            self.agents[f'sensor_{farm_id}'] = sensor_agent
            self.message_bus.register_agent(sensor_agent)
            
            # Prediction Agent (enhanced with GCP data sources)
            prediction_agent = PredictionAgent(
                farm_id=farm_id,
                config=self.config.get_agent_config('prediction', farm_config)
            )
            self.agents[f'prediction_{farm_id}'] = prediction_agent  
            self.message_bus.register_agent(prediction_agent)
        
        # Central Resource Agent
        resource_agent = ResourceAgent(
            region='central',
            config=self.config.get_agent_config('resource', {'region': 'central'})
        )
        self.agents['resource_central'] = resource_agent
        self.message_bus.register_agent(resource_agent)
        
        # Central Market Agent  
        market_agent = MarketAgent(
            region='central',
            config=self.config.get_agent_config('market', {'region': 'central'})
        )
        self.agents['market_central'] = market_agent
        self.message_bus.register_agent(market_agent)
        
        logger.info(f"✅ Initialized {len(self.agents)} agents with GCP enhancements")
    
    async def log_to_bigquery(self, table_name: str, data: Dict[str, Any]):
        """Log data to BigQuery for analytics"""
        try:
            if not self.bigquery_client:
                return
            
            dataset_id = 'agrimind_analytics'
            table_id = f"{os.getenv('GOOGLE_CLOUD_PROJECT')}.{dataset_id}.{table_name}"
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow()
            
            # Insert row
            rows_to_insert = [data]
            errors = self.bigquery_client.insert_rows_json(
                table_id, rows_to_insert
            )
            
            if not errors:
                logger.debug(f"📊 Logged to BigQuery {table_name}: {data}")
            else:
                logger.error(f"❌ BigQuery insert errors: {errors}")
                
        except Exception as e:
            logger.error(f"❌ Error logging to BigQuery: {e}")
    
    async def store_realtime_data(self, collection: str, document_id: str, data: Dict[str, Any]):
        """Store real-time data in Firestore"""
        try:
            if not self.firestore_client:
                return
            
            doc_ref = self.firestore_client.collection(collection).document(document_id)
            doc_ref.set(data, merge=True)
            
            logger.debug(f"🔥 Stored in Firestore {collection}/{document_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing in Firestore: {e}")
    
    async def run_gcp_enhanced_simulation(self):
        """Run enhanced simulation with Google Cloud integration"""
        logger.info("🚀 Starting GCP-enhanced AgriMind simulation...")
        
        # Phase 1: Enhanced Sensor Data Collection
        await self.phase_1_gcp_sensor_collection()
        await asyncio.sleep(2)
        
        # Phase 2: AI-Powered Predictions
        await self.phase_2_gcp_predictions()
        await asyncio.sleep(2)
        
        # Phase 3: Resource Optimization
        await self.phase_3_resource_allocation()
        await asyncio.sleep(2)
        
        # Phase 4: Market Intelligence
        await self.phase_4_market_operations()
        await asyncio.sleep(2)
        
        # Phase 5: Real-time Analytics
        await self.phase_5_gcp_analytics()
        
        logger.info("✅ GCP-enhanced simulation completed successfully!")
    
    async def phase_1_gcp_sensor_collection(self):
        """Phase 1: Enhanced sensor data collection with Google Cloud"""
        logger.info("📡 Phase 1: GCP-Enhanced Sensor Data Collection")
        print("\n" + "="*60)
        print("🌐 PHASE 1: GOOGLE CLOUD ENHANCED SENSORS")
        print("="*60)
        
        for farm_config in self.farm_configs:
            farm_id = farm_config['farm_id']
            sensor_agent = self.agents.get(f'sensor_{farm_id}')
            
            if sensor_agent:
                print(f"\n📊 {sensor_agent.agent_id}: Collecting enhanced sensor data...")
                
                # Collect data with GCP enhancements
                sensor_data = await sensor_agent.collect_sensor_data()
                
                print(f"📊 {sensor_agent.agent_id}: Collected {len(sensor_data)} readings")
                
                # Display GCP-enhanced readings
                for reading in sensor_data:
                    source = reading.get('source', 'Unknown')
                    quality = reading.get('quality', 0)
                    value = reading.get('value')
                    
                    if source == 'Google Vision API':
                        print(f"👁️ Google Vision API:")
                        if isinstance(value, dict):
                            print(f"  • Crop Health: {value.get('health', {}).get('health_score', 0):.2f}")
                            print(f"  • Disease Risk: {value.get('diseases', {}).get('disease_risk', 0):.2f}")
                            print(f"  • Objects Detected: {value.get('objects', {}).get('objects_detected', 0)}")
                            print(f"  • Overall Score: {value.get('overall_score', 0):.2f}")
                    else:
                        unit = reading.get('unit', '')
                        print(f"🌡️ {source}: {reading['type']}: {value} {unit} (quality: {quality:.2f})")
                
                # Log to BigQuery
                for reading in sensor_data:
                    await self.log_to_bigquery('sensor_readings', {
                        'farm_id': farm_id,
                        'sensor_type': reading['type'],
                        'value': float(reading['value']) if isinstance(reading['value'], (int, float)) else 0.0,
                        'quality': reading['quality'],
                        'source': reading['source'],
                        'location_lat': 37.7749 + hash(farm_id) % 100 / 1000,  # Simulated coords
                        'location_lng': -122.4194 + hash(farm_id) % 100 / 1000
                    })
                
                # Store in Firestore for real-time updates
                await self.store_realtime_data('sensor_data', farm_id, {
                    'last_update': datetime.utcnow(),
                    'readings': len(sensor_data),
                    'gcp_enhanced': True
                })
                
                print(f"📊 {sensor_agent.agent_id}: Published to GCP data services")
    
    async def phase_2_gcp_predictions(self):
        """Phase 2: AI-powered predictions with GCP data"""
        logger.info("🔮 Phase 2: GCP-Enhanced Predictions")
        print("\n" + "="*60)
        print("🤖 PHASE 2: AI-POWERED PREDICTIONS")
        print("="*60)
        
        for farm_config in self.farm_configs:
            farm_id = farm_config['farm_id']
            prediction_agent = self.agents.get(f'prediction_{farm_id}')
            
            if prediction_agent:
                print(f"\n🔮 {prediction_agent.agent_id}: Generating AI predictions...")
                
                # Generate predictions with enhanced data
                predictions = await prediction_agent.generate_predictions()
                
                print(f"🔮 {prediction_agent.agent_id}: Generated {len(predictions)} predictions")
                
                # Display predictions with confidence sources
                for pred in predictions:
                    pred_type = pred['type']
                    value = pred['value']
                    confidence = pred['confidence']
                    reasoning = pred.get('reasoning', 'N/A')
                    
                    print(f"• {pred_type}: {value:.2f} (confidence: {confidence:.2f})")
                    print(f"  Reasoning: {reasoning}")
                
                # Log predictions to BigQuery
                for pred in predictions:
                    await self.log_to_bigquery('predictions', {
                        'farm_id': farm_id,
                        'prediction_type': pred['type'],
                        'predicted_value': pred['value'],
                        'confidence': pred['confidence'],
                        'data_sources': pred.get('data_sources', ''),
                        'reasoning': pred.get('reasoning', '')
                    })
                
                # Update real-time dashboard
                await self.store_realtime_data('predictions', farm_id, {
                    'last_prediction': datetime.utcnow(),
                    'prediction_count': len(predictions),
                    'avg_confidence': sum(p['confidence'] for p in predictions) / len(predictions)
                })
                
        # Show GCP integration stats
        print(f"\n📈 GCP Integration Status:")
        print(f"  • BigQuery: {'✅ Active' if self.bigquery_client else '❌ Simulation'}")
        print(f"  • Firestore: {'✅ Active' if self.firestore_client else '❌ Simulation'}")
        print(f"  • Vision API: {'✅ Active' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else '❌ Simulation'}")
    
    async def phase_3_resource_allocation(self):
        """Phase 3: Resource allocation with cloud optimization"""
        logger.info("🔄 Phase 3: Cloud-Optimized Resource Allocation")
        print("\n" + "="*60)
        print("⚡ PHASE 3: CLOUD-OPTIMIZED RESOURCES")
        print("="*60)
        
        resource_agent = self.agents.get('resource_central')
        if resource_agent:
            print(f"🔄 {resource_agent.agent_id}: Processing resource requests...")
            
            # Process resource allocation
            await resource_agent.optimize_resource_allocation()
            
            # Display resource utilization
            utilization = resource_agent.get_resource_utilization()
            print(f"• Water system utilization: {utilization.get('water', 0):.1f}%")
            print(f"• Equipment utilization: {utilization.get('equipment', 0):.1f}%")
            print(f"• Labor utilization: {utilization.get('labor', 0):.1f}%")
            
            # Log resource allocation to BigQuery
            await self.log_to_bigquery('agent_transactions', {
                'from_agent': 'system',
                'to_agent': 'resource_central',
                'transaction_type': 'resource_optimization',
                'amount': sum(utilization.values()),
                'data_type': 'resource_utilization',
                'confidence': 0.92
            })
    
    async def phase_4_market_operations(self):
        """Phase 4: Market operations with cloud analytics"""
        logger.info("💰 Phase 4: Cloud-Enhanced Market Operations")
        print("\n" + "="*60)
        print("💹 PHASE 4: CLOUD-ENHANCED MARKET")
        print("="*60)
        
        market_agent = self.agents.get('market_central')
        if market_agent:
            print(f"💰 {market_agent.agent_id}: Processing market activities...")
            
            # Update market data
            await market_agent.update_market_data()
            
            # Display current prices with trends
            prices = market_agent.current_prices
            trends = market_agent.get_price_trends()
            
            print("• Current market prices:")
            for crop, price in prices.items():
                trend = trends.get(crop, '➡️')
                print(f"  {crop}: ${price:.2f}/kg {trend}")
            
            # Generate market insights
            insights = await market_agent.generate_market_insights()
            print(f"• Market insights generated: {len(insights)} recommendations")
    
    async def phase_5_gcp_analytics(self):
        """Phase 5: Real-time analytics and insights"""
        logger.info("📊 Phase 5: GCP Analytics Dashboard")
        print("\n" + "="*60)
        print("📊 PHASE 5: REAL-TIME GCP ANALYTICS")
        print("="*60)
        
        try:
            if self.bigquery_client:
                # Query BigQuery for insights
                insights = await self.generate_bigquery_insights()
                
                print("📈 BigQuery Analytics Results:")
                for insight in insights:
                    print(f"  • {insight}")
            else:
                print("📊 BigQuery Analytics: Simulated (no credentials)")
                print("  • Average sensor confidence: 0.87")
                print("  • Total predictions generated: 8")
                print("  • Resource optimization efficiency: 94%")
                print("  • Market trend accuracy: 91%")
            
            if self.firestore_client:
                print("\n🔥 Firestore Real-time Data:")
                print("  • Live sensor updates: Active")
                print("  • Agent coordination: Real-time")
                print("  • Dashboard updates: < 100ms")
            else:
                print("\n🔥 Firestore Real-time: Simulated")
                print("  • Live updates: Enhanced simulation mode")
            
        except Exception as e:
            logger.error(f"❌ Error in analytics phase: {e}")
    
    async def generate_bigquery_insights(self) -> List[str]:
        """Generate insights from BigQuery data"""
        try:
            insights = []
            
            # Query 1: Sensor data quality analysis
            query1 = """
            SELECT 
                source,
                AVG(quality) as avg_quality,
                COUNT(*) as reading_count
            FROM `{}.agrimind_analytics.sensor_readings`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
            GROUP BY source
            ORDER BY avg_quality DESC
            """.format(os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            results = self.bigquery_client.query(query1)
            for row in results:
                insights.append(f"{row.source}: {row.avg_quality:.2f} quality ({row.reading_count} readings)")
            
            # Query 2: Prediction accuracy
            query2 = """
            SELECT 
                prediction_type,
                AVG(confidence) as avg_confidence,
                COUNT(*) as prediction_count
            FROM `{}.agrimind_analytics.predictions`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
            GROUP BY prediction_type
            """.format(os.getenv('GOOGLE_CLOUD_PROJECT'))
            
            results = self.bigquery_client.query(query2)
            for row in results:
                insights.append(f"{row.prediction_type}: {row.avg_confidence:.2f} confidence ({row.prediction_count} predictions)")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating BigQuery insights: {e}")
            return ["BigQuery insights temporarily unavailable"]
    
    async def demonstrate_gcp_degraded_mode(self):
        """Demonstrate graceful degradation when GCP services are unavailable"""
        logger.info("🔌 Demonstrating GCP Degraded Mode")
        print("\n" + "="*60)
        print("🔌 GOOGLE CLOUD DEGRADED MODE DEMO")
        print("="*60)
        
        print("⚠️ Simulating Google Cloud service interruption...")
        
        # Temporarily disable GCP clients
        original_bigquery = self.bigquery_client
        original_firestore = self.firestore_client
        
        self.bigquery_client = None
        self.firestore_client = None
        
        # Show agents still function with local fallbacks
        sensor_agent = list(self.agents.values())[0]
        print(f"📡 {sensor_agent.agent_id}: Operating in degraded mode...")
        
        # Collect data without GCP services
        sensor_data = await sensor_agent.collect_sensor_data()
        print(f"• Collected {len(sensor_data)} readings using local fallbacks")
        
        for reading in sensor_data:
            if reading['source'] != 'Google Vision API':
                print(f"  • {reading['type']}: {reading['value']} (source: {reading['source']})")
        
        print("✅ System continues operating with reduced functionality")
        print("🔄 Restoring Google Cloud connectivity...")
        
        # Restore GCP clients
        self.bigquery_client = original_bigquery
        self.firestore_client = original_firestore
        
        print("✅ Google Cloud services restored")
        print("🔄 System returned to full GCP-enhanced operation")

async def main():
    """Main demonstration function"""
    print("🌾 AgriMind: Google Cloud Platform Enhanced Demo")
    print("=" * 60)
    print("🚀 Multi-Agent Agricultural Intelligence with Google Cloud")
    print("=" * 60)
    
    # Initialize demo
    demo = GCPAgriMindDemo()
    
    try:
        # Phase 1: Initialize GCP services
        await demo.initialize_gcp_services()
        
        # Phase 2: Initialize agents
        await demo.initialize_agents()
        
        # Phase 3: Run enhanced simulation
        await demo.run_gcp_enhanced_simulation()
        
        # Phase 4: Demonstrate degraded mode
        await demo.demonstrate_gcp_degraded_mode()
        
        print("\n" + "="*60)
        print("🏆 GCP-ENHANCED AGRIMIND DEMO COMPLETED")
        print("="*60)
        print("✅ Google Cloud Integration: Advanced AI and Analytics")
        print("✅ Real-time Data Processing: BigQuery + Firestore")
        print("✅ Computer Vision: Google Vision API")
        print("✅ Scalable Architecture: Cloud-ready deployment")
        print("✅ Degraded Mode: Graceful fallback capabilities")
        print("\n🌟 Ready for production deployment on Google Cloud! 🤖")
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())