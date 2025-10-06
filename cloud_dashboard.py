#!/usr/bin/env python3
"""
AgriMind Cloud Dashboard - Google Cloud Ready
Enhanced dashboard optimized for cloud deployment
"""
import json
import time
import random
import threading
import os
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

class CloudAgriMindHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Clean logging with timestamps"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def do_GET(self):
        """Handle all GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard()
            elif self.path.startswith('/api/'):
                self.handle_api()
            elif self.path == '/health':
                self.health_check()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"❌ Error handling {self.path}: {e}")
            self.send_error(500, str(e))
    
    def health_check(self):
        """Health check endpoint for Cloud Run"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'agrimind-dashboard'
        }
        self.wfile.write(json.dumps(health).encode())
    
    def serve_dashboard(self):
        """Serve enhanced dashboard HTML"""
        try:
            html = self.get_enhanced_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error serving dashboard: {e}")
            self.send_error(500, str(e))
    
    def handle_api(self):
        """Handle API requests for real-time data"""
        try:
            if self.path == '/api/status':
                data = self.get_system_status()
            elif self.path == '/api/agents':
                data = self.get_agents_data()
            elif self.path == '/api/transactions':
                data = self.get_transactions_data()
            elif self.path == '/api/analytics':
                data = self.get_analytics_data()
            elif self.path == '/api/alerts':
                data = self.get_alerts_data()
            elif self.path == '/api/predictions':
                data = self.get_predictions_data()
            else:
                data = {'error': 'Unknown endpoint'}
            
            json_response = json.dumps(data, indent=2)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(json_response)))
            self.end_headers()
            self.wfile.write(json_response.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ API error: {e}")
            error_response = json.dumps({'error': str(e), 'endpoint': self.path})
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(error_response)))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
    
    def get_system_status(self):
        """Enhanced system status with more metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'health': round(random.uniform(88, 99), 1),
                'uptime_hours': random.randint(24, 168),
                'cpu_usage': round(random.uniform(15, 45), 1),
                'memory_usage': round(random.uniform(35, 70), 1),
                'disk_usage': round(random.uniform(25, 60), 1)
            },
            'agents': {
                'total': 4,
                'active': random.randint(3, 4),
                'degraded': random.randint(0, 1),
                'offline': random.randint(0, 1)
            },
            'environment': {
                'temperature': round(random.uniform(18, 35), 1),
                'humidity': round(random.uniform(40, 85), 0),
                'soil_moisture': round(random.uniform(30, 70), 1),
                'light_intensity': round(random.uniform(20000, 50000), 0),
                'conditions': random.choice(['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain'])
            },
            'business': {
                'revenue_today': round(random.uniform(5000, 15000), 2),
                'profit_margin': round(random.uniform(12, 25), 1),
                'efficiency_score': round(random.uniform(85, 96), 1)
            }
        }
    
    def get_agents_data(self):
        """Enhanced agent data"""
        agents = []
        agent_configs = [
            {
                'id': 'sensor-field-001',
                'name': 'Field Sensor Network',
                'type': 'Environmental Monitor',
                'icon': '🌱',
                'color': '#4CAF50'
            },
            {
                'id': 'ai-predictor-001', 
                'name': 'ML Prediction Engine',
                'type': 'AI Forecaster',
                'icon': '🧠',
                'color': '#2196F3'
            },
            {
                'id': 'resource-manager-001',
                'name': 'Resource Optimizer',
                'type': 'Smart Controller',
                'icon': '⚡',
                'color': '#FF9800'
            },
            {
                'id': 'market-analyzer-001',
                'name': 'Market Intelligence',
                'type': 'Trade Optimizer',
                'icon': '💹',
                'color': '#9C27B0'
            }
        ]
        
        for config in agent_configs:
            status = random.choice(['active', 'active', 'active', 'degraded', 'busy'])
            agents.append({
                **config,
                'status': status,
                'health': random.randint(75, 100),
                'last_heartbeat': (datetime.now() - timedelta(seconds=random.randint(5, 300))).isoformat(),
                'metrics': {
                    'efficiency': round(random.uniform(80, 98), 1),
                    'accuracy': round(random.uniform(85, 99), 1),
                    'response_time': round(random.uniform(25, 150), 0),
                    'success_rate': round(random.uniform(90, 99), 1)
                },
                'current_task': random.choice([
                    'Processing sensor data',
                    'Running ML inference', 
                    'Optimizing resources',
                    'Analyzing market trends',
                    'Generating reports',
                    'Idle - awaiting tasks'
                ])
            })
        
        return {'agents': agents, 'timestamp': datetime.now().isoformat()}
    
    def get_transactions_data(self):
        """Enhanced transaction data"""
        transactions = []
        tx_categories = [
            {'type': 'resource_allocation', 'name': 'Resource Allocation', 'icon': '💧', 'priority': 'high'},
            {'type': 'data_sync', 'name': 'Data Synchronization', 'icon': '🔄', 'priority': 'medium'},
            {'type': 'ai_inference', 'name': 'AI Prediction', 'icon': '🧠', 'priority': 'high'},
            {'type': 'market_analysis', 'name': 'Market Analysis', 'icon': '📈', 'priority': 'medium'},
            {'type': 'alert_notification', 'name': 'Alert Notification', 'icon': '⚠️', 'priority': 'critical'}
        ]
        
        for i in range(12):
            category = random.choice(tx_categories)
            transactions.append({
                'id': f'tx-{random.randint(10000, 99999)}',
                'category': category,
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                'value': round(random.uniform(50, 2000), 2),
                'status': random.choice(['completed', 'completed', 'completed', 'pending']),
                'duration_ms': random.randint(50, 2000)
            })
        
        return {'transactions': sorted(transactions, key=lambda x: x['timestamp'], reverse=True)}
    
    def get_analytics_data(self):
        """Analytics and KPIs"""
        return {
            'kpis': {
                'crop_yield_prediction': f"{random.randint(85, 120)}%",
                'water_savings': f"{random.randint(15, 35)}%",
                'energy_efficiency': f"{random.randint(78, 92)}%",
                'profit_optimization': f"{random.randint(12, 28)}%",
                'risk_reduction': f"{random.randint(40, 65)}%"
            },
            'trends': {
                'weekly_growth': round(random.uniform(5, 15), 1),
                'monthly_savings': round(random.uniform(1000, 5000), 2)
            }
        }
    
    def get_alerts_data(self):
        """System alerts"""
        messages = [
            {'text': 'Crop yield prediction model updated successfully', 'severity': 'success'},
            {'text': 'Weather alert: Rain expected in 6 hours', 'severity': 'warning'},
            {'text': 'Resource optimization saved 15% water usage', 'severity': 'success'},
            {'text': 'Market opportunity: High demand detected', 'severity': 'info'}
        ]
        
        alerts = []
        for i in range(random.randint(3, 6)):
            message = random.choice(messages)
            alerts.append({
                'id': f'alert-{random.randint(1000, 9999)}',
                'message': message['text'],
                'type': message['severity'],
                'icon': '✅' if message['severity'] == 'success' else '⚠️',
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 180))).isoformat(),
                'source': random.choice(['Sensor Network', 'AI Predictor', 'Resource Manager'])
            })
        
        return {'alerts': sorted(alerts, key=lambda x: x['timestamp'], reverse=True)}
    
    def get_predictions_data(self):
        """AI predictions"""
        crops = ['Wheat', 'Corn', 'Soybeans', 'Tomatoes']
        predictions = []
        
        for crop in crops:
            predictions.append({
                'crop': crop,
                'yield_forecast': round(random.uniform(80, 120), 1),
                'confidence': round(random.uniform(85, 98), 1)
            })
        
        return {'crop_predictions': predictions}
    
    def get_enhanced_html(self):
        """Return enhanced dashboard HTML optimized for cloud"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AgriMind Pro - Live Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #fff, #f0f0f0, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.4rem;
            opacity: 0.9;
            margin-bottom: 25px;
        }
        
        .status-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .status-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        }
        
        .status-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: block;
        }
        
        .status-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #4CAF50;
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.5);
            margin-bottom: 5px;
        }
        
        .status-label {
            font-size: 0.95rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(25px);
            border-radius: 25px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 60px rgba(0, 0, 0, 0.2);
            transition: all 0.4s ease;
        }
        
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
        }
        
        .card h3 {
            font-size: 1.8rem;
            margin-bottom: 25px;
            text-align: center;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .agent-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 20px;
            border-left: 5px solid #4CAF50;
            transition: all 0.3s ease;
        }
        
        .agent-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(15px) scale(1.02);
        }
        
        .agent-item.active { border-left-color: #4CAF50; }
        .agent-item.degraded { border-left-color: #FF9800; }
        .agent-item.busy { border-left-color: #2196F3; }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .agent-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .agent-icon {
            font-size: 3rem;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        .agent-details h4 {
            font-size: 1.3rem;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .agent-type {
            font-size: 0.95rem;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        .agent-task {
            font-size: 0.85rem;
            opacity: 0.7;
            font-style: italic;
        }
        
        .status-badge {
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        
        .status-active {
            background: linear-gradient(45deg, #4CAF50, #66BB6A);
            color: white;
        }
        
        .status-degraded {
            background: linear-gradient(45deg, #FF9800, #FFB74D);
            color: white;
        }
        
        .status-busy {
            background: linear-gradient(45deg, #2196F3, #42A5F5);
            color: white;
        }
        
        .agent-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric {
            background: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.05);
        }
        
        .metric-value {
            font-size: 1.4rem;
            font-weight: 700;
            color: #4CAF50;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.8rem;
            opacity: 0.9;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            font-size: 1.3rem;
            opacity: 0.8;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .transaction-list, .alert-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .transaction-item, .alert-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #2196F3;
            transition: all 0.3s ease;
        }
        
        .transaction-item:hover, .alert-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(10px);
        }
        
        .item-info {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }
        
        .item-icon {
            font-size: 1.8rem;
        }
        
        .item-details h5 {
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        
        .item-meta {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        
        .item-value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #4CAF50;
        }
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .kpi-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .kpi-card:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.05);
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: #4CAF50;
            margin-bottom: 8px;
        }
        
        .kpi-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            padding: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 AgriMind Pro</h1>
            <p class="subtitle">Advanced Agricultural Intelligence • Cloud-Deployed Dashboard</p>
            <div id="status-overview" class="status-overview">
                <div class="loading">🚀 Loading system status...</div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="card">
                <h3>🤖 Intelligent Agent Network</h3>
                <div id="agents-container" class="loading">⚡ Initializing agents...</div>
            </div>
            
            <div class="card">
                <h3>📊 Performance Analytics</h3>
                <div id="analytics-container" class="loading">📈 Loading analytics...</div>
            </div>
            
            <div class="card">
                <h3>💫 Smart Transactions</h3>
                <div id="transactions-container" class="loading">💼 Loading transactions...</div>
            </div>
            
            <div class="card">
                <h3>🧠 AI Predictions</h3>
                <div id="predictions-container" class="loading">🔮 Loading predictions...</div>
            </div>
            
            <div class="card">
                <h3>🚨 Smart Alerts</h3>
                <div id="alerts-container" class="loading">⚠️ Loading alerts...</div>
            </div>
            
            <div class="card">
                <h3>📈 Real-time Charts</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            🌐 Deployed on Google Cloud | 🔄 Auto-refresh: 3 seconds | 🏆 Hackathon Ready
        </div>
    </div>

    <script>
        class CloudAgriMindDashboard {
            constructor() {
                this.updateInterval = 3000;
                this.chart = null;
                console.log('🌐 Cloud AgriMind Dashboard initialized');
                this.init();
            }
            
            async init() {
                console.log('⚡ Starting cloud dashboard...');
                await this.updateAll();
                this.initChart();
                this.startAutoUpdate();
            }
            
            async updateAll() {
                console.log('🔄 Updating all data...');
                try {
                    await Promise.all([
                        this.updateSystemStatus(),
                        this.updateAgents(),
                        this.updateTransactions(),
                        this.updateAnalytics(),
                        this.updateAlerts(),
                        this.updatePredictions()
                    ]);
                } catch (error) {
                    console.error('❌ Update error:', error);
                }
            }
            
            async fetchData(endpoint) {
                try {
                    const response = await fetch(`/api/${endpoint}`);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    return await response.json();
                } catch (error) {
                    console.error(`❌ Error fetching ${endpoint}:`, error);
                    return null;
                }
            }
            
            async updateSystemStatus() {
                const data = await this.fetchData('status');
                if (!data) return;
                
                const container = document.getElementById('status-overview');
                container.innerHTML = `
                    <div class="status-card">
                        <div class="status-icon">🏥</div>
                        <div class="status-value">${data.system.health}%</div>
                        <div class="status-label">System Health</div>
                    </div>
                    <div class="status-card">
                        <div class="status-icon">⚡</div>
                        <div class="status-value">${data.system.cpu_usage}%</div>
                        <div class="status-label">CPU Usage</div>
                    </div>
                    <div class="status-card">
                        <div class="status-icon">🌡️</div>
                        <div class="status-value">${data.environment.temperature}°C</div>
                        <div class="status-label">Temperature</div>
                    </div>
                    <div class="status-card">
                        <div class="status-icon">💧</div>
                        <div class="status-value">${data.environment.soil_moisture}%</div>
                        <div class="status-label">Soil Moisture</div>
                    </div>
                    <div class="status-card">
                        <div class="status-icon">💰</div>
                        <div class="status-value">$${data.business.revenue_today.toLocaleString()}</div>
                        <div class="status-label">Revenue Today</div>
                    </div>
                `;
            }
            
            async updateAgents() {
                const data = await this.fetchData('agents');
                if (!data) return;
                
                const container = document.getElementById('agents-container');
                container.innerHTML = '';
                container.className = 'agent-list';
                
                data.agents.forEach(agent => {
                    const agentDiv = document.createElement('div');
                    agentDiv.className = `agent-item ${agent.status}`;
                    agentDiv.innerHTML = `
                        <div class="agent-header">
                            <div class="agent-info">
                                <div class="agent-icon">${agent.icon}</div>
                                <div class="agent-details">
                                    <h4>${agent.name}</h4>
                                    <div class="agent-type">${agent.type}</div>
                                    <div class="agent-task">${agent.current_task}</div>
                                </div>
                            </div>
                            <span class="status-badge status-${agent.status}">${agent.status}</span>
                        </div>
                        <div class="agent-metrics">
                            <div class="metric">
                                <div class="metric-value">${agent.health}%</div>
                                <div class="metric-label">Health</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${agent.metrics.efficiency}%</div>
                                <div class="metric-label">Efficiency</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${agent.metrics.response_time}ms</div>
                                <div class="metric-label">Response</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${agent.metrics.success_rate}%</div>
                                <div class="metric-label">Success</div>
                            </div>
                        </div>
                    `;
                    container.appendChild(agentDiv);
                });
            }
            
            async updateTransactions() {
                const data = await this.fetchData('transactions');
                if (!data) return;
                
                const container = document.getElementById('transactions-container');
                container.innerHTML = '';
                container.className = 'transaction-list';
                
                data.transactions.slice(0, 6).forEach(tx => {
                    const txDiv = document.createElement('div');
                    txDiv.className = 'transaction-item';
                    const time = new Date(tx.timestamp).toLocaleTimeString();
                    
                    txDiv.innerHTML = `
                        <div class="item-info">
                            <div class="item-icon">${tx.category.icon}</div>
                            <div class="item-details">
                                <h5>${tx.category.name}</h5>
                                <div class="item-meta">${time} | ${tx.duration_ms}ms</div>
                            </div>
                        </div>
                        <div class="item-value">$${tx.value.toFixed(0)}</div>
                    `;
                    container.appendChild(txDiv);
                });
            }
            
            async updateAnalytics() {
                const data = await this.fetchData('analytics');
                if (!data) return;
                
                const container = document.getElementById('analytics-container');
                container.innerHTML = `
                    <div class="analytics-grid">
                        <div class="kpi-card">
                            <div class="kpi-value">${data.kpis.crop_yield_prediction}</div>
                            <div class="kpi-label">Yield Prediction</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">${data.kpis.water_savings}</div>
                            <div class="kpi-label">Water Savings</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">${data.kpis.energy_efficiency}</div>
                            <div class="kpi-label">Energy Efficiency</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">${data.kpis.profit_optimization}</div>
                            <div class="kpi-label">Profit Growth</div>
                        </div>
                    </div>
                `;
            }
            
            async updateAlerts() {
                const data = await this.fetchData('alerts');
                if (!data) return;
                
                const container = document.getElementById('alerts-container');
                container.innerHTML = '';
                container.className = 'alert-list';
                
                data.alerts.slice(0, 5).forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert-item ${alert.type}`;
                    const time = new Date(alert.timestamp).toLocaleTimeString();
                    
                    alertDiv.innerHTML = `
                        <div class="item-info">
                            <div class="item-icon">${alert.icon}</div>
                            <div class="item-details">
                                <h5>${alert.message}</h5>
                                <div class="item-meta">${alert.source} | ${time}</div>
                            </div>
                        </div>
                    `;
                    container.appendChild(alertDiv);
                });
            }
            
            async updatePredictions() {
                const data = await this.fetchData('predictions');
                if (!data) return;
                
                const container = document.getElementById('predictions-container');
                container.innerHTML = '';
                
                const predictionsHtml = data.crop_predictions.map(pred => `
                    <div class="kpi-card">
                        <div class="kpi-value">${pred.yield_forecast}%</div>
                        <div class="kpi-label">${pred.crop} Yield</div>
                    </div>
                `).join('');
                
                container.innerHTML = `<div class="analytics-grid">${predictionsHtml}</div>`;
            }
            
            initChart() {
                const ctx = document.getElementById('performanceChart').getContext('2d');
                this.chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'System Efficiency',
                            data: [],
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: 'white' }
                            }
                        },
                        scales: {
                            y: {
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255,255,255,0.1)' }
                            },
                            x: {
                                ticks: { color: 'white' },
                                grid: { color: 'rgba(255,255,255,0.1)' }
                            }
                        }
                    }
                });
                
                this.updateChart();
            }
            
            updateChart() {
                if (!this.chart) return;
                
                const now = new Date().toLocaleTimeString();
                const maxPoints = 15;
                
                if (this.chart.data.labels.length >= maxPoints) {
                    this.chart.data.labels.shift();
                    this.chart.data.datasets[0].data.shift();
                }
                
                this.chart.data.labels.push(now);
                this.chart.data.datasets[0].data.push(Math.random() * 20 + 80);
                
                this.chart.update('none');
            }
            
            startAutoUpdate() {
                setInterval(() => {
                    this.updateAll();
                    this.updateChart();
                }, this.updateInterval);
            }
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            new CloudAgriMindDashboard();
        });
    </script>
</body>
</html>
        '''

def main():
    """Start the Cloud-optimized AgriMind Dashboard"""
    print("🌾 AgriMind Cloud Dashboard")
    print("=" * 60)
    print("🌐 Optimized for Google Cloud deployment")
    
    # Get port from environment variable (Cloud Run uses PORT)
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'  # Bind to all interfaces for cloud deployment
    
    try:
        server = HTTPServer((host, port), CloudAgriMindHandler)
        
        print(f"\n✅ Server starting on {host}:{port}")
        print("🎯 Features:")
        print("   • 🌐 Cloud-optimized")
        print("   • 🏥 Health check endpoint")
        print("   • 📊 6 API endpoints")
        print("   • ⚡ 3-second updates")
        print("   • 🧠 Enhanced AI agents")
        print("   • 💹 Smart transactions")
        
        print(f"\n💡 Ready for cloud deployment!")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()