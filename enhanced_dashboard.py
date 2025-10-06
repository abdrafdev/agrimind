#!/usr/bin/env python3
"""
AgriMind Enhanced Dashboard - Advanced Features & Better Icons
Professional dashboard with advanced analytics and modern UI
"""
import json
import time
import random
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import socket
import math

class AdvancedAgriMindHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Clean logging with timestamps"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def do_GET(self):
        """Handle all GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard()
            elif self.path == '/api/status':
                self.serve_api('status')
            elif self.path == '/api/agents':
                self.serve_api('agents')
            elif self.path == '/api/transactions':
                self.serve_api('transactions')
            elif self.path == '/api/analytics':
                self.serve_api('analytics')
            elif self.path == '/api/alerts':
                self.serve_api('alerts')
            elif self.path == '/api/predictions':
                self.serve_api('predictions')
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"❌ Error handling {self.path}: {e}")
            self.send_error(500, str(e))
    
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
    
    def serve_api(self, endpoint):
        """Serve JSON API data"""
        try:
            if endpoint == 'status':
                data = self.get_system_status()
            elif endpoint == 'agents':
                data = self.get_agents_data()
            elif endpoint == 'transactions':
                data = self.get_transactions_data()
            elif endpoint == 'analytics':
                data = self.get_analytics_data()
            elif endpoint == 'alerts':
                data = self.get_alerts_data()
            elif endpoint == 'predictions':
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
            print(f"❌ API error for {endpoint}: {e}")
            error_response = json.dumps({'error': str(e), 'endpoint': endpoint})
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
            'network': {
                'latency_ms': round(random.uniform(10, 50), 1),
                'throughput_mbps': round(random.uniform(50, 100), 1),
                'packet_loss': round(random.uniform(0, 0.5), 2)
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
        """Enhanced agent data with more details"""
        agents = []
        agent_configs = [
            {
                'id': 'sensor-field-001',
                'name': 'Field Sensor Network',
                'type': 'Environmental Monitor',
                'icon': '🌱',
                'color': '#4CAF50',
                'location': 'Field Zone A-1',
                'capabilities': ['Temperature', 'Humidity', 'Soil pH', 'Moisture']
            },
            {
                'id': 'ai-predictor-001', 
                'name': 'ML Prediction Engine',
                'type': 'AI Forecaster',
                'icon': '🧠',
                'color': '#2196F3',
                'location': 'Data Center',
                'capabilities': ['Yield Prediction', 'Weather Forecast', 'Risk Analysis', 'Market Trends']
            },
            {
                'id': 'resource-manager-001',
                'name': 'Resource Optimizer',
                'type': 'Smart Controller',
                'icon': '⚡',
                'color': '#FF9800',
                'location': 'Control Hub',
                'capabilities': ['Water Management', 'Nutrient Control', 'Energy Optimization', 'Automation']
            },
            {
                'id': 'market-analyzer-001',
                'name': 'Market Intelligence',
                'type': 'Trade Optimizer',
                'icon': '💹',
                'color': '#9C27B0',
                'location': 'Trading Platform',
                'capabilities': ['Price Analysis', 'Demand Forecast', 'Supply Chain', 'Risk Management']
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
                    'success_rate': round(random.uniform(90, 99), 1),
                    'tasks_completed': random.randint(50, 500),
                    'errors_count': random.randint(0, 5)
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
        
        return {
            'agents': agents,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_agents': len(agents),
                'active_count': len([a for a in agents if a['status'] == 'active']),
                'avg_health': round(sum(a['health'] for a in agents) / len(agents), 1),
                'avg_efficiency': round(sum(a['metrics']['efficiency'] for a in agents) / len(agents), 1)
            }
        }
    
    def get_transactions_data(self):
        """Enhanced transaction data with categories and priorities"""
        transactions = []
        tx_categories = [
            {'type': 'resource_allocation', 'name': 'Resource Allocation', 'icon': '💧', 'priority': 'high'},
            {'type': 'data_sync', 'name': 'Data Synchronization', 'icon': '🔄', 'priority': 'medium'},
            {'type': 'ai_inference', 'name': 'AI Prediction', 'icon': '🧠', 'priority': 'high'},
            {'type': 'market_analysis', 'name': 'Market Analysis', 'icon': '📈', 'priority': 'medium'},
            {'type': 'alert_notification', 'name': 'Alert Notification', 'icon': '⚠️', 'priority': 'critical'},
            {'type': 'system_maintenance', 'name': 'System Maintenance', 'icon': '🔧', 'priority': 'low'},
            {'type': 'crop_monitoring', 'name': 'Crop Monitoring', 'icon': '🌾', 'priority': 'medium'},
            {'type': 'weather_update', 'name': 'Weather Update', 'icon': '🌤️', 'priority': 'high'}
        ]
        
        for i in range(15):
            category = random.choice(tx_categories)
            transactions.append({
                'id': f'tx-{random.randint(10000, 99999)}',
                'category': category,
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                'from_agent': random.choice(['sensor-field-001', 'ai-predictor-001', 'resource-manager-001', 'market-analyzer-001']),
                'to_agent': random.choice(['sensor-field-001', 'ai-predictor-001', 'resource-manager-001', 'market-analyzer-001']),
                'value': round(random.uniform(50, 2000), 2),
                'status': random.choice(['completed', 'completed', 'completed', 'pending', 'processing']),
                'duration_ms': random.randint(50, 2000),
                'data_size_kb': round(random.uniform(1, 500), 1)
            })
        
        # Sort by timestamp, most recent first
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'transactions': transactions,
            'summary': {
                'total_count': len(transactions),
                'completed': len([t for t in transactions if t['status'] == 'completed']),
                'pending': len([t for t in transactions if t['status'] == 'pending']),
                'total_value': round(sum(t['value'] for t in transactions), 2)
            }
        }
    
    def get_analytics_data(self):
        """Advanced analytics and KPIs"""
        # Generate time series data for charts
        hours = []
        efficiency_data = []
        throughput_data = []
        revenue_data = []
        
        for i in range(24):  # Last 24 hours
            hour = (datetime.now() - timedelta(hours=23-i)).strftime('%H:00')
            hours.append(hour)
            efficiency_data.append(round(85 + random.uniform(-5, 10), 1))
            throughput_data.append(random.randint(80, 200))
            revenue_data.append(round(random.uniform(200, 800), 2))
        
        return {
            'charts': {
                'time_series': {
                    'labels': hours,
                    'efficiency': efficiency_data,
                    'throughput': throughput_data, 
                    'revenue': revenue_data
                },
                'agent_performance': [
                    {'agent': 'Sensor Network', 'score': round(random.uniform(85, 98), 1)},
                    {'agent': 'AI Predictor', 'score': round(random.uniform(88, 96), 1)},
                    {'agent': 'Resource Manager', 'score': round(random.uniform(82, 94), 1)},
                    {'agent': 'Market Analyzer', 'score': round(random.uniform(86, 95), 1)}
                ]
            },
            'kpis': {
                'crop_yield_prediction': f"{random.randint(85, 120)}%",
                'water_savings': f"{random.randint(15, 35)}%",
                'energy_efficiency': f"{random.randint(78, 92)}%",
                'profit_optimization': f"{random.randint(12, 28)}%",
                'risk_reduction': f"{random.randint(40, 65)}%"
            },
            'trends': {
                'weekly_growth': round(random.uniform(5, 15), 1),
                'monthly_savings': round(random.uniform(1000, 5000), 2),
                'efficiency_improvement': round(random.uniform(2, 8), 1)
            }
        }
    
    def get_alerts_data(self):
        """System alerts and notifications"""
        alert_types = [
            {'type': 'success', 'icon': '✅', 'color': '#4CAF50'},
            {'type': 'info', 'icon': 'ℹ️', 'color': '#2196F3'},
            {'type': 'warning', 'icon': '⚠️', 'color': '#FF9800'},
            {'type': 'error', 'icon': '❌', 'color': '#F44336'},
            {'type': 'critical', 'icon': '🚨', 'color': '#D32F2F'}
        ]
        
        messages = [
            {'text': 'Crop yield prediction model updated successfully', 'severity': 'success'},
            {'text': 'Soil moisture levels optimal in Field A-1', 'severity': 'info'},
            {'text': 'Weather alert: Heavy rain expected in 6 hours', 'severity': 'warning'},
            {'text': 'Sensor network connectivity restored', 'severity': 'success'},
            {'text': 'Market opportunity: High demand for organic produce', 'severity': 'info'},
            {'text': 'Resource optimization saved 15% water usage today', 'severity': 'success'},
            {'text': 'AI model accuracy improved by 3.2%', 'severity': 'success'},
            {'text': 'Irrigation system scheduled for maintenance', 'severity': 'warning'}
        ]
        
        alerts = []
        for i in range(random.randint(5, 8)):
            message = random.choice(messages)
            alert_type = next(a for a in alert_types if a['type'] == message['severity'])
            
            alerts.append({
                'id': f'alert-{random.randint(1000, 9999)}',
                'message': message['text'],
                'type': alert_type['type'],
                'icon': alert_type['icon'],
                'color': alert_type['color'],
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 180))).isoformat(),
                'acknowledged': random.choice([True, False]),
                'source': random.choice(['Sensor Network', 'AI Predictor', 'Resource Manager', 'Market Analyzer'])
            })
        
        return {
            'alerts': sorted(alerts, key=lambda x: x['timestamp'], reverse=True),
            'summary': {
                'total': len(alerts),
                'unacknowledged': len([a for a in alerts if not a['acknowledged']]),
                'critical': len([a for a in alerts if a['type'] == 'critical']),
                'warnings': len([a for a in alerts if a['type'] == 'warning'])
            }
        }
    
    def get_predictions_data(self):
        """AI predictions and forecasts"""
        # Generate prediction data
        crops = ['Wheat', 'Corn', 'Soybeans', 'Tomatoes', 'Lettuce']
        predictions = []
        
        for crop in crops:
            predictions.append({
                'crop': crop,
                'yield_forecast': round(random.uniform(80, 120), 1),  # % of expected
                'confidence': round(random.uniform(85, 98), 1),
                'harvest_date': (datetime.now() + timedelta(days=random.randint(30, 120))).strftime('%Y-%m-%d'),
                'market_price_trend': random.choice(['bullish', 'bearish', 'stable']),
                'risk_factors': random.sample(['drought', 'pests', 'disease', 'weather', 'market_volatility'], k=random.randint(1, 3))
            })
        
        # Weather forecast
        weather_forecast = []
        for i in range(7):
            date = datetime.now() + timedelta(days=i)
            weather_forecast.append({
                'date': date.strftime('%Y-%m-%d'),
                'temperature_high': round(random.uniform(20, 35), 1),
                'temperature_low': round(random.uniform(10, 25), 1),
                'precipitation_chance': random.randint(0, 80),
                'conditions': random.choice(['sunny', 'cloudy', 'rainy', 'partly-cloudy']),
                'wind_speed': round(random.uniform(5, 25), 1)
            })
        
        return {
            'crop_predictions': predictions,
            'weather_forecast': weather_forecast,
            'market_insights': {
                'trending_crops': random.sample(crops, 3),
                'price_volatility': round(random.uniform(5, 15), 1),
                'demand_forecast': random.choice(['increasing', 'stable', 'decreasing'])
            }
        }
    
    def get_enhanced_html(self):
        """Return enhanced dashboard HTML"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AgriMind Pro - Advanced Agricultural Intelligence</title>
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
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: rotate(45deg);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #fff, #f0f0f0, #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .subtitle {
            font-size: 1.4rem;
            opacity: 0.9;
            margin-bottom: 25px;
            position: relative;
            z-index: 1;
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
            position: relative;
            overflow: hidden;
        }
        
        .status-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.25);
        }
        
        .status-icon {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: block;
            filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
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
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(25px);
            border-radius: 25px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 15px 60px rgba(0, 0, 0, 0.2);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }
        
        .card:hover::before {
            left: 100%;
        }
        
        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .card h3 {
            font-size: 1.8rem;
            margin-bottom: 25px;
            text-align: center;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
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
            border-left: 5px solid;
            transition: all 0.3s ease;
            backdrop-filter: blur(15px);
            position: relative;
        }
        
        .agent-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(15px) scale(1.02);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
        }
        
        .agent-item.active { border-left-color: #4CAF50; }
        .agent-item.degraded { border-left-color: #FF9800; }
        .agent-item.busy { border-left-color: #2196F3; }
        .agent-item.offline { border-left-color: #F44336; }
        
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
            filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.4));
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
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
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
            backdrop-filter: blur(10px);
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
            text-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.8rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .transaction-list, .alert-list {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        .transaction-list::-webkit-scrollbar, .alert-list::-webkit-scrollbar {
            width: 8px;
        }
        
        .transaction-list::-webkit-scrollbar-track, .alert-list::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        .transaction-list::-webkit-scrollbar-thumb, .alert-list::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.5));
            border-radius: 10px;
        }
        
        .transaction-item, .alert-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .transaction-item:hover, .alert-item:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(10px) scale(1.02);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .transaction-item { border-left-color: #2196F3; }
        .alert-item.success { border-left-color: #4CAF50; }
        .alert-item.warning { border-left-color: #FF9800; }
        .alert-item.error { border-left-color: #F44336; }
        .alert-item.info { border-left-color: #2196F3; }
        .alert-item.critical { border-left-color: #D32F2F; }
        
        .item-info {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }
        
        .item-icon {
            font-size: 2rem;
            filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.3));
        }
        
        .item-details h5 {
            font-size: 1.1rem;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .item-meta {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        
        .item-value {
            font-size: 1.3rem;
            font-weight: 700;
            color: #4CAF50;
            text-shadow: 0 2px 8px rgba(76, 175, 80, 0.4);
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 15px;
            padding: 15px;
        }
        
        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .kpi-card {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
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
            text-shadow: 0 2px 10px rgba(76, 175, 80, 0.5);
            margin-bottom: 8px;
        }
        
        .kpi-label {
            font-size: 0.9rem;
            opacity: 0.9;
            font-weight: 500;
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            font-size: 1.3rem;
            opacity: 0.8;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.02); }
        }
        
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 25px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(20px);
            font-size: 1.1rem;
            opacity: 0.9;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .control-btn {
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        .control-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .control-btn.active {
            background: linear-gradient(45deg, #4CAF50, #66BB6A);
        }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .header h1 { font-size: 2.5rem; }
            .main-grid { grid-template-columns: 1fr; }
            .agent-metrics { grid-template-columns: repeat(2, 1fr); }
            .status-overview { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 AgriMind Pro</h1>
            <p class="subtitle">Advanced Agricultural Intelligence • Real-Time Multi-Agent Dashboard</p>
            <div class="controls">
                <button class="control-btn active" onclick="toggleRefresh()">🔄 Auto-Refresh</button>
                <button class="control-btn" onclick="toggleSound()">🔊 Sound</button>
                <button class="control-btn" onclick="exportData()">💾 Export</button>
                <button class="control-btn" onclick="toggleFullscreen()">🖥️ Fullscreen</button>
            </div>
            <div id="status-overview" class="status-overview">
                <div class="loading">🚀 Loading system status...</div>
            </div>
        </div>
        
        <div class="main-grid">
            <!-- Enhanced Agents Card -->
            <div class="card">
                <h3>🤖 Intelligent Agent Network</h3>
                <div id="agents-container" class="loading">⚡ Initializing agents...</div>
            </div>
            
            <!-- Advanced Analytics -->
            <div class="card">
                <h3>📊 Performance Analytics</h3>
                <div id="analytics-container" class="loading">📈 Loading analytics...</div>
            </div>
            
            <!-- Smart Transactions -->
            <div class="card">
                <h3>💫 Smart Transactions</h3>
                <div id="transactions-container" class="loading">💼 Loading transactions...</div>
            </div>
            
            <!-- AI Predictions -->
            <div class="card">
                <h3>🧠 AI Predictions</h3>
                <div id="predictions-container" class="loading">🔮 Loading predictions...</div>
            </div>
            
            <!-- System Alerts -->
            <div class="card">
                <h3>🚨 Smart Alerts</h3>
                <div id="alerts-container" class="loading">⚠️ Loading alerts...</div>
            </div>
            
            <!-- Real-time Charts -->
            <div class="card">
                <h3>📈 Real-time Charts</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            🔄 Auto-refresh: 2 seconds | 🧠 AI-Powered | 🌱 Sustainable Agriculture | 🏆 Hackathon Ready
        </div>
    </div>

    <script>
        class EnhancedAgriMindDashboard {
            constructor() {
                this.updateInterval = 2000; // 2 seconds - faster updates
                this.autoRefresh = true;
                this.soundEnabled = false;
                this.chart = null;
                console.log('🚀 Enhanced AgriMind Dashboard initialized');
                this.init();
            }
            
            async init() {
                console.log('⚡ Starting enhanced dashboard...');
                await this.updateAll();
                this.initChart();
                this.startAutoUpdate();
            }
            
            async updateAll() {
                if (!this.autoRefresh) return;
                
                console.log('🔄 Updating all enhanced data...');
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
                        <div class="status-icon">🌞</div>
                        <div class="status-value">${data.environment.light_intensity}</div>
                        <div class="status-label">Light (lux)</div>
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
                
                data.transactions.slice(0, 8).forEach(tx => {
                    const txDiv = document.createElement('div');
                    txDiv.className = 'transaction-item';
                    const time = new Date(tx.timestamp).toLocaleTimeString();
                    
                    txDiv.innerHTML = `
                        <div class="item-info">
                            <div class="item-icon">${tx.category.icon}</div>
                            <div class="item-details">
                                <h5>${tx.category.name}</h5>
                                <div class="item-meta">${tx.from_agent} → ${tx.to_agent} | ${time} | ${tx.duration_ms}ms</div>
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
                        <div class="kpi-card">
                            <div class="kpi-value">${data.kpis.risk_reduction}</div>
                            <div class="kpi-label">Risk Reduction</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-value">+${data.trends.weekly_growth}%</div>
                            <div class="kpi-label">Weekly Growth</div>
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
                
                data.alerts.slice(0, 6).forEach(alert => {
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
                
                const predictionsHtml = data.crop_predictions.slice(0, 4).map(pred => `
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
                        }, {
                            label: 'AI Accuracy',
                            data: [],
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.1)',
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
                const maxPoints = 20;
                
                if (this.chart.data.labels.length >= maxPoints) {
                    this.chart.data.labels.shift();
                    this.chart.data.datasets[0].data.shift();
                    this.chart.data.datasets[1].data.shift();
                }
                
                this.chart.data.labels.push(now);
                this.chart.data.datasets[0].data.push(Math.random() * 20 + 80);
                this.chart.data.datasets[1].data.push(Math.random() * 15 + 85);
                
                this.chart.update('none');
            }
            
            startAutoUpdate() {
                setInterval(() => {
                    this.updateAll();
                    this.updateChart();
                }, this.updateInterval);
            }
        }
        
        // Control functions
        let dashboard;
        
        function toggleRefresh() {
            dashboard.autoRefresh = !dashboard.autoRefresh;
            const btn = event.target;
            btn.classList.toggle('active');
            console.log('🔄 Auto-refresh:', dashboard.autoRefresh ? 'ON' : 'OFF');
        }
        
        function toggleSound() {
            dashboard.soundEnabled = !dashboard.soundEnabled;
            event.target.classList.toggle('active');
            console.log('🔊 Sound:', dashboard.soundEnabled ? 'ON' : 'OFF');
        }
        
        function exportData() {
            console.log('💾 Exporting data...');
            alert('📊 Data export feature coming soon!');
        }
        
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🌾 Enhanced AgriMind Dashboard loading...');
            dashboard = new EnhancedAgriMindDashboard();
        });
    </script>
</body>
</html>
        '''

def find_available_port():
    """Find an available port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def main():
    """Start Enhanced AgriMind Dashboard"""
    print("🌾 AgriMind Enhanced Dashboard - Pro Edition")
    print("=" * 70)
    print("🚀 Initializing advanced agricultural intelligence dashboard...")
    
    port = find_available_port()
    print(f"🔍 Using port: {port}")
    
    try:
        server = HTTPServer(('localhost', port), AdvancedAgriMindHandler)
        
        print(f"\n✅ Enhanced server running on http://localhost:{port}")
        print("\n🎯 Advanced Features:")
        print("   • 🧠 Enhanced AI agent monitoring")
        print("   • 📊 Real-time performance analytics")
        print("   • 💫 Smart transaction tracking")
        print("   • 🔮 AI-powered predictions")
        print("   • 🚨 Intelligent alert system") 
        print("   • 📈 Live performance charts")
        print("   • 🎛️ Interactive dashboard controls")
        print("   • 📱 Responsive modern UI")
        print("   • ⚡ 2-second real-time updates")
        
        print("\n🎮 Dashboard Controls:")
        print("   • 🔄 Toggle auto-refresh")
        print("   • 🔊 Sound notifications")
        print("   • 💾 Data export")
        print("   • 🖥️ Fullscreen mode")
        
        print(f"\n💡 Press Ctrl+C to stop the server")
        
        # Auto-open browser
        def launch_browser():
            time.sleep(1.5)
            try:
                webbrowser.open(f'http://localhost:{port}')
                print(f"\n🌐 Enhanced dashboard opened at http://localhost:{port}")
                print("🎉 Ready to impress hackathon judges!")
            except:
                print(f"🌐 Please open http://localhost:{port} in your browser")
        
        threading.Thread(target=launch_browser, daemon=True).start()
        
        print("\n" + "=" * 70)
        print("🏆 Enhanced AgriMind Dashboard is running!")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Enhanced dashboard stopped")
        print("✅ Thank you for using AgriMind Pro!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()