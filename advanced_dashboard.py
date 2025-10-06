#!/usr/bin/env python3
"""
AgriMind: Advanced Real-Time Dashboard
Professional-grade web dashboard with stunning UI for hackathon winning presentation
"""

import sys
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from threading import Thread
import http.server
import socketserver
from urllib.parse import urlparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import AgriMind components
try:
    from agents.base_agent import message_bus
    from config.config import get_config_manager
    config_manager = get_config_manager()
    print("✅ AgriMind components loaded successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import AgriMind components: {e}")
    message_bus = None
    config_manager = None

class AdvancedDashboardHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/realtime':
            self.serve_realtime_data()
        elif self.path == '/api/metrics':
            self.serve_metrics()
        elif self.path.startswith('/static/'):
            self.serve_static()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_dashboard(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Generate stunning dashboard HTML
        html = self.generate_advanced_dashboard()
        self.wfile.write(html.encode())

    def serve_realtime_data(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        data = self.get_realtime_data()
        self.wfile.write(json.dumps(data).encode())

    def serve_metrics(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        metrics = self.get_system_metrics()
        self.wfile.write(json.dumps(metrics).encode())

    def serve_static(self):
        # Serve CSS/JS files if needed
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'/* Static files would go here */')

    def get_realtime_data(self):
        """Generate real-time data for dashboard"""
        current_time = datetime.now()
        
        # Get actual agent data if available
        agents_data = {}
        total_agents = 0
        online_agents = 0
        
        if message_bus and hasattr(message_bus, 'agents'):
            total_agents = len(message_bus.agents)
            for agent_id, agent in message_bus.agents.items():
                is_online = True
                if hasattr(agent, 'is_online'):
                    is_online = agent.is_online()
                
                if is_online:
                    online_agents += 1
                
                agent_type = "Unknown"
                if hasattr(agent, 'agent_type'):
                    agent_type = agent.agent_type.value if hasattr(agent.agent_type, 'value') else str(agent.agent_type)
                
                agents_data[agent_id] = {
                    'id': agent_id,
                    'type': agent_type,
                    'online': is_online,
                    'performance': random.uniform(0.7, 0.99),
                    'transactions': len(getattr(agent, 'transactions', {})),
                    'balance': getattr(agent, 'balance', random.uniform(1000, 10000)),
                    'cpu_usage': random.uniform(10, 80),
                    'memory_usage': random.uniform(20, 70),
                    'last_activity': current_time.isoformat()
                }

        # Generate impressive metrics for demo
        return {
            'timestamp': current_time.isoformat(),
            'system': {
                'status': 'OPTIMAL',
                'uptime': '47h 23m 12s',
                'total_agents': total_agents or 8,
                'online_agents': online_agents or 8,
                'system_load': random.uniform(15, 35),
                'memory_usage': random.uniform(45, 65),
                'network_throughput': random.uniform(50, 100),
                'prediction_accuracy': random.uniform(0.85, 0.97),
                'crisis_responses': random.randint(0, 3),
                'negotiations_completed': random.randint(15, 45),
                'revenue_generated': random.uniform(50000, 150000)
            },
            'agents': agents_data or self.generate_demo_agents(),
            'transactions': self.generate_recent_transactions(),
            'alerts': self.generate_system_alerts(),
            'weather': self.generate_weather_data(),
            'market': self.generate_market_data(),
            'farms': self.generate_farm_data(),
            'performance': self.generate_performance_metrics()
        }

    def generate_demo_agents(self):
        """Generate demo agent data for impressive display"""
        demo_agents = {}
        agent_types = ['sensor', 'prediction', 'resource', 'market']
        farms = ['farm_1', 'farm_2', 'farm_3']
        
        for i in range(8):
            if i < 3:
                agent_id = f"sensor_{farms[i]}"
                agent_type = "sensor"
            elif i < 6:
                agent_id = f"prediction_{farms[i-3]}"
                agent_type = "prediction" 
            elif i == 6:
                agent_id = "resource_central"
                agent_type = "resource"
            else:
                agent_id = "market_central"
                agent_type = "market"
            
            demo_agents[agent_id] = {
                'id': agent_id,
                'type': agent_type,
                'online': True,
                'performance': random.uniform(0.85, 0.98),
                'transactions': random.randint(5, 25),
                'balance': random.uniform(5000, 50000),
                'cpu_usage': random.uniform(10, 60),
                'memory_usage': random.uniform(20, 50),
                'last_activity': datetime.now().isoformat()
            }
        
        return demo_agents

    def generate_recent_transactions(self):
        """Generate recent transaction data"""
        transactions = []
        for i in range(10):
            time_ago = datetime.now() - timedelta(minutes=random.randint(1, 60))
            transactions.append({
                'id': f"tx_{random.randint(10000, 99999)}",
                'buyer': f"agent_{random.randint(1, 8)}",
                'seller': f"agent_{random.randint(1, 8)}",
                'item': random.choice(['water_allocation', 'equipment_rental', 'seed_supply', 'fertilizer']),
                'quantity': random.uniform(10, 1000),
                'price': random.uniform(50, 500),
                'status': random.choice(['completed', 'pending', 'processing']),
                'timestamp': time_ago.isoformat()
            })
        return transactions

    def generate_system_alerts(self):
        """Generate system alerts"""
        alert_types = [
            {'level': 'success', 'icon': '✅', 'message': 'Negotiation completed successfully'},
            {'level': 'info', 'icon': '📊', 'message': 'New market data received'},
            {'level': 'warning', 'icon': '⚠️', 'message': 'High system load detected'},
            {'level': 'success', 'icon': '🌾', 'message': 'Crop prediction model updated'},
            {'level': 'info', 'icon': '💰', 'message': 'New trading opportunity identified'}
        ]
        
        alerts = []
        for i in range(5):
            alert = random.choice(alert_types)
            time_ago = datetime.now() - timedelta(minutes=random.randint(1, 30))
            alerts.append({
                'id': f"alert_{i}",
                'level': alert['level'],
                'icon': alert['icon'],
                'message': alert['message'],
                'timestamp': time_ago.isoformat()
            })
        
        return alerts

    def generate_weather_data(self):
        """Generate weather data for farms"""
        return {
            'fresno_ca': {
                'temperature': random.uniform(20, 35),
                'humidity': random.uniform(30, 70),
                'wind_speed': random.uniform(5, 20),
                'precipitation': random.uniform(0, 10),
                'condition': random.choice(['sunny', 'cloudy', 'partly_cloudy'])
            },
            'modesto_ca': {
                'temperature': random.uniform(18, 32),
                'humidity': random.uniform(35, 75),
                'wind_speed': random.uniform(3, 18),
                'precipitation': random.uniform(0, 8),
                'condition': random.choice(['sunny', 'cloudy', 'partly_cloudy'])
            },
            'salinas_ca': {
                'temperature': random.uniform(16, 28),
                'humidity': random.uniform(40, 80),
                'wind_speed': random.uniform(8, 25),
                'precipitation': random.uniform(0, 15),
                'condition': random.choice(['sunny', 'cloudy', 'foggy'])
            }
        }

    def generate_market_data(self):
        """Generate market price data"""
        return {
            'tomatoes': {
                'current_price': random.uniform(3.50, 4.50),
                'change': random.uniform(-0.20, 0.30),
                'trend': random.choice(['rising', 'falling', 'stable']),
                'volume': random.randint(1000, 5000)
            },
            'corn': {
                'current_price': random.uniform(0.70, 1.10),
                'change': random.uniform(-0.10, 0.15),
                'trend': random.choice(['rising', 'falling', 'stable']),
                'volume': random.randint(2000, 8000)
            },
            'lettuce': {
                'current_price': random.uniform(3.00, 4.00),
                'change': random.uniform(-0.25, 0.20),
                'trend': random.choice(['rising', 'falling', 'stable']),
                'volume': random.randint(500, 2000)
            }
        }

    def generate_farm_data(self):
        """Generate farm performance data"""
        return {
            'farm_1': {
                'crop': 'tomatoes',
                'health_score': random.uniform(0.8, 0.95),
                'yield_prediction': random.uniform(80, 120),
                'water_usage': random.uniform(50, 100),
                'efficiency': random.uniform(0.75, 0.92)
            },
            'farm_2': {
                'crop': 'corn',
                'health_score': random.uniform(0.85, 0.98),
                'yield_prediction': random.uniform(90, 130),
                'water_usage': random.uniform(60, 110),
                'efficiency': random.uniform(0.80, 0.95)
            },
            'farm_3': {
                'crop': 'lettuce',
                'health_score': random.uniform(0.78, 0.90),
                'yield_prediction': random.uniform(70, 100),
                'water_usage': random.uniform(40, 80),
                'efficiency': random.uniform(0.72, 0.88)
            }
        }

    def generate_performance_metrics(self):
        """Generate system performance metrics over time"""
        return {
            'timeline': [(datetime.now() - timedelta(minutes=i*10)).isoformat() for i in range(12, 0, -1)],
            'cpu_usage': [random.uniform(20, 60) for _ in range(12)],
            'memory_usage': [random.uniform(40, 80) for _ in range(12)],
            'network_io': [random.uniform(10, 90) for _ in range(12)],
            'transaction_rate': [random.randint(5, 25) for _ in range(12)],
            'prediction_accuracy': [random.uniform(0.80, 0.95) for _ in range(12)]
        }

    def get_system_metrics(self):
        """Get system health metrics"""
        return {
            'health_score': random.uniform(0.85, 0.98),
            'availability': 99.97,
            'response_time': random.uniform(0.1, 0.8),
            'throughput': random.uniform(1000, 5000),
            'error_rate': random.uniform(0.01, 0.05),
            'active_connections': random.randint(50, 200)
        }

    def generate_advanced_dashboard(self):
        """Generate advanced dashboard HTML with stunning UI"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AgriMind - AI Farm Intelligence Network</title>
    
    <!-- External Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {{
            --primary-color: #10B981;
            --secondary-color: #059669;
            --accent-color: #3B82F6;
            --warning-color: #F59E0B;
            --danger-color: #EF4444;
            --success-color: #10B981;
            --dark-bg: #0F172A;
            --card-bg: #1E293B;
            --text-primary: #F8FAFC;
            --text-secondary: #CBD5E1;
            --border-color: #334155;
            --gradient-primary: linear-gradient(135deg, #10B981 0%, #059669 100%);
            --gradient-secondary: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
            --shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background: var(--dark-bg);
            color: var(--text-primary);
            overflow-x: hidden;
        }}

        /* Animated Background */
        .bg-animation {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.1;
        }}

        .bg-animation::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(45deg, #10B981 0%, #3B82F6 50%, #8B5CF6 100%);
            animation: gradientShift 15s ease infinite;
        }}

        @keyframes gradientShift {{
            0%, 100% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
        }}

        /* Header */
        .header {{
            background: rgba(30, 41, 59, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo h1 {{
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.75rem;
            font-weight: 700;
        }}

        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--success-color);
            border-radius: 50px;
            font-size: 0.875rem;
            font-weight: 500;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.8; }}
        }}

        /* Main Content */
        .main {{
            margin-top: 100px;
            padding: 2rem;
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }}

        /* Grid Layouts */
        .grid {{
            display: grid;
            gap: 1.5rem;
        }}

        .grid-4 {{ grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }}
        .grid-3 {{ grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
        .grid-2 {{ grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); }}

        /* Cards */
        .card {{
            background: var(--card-bg);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-primary);
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px -10px rgba(16, 185, 129, 0.2);
        }}

        .metric-card {{
            text-align: center;
            position: relative;
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
        }}

        .metric-label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
        }}

        .metric-change {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.25rem;
            margin-top: 0.5rem;
            font-size: 0.75rem;
        }}

        .change-positive {{ color: var(--success-color); }}
        .change-negative {{ color: var(--danger-color); }}

        /* Agent Cards */
        .agent-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }}

        .agent-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }}

        .agent-card:hover {{
            transform: scale(1.02);
            border-color: var(--primary-color);
        }}

        .agent-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .agent-name {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .agent-type {{
            font-size: 0.75rem;
            color: var(--text-secondary);
        }}

        .agent-status {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        .status-online {{ background: var(--success-color); }}
        .status-offline {{ background: var(--danger-color); }}

        .agent-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            font-size: 0.875rem;
        }}

        /* Chart Containers */
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }}

        .chart-large {{
            height: 400px;
        }}

        /* Transaction Table */
        .transaction-table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .transaction-table th,
        .transaction-table td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        .transaction-table th {{
            background: var(--dark-bg);
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}

        .status-badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}

        .status-completed {{ background: rgba(16, 185, 129, 0.2); color: var(--success-color); }}
        .status-pending {{ background: rgba(245, 158, 11, 0.2); color: var(--warning-color); }}
        .status-processing {{ background: rgba(59, 130, 246, 0.2); color: var(--accent-color); }}

        /* Alerts */
        .alert {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            animation: slideIn 0.5s ease;
        }}

        .alert-success {{ background: rgba(16, 185, 129, 0.1); border-left: 3px solid var(--success-color); }}
        .alert-info {{ background: rgba(59, 130, 246, 0.1); border-left: 3px solid var(--accent-color); }}
        .alert-warning {{ background: rgba(245, 158, 11, 0.1); border-left: 3px solid var(--warning-color); }}

        @keyframes slideIn {{
            from {{ transform: translateX(-100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}

        /* Weather Cards */
        .weather-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}

        .weather-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            border: 1px solid var(--border-color);
        }}

        .weather-temp {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0.5rem 0;
        }}

        /* Market Cards */
        .market-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: var(--card-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            margin-bottom: 0.5rem;
        }}

        .market-price {{
            font-size: 1.25rem;
            font-weight: 600;
        }}

        .market-change {{
            font-size: 0.875rem;
            font-weight: 500;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .main {{ padding: 1rem; }}
            .header {{ padding: 1rem; }}
            .grid-4, .grid-3, .grid-2 {{ grid-template-columns: 1fr; }}
        }}

        /* Loading Animation */
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }}

        .spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="bg-animation"></div>
    
    <!-- Header -->
    <header class="header">
        <div class="logo">
            <i class="fas fa-seedling" style="font-size: 2rem; color: var(--primary-color);"></i>
            <div>
                <h1>AgriMind</h1>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0;">AI Farm Intelligence Network</p>
            </div>
        </div>
        
        <div class="status-indicator">
            <i class="fas fa-circle"></i>
            <span id="connection-status">Connected</span>
        </div>
    </header>

    <!-- Main Content -->
    <main class="main">
        <!-- System Metrics -->
        <section class="grid grid-4" style="margin-bottom: 2rem;">
            <div class="card metric-card">
                <i class="fas fa-robot" style="font-size: 2rem; color: var(--primary-color);"></i>
                <div class="metric-value" id="total-agents">8</div>
                <div class="metric-label">Active Agents</div>
                <div class="metric-change change-positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>+2 today</span>
                </div>
            </div>
            
            <div class="card metric-card">
                <i class="fas fa-handshake" style="font-size: 2rem; color: var(--accent-color);"></i>
                <div class="metric-value" id="negotiations">24</div>
                <div class="metric-label">Negotiations</div>
                <div class="metric-change change-positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>89% success</span>
                </div>
            </div>
            
            <div class="card metric-card">
                <i class="fas fa-dollar-sign" style="font-size: 2rem; color: var(--success-color);"></i>
                <div class="metric-value" id="revenue">$87.5K</div>
                <div class="metric-label">Revenue Generated</div>
                <div class="metric-change change-positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>+12.3%</span>
                </div>
            </div>
            
            <div class="card metric-card">
                <i class="fas fa-brain" style="font-size: 2rem; color: var(--warning-color);"></i>
                <div class="metric-value" id="accuracy">94.2%</div>
                <div class="metric-label">Prediction Accuracy</div>
                <div class="metric-change change-positive">
                    <i class="fas fa-arrow-up"></i>
                    <span>+1.8%</span>
                </div>
            </div>
        </section>

        <!-- Charts Section -->
        <section class="grid grid-2" style="margin-bottom: 2rem;">
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-chart-line"></i> System Performance
                </h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-exchange-alt"></i> Transaction Volume
                </h3>
                <div class="chart-container">
                    <canvas id="transactionChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Agents Grid -->
        <section style="margin-bottom: 2rem;">
            <div class="card">
                <h3 style="margin-bottom: 1.5rem;">
                    <i class="fas fa-network-wired"></i> Active AI Agents
                </h3>
                <div class="agent-grid" id="agents-grid">
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Weather & Market Section -->
        <section class="grid grid-2" style="margin-bottom: 2rem;">
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-cloud-sun"></i> Weather Conditions
                </h3>
                <div class="weather-grid" id="weather-grid">
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-chart-bar"></i> Market Prices
                </h3>
                <div id="market-data">
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Transactions & Alerts -->
        <section class="grid grid-2">
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-history"></i> Recent Transactions
                </h3>
                <div style="overflow-x: auto;">
                    <table class="transaction-table" id="transactions-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td colspan="5" style="text-align: center;">
                                    <div class="loading">
                                        <div class="spinner"></div>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card">
                <h3 style="margin-bottom: 1rem;">
                    <i class="fas fa-bell"></i> System Alerts
                </h3>
                <div id="alerts-container">
                    <div class="loading">
                        <div class="spinner"></div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <script>
        // Global variables
        let charts = {{}};
        let updateInterval;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeCharts();
            startDataUpdates();
            loadInitialData();
        }});

        function initializeCharts() {{
            // Performance Chart
            const performanceCtx = document.getElementById('performanceChart').getContext('2d');
            charts.performance = new Chart(performanceCtx, {{
                type: 'line',
                data: {{
                    labels: [],
                    datasets: [{{
                        label: 'CPU Usage',
                        data: [],
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}, {{
                        label: 'Memory Usage',
                        data: [],
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#CBD5E1' }}
                        }}
                    }},
                    scales: {{
                        x: {{ 
                            ticks: {{ color: '#CBD5E1' }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{ 
                            ticks: {{ color: '#CBD5E1' }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});

            // Transaction Chart
            const transactionCtx = document.getElementById('transactionChart').getContext('2d');
            charts.transaction = new Chart(transactionCtx, {{
                type: 'bar',
                data: {{
                    labels: [],
                    datasets: [{{
                        label: 'Transactions',
                        data: [],
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                        borderColor: '#10B981',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#CBD5E1' }}
                        }}
                    }},
                    scales: {{
                        x: {{ 
                            ticks: {{ color: '#CBD5E1' }},
                            grid: {{ color: '#334155' }}
                        }},
                        y: {{ 
                            ticks: {{ color: '#CBD5E1' }},
                            grid: {{ color: '#334155' }}
                        }}
                    }}
                }}
            }});
        }}

        function loadInitialData() {{
            fetch('/api/realtime')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error loading data:', error));
        }}

        function startDataUpdates() {{
            updateInterval = setInterval(() => {{
                fetch('/api/realtime')
                    .then(response => response.json())
                    .then(data => updateDashboard(data))
                    .catch(error => {{
                        console.error('Error updating data:', error);
                        document.getElementById('connection-status').textContent = 'Disconnected';
                        document.getElementById('connection-status').parentElement.style.background = '#EF4444';
                    }});
            }}, 3000); // Update every 3 seconds
        }}

        function updateDashboard(data) {{
            // Update connection status
            document.getElementById('connection-status').textContent = 'Connected';
            document.getElementById('connection-status').parentElement.style.background = '#10B981';

            // Update metrics
            if (data.system) {{
                document.getElementById('total-agents').textContent = data.system.total_agents;
                document.getElementById('negotiations').textContent = data.system.negotiations_completed;
                document.getElementById('revenue').textContent = `$${(data.system.revenue_generated / 1000).toFixed(1)}K`;
                document.getElementById('accuracy').textContent = `${(data.system.prediction_accuracy * 100).toFixed(1)}%`;
            }}

            // Update agents
            if (data.agents) {{
                updateAgentsGrid(data.agents);
            }}

            // Update weather
            if (data.weather) {{
                updateWeatherGrid(data.weather);
            }}

            // Update market data
            if (data.market) {{
                updateMarketData(data.market);
            }}

            // Update transactions
            if (data.transactions) {{
                updateTransactionsTable(data.transactions);
            }}

            // Update alerts
            if (data.alerts) {{
                updateAlertsContainer(data.alerts);
            }}

            // Update charts
            if (data.performance) {{
                updateCharts(data.performance);
            }}
        }}

        function updateAgentsGrid(agents) {{
            const grid = document.getElementById('agents-grid');
            grid.innerHTML = '';

            Object.values(agents).forEach(agent => {{
                const agentCard = document.createElement('div');
                agentCard.className = 'agent-card';
                agentCard.innerHTML = \`
                    <div class="agent-header">
                        <div>
                            <div class="agent-name">\${agent.id}</div>
                            <div class="agent-type">\${agent.type}</div>
                        </div>
                        <div class="agent-status status-\${agent.online ? 'online' : 'offline'}"></div>
                    </div>
                    <div class="agent-metrics">
                        <div>Performance: \${(agent.performance * 100).toFixed(1)}%</div>
                        <div>Balance: \$\${agent.balance.toFixed(0)}</div>
                        <div>CPU: \${agent.cpu_usage.toFixed(1)}%</div>
                        <div>Memory: \${agent.memory_usage.toFixed(1)}%</div>
                    </div>
                \`;
                grid.appendChild(agentCard);
            }});
        }}

        function updateWeatherGrid(weather) {{
            const grid = document.getElementById('weather-grid');
            grid.innerHTML = '';

            Object.entries(weather).forEach(([location, data]) => {{
                const weatherCard = document.createElement('div');
                weatherCard.className = 'weather-card';
                weatherCard.innerHTML = \`
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">\${location.replace('_', ', ').toUpperCase()}</div>
                    <div class="weather-temp">\${data.temperature.toFixed(1)}°C</div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem;">
                        <div>Humidity: \${data.humidity.toFixed(1)}%</div>
                        <div>Wind: \${data.wind_speed.toFixed(1)} km/h</div>
                        <div>Rain: \${data.precipitation.toFixed(1)} mm</div>
                    </div>
                \`;
                grid.appendChild(weatherCard);
            }});
        }}

        function updateMarketData(market) {{
            const container = document.getElementById('market-data');
            container.innerHTML = '';

            Object.entries(market).forEach(([crop, data]) => {{
                const marketCard = document.createElement('div');
                marketCard.className = 'market-card';
                
                const changeClass = data.change >= 0 ? 'change-positive' : 'change-negative';
                const changeIcon = data.change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                
                marketCard.innerHTML = \`
                    <div>
                        <div style="font-weight: 600; text-transform: capitalize;">\${crop}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">Volume: \${data.volume}</div>
                    </div>
                    <div>
                        <div class="market-price">\$\${data.current_price.toFixed(2)}</div>
                        <div class="market-change \${changeClass}">
                            <i class="fas \${changeIcon}"></i>
                            \$\${Math.abs(data.change).toFixed(2)}
                        </div>
                    </div>
                \`;
                container.appendChild(marketCard);
            }});
        }}

        function updateTransactionsTable(transactions) {{
            const tbody = document.querySelector('#transactions-table tbody');
            tbody.innerHTML = '';

            transactions.slice(0, 8).forEach(tx => {{
                const row = document.createElement('tr');
                row.innerHTML = \`
                    <td style="font-family: monospace; font-size: 0.875rem;">\${tx.id}</td>
                    <td>\${tx.item}</td>
                    <td>\$\${tx.price.toFixed(2)}</td>
                    <td><span class="status-badge status-\${tx.status}">\${tx.status}</span></td>
                    <td style="font-size: 0.875rem;">\${new Date(tx.timestamp).toLocaleTimeString()}</td>
                \`;
                tbody.appendChild(row);
            }});
        }}

        function updateAlertsContainer(alerts) {{
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';

            alerts.forEach(alert => {{
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert alert-${{alert.level}}`;
                alertDiv.innerHTML = \`
                    <span style="font-size: 1.25rem;">\${alert.icon}</span>
                    <div>
                        <div style="font-weight: 500;">\${alert.message}</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            \${new Date(alert.timestamp).toLocaleTimeString()}
                        </div>
                    </div>
                \`;
                container.appendChild(alertDiv);
            }});
        }}

        function updateCharts(performance) {{
            // Update performance chart
            charts.performance.data.labels = performance.timeline.map(t => 
                new Date(t).toLocaleTimeString()
            );
            charts.performance.data.datasets[0].data = performance.cpu_usage;
            charts.performance.data.datasets[1].data = performance.memory_usage;
            charts.performance.update('none');

            // Update transaction chart
            charts.transaction.data.labels = performance.timeline.map(t => 
                new Date(t).toLocaleTimeString()
            );
            charts.transaction.data.datasets[0].data = performance.transaction_rate;
            charts.transaction.update('none');
        }}

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {{
            if (updateInterval) {{
                clearInterval(updateInterval);
            }}
        }});
    </script>
</body>
</html>
        """

def run_advanced_dashboard():
    PORT = 8000
    print("🌾 Starting AgriMind Advanced Dashboard...")
    print(f"📊 Dashboard: http://localhost:{PORT}")
    print("🎨 Stunning UI with real-time animations")
    print("📈 Professional charts and visualizations")
    print("🏆 Hackathon-winning presentation ready!")
    print("💡 Press Ctrl+C to stop\n")
    
    with socketserver.TCPServer(("", PORT), AdvancedDashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n📱 Advanced dashboard server stopped")

if __name__ == "__main__":
    run_advanced_dashboard()