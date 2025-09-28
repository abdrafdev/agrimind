#!/usr/bin/env python3
"""
AgriMind Hackathon Dashboard - Clean Working Version
Beautiful real-time dashboard showcasing the multi-agent agricultural system
"""
import json
import time
import random
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

class AgriMindDashboard(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_main_page()
        elif self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        html = self.get_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_api(self):
        if self.path == '/api/status':
            data = self.get_system_status()
        elif self.path == '/api/agents':
            data = self.get_agents()
        elif self.path == '/api/transactions':
            data = self.get_transactions()
        else:
            data = {'error': 'Not found'}
        
        response = json.dumps(data, indent=2)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response.encode())
    
    def get_system_status(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'system_health': random.uniform(0.85, 0.98),
            'active_agents': random.randint(3, 4),
            'total_transactions': random.randint(45, 120),
            'uptime_hours': random.randint(12, 72),
            'weather': {
                'temperature': random.uniform(18, 32),
                'humidity': random.uniform(45, 85),
                'conditions': random.choice(['sunny', 'cloudy', 'partly_cloudy'])
            }
        }
    
    def get_agents(self):
        agents = []
        agent_types = [
            ('Sensor Agent', 'sensor-001', 'Field Monitor'),
            ('Prediction Agent', 'predict-001', 'ML Forecaster'),
            ('Resource Agent', 'resource-001', 'Water Manager'),
            ('Market Agent', 'market-001', 'Trade Optimizer')
        ]
        
        for agent_type, agent_id, role in agent_types:
            status = random.choice(['active', 'active', 'active', 'degraded'])
            agents.append({
                'id': agent_id,
                'type': agent_type,
                'role': role,
                'status': status,
                'health': random.randint(75, 100),
                'last_update': (datetime.now() - timedelta(seconds=random.randint(1, 300))).isoformat(),
                'metrics': {
                    'efficiency': random.uniform(0.80, 0.95),
                    'accuracy': random.uniform(0.85, 0.98),
                    'response_time': random.uniform(50, 200)
                }
            })
        
        return {'agents': agents, 'timestamp': datetime.now().isoformat()}
    
    def get_transactions(self):
        transactions = []
        tx_types = ['resource_allocation', 'data_exchange', 'prediction_request', 'market_trade']
        
        for i in range(15):
            transactions.append({
                'id': f'tx-{random.randint(1000, 9999)}',
                'type': random.choice(tx_types),
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat(),
                'from_agent': f'agent-{random.randint(1, 4)}',
                'to_agent': f'agent-{random.randint(1, 4)}',
                'value': random.uniform(10, 500),
                'status': random.choice(['completed', 'completed', 'pending'])
            })
        
        return {'transactions': transactions}
    
    def get_html(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgriMind Dashboard - Hackathon Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            font-size: 2.8rem;
            margin-bottom: 10px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .header .tagline {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .status-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .status-value {
            font-size: 2rem;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 5px;
        }
        
        .status-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
        }
        
        .card h3 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            text-align: center;
            color: #fff;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 10px;
        }
        
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .agent-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            border-left: 4px solid #4CAF50;
            transition: all 0.3s ease;
        }
        
        .agent-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(5px);
        }
        
        .agent-item.degraded {
            border-left-color: #FF9800;
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .agent-name {
            font-weight: bold;
            font-size: 1.1rem;
        }
        
        .agent-role {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .status-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-active {
            background: rgba(76, 175, 80, 0.3);
            color: #4CAF50;
            border: 1px solid #4CAF50;
        }
        
        .status-degraded {
            background: rgba(255, 152, 0, 0.3);
            color: #FF9800;
            border: 1px solid #FF9800;
        }
        
        .agent-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .metric {
            text-align: center;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }
        
        .metric-value {
            font-weight: bold;
            font-size: 1.1rem;
            color: #4CAF50;
        }
        
        .metric-label {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        
        .transaction-list {
            max-height: 400px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .transaction-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 3px solid #2196F3;
        }
        
        .transaction-info {
            flex: 1;
        }
        
        .transaction-type {
            font-weight: bold;
            margin-bottom: 3px;
            text-transform: capitalize;
        }
        
        .transaction-details {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .transaction-value {
            font-weight: bold;
            font-size: 1.1rem;
            color: #4CAF50;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 1.1rem;
            opacity: 0.7;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
        
        .refresh-info {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .weather-display {
            display: flex;
            justify-content: space-around;
            align-items: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-top: 15px;
        }
        
        .weather-item {
            text-align: center;
        }
        
        .weather-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .weather-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 AgriMind Dashboard</h1>
            <p class="tagline">Intelligent Multi-Agent Agricultural Network • Real-Time Monitoring</p>
            <div id="status-bar" class="status-bar">
                <div class="loading">Loading system status...</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Agent Status Card -->
            <div class="card">
                <h3>🤖 Active Agents</h3>
                <div id="agents-container" class="loading">Loading agent information...</div>
            </div>
            
            <!-- System Weather Card -->
            <div class="card">
                <h3>🌤️ Environmental Conditions</h3>
                <div id="weather-container" class="loading">Loading weather data...</div>
            </div>
            
            <!-- Recent Transactions Card -->
            <div class="card">
                <h3>📊 Recent Transactions</h3>
                <div id="transactions-container" class="loading">Loading transaction history...</div>
            </div>
            
            <!-- System Metrics Card -->
            <div class="card">
                <h3>⚡ Performance Metrics</h3>
                <div id="metrics-container" class="loading">Loading system metrics...</div>
            </div>
        </div>
        
        <div class="refresh-info">
            🔄 Dashboard updates every 5 seconds | 📡 Real-time agent monitoring | 🎯 Hackathon Demo Version
        </div>
    </div>

    <script>
        class AgriMindDashboard {
            constructor() {
                this.updateInterval = 5000; // 5 seconds
                this.init();
            }
            
            async init() {
                await this.updateAll();
                this.startAutoUpdate();
            }
            
            async updateAll() {
                await Promise.all([
                    this.updateSystemStatus(),
                    this.updateAgents(),
                    this.updateTransactions()
                ]);
            }
            
            async fetchData(endpoint) {
                try {
                    const response = await fetch(`/api/${endpoint}`);
                    return await response.json();
                } catch (error) {
                    console.error(`Error fetching ${endpoint}:`, error);
                    return null;
                }
            }
            
            async updateSystemStatus() {
                const data = await this.fetchData('status');
                if (!data) return;
                
                const container = document.getElementById('status-bar');
                container.innerHTML = `
                    <div class="status-item">
                        <div class="status-value">${(data.system_health * 100).toFixed(1)}%</div>
                        <div class="status-label">System Health</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${data.active_agents}</div>
                        <div class="status-label">Active Agents</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${data.total_transactions}</div>
                        <div class="status-label">Total Transactions</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">${data.uptime_hours}h</div>
                        <div class="status-label">System Uptime</div>
                    </div>
                `;
                
                // Update weather
                const weatherContainer = document.getElementById('weather-container');
                weatherContainer.innerHTML = `
                    <div class="weather-display">
                        <div class="weather-item">
                            <div class="weather-value">${data.weather.temperature.toFixed(1)}°C</div>
                            <div class="weather-label">Temperature</div>
                        </div>
                        <div class="weather-item">
                            <div class="weather-value">${data.weather.humidity.toFixed(0)}%</div>
                            <div class="weather-label">Humidity</div>
                        </div>
                        <div class="weather-item">
                            <div class="weather-value">${data.weather.conditions.replace('_', ' ')}</div>
                            <div class="weather-label">Conditions</div>
                        </div>
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
                            <div>
                                <div class="agent-name">${agent.id}</div>
                                <div class="agent-role">${agent.role}</div>
                            </div>
                            <span class="status-badge status-${agent.status}">${agent.status}</span>
                        </div>
                        <div class="agent-metrics">
                            <div class="metric">
                                <div class="metric-value">${agent.health}%</div>
                                <div class="metric-label">Health</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${(agent.metrics.efficiency * 100).toFixed(0)}%</div>
                                <div class="metric-label">Efficiency</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${agent.metrics.response_time.toFixed(0)}ms</div>
                                <div class="metric-label">Response</div>
                            </div>
                        </div>
                    `;
                    container.appendChild(agentDiv);
                });
                
                // Update metrics display
                const metricsContainer = document.getElementById('metrics-container');
                const avgEfficiency = data.agents.reduce((sum, agent) => sum + agent.metrics.efficiency, 0) / data.agents.length;
                const avgHealth = data.agents.reduce((sum, agent) => sum + agent.health, 0) / data.agents.length;
                const activeCount = data.agents.filter(agent => agent.status === 'active').length;
                
                metricsContainer.innerHTML = `
                    <div class="weather-display">
                        <div class="weather-item">
                            <div class="weather-value">${(avgEfficiency * 100).toFixed(1)}%</div>
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
            }
            
            async updateTransactions() {
                const data = await this.fetchData('transactions');
                if (!data) return;
                
                const container = document.getElementById('transactions-container');
                container.innerHTML = '';
                container.className = 'transaction-list';
                
                data.transactions.slice(0, 8).forEach(tx => {
                    const txDiv = document.createElement('div');
                    txDiv.className = 'transaction-item';
                    const time = new Date(tx.timestamp).toLocaleTimeString();
                    txDiv.innerHTML = `
                        <div class="transaction-info">
                            <div class="transaction-type">${tx.type.replace('_', ' ')}</div>
                            <div class="transaction-details">${tx.from_agent} → ${tx.to_agent} at ${time}</div>
                        </div>
                        <div class="transaction-value">$${tx.value.toFixed(0)}</div>
                    `;
                    container.appendChild(txDiv);
                });
            }
            
            startAutoUpdate() {
                setInterval(() => {
                    this.updateAll();
                }, this.updateInterval);
            }
        }
        
        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', () => {
            new AgriMindDashboard();
        });
    </script>
</body>
</html>
        """

def main():
    """Start the AgriMind Dashboard Server"""
    print("🌱 AgriMind Hackathon Dashboard")
    print("=" * 50)
    print("🚀 Starting beautiful real-time dashboard...")
    
    try:
        port = 8000
        server = HTTPServer(('localhost', port), AgriMindDashboard)
        
        print(f"\n✅ Server running on http://localhost:{port}")
        print("🎯 Features:")
        print("   • Real-time agent monitoring")
        print("   • Live transaction tracking") 
        print("   • System health metrics")
        print("   • Environmental conditions")
        print("   • Auto-refresh every 5 seconds")
        print("\n💡 Press Ctrl+C to stop")
        
        # Open browser automatically
        def open_browser():
            time.sleep(1)  # Give server time to start
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("\n🌐 Dashboard opened in your browser!")
            except:
                print(f"\n🌐 Open http://localhost:{port} manually")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        print("\n" + "=" * 50)
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped")
        print("Thanks for using AgriMind! 🌾")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()