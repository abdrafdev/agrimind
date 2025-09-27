# AgriMind System Architecture Diagram Description

This document provides a structured description of the AgriMind system architecture, formatted for easy conversion to a visual diagram with boxes, arrows, and labels.

## System Overview Layout

### Top-Level Components (Main Boxes)

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgriMind System                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────│
│  │ Data Sources│  │    Agents   │  │ Message Bus │  │ Ledger  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────│
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Cache    │  │     DAL     │  │Mode Control │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Data Sources Layer

### Box: Data Sources
**Components:**
- **Sub-box: Datasets (Primary)**
  - sensor.json (field/IoT readings: soil moisture, temperature, humidity, NDVI)
  - weather.csv (historical/forecast weather data)
  - resources.json (machinery, labor, inputs inventory with costs)
  - market.csv (historical and current market prices for commodities)

- **Sub-box: External APIs (Secondary)**
  - WeatherAPI (weather forecasting service)
  - OpenWeather (alternative weather service)
  - AgroMonitoring (satellite/agricultural data)
  - StormGlass (marine/weather data)

- **Sub-box: Mock Generators (Fallback)**
  - Synthetic Sensor Generator
  - Synthetic Weather Generator
  - Synthetic Resources Generator
  - Synthetic Market Generator

**Labels:**
- Priority Order: Dataset → API → Mock
- Fallback Chain: Primary → Secondary → Tertiary

## 2. Data Access Layer (DAL)

### Box: Data Access Layer + Priority Controller
**Components:**
- Priority Controller (implements Dataset → API → Mock priority)
- Domain-Specific Adapters:
  - Sensor Adapter
  - Weather Adapter
  - Resources Adapter
  - Market Adapter

**Arrows:**
- DAL → Datasets [Priority 1: First attempt]
- DAL → External APIs [Priority 2: If dataset unavailable/stale]
- DAL → Mock Generators [Priority 3: Last fallback]

**Labels:**
- Returns: {value, metadata.source, metadata.ttl, last_updated}
- metadata.source ∈ {dataset, api:<provider>, mock}

## 3. Caching Layer

### Box: Caching Layer (Read-Through + TTL)
**Components:**
- sensor_cache (TTL: seconds to minutes)
- weather_cache (TTL: minutes to hours)
- resources_cache (TTL: hours)
- market_cache (TTL: minutes)

**Cache Keys:**
- weather:{location}:{date_range}
- sensor:{field}:{timestamp_bucket}
- resources:inventory:v1
- market:{commodity}:{market}:{date_bucket}

**Arrows:**
- Agents → Cache [read-through get()]
- Cache (miss) → DAL [fetch]
- DAL → Cache [set(key, value, TTL, metadata.source)]

## 4. Agents Layer

### Box: Sensor Agent
**Responsibilities:**
- Collect and normalize sensor readings
- Aggregate weather data (optional)

**Inputs (via Cache/DAL):**
- sensor.json (primary)
- weather.csv or API (enrichment)

**Outputs (via Message Bus):**
- sensor.data topic
- weather.data topic (if applicable)

**Arrows:**
- Sensor Agent → Cache → DAL → Data Sources
- Sensor Agent → Message Bus [publish sensor.data]

### Box: Prediction Agent
**Responsibilities:**
- Generate yield forecasts
- Calculate risk indices
- Recommend irrigation/fertilization actions

**Subscriptions:**
- sensor.data
- weather.data

**Inputs (via Cache/DAL):**
- weather.csv/API for forecasting

**Outputs:**
- predictions.out (yield forecast, risk scores, recommendations)

**Arrows:**
- Message Bus → Prediction Agent [sensor.data, weather.data]
- Prediction Agent → Message Bus [publish predictions.out]

### Box: Resource Agent
**Responsibilities:**
- Create resource allocation plans
- Initiate market negotiations
- Schedule operations

**Subscriptions:**
- predictions.out

**Inputs (via Cache/DAL):**
- resources.json (inventory, availability, costs)

**Market Interactions:**
- Sends trade.proposals
- Receives market.quotes

**Outputs:**
- resources.plan (schedules, machinery use, irrigation plans)
- trade.proposals (procurement/sales)

**Arrows:**
- Message Bus → Resource Agent [predictions.out]
- Resource Agent → Message Bus [resources.plan, trade.proposals]
- Resource Agent ↔ Message Bus [trade negotiations]

### Box: Market Agent
**Responsibilities:**
- Price discovery and quoting
- Process trade proposals
- Settlement processing

**Inputs (via Cache/DAL):**
- market.csv/API (prices, basis, volatility)

**Subscriptions:**
- trade.proposals

**Outputs:**
- market.prices (periodic broadcast)
- market.quotes (proposal responses)
- trade.settlements (confirmed trades)

**Arrows:**
- Market Agent → Message Bus [market.prices]
- Message Bus → Market Agent [trade.proposals]
- Market Agent → Message Bus [market.quotes, trade.settlements]

## 5. Message Bus (Pub/Sub)

### Box: Message Bus
**Topics and Flow:**

**Data Topics:**
- sensor.data: Sensor Agent → Prediction Agent
- weather.data: Sensor Agent → Prediction Agent
- predictions.out: Prediction Agent → Resource Agent

**Resource Topics:**
- resources.plan: Resource Agent → [Monitoring, Ledger]
- resources.request: Resource Agent → [Internal systems]

**Market Topics:**
- market.prices: Market Agent → [Resource Agent, Monitoring]
- trade.proposals: Resource Agent → Market Agent
- market.quotes: Market Agent → Resource Agent
- trade.settlements: Market Agent → [Resource Agent, Ledger]

**System Topics:**
- system.health: Mode Controller → All Agents
- ledger.events: All Agents → Ledger Service

**Arrows:**
- Show pub/sub relationships between all agents
- Label each arrow with topic name and direction

## 6. Mode/Health Controller

### Box: Mode/Health Controller
**Responsibilities:**
- Monitor API connectivity
- Monitor filesystem access
- Switch between Normal/Degraded modes

**Monitors:**
- Filesystem: sensor.json, weather.csv, resources.json, market.csv
- APIs: DNS, HTTP status, latency
- System health metrics

**Outputs:**
- system.health events (online/offline status)

**Mode Effects:**
- **Normal Mode:** Full Dataset → API → Mock chain
- **Degraded Mode:** Dataset-only, cache fallback

**Arrows:**
- Mode Controller → Message Bus [system.health]
- Mode Controller → DAL [mode restrictions]

## 7. Ledger Service

### Box: Ledger Service (Transaction/Negotiation Log)
**Storage:**
- Append-only store (ledger.json or SQLite)
- Event-sourced architecture

**Subscriptions:**
- trade.proposals, market.quotes, trade.settlements
- predictions.out, resources.plan (audit trail)
- ledger.events (lifecycle events)

**Event Types:**
- NegotiationStarted {negotiation_id, initiator, counterparty, intent, timestamp}
- QuoteProvided {negotiation_id, price, quantity, terms, agent, timestamp}
- CounterOffer {negotiation_id, price, quantity, terms, agent, timestamp}
- QuoteAccepted {negotiation_id, agent, timestamp}
- SettlementRecorded {negotiation_id, instrument, quantity, price, timestamp}
- PlanPublished {plan_id, agent, summary, timestamp}
- PredictionPublished {prediction_id, horizon, confidence, timestamp}

**Integrity:**
- hash(prev_hash + event_payload)
- Sequential numbering
- Mode tracking (normal/degraded)

**Arrows:**
- Message Bus → Ledger Service [all subscribed events]
- Ledger Service → Storage [append-only writes]

## Data Flow Diagrams

### Normal Mode Flow
```
1. Sensor Data Collection:
   Sensor Agent → Cache → DAL → sensor.json → Sensor Agent → Message Bus [sensor.data]

2. Weather Data (if dataset stale):
   Prediction Agent → Cache → DAL → weather.csv
   If stale: DAL → WeatherAPI → Cache → Prediction Agent
   Fallback: DAL → Mock Generator

3. Prediction Generation:
   Message Bus [sensor.data, weather.data] → Prediction Agent → Message Bus [predictions.out]

4. Resource Planning:
   Message Bus [predictions.out] → Resource Agent → Cache → DAL → resources.json
   Resource Agent → Message Bus [trade.proposals]

5. Market Interaction:
   Message Bus [trade.proposals] → Market Agent → Cache → DAL → market.csv/API
   Market Agent → Message Bus [market.quotes] → Resource Agent
   Upon agreement: Market Agent → Message Bus [trade.settlements]

6. Ledger Recording:
   Message Bus [all trade events] → Ledger Service → Storage [append]
```

### Degraded Mode Flow
```
1. Mode Detection:
   Mode Controller detects API failures → Message Bus [system.health offline=true]

2. Restricted Data Access:
   All DAL requests → Datasets only (no API, no Mock)
   Cache serves existing data with degraded metadata

3. Agent Adaptation:
   - Predictions marked with lower confidence
   - Resource plans use cached market data
   - Trade proposals may be suspended
   - All events logged with mode=degraded
```

## System Characteristics

### Performance Labels
- **Latency:** Cache-first design minimizes data fetch times
- **Throughput:** Message Bus enables parallel agent processing
- **Resilience:** Multi-tier fallback ensures continuous operation

### Security Labels
- **Access Control:** Agents read-only to datasets, write-only to message bus
- **Audit Trail:** Complete transaction history in ledger
- **Data Integrity:** Hash-chained event log

### Scalability Labels
- **Horizontal:** Each agent type can scale independently
- **Vertical:** Cache and DAL can be scaled per data type
- **Message Bus:** Topic-based routing supports agent multiplication

## Visual Diagram Instructions

1. **Draw main system boundary** containing all components
2. **Position Data Sources at top** with three sub-levels
3. **Place DAL and Cache in middle tier** showing data flow priority
4. **Arrange Agents in center** with clear pub/sub connections
5. **Show Message Bus as central hub** with labeled topic flows
6. **Position Ledger and Mode Controller** as system services
7. **Use different arrow styles** for:
   - Data flow (solid arrows)
   - Pub/sub (dashed arrows)
   - Control/monitoring (dotted arrows)
8. **Color code by priority**:
   - Primary paths (green)
   - Secondary paths (yellow)
   - Fallback paths (red)
   - System/control (blue)

## Key Annotations for Diagram

- **Priority Order:** Dataset → API → Mock (prominently displayed)
- **Mode Switch:** Normal ↔ Degraded (with trigger conditions)
- **Cache TTLs:** Per-domain timing annotations
- **Message Topics:** Clear labeling of all pub/sub topics
- **Event Types:** Key ledger event categories
- **Failure Paths:** How system degrades gracefully

This architecture ensures robust agricultural intelligence with multiple fallback layers, complete auditability, and graceful degradation capabilities.