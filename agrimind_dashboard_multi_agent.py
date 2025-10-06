#!/usr/bin/env python3
"""
AgriMind Multi-Agent Dashboard
Shows how agents collaborate to help small and medium-scale farmers
"""
import json
import time
import random
import threading
import webbrowser
import socket
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from agrimind_multi_agent_system import agrimind_system, ConnectivityMode, AgentType
from real_time_data_integration import RealTimeDataIntegrator

class AgriMindMultiAgentHandler(BaseHTTPRequestHandler):
    # Initialize real-time data integrator
    data_integrator = RealTimeDataIntegrator()
    
    def log_message(self, format, *args):
        """Clean logging with timestamps"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def do_GET(self):
        """Handle all GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard()
            elif self.path == '/api/system_status':
                self.serve_api('system_status')
            elif self.path == '/api/agent_details':
                self.serve_api('agent_details')
            elif self.path == '/api/agent_interactions':
                self.serve_api('agent_interactions')
            elif self.path == '/api/farmer_benefits':
                self.serve_api('farmer_benefits')
            elif self.path == '/api/transactions':
                self.serve_api('transactions')
            elif self.path == '/api/connectivity_toggle':
                self.serve_api('connectivity_toggle')
            elif self.path == '/api/real_time_weather':
                self.serve_api('real_time_weather')
            elif self.path == '/api/real_time_market':
                self.serve_api('real_time_market')
            elif self.path == '/api/real_time_comprehensive':
                self.serve_api('real_time_comprehensive')
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"❌ Error handling {self.path}: {e}")
            self.send_error(500, str(e))
    
    def serve_dashboard(self):
        """Serve the multi-agent dashboard HTML"""
        try:
            html = self.get_dashboard_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error serving dashboard: {e}")
            self.send_error(500, str(e))
    
    def serve_api(self, endpoint):
        """Serve JSON API data"""
        try:
            if endpoint == 'system_status':
                data = agrimind_system.get_system_status()
            elif endpoint == 'agent_details':
                data = agrimind_system.get_agent_details()
            elif endpoint == 'agent_interactions':
                data = self.get_agent_interactions()
            elif endpoint == 'farmer_benefits':
                data = self.get_farmer_benefits()
            elif endpoint == 'transactions':
                data = self.get_recent_transactions()
            elif endpoint == 'connectivity_toggle':
                data = self.toggle_connectivity_mode()
            elif endpoint == 'real_time_weather':
                data = self.data_integrator.get_real_weather_data()
            elif endpoint == 'real_time_market':
                data = self.data_integrator.get_real_market_data()
            elif endpoint == 'real_time_comprehensive':
                data = self.data_integrator.get_comprehensive_real_time_data()
            else:
                data = {'error': 'Unknown endpoint'}
            
            json_response = json.dumps(data, indent=2, default=str)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(json_response)))
            self.end_headers()
            self.wfile.write(json_response.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ API error for {endpoint}: {e}")
            error_response = json.dumps({'error': str(e), 'endpoint': endpoint})
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(error_response)))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
    
    def get_agent_interactions(self):
        """Get current agent interactions and collaboration"""
        interactions = agrimind_system.simulate_agent_interactions()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_interactions': len(interactions),
            'collaboration_examples': [
                {
                    'id': 'sensor-prediction-collab',
                    'title': 'Data Purchase & Weather Forecasting',
                    'description': 'Sensor agents sell environmental data to prediction agents for accurate weather forecasting',
                    'participants': ['sensor_field_A', 'weather_ai_001'],
                    'farmer_benefit': 'Get precise irrigation timing recommendations',
                    'economic_value': '$15.50 data transaction + $280 water savings',
                    'status': 'active'
                },
                {
                    'id': 'prediction-resource-collab',
                    'title': 'Forecast-Based Resource Optimization',
                    'description': 'Weather predictions drive smart irrigation scheduling and resource allocation',
                    'participants': ['weather_ai_001', 'irrigation_001'],
                    'farmer_benefit': 'Automated irrigation saves 25% water usage',
                    'economic_value': '$450 monthly water cost reduction',
                    'status': 'active'
                },
                {
                    'id': 'market-timing-collab',
                    'title': 'Market Intelligence & Selling Optimization',
                    'description': 'Market agents track prices and connect farmers with best buyers',
                    'participants': ['market_crops_001'],
                    'farmer_benefit': 'Sell crops at optimal times for maximum profit',
                    'economic_value': '15-20% higher revenue per harvest',
                    'status': 'active'
                },
                {
                    'id': 'resource-sharing-collab',
                    'title': 'Inter-Farm Resource Sharing',
                    'description': 'Resource agents negotiate equipment and water sharing between nearby farms',
                    'participants': ['irrigation_001', 'equipment_001'],
                    'farmer_benefit': 'Access expensive equipment without ownership',
                    'economic_value': '$2,400 equipment rental savings annually',
                    'status': 'active'
                }
            ],
            'recent_negotiations': [
                {
                    'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                    'type': 'resource_sharing',
                    'description': 'Farm A requested 500L water from Farm B',
                    'outcome': 'Approved at $0.08/L emergency rate',
                    'farmer_impact': 'Prevented crop loss during pump failure'
                },
                {
                    'timestamp': (datetime.now() - timedelta(minutes=12)).isoformat(),
                    'type': 'market_timing',
                    'description': 'Market agent recommended delaying tomato sale',
                    'outcome': 'Price increased 8% in 3 days',
                    'farmer_impact': '$840 additional revenue on 2.5 ton harvest'
                }
            ]
        }
    
    def get_farmer_benefits(self):
        """Show concrete benefits to farmers"""
        return {
            'timestamp': datetime.now().isoformat(),
            'problem_solutions': {
                'unpredictable_weather': {
                    'challenge': 'Farmers struggle with unpredictable weather patterns',
                    'agent_solution': 'Weather Prediction Agents analyze multiple data sources',
                    'farmer_benefit': 'Get 7-day forecasts with 88% accuracy',
                    'economic_impact': '$1,200 annual crop loss prevention',
                    'agent_responsible': 'weather_ai_001'
                },
                'limited_resources': {
                    'challenge': 'Small farms cannot afford expensive equipment',
                    'agent_solution': 'Resource Allocation Agents enable equipment sharing',
                    'farmer_benefit': 'Access to $50K+ equipment for $25/hour',
                    'economic_impact': '$15,000 annual equipment cost savings',
                    'agent_responsible': 'equipment_001'
                },
                'market_volatility': {
                    'challenge': 'Farmers sell at wrong times, missing profit opportunities',
                    'agent_solution': 'Market Agents track prices and identify optimal selling windows',
                    'farmer_benefit': 'Sell crops when prices are 15-25% higher',
                    'economic_impact': '$3,500 additional revenue per harvest cycle',
                    'agent_responsible': 'market_crops_001'
                },
                'isolation_insights': {
                    'challenge': 'Farmers work in isolation without collaborative insights',
                    'agent_solution': 'Sensor Agents create network of shared agricultural intelligence',
                    'farmer_benefit': 'Learn from neighboring farms\' success patterns',
                    'economic_impact': '12% average yield improvement',
                    'agent_responsible': 'sensor_field_A, sensor_field_B'
                }
            },
            'success_metrics': {
                'water_savings': '28%',
                'yield_improvement': '15%',
                'cost_reduction': '22%',
                'revenue_increase': '18%',
                'time_savings': '35%',
                'risk_reduction': '45%'
            },
            'accessibility_features': {
                'offline_mode': 'Works with limited connectivity using cached data',
                'low_cost': 'Virtual economy makes services affordable for small farmers',
                'simple_interface': 'Easy-to-understand recommendations and alerts',
                'multilingual': 'Supports local languages (future feature)',
                'mobile_friendly': 'Works on smartphones for field access'
            }
        }
    
    def get_recent_transactions(self):
        """Get recent agent transactions"""
        recent_txs = agrimind_system.transactions[-20:] if agrimind_system.transactions else []
        
        formatted_txs = []
        for tx in recent_txs:
            formatted_txs.append({
                'id': tx.id,
                'from_agent': tx.from_agent,
                'to_agent': tx.to_agent,
                'type': tx.transaction_type.value,
                'amount': tx.amount,
                'status': tx.status,
                'timestamp': tx.timestamp.isoformat(),
                'reasoning': tx.reasoning,
                'data_summary': self._summarize_transaction_data(tx.data_payload)
            })
        
        return {
            'transactions': formatted_txs,
            'summary': {
                'total_value': sum(tx.amount for tx in recent_txs),
                'successful_rate': len([tx for tx in recent_txs if tx.status == 'completed']) / max(len(recent_txs), 1),
                'most_active_agent': self._get_most_active_agent(recent_txs)
            }
        }
    
    def _summarize_transaction_data(self, data_payload):
        """Create human-readable summary of transaction data"""
        if 'data_type' in data_payload:
            return f"Sensor data: {data_payload['data_type']}"
        elif 'resource' in data_payload:
            return f"Resource: {data_payload['amount']} units of {data_payload['resource']}"
        elif 'crop' in data_payload:
            return f"Market advice: {data_payload['crop']} selling recommendation"
        else:
            return "Service transaction"
    
    def _get_most_active_agent(self, transactions):
        """Find most active agent in recent transactions"""
        if not transactions:
            return "N/A"
        
        agent_activity = {}
        for tx in transactions:
            agent_activity[tx.from_agent] = agent_activity.get(tx.from_agent, 0) + 1
        
        return max(agent_activity, key=agent_activity.get) if agent_activity else "N/A"
    
    def toggle_connectivity_mode(self):
        """Toggle system connectivity mode for demo"""
        current_mode = agrimind_system.connectivity_mode
        
        if current_mode == ConnectivityMode.ONLINE:
            new_mode = ConnectivityMode.DEGRADED
        elif current_mode == ConnectivityMode.DEGRADED:
            new_mode = ConnectivityMode.OFFLINE
        else:
            new_mode = ConnectivityMode.ONLINE
        
        agrimind_system.set_system_connectivity(new_mode)
        
        return {
            'previous_mode': current_mode.value,
            'new_mode': new_mode.value,
            'timestamp': datetime.now().isoformat(),
            'impact': self._get_mode_impact_description(new_mode)
        }
    
    def _get_mode_impact_description(self, mode):
        """Get description of connectivity mode impact"""
        descriptions = {
            ConnectivityMode.ONLINE: 'Full functionality - Real-time data sharing and ML predictions',
            ConnectivityMode.DEGRADED: 'Reduced functionality - Using cached data with limited updates',
            ConnectivityMode.OFFLINE: 'Offline mode - Rule-based decisions using historical data'
        }
        return descriptions.get(mode, 'Unknown mode')
    
    def get_dashboard_html(self):
        """Generate the comprehensive multi-agent dashboard HTML"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AgriMind Multi-Agent Swarm - Helping Small & Medium Farmers</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .problem-statement {
            background: rgba(255,100,100,0.2);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            border-left: 5px solid #ff6b6b;
        }
        
        .solution-overview {
            background: rgba(100,255,100,0.2);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #51cf66;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .agent-card {
            position: relative;
        }
        
        .agent-status {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-online { background: #51cf66; }
        .status-degraded { background: #ffd43b; }
        .status-offline { background: #ff6b6b; }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .benefit-item {
            background: rgba(255,255,255,0.15);
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #4ecdc4;
        }
        
        .benefit-item strong {
            color: #4ecdc4;
        }
        
        .transaction-item {
            background: rgba(255,255,255,0.1);
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        .transaction-amount {
            color: #51cf66;
            font-weight: bold;
        }
        
        .controls {
            text-align: center;
            margin: 30px 0;
        }
        
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .metrics {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        
        .metric {
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            margin: 5px;
            min-width: 120px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4ecdc4;
        }
        
        .collaboration-flow {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        
        .flow-step {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        
        .step-number {
            background: #4ecdc4;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
        }
        
        .connectivity-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 25px;
            z-index: 1000;
        }
        
        .auto-refresh {
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .problem-tag {
            background: #ff6b6b;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin: 2px;
            display: inline-block;
        }
        
        .solution-tag {
            background: #51cf66;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin: 2px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="connectivity-indicator" id="connectivity-status">
        🟢 Online Mode
    </div>
    
    <div class="container">
        <div class="header">
            <h1>🌾 AgriMind Multi-Agent Swarm System</h1>
            <p style="font-size: 1.2em; margin-top: 10px;">Empowering Small & Medium-Scale Farmers Through AI Agent Collaboration</p>
            
            <div class="problem-statement">
                <h3>🚨 Farmer Challenges We Solve:</h3>
                <div style="margin: 15px 0;">
                    <span class="problem-tag">Unpredictable Weather</span>
                    <span class="problem-tag">Limited Resources</span>
                    <span class="problem-tag">Market Volatility</span>
                    <span class="problem-tag">Isolation from Insights</span>
                    <span class="problem-tag">Expensive Tools</span>
                </div>
            </div>
            
            <div class="solution-overview">
                <h3>✅ Our Multi-Agent Solution:</h3>
                <div style="margin: 15px 0;">
                    <span class="solution-tag">🌡️ Sensor Agents - Data Collection</span>
                    <span class="solution-tag">🧠 Prediction Agents - AI Forecasting</span>
                    <span class="solution-tag">💧 Resource Agents - Smart Allocation</span>
                    <span class="solution-tag">💹 Market Agents - Profit Optimization</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn" onclick="toggleConnectivity()">🔄 Toggle Connectivity Mode</button>
            <button class="btn" onclick="simulateCollaboration()">🤖 Simulate Agent Collaboration</button>
            <button class="btn" onclick="showFarmerBenefits()">🌾 Show Farmer Benefits</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 System Status</h3>
                <div id="system-status">Loading...</div>
            </div>
            
            <div class="card">
                <h3>🤝 How We Help Farmers</h3>
                <div id="farmer-benefits">
                    <div class="benefit-item">
                        <strong>Weather Prediction:</strong> Get 7-day forecasts with 88% accuracy to plan irrigation and planting
                    </div>
                    <div class="benefit-item">
                        <strong>Resource Sharing:</strong> Access expensive equipment for $25/hour instead of $50K purchase
                    </div>
                    <div class="benefit-item">
                        <strong>Market Timing:</strong> Sell crops when prices are 15-25% higher for maximum profit
                    </div>
                    <div class="benefit-item">
                        <strong>Collaborative Intelligence:</strong> Learn from neighboring farms' success patterns
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-bottom: 20px;">
            <h3>🔄 Agent Collaboration Flow - How It Works</h3>
            <div class="collaboration-flow">
                <div class="flow-step">
                    <div class="step-number">1</div>
                    <div>
                        <strong>🌡️ Sensor Agents collect data:</strong> Soil moisture, temperature, humidity, pest detection from your fields
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">2</div>
                    <div>
                        <strong>🧠 Prediction Agents buy data:</strong> Purchase sensor data and generate weather, pest, and yield forecasts
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">3</div>
                    <div>
                        <strong>💧 Resource Agents optimize:</strong> Use predictions to schedule irrigation, negotiate fertilizer sharing
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">4</div>
                    <div>
                        <strong>💹 Market Agents advise:</strong> Track crop prices and recommend optimal selling times
                    </div>
                </div>
                <div class="flow-step">
                    <div class="step-number">5</div>
                    <div>
                        <strong>🌾 Farmer Benefits:</strong> Get automated recommendations that save water, increase yield, and maximize profit
                    </div>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🤖 Active Agents</h3>
                <div id="agent-details">Loading agent information...</div>
            </div>
            
            <div class="card">
                <h3>💰 Recent Transactions</h3>
                <div id="recent-transactions">Loading transactions...</div>
            </div>
        </div>
        
        <div class="card">
            <h3>📈 Farmer Success Metrics</h3>
            <div class="metrics" id="success-metrics">
                <div class="metric">
                    <div class="metric-value">28%</div>
                    <div>Water Savings</div>
                </div>
                <div class="metric">
                    <div class="metric-value">15%</div>
                    <div>Yield Increase</div>
                </div>
                <div class="metric">
                    <div class="metric-value">22%</div>
                    <div>Cost Reduction</div>
                </div>
                <div class="metric">
                    <div class="metric-value">18%</div>
                    <div>Revenue Increase</div>
                </div>
                <div class="metric">
                    <div class="metric-value">45%</div>
                    <div>Risk Reduction</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh data every 5 seconds
        setInterval(refreshAllData, 5000);
        
        // Initial load
        refreshAllData();
        
        function refreshAllData() {
            refreshSystemStatus();
            refreshAgentDetails();
            refreshTransactions();
            updateConnectivityStatus();
        }
        
        function refreshSystemStatus() {
            fetch('/api/system_status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('system-status');
                    statusDiv.className = 'auto-refresh';
                    statusDiv.innerHTML = `
                        <div style="margin: 10px 0;">
                            <strong>Connectivity:</strong> ${data.connectivity_mode.toUpperCase()} 
                            ${getConnectivityIcon(data.connectivity_mode)}
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>Active Agents:</strong> ${data.agents.active}/${data.agents.total}
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>Total Economy Value:</strong> $${data.economy.total_balance.toFixed(2)}
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>Today's Transactions:</strong> ${data.economy.total_transactions}
                        </div>
                        <div style="margin: 10px 0;">
                            <strong>System Efficiency:</strong> ${data.performance.system_efficiency}%
                        </div>
                    `;
                })
                .catch(error => console.error('Error fetching system status:', error));
        }
        
        function refreshAgentDetails() {
            fetch('/api/agent_details')
                .then(response => response.json())
                .then(data => {
                    const agentDiv = document.getElementById('agent-details');
                    agentDiv.className = 'auto-refresh';
                    
                    let agentHtml = '';
                    Object.values(data).forEach(agent => {
                        const statusClass = getStatusClass(agent.connectivity);
                        agentHtml += `
                            <div class="agent-card" style="margin: 10px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                                <div class="agent-status ${statusClass}"></div>
                                <strong>${getAgentIcon(agent.type)} ${agent.id}</strong><br>
                                <small>Type: ${agent.type} | Balance: $${agent.balance}</small><br>
                                <small>Status: ${agent.current_status}</small><br>
                                <small>Earnings Today: <span style="color: #51cf66;">$${agent.earnings_today}</span></small>
                            </div>
                        `;
                    });
                    
                    agentDiv.innerHTML = agentHtml;
                })
                .catch(error => console.error('Error fetching agent details:', error));
        }
        
        function refreshTransactions() {
            fetch('/api/transactions')
                .then(response => response.json())
                .then(data => {
                    const txDiv = document.getElementById('recent-transactions');
                    txDiv.className = 'auto-refresh';
                    
                    let txHtml = `
                        <div style="margin-bottom: 15px;">
                            <strong>Total Value:</strong> <span class="transaction-amount">$${data.summary.total_value.toFixed(2)}</span><br>
                            <strong>Success Rate:</strong> ${(data.summary.successful_rate * 100).toFixed(1)}%
                        </div>
                    `;
                    
                    data.transactions.slice(-5).forEach(tx => {
                        txHtml += `
                            <div class="transaction-item">
                                <strong>${tx.from_agent}</strong> → <strong>${tx.to_agent}</strong><br>
                                <small>${tx.reasoning}</small><br>
                                <small>Amount: <span class="transaction-amount">$${tx.amount.toFixed(2)}</span></small>
                            </div>
                        `;
                    });
                    
                    txDiv.innerHTML = txHtml;
                })
                .catch(error => console.error('Error fetching transactions:', error));
        }
        
        function getAgentIcon(type) {
            const icons = {
                'sensor': '🌡️',
                'prediction': '🧠',
                'resource_allocation': '💧',
                'market': '💹'
            };
            return icons[type] || '🤖';
        }
        
        function getConnectivityIcon(mode) {
            const icons = {
                'online': '🟢',
                'degraded': '🟡', 
                'offline': '🔴'
            };
            return icons[mode] || '❓';
        }
        
        function getStatusClass(connectivity) {
            const classes = {
                'online': 'status-online',
                'degraded': 'status-degraded',
                'offline': 'status-offline'
            };
            return classes[connectivity] || 'status-offline';
        }
        
        function updateConnectivityStatus() {
            fetch('/api/system_status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('connectivity-status');
                    const icon = getConnectivityIcon(data.connectivity_mode);
                    statusDiv.textContent = `${icon} ${data.connectivity_mode.charAt(0).toUpperCase() + data.connectivity_mode.slice(1)} Mode`;
                })
                .catch(error => console.error('Error updating connectivity status:', error));
        }
        
        function toggleConnectivity() {
            fetch('/api/connectivity_toggle')
                .then(response => response.json())
                .then(data => {
                    alert(`Connectivity changed from ${data.previous_mode} to ${data.new_mode}\\n\\nImpact: ${data.impact}`);
                    refreshAllData();
                })
                .catch(error => console.error('Error toggling connectivity:', error));
        }
        
        function simulateCollaboration() {
            fetch('/api/agent_interactions')
                .then(response => response.json())
                .then(data => {
                    let message = `🤖 Agent Collaboration Simulation\\n\\n`;
                    message += `Active Interactions: ${data.active_interactions}\\n\\n`;
                    
                    data.collaboration_examples.slice(0, 2).forEach(example => {
                        message += `${example.title}:\\n`;
                        message += `- ${example.description}\\n`;
                        message += `- Farmer Benefit: ${example.farmer_benefit}\\n`;
                        message += `- Economic Value: ${example.economic_value}\\n\\n`;
                    });
                    
                    alert(message);
                })
                .catch(error => console.error('Error simulating collaboration:', error));
        }
        
        function showFarmerBenefits() {
            fetch('/api/farmer_benefits')
                .then(response => response.json())
                .then(data => {
                    let message = `🌾 How AgriMind Helps Farmers\\n\\n`;
                    
                    Object.values(data.problem_solutions).forEach(solution => {
                        message += `Problem: ${solution.challenge}\\n`;
                        message += `Solution: ${solution.agent_solution}\\n`;
                        message += `Benefit: ${solution.farmer_benefit}\\n`;
                        message += `Economic Impact: ${solution.economic_impact}\\n\\n`;
                    });
                    
                    alert(message);
                })
                .catch(error => console.error('Error showing farmer benefits:', error));
        }
    </script>
</body>
</html>
        '''

def find_free_port():
    """Find an available port on localhost"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_dashboard():
    """Start the AgriMind Multi-Agent Dashboard"""
    try:
        port = find_free_port()
        server_address = ('localhost', port)
        
        print(f"🌾 Starting AgriMind Multi-Agent Dashboard...")
        print(f"🚀 Server starting on http://localhost:{port}")
        print(f"📊 Demonstrating agent collaboration for farmers")
        print("=" * 60)
        
        # Start background agent simulation
        def simulate_continuous_activity():
            while True:
                agrimind_system.simulate_agent_interactions()
                time.sleep(30)  # Simulate every 30 seconds
        
        simulation_thread = threading.Thread(target=simulate_continuous_activity, daemon=True)
        simulation_thread.start()
        
        # Create and start HTTP server
        httpd = HTTPServer(server_address, AgriMindMultiAgentHandler)
        
        # Open browser automatically
        try:
            webbrowser.open(f'http://localhost:{port}')
            print(f"🌐 Dashboard opened in your default browser")
        except Exception as e:
            print(f"⚠️ Could not open browser automatically: {e}")
        
        print(f"🎯 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start serving
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_dashboard()