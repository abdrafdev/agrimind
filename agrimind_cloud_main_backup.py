#!/usr/bin/env python3
"""
AgriMind Working Dashboard - Guaranteed to Work
Simple, reliable dashboard with proper error handling
"""
import json
import time
import random
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import socket

class AgriMindHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to show cleaner logs"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard()
            elif self.path == '/api/status':
                self.serve_api_data('status')
            elif self.path == '/api/agents':
                self.serve_api_data('agents')
            elif self.path == '/api/transactions':
                self.serve_api_data('transactions')
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            print(f"Error handling request {self.path}: {e}")
            self.send_error(500, str(e))
    
    def serve_dashboard(self):
        """Serve the main HTML dashboard"""
        try:
            html = self.get_dashboard_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            print(f"Error serving dashboard: {e}")
            self.send_error(500, str(e))
    
    def serve_api_data(self, endpoint):
        """Serve JSON API data"""
        try:
            if endpoint == 'status':
                data = self.get_status_data()
            elif endpoint == 'agents':
                data = self.get_agents_data()
            elif endpoint == 'transactions':
                data = self.get_transactions_data()
            else:
                data = {'error': 'Unknown endpoint'}
            
            json_data = json.dumps(data, indent=2)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(json_data)))
            self.end_headers()
            self.wfile.write(json_data.encode('utf-8'))
            
        except Exception as e:
            print(f"Error serving API data for {endpoint}: {e}")
            error_response = json.dumps({'error': str(e)})
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(error_response)))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
    
    def get_status_data(self):
        """Generate system status data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_health': round(random.uniform(85, 98), 1),
            'active_agents': random.randint(3, 4),
            'total_transactions': random.randint(45, 120),
            'uptime_hours': random.randint(12, 72),
            'weather': {
                'temperature': round(random.uniform(18, 32), 1),
                'humidity': round(random.uniform(45, 85), 0),
                'conditions': random.choice(['Sunny', 'Cloudy', 'Partly Cloudy', 'Clear'])
            }
        }
    
    def get_agents_data(self):
        """Generate agents data"""
        agents = []
        agent_configs = [
            ('sensor-001', 'Sensor Agent', 'Field Monitor', '🌾'),
            ('predict-001', 'Prediction Agent', 'ML Forecaster', '🔮'),
            ('resource-001', 'Resource Agent', 'Water Manager', '💧'),
            ('market-001', 'Market Agent', 'Trade Optimizer', '📈')
        ]
        
        for agent_id, agent_type, role, icon in agent_configs:
            agents.append({
                'id': agent_id,
                'type': agent_type,
                'role': role,
                'icon': icon,
                'status': random.choice(['active', 'active', 'active', 'degraded']),
                'health': random.randint(75, 100),
                'last_update': (datetime.now() - timedelta(seconds=random.randint(1, 300))).isoformat(),
                'metrics': {
                    'efficiency': round(random.uniform(80, 95), 1),
                    'accuracy': round(random.uniform(85, 98), 1),
                    'response_time': round(random.uniform(50, 200), 0)
                }
            })
        
        return {
            'agents': agents,
            'timestamp': datetime.now().isoformat(),
            'total_count': len(agents)
        }
    
    def get_transactions_data(self):
        """Generate transaction data"""
        transactions = []
        tx_types = [
            ('resource_allocation', 'Resource Allocation', '💧'),
            ('data_exchange', 'Data Exchange', '📊'),
            ('prediction_request', 'Prediction Request', '🔮'),
            ('market_trade', 'Market Trade', '💰')
        ]
        
        for i in range(12):
            tx_type, display_name, icon = random.choice(tx_types)
            transactions.append({
                'id': f'tx-{random.randint(1000, 9999)}',
                'type': tx_type,
                'display_name': display_name,
                'icon': icon,
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                'from_agent': f'agent-{random.randint(1, 4)}',
                'to_agent': f'agent-{random.randint(1, 4)}',
                'value': round(random.uniform(10, 500), 2),
                'status': random.choice(['completed', 'completed', 'completed', 'pending'])
            })
        
        return {
            'transactions': sorted(transactions, key=lambda x: x['timestamp'], reverse=True),
            'total_count': len(transactions)
        }
    
    def get_dashboard_html(self):
        """Return the complete dashboard HTML"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌱 AgriMind Dashboard - Live Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 15px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.3rem;
            opacity: 0.9;
            margin-bottom: 25px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .status-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .status-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }
        
        .status-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
            margin-bottom: 8px;
        }
        
        .status-label {
            font-size: 1rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 25px;
            padding: 35px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 10px 50px rgba(0, 0, 0, 0.15);
            transition: all 0.4s ease;
        }
        
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
            background: rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            font-size: 1.6rem;
            margin-bottom: 25px;
            text-align: center;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.2rem;
            opacity: 0.8;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .agent-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 20px;
            border-left: 5px solid #4CAF50;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .agent-item:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: translateX(10px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .agent-item.degraded {
            border-left-color: #FF9800;
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .agent-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .agent-icon {
            font-size: 2rem;
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
        }
        
        .agent-details h4 {
            font-size: 1.2rem;
            margin-bottom: 5px;
        }
        
        .agent-role {
            font-size: 0.95rem;
            opacity: 0.85;
        }
        
        .status-badge {
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 0.85rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-active {
            background: rgba(76, 175, 80, 0.3);
            color: #4CAF50;
            border: 2px solid #4CAF50;
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        
        .status-degraded {
            background: rgba(255, 152, 0, 0.3);
            color: #FF9800;
            border: 2px solid #FF9800;
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        
        .agent-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .metric {
            background: rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .metric-value {
            font-size: 1.4rem;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.85rem;
            opacity: 0.9;
        }
        
        .transaction-list {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .transaction-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .transaction-list::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        .transaction-list::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        }
        
        .transaction-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #2196F3;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .transaction-item:hover {
            background: rgba(255, 255, 255, 0.25);
            transform: scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }
        
        .transaction-info {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }
        
        .transaction-icon {
            font-size: 1.8rem;
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
        }
        
        .transaction-details h5 {
            font-size: 1.1rem;
            margin-bottom: 5px;
        }
        
        .transaction-meta {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .transaction-value {
            font-size: 1.3rem;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        }
        
        .weather-display {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        
        .weather-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .weather-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
            margin-bottom: 8px;
        }
        
        .weather-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        .footer-info {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(15px);
            font-size: 1rem;
            opacity: 0.9;
        }
        
        .error {
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 AgriMind Dashboard</h1>
            <p class="subtitle">Intelligent Multi-Agent Agricultural Network • Live Demo</p>
            <div id="status-overview" class="status-grid">
                <div class="loading">Loading system status...</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Agents Card -->
            <div class="card">
                <h3>🤖 Agent Network Status</h3>
                <div id="agents-container" class="loading">Loading agent data...</div>
            </div>
            
            <!-- Environmental Conditions -->
            <div class="card">
                <h3>🌤️ Environmental Conditions</h3>
                <div id="weather-container" class="loading">Loading weather data...</div>
            </div>
            
            <!-- Recent Transactions -->
            <div class="card">
                <h3>📊 Recent Transactions</h3>
                <div id="transactions-container" class="loading">Loading transactions...</div>
            </div>
            
            <!-- System Performance -->
            <div class="card">
                <h3>⚡ System Performance</h3>
                <div id="performance-container" class="loading">Loading performance data...</div>
            </div>
        </div>
        
        <div class="footer-info">
            🔄 Auto-refresh every 3 seconds | 📡 Real-time monitoring | 🎯 AgriMind Hackathon Demo
        </div>
    </div>

    <script>
        class AgriMindDashboard {
            constructor() {
                this.updateInterval = 3000; // 3 seconds
                this.retryCount = 0;
                this.maxRetries = 5;
                console.log('🌱 AgriMind Dashboard initialized');
                this.init();
            }
            
            async init() {
                console.log('🚀 Starting dashboard...');
                await this.updateAll();
                this.startAutoUpdate();
            }
            
            async updateAll() {
                console.log('🔄 Updating all data...');
                try {
                    await Promise.all([
                        this.updateStatus(),
                        this.updateAgents(),
                        this.updateTransactions()
                    ]);
                    this.retryCount = 0; // Reset retry count on success
                } catch (error) {
                    console.error('❌ Error updating data:', error);
                    this.handleError(error);
                }
            }
            
            async fetchData(endpoint) {
                try {
                    console.log(`📡 Fetching ${endpoint}...`);
                    const response = await fetch(`/api/${endpoint}`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    const data = await response.json();
                    console.log(`✅ ${endpoint} data loaded:`, data);
                    return data;
                } catch (error) {
                    console.error(`❌ Error fetching ${endpoint}:`, error);
                    throw error;
                }
            }
            
            async updateStatus() {
                try {
                    const data = await this.fetchData('status');
                    const container = document.getElementById('status-overview');
                    container.innerHTML = `
                        <div class="status-card">
                            <div class="status-value">${data.system_health}%</div>
                            <div class="status-label">System Health</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value">${data.active_agents}</div>
                            <div class="status-label">Active Agents</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value">${data.total_transactions}</div>
                            <div class="status-label">Total Transactions</div>
                        </div>
                        <div class="status-card">
                            <div class="status-value">${data.uptime_hours}h</div>
                            <div class="status-label">System Uptime</div>
                        </div>
                    `;
                    
                    // Update weather
                    const weatherContainer = document.getElementById('weather-container');
                    weatherContainer.innerHTML = `
                        <div class="weather-display">
                            <div class="weather-item">
                                <div class="weather-value">${data.weather.temperature}°C</div>
                                <div class="weather-label">Temperature</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-value">${data.weather.humidity}%</div>
                                <div class="weather-label">Humidity</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-value">${data.weather.conditions}</div>
                                <div class="weather-label">Conditions</div>
                            </div>
                        </div>
                    `;
                } catch (error) {
                    this.showError('status-overview', 'Failed to load system status');
                    throw error;
                }
            }
            
            async updateAgents() {
                try {
                    const data = await this.fetchData('agents');
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
                                        <h4>${agent.id}</h4>
                                        <div class="agent-role">${agent.role}</div>
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
                            </div>
                        `;
                        container.appendChild(agentDiv);
                    });
                    
                    // Update performance metrics
                    const performanceContainer = document.getElementById('performance-container');
                    const avgEfficiency = data.agents.reduce((sum, agent) => sum + agent.metrics.efficiency, 0) / data.agents.length;
                    const avgHealth = data.agents.reduce((sum, agent) => sum + agent.health, 0) / data.agents.length;
                    const activeCount = data.agents.filter(agent => agent.status === 'active').length;
                    
                    performanceContainer.innerHTML = `
                        <div class="weather-display">
                            <div class="weather-item">
                                <div class="weather-value">${avgEfficiency.toFixed(1)}%</div>
                                <div class="weather-label">Avg Efficiency</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-value">${avgHealth.toFixed(0)}%</div>
                                <div class="weather-label">Avg Health</div>
                            </div>
                            <div class="weather-item">
                                <div class="weather-value">${activeCount}/${data.agents.length}</div>
                                <div class="weather-label">Active/Total</div>
                            </div>
                        </div>
                    `;
                } catch (error) {
                    this.showError('agents-container', 'Failed to load agent data');
                    throw error;
                }
            }
            
            async updateTransactions() {
                try {
                    const data = await this.fetchData('transactions');
                    const container = document.getElementById('transactions-container');
                    container.innerHTML = '';
                    container.className = 'transaction-list';
                    
                    data.transactions.slice(0, 8).forEach(tx => {
                        const txDiv = document.createElement('div');
                        txDiv.className = 'transaction-item';
                        const time = new Date(tx.timestamp).toLocaleTimeString();
                        
                        txDiv.innerHTML = `
                            <div class="transaction-info">
                                <div class="transaction-icon">${tx.icon}</div>
                                <div class="transaction-details">
                                    <h5>${tx.display_name}</h5>
                                    <div class="transaction-meta">${tx.from_agent} → ${tx.to_agent} at ${time}</div>
                                </div>
                            </div>
                            <div class="transaction-value">$${tx.value.toFixed(0)}</div>
                        `;
                        container.appendChild(txDiv);
                    });
                } catch (error) {
                    this.showError('transactions-container', 'Failed to load transaction data');
                    throw error;
                }
            }
            
            showError(containerId, message) {
                const container = document.getElementById(containerId);
                container.innerHTML = `<div class="error">⚠️ ${message}</div>`;
            }
            
            handleError(error) {
                this.retryCount++;
                if (this.retryCount <= this.maxRetries) {
                    console.log(`🔄 Retrying in 5 seconds (attempt ${this.retryCount}/${this.maxRetries})`);
                    setTimeout(() => this.updateAll(), 5000);
                } else {
                    console.error('❌ Max retries reached. Please check the server.');
                }
            }
            
            startAutoUpdate() {
                console.log(`⏰ Starting auto-update every ${this.updateInterval/1000} seconds`);
                setInterval(() => {
                    this.updateAll();
                }, this.updateInterval);
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🌐 Page loaded, initializing dashboard...');
            new AgriMindDashboard();
        });
        
        // Show connection status
        window.addEventListener('online', () => {
            console.log('🌐 Connection restored');
        });
        
        window.addEventListener('offline', () => {
            console.log('📡 Connection lost');
        });
    </script>
</body>
</html>
        '''

def find_free_port():
    """Find a free port to use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def main():
    """Start the AgriMind Dashboard Server"""
    print("🌱 AgriMind Working Dashboard")
    print("=" * 60)
    print("🔧 Initializing robust dashboard with error handling...")
    
    # Find a free port
    port = find_free_port()
    print(f"🔍 Found free port: {port}")
    
    try:
        server = HTTPServer(('localhost', port), AgriMindHandler)
        
        print(f"\n✅ Server starting on http://localhost:{port}")
        print("🎯 Features:")
        print("   • ✨ Beautiful glassmorphism UI")
        print("   • 📊 Real-time agent monitoring")
        print("   • 💼 Live transaction tracking")
        print("   • 🌤️ Environmental data display")
        print("   • 🔄 Auto-refresh every 3 seconds")
        print("   • 🛡️ Error handling and retry logic")
        print("   • 📝 Detailed console logging")
        
        print(f"\n💡 Press Ctrl+C to stop the server")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f'http://localhost:{port}')
                print(f"\n🌐 Dashboard opened at http://localhost:{port}")
                print("📱 If it doesn't open automatically, copy the URL above")
            except Exception as e:
                print(f"🌐 Please open http://localhost:{port} manually")
        
        # Start browser opener in background
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("\n" + "=" * 60)
        print("🚀 Server is running! Check your browser...")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
        print("✅ Thank you for using AgriMind!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        print("🔧 Try running the script again")

if __name__ == "__main__":
    main()