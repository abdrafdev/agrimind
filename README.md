# 🌾 AgriMind: Collaborative Farm Intelligence Network

**NATIONAL AGENTIC AI HACKATHON Project**

A multi-agent swarm system where different AI agents collaborate to help farmers optimize their operations through intelligent resource sharing, predictive analytics, and market integration.

## 🚀 System Overview

AgriMind demonstrates a sophisticated multi-agent system built with the Google Agentic Development Kit (Google ADK) where specialized AI agents work together to create a collaborative farm intelligence network:

- **Sensor Agents** 📊 - Collect environmental data and sell it to other agents
- **Prediction Agents** 🔮 - Buy sensor data and generate farming predictions
- **Resource Allocation Agents** 🔄 - Negotiate and optimize resource sharing between farms
- **Market Agents** 💰 - Track crop prices and connect farmers with buyers

## ✨ Key Features

### 🤝 Agent Collaboration
- **Data Economy**: Sensor agents sell data to prediction agents
- **Resource Sharing**: Farms share water, equipment, and labor through negotiations
- **Market Integration**: Real-time price tracking and buyer-seller matching
- **Transaction Logging**: Complete audit trail of all agent interactions

### 🔌 Degraded Mode Operation
- **Offline Capability**: System continues operating without internet
- **Cached Data**: Uses local cached data when APIs are unavailable
- **Rule-based Fallbacks**: Simple heuristics when ML models can't run
- **Graceful Degradation**: Maintains functionality with reduced confidence

### 📡 Real-time Intelligence
- **Live Data Integration**: Weather, soil, and market data from external APIs
- **Predictive Analytics**: ML models for irrigation, pest risk, and harvest timing
- **Dynamic Pricing**: Market-driven resource allocation and crop pricing
- **Automated Negotiations**: Agents negotiate resources and resolve conflicts

## 🏗️ Architecture

```
AgriMind System Architecture

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Farm Alpha    │    │   Farm Beta     │    │   Farm Gamma    │
│                 │    │                 │    │                 │
│ 📊 Sensor Agent │◄──►│ 📊 Sensor Agent │◄──►│ 📊 Sensor Agent │
│ 🔮 Predict Agent│    │ 🔮 Predict Agent│    │ 🔮 Predict Agent│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                ┌────────────────────────────────────┐
                │         Central Services           │
                │                                    │
                │ 🔄 Resource Allocation Agent       │
                │ 💰 Market Intelligence Agent       │
                └────────────────────────────────────┘
                                 │
                    ┌─────────────────────────┐
                    │   External Services     │
                    │                         │
                    │ 🌐 Weather APIs        │
                    │ 🌱 Soil Data APIs      │
                    │ 📈 Market Price APIs   │
                    └─────────────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager  
- Internet connection (for API data, optional)

### Quick Start

1. **Clone and navigate to the project:**
```bash
cd agrimind
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Prepare Official Datasets (Optional):**
Place the official hackathon datasets in a `datasets/` folder:
```bash
mkdir datasets
# Copy your dataset files:
# - farm_sensor_data_tehsil_with_date.json
# - weather_data_tehsil.csv
# - farm_resources.json
# - market_prices.csv
```

4. **Run the demo:**
```bash
# Hybrid mode (datasets + APIs + mock fallback) - DEFAULT:
python agrimind_demo.py
# or explicitly:
python agrimind_demo.py hybrid

# Offline mode (datasets only, no API calls):
python agrimind_demo.py offline

# Mock mode (synthetic data only, no datasets or APIs):
python agrimind_demo.py mock
```

5. **Verify all modes work (optional):**
```bash
# Test all demo modes automatically:
python test_demo_modes.py
```

### Configuration

1. **Official Datasets Integration:**
The system supports official hackathon datasets with the following priority:
**Dataset → API → Mock/Cache**

**Dataset Files Expected:**
- `datasets/farm_sensor_data_tehsil_with_date.json` - Sensor readings (soil moisture, temperature, humidity, pest detection)
- `datasets/weather_data_tehsil.csv` - Historical weather data for predictions
- `datasets/farm_resources.json` - Farm resource availability (water, equipment, fertilizer, labor)
- `datasets/market_prices.csv` - Historical crop market prices and trends

**Data Source Logging:**
All agents log which data source they used with DATA_SOURCE_METADATA tags:
```
📊 SensorAgent sensor_farm_1 DATA_SOURCE_METADATA: dataset (farm_sensor_data_tehsil_with_date.json)
🌤️ PredictionAgent prediction_farm_1 DATA_SOURCE_METADATA: weather dataset (weather_data_tehsil.csv, 1801 records, confidence=0.9)
💾 ResourceAgent resource_central DATA_SOURCE_METADATA: loaded from dataset (farm_resources.json)
📈 MarketAgent market_central DATA_SOURCE_METADATA: tomatoes dataset (42 records); corn mock (48 records)
```

2. **API Keys (Optional):**
Create a `.env` file with your API keys:
```env
WEATHER_API_KEY=your_weatherapi_key
AGRO_API_KEY=your_agromonitoring_key
OPENWEATHER_API_KEY=your_openweather_key
```

3. **System Configuration:**
Edit `config/agrimind_config.yaml` for custom settings (auto-generated on first run).

## 🎮 Demo Walkthrough

The demo showcases a complete collaboration cycle:

### Phase 1: Sensor Data Collection 📊
- Sensor agents collect environmental data (soil moisture, temperature, humidity, pest detection)
- Data is published to the marketplace with pricing
- Real API integration with fallback to mock data

### Phase 2: Prediction Generation 🔮
- Prediction agents purchase sensor data from multiple sources
- Generate irrigation needs, weather forecasts, pest risk assessments
- ML models with confidence scoring and validation

### Phase 3: Resource Allocation 🔄
- Resource agent receives requests for water, equipment, labor
- Negotiates optimal allocation based on priority and availability
- Handles conflicts through alternative scheduling and pricing

### Phase 4: Market Operations 💰
- Market agent tracks real-time crop prices with trend analysis
- Matches farmers with buyers based on quality and quantity needs
- Facilitates negotiations and commission-based transactions

### Phase 5: Degraded Mode Demo 🔌
- Simulates network connectivity loss
- Shows continued operation using cached data and rule-based fallbacks
- Demonstrates system resilience and offline capability

## 📊 Sample Output

```
🌾 AgriMind: Collaborative Farm Intelligence Network
   NATIONAL AGENTIC AI HACKATHON Demo
============================================================
🚀 Initializing AgriMind System...
✅ Configuration validation passed
🌾 Setting up farm_1 (tomatoes farm)
🌾 Setting up farm_2 (corn farm)
🌾 Setting up farm_3 (lettuce farm)
✅ Initialized 8 agents
   📊 Sensor Agents: 3
   🔮 Prediction Agents: 3
   🔄 Resource Agents: 1
   💰 Market Agents: 1

============================================================
🎬 Starting AgriMind Collaboration Demo Cycle
============================================================

📡 Phase 1: Sensor Data Collection
   📊 sensor_farm_1: Collecting environmental data...
   📊 sensor_farm_1: Collected 4 sensor readings
      • soil_moisture: 0.42 volumetric (quality: 0.85)
      • temperature: 24.30 celsius (quality: 0.85)
      • humidity: 58.20 percentage (quality: 0.85)
      • pest_detection: 0.15 confidence (quality: 0.80)
   📊 sensor_farm_1: Published data to marketplace

🔮 Phase 2: Prediction Generation
   🔮 prediction_farm_1: Analyzing data and generating predictions...
   🔮 prediction_farm_1: Generated 4 predictions
      • irrigation_need: 0.60 (confidence: 0.75)
      • weather_forecast: 25.10 (confidence: 0.60)
      • pest_risk: 0.25 (confidence: 0.70)
      • harvest_timing: 85.30 (confidence: 0.70)

🔄 Phase 3: Resource Allocation
   🔄 resource_central: Processing resource requests...
      • Processed water request from sensor_farm_1: 1250L
      • Processed water request from sensor_farm_2: 1800L
      • Water system utilization: 30.5%

💰 Phase 4: Market Operations
   💰 market_central: Processing market activities...
      • Current market prices:
        tomatoes: $3.42/kg 📈
        corn: $0.87/kg ➡️
        lettuce: $2.95/kg 📉
      • Registered sell offer: 500kg tomatoes at $3.25/kg

📈 Phase 5: Collaboration Results
   📈 System-wide collaboration results:
      • sensor_farm_1: 2 transactions, balance: $1001.50
      • prediction_farm_1: 1 transactions, balance: $996.50
      • resource_central: 2 transactions, balance: $5090.00
      • Total system transactions: 5
      • Messages in system: 12
      • Total sensor readings collected: 36
      • Total predictions generated: 12
```

## 🔧 System Components

### Sensor Agents (`agents/sensor_agent.py`)
- **Environmental Monitoring**: Soil moisture, temperature, humidity, pest detection
- **API Integration**: Weather APIs with degraded mode fallback
- **Data Marketplace**: Pricing and transaction management
- **Quality Assurance**: Data quality scoring and source tracking

### Prediction Agents (`agents/prediction_agent.py`)
- **Data Purchasing**: Automated data acquisition from sensor agents
- **ML Models**: Irrigation need, weather forecast, pest risk, harvest timing
- **Confidence Scoring**: Prediction reliability assessment
- **Rule-based Fallbacks**: Simple heuristics for degraded mode

### Resource Allocation Agents (`agents/resource_agent.py`)
- **Multi-resource Management**: Water, fertilizer, equipment, labor
- **Scheduling Optimization**: Time-slot allocation with conflict resolution
- **Negotiation System**: Alternative proposals and price adjustments
- **Efficiency Tracking**: Resource utilization and performance metrics

### Market Agents (`agents/market_agent.py`)
- **Price Tracking**: Real-time market data with trend analysis
- **Buyer-Seller Matching**: Quality, quantity, and location-based matching
- **Transaction Facilitation**: Commission-based trade processing
- **Market Intelligence**: Volatility analysis and trading recommendations

## 📁 Project Structure

```
agrimind/
├── agents/                 # All agent implementations
│   ├── __init__.py
│   ├── base_agent.py      # Foundation agent class
│   ├── sensor_agent.py    # Environmental data collection
│   ├── prediction_agent.py # ML predictions and analysis
│   ├── resource_agent.py  # Resource allocation and negotiation
│   └── market_agent.py    # Market intelligence and trading
├── config/                # Configuration management
│   ├── __init__.py
│   └── config.py         # System configuration
├── data/                 # Cached data and persistence
├── logs/                 # System and transaction logs
├── tests/               # Unit tests (future)
├── requirements.txt     # Python dependencies
├── agrimind_demo.py    # Main demo script
└── README.md           # This file
```

## 🌐 API Integration

The system integrates with multiple external APIs:

### Weather Data
- **WeatherAPI.com**: Real-time weather data
- **OpenWeather**: Alternative weather source
- **Fallback**: Mock weather generation with realistic patterns

### Soil Data  
- **AgroMonitoring**: Satellite-based soil moisture data
- **Fallback**: Physics-based soil moisture simulation

### Market Data
- **Mock Market APIs**: Realistic price simulation with volatility
- **Trend Analysis**: Technical indicators and seasonal patterns

## 🔄 Degraded Mode Features

When internet connectivity is lost or APIs are unavailable:

1. **Cached Data Usage**: Recent data stored locally with timestamps
2. **Rule-based Fallbacks**: Simple heuristics for critical decisions
3. **Confidence Reduction**: Lower confidence scores for degraded data  
4. **Graceful Recovery**: Automatic restoration when connectivity returns

Example degraded mode logic:
- **Irrigation**: If soil moisture < 30% → recommend irrigation  
- **Pricing**: Use seasonal averages with high uncertainty
- **Weather**: Conservative estimates based on historical patterns

## 📊 Transaction & Logging System

### Transaction Types
- **Data Sales**: Sensor data purchases between agents
- **Resource Allocation**: Water, equipment, labor assignments
- **Market Trades**: Crop sales and buyer connections
- **Predictions**: Forecast sharing and consultation fees

### Logging Features
- **Agent Communication**: All message passing logged
- **Transaction Audit**: Complete financial transaction history
- **Performance Metrics**: Agent efficiency and system utilization
- **Error Tracking**: Degraded mode events and recovery

## 🧪 Testing & Validation

### Automated Demo Scenarios
- **Normal Operation**: Full API connectivity and agent collaboration
- **Degraded Mode**: Simulated network failures and recovery
- **Resource Conflicts**: Multiple farms competing for limited resources
- **Market Fluctuations**: Price volatility and trading opportunities

### Performance Metrics
- **Transaction Throughput**: Messages processed per minute
- **Prediction Accuracy**: ML model performance tracking
- **Resource Utilization**: Efficiency of resource allocation
- **Network Resilience**: Uptime during connectivity issues

## 🚀 Future Enhancements

### Phase 2 Development
- **Advanced ML Models**: Deep learning for more accurate predictions
- **IoT Integration**: Real sensor hardware integration
- **Blockchain Transactions**: Immutable transaction ledger
- **Mobile Interface**: Farmer mobile app for monitoring

### Scalability Features
- **Multi-region Support**: Distributed agent networks
- **Load Balancing**: Dynamic agent scaling
- **Real-time Analytics**: Dashboard and monitoring tools
- **API Marketplace**: Third-party data source integration

## 🤝 Contributing

This is a hackathon project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is created for the National Agentic AI Hackathon. See individual API terms for external service usage.

## 🏆 Hackathon Compliance

### Required Features ✅
- ✅ **Multi-agent swarm system** - 4 different agent types with specialization
- ✅ **Agent collaboration** - Data economy with transactions between agents  
- ✅ **Google ADK integration** - Built on Google Agentic Development Kit framework
- ✅ **Transaction/negotiation logic** - Resource allocation with conflict resolution
- ✅ **Degraded mode** - Offline operation with cached data and rule-based fallbacks
- ✅ **Demo function** - Complete simulation showing one cycle of collaboration
- ✅ **Modular code** - Clean separation of agent types and responsibilities
- ✅ **Logging** - Comprehensive transaction and reasoning logs

### Innovation Highlights 🌟
- **Agent-to-Agent Economy**: Real marketplace dynamics between AI agents
- **Predictive Resource Allocation**: ML-driven optimization of farm resources  
- **Resilient Architecture**: Continues operating even when internet fails
- **Real-world Integration**: Uses actual agricultural APIs and market data
- **Collaborative Intelligence**: Agents specialize but share knowledge for mutual benefit

---

**Built with ❤️ for the National Agentic AI Hackathon**

*AgriMind demonstrates the future of collaborative AI in agriculture, where intelligent agents work together to optimize farming operations while maintaining resilience and scalability.*