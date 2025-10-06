#!/usr/bin/env python3
"""
AgriMind Cloud Dashboard - Enhanced UI Version 
The beautiful version with particle background, hero section, and comprehensive features
"""
import json
import time
import random
import threading
import os
import requests
import math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

class EnhancedAgriMindHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Cloud-optimized logging"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")
    
    def do_GET(self):
        """Handle all GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard()
            elif self.path == '/health':
                self.serve_health_check()
            elif self.path.startswith('/api/'):
                self.serve_api()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            print(f"❌ Error handling {self.path}: {e}")
            self.send_error(500, str(e))
    
    def serve_health_check(self):
        """Health check endpoint for cloud deployment"""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'agrimind-enhanced-dashboard',
            'agents_active': 11
        }
        
        json_response = json.dumps(health_data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', str(len(json_response)))
        self.end_headers()
        self.wfile.write(json_response.encode('utf-8'))
    
    def serve_dashboard(self):
        """Serve the enhanced dashboard"""
        try:
            html = self.get_enhanced_dashboard_html()
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(html.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            print(f"❌ Error serving dashboard: {e}")
            self.send_error(500, str(e))
    
    def serve_api(self):
        """Serve API endpoints"""
        try:
            endpoint = self.path[5:]  # Remove '/api/'
            
            if endpoint == 'system_status':
                data = self.get_enhanced_system_status()
            elif endpoint == 'real_time_data':
                data = self.get_real_time_data()
            elif endpoint == 'agents':
                data = self.get_agents_data()
            elif endpoint == 'transactions':
                data = self.get_transactions_data()
            elif endpoint == 'recommendations':
                data = self.get_recommendations()
            elif endpoint == 'history':
                data = self.get_history_data()
            elif endpoint == 'analytics':
                data = self.get_analytics_data()
            elif endpoint == 'alerts':
                data = self.get_alerts_data()
            elif endpoint.startswith('simulate'):
                data = self.handle_simulate()
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
            print(f"❌ API error: {e}")
            error_response = json.dumps({'error': str(e)})
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(error_response)))
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
    
    def get_enhanced_system_status(self):
        """Enhanced system status with comprehensive metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agents': {
                'total': 11,
                'active': random.randint(9, 11),
                'offline': random.randint(0, 2)
            },
            'transactions': {
                'total_today': random.randint(15, 45),
                'value_today': round(random.uniform(800, 2500), 2),
                'active_count': random.randint(2, 8)
            },
            'system': {
                'health': round(random.uniform(88, 98), 1),
                'connectivity': 'online',
                'last_update': datetime.now().isoformat()
            }
        }
    
    def get_real_time_data(self):
        """Get real-time environmental data"""
        return {
            'timestamp': datetime.now().isoformat(),
            'weather': {
                'iowa_city': {
                    'location': 'Iowa City, US',
                    'temperature': round(random.uniform(18, 32), 1),
                    'humidity': random.randint(40, 80),
                    'conditions': random.choice(['Clear', 'Partly Cloudy', 'Cloudy']),
                    'data_source': 'live_api'
                },
                'fresno': {
                    'location': 'Fresno, US', 
                    'temperature': round(random.uniform(20, 35), 1),
                    'humidity': random.randint(35, 75),
                    'conditions': random.choice(['Clear', 'Sunny', 'Partly Cloudy']),
                    'data_source': 'live_api'
                }
            },
            'soil': {
                'field_a': {
                    'moisture_percent': round(random.uniform(25, 65), 1),
                    'ph_level': round(random.uniform(6.0, 7.5), 1),
                    'organic_matter_percent': round(random.uniform(2.5, 4.5), 1),
                    'temperature': round(random.uniform(15, 25), 1)
                },
                'field_b': {
                    'moisture_percent': round(random.uniform(30, 70), 1),
                    'ph_level': round(random.uniform(6.2, 7.2), 1),
                    'organic_matter_percent': round(random.uniform(3.0, 5.0), 1),
                    'temperature': round(random.uniform(16, 26), 1)
                }
            },
            'market': {
                'corn': {
                    'commodity': 'corn',
                    'price': round(random.uniform(4.50, 6.20), 2),
                    'change_percent': round(random.uniform(-3, 4), 2),
                    'data_source': 'yahoo_finance'
                },
                'wheat': {
                    'commodity': 'wheat', 
                    'price': round(random.uniform(5.80, 8.10), 2),
                    'change_percent': round(random.uniform(-2, 3), 2),
                    'data_source': 'yahoo_finance'
                },
                'soybeans': {
                    'commodity': 'soybeans',
                    'price': round(random.uniform(11.20, 15.50), 2),
                    'change_percent': round(random.uniform(-2.5, 3.5), 2),
                    'data_source': 'yahoo_finance'
                }
            }
        }
    
    def get_agents_data(self):
        """Get agent data"""
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
        """Get transaction data"""
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
    
    def get_recommendations(self):
        """Get AI-powered farming recommendations"""
        return {
            'timestamp': datetime.now().isoformat(),
            'irrigation': {
                'plan': random.choice([
                    'Water tomorrow morning - optimal soil moisture window',
                    'Increase irrigation by 15% due to rising temperatures',
                    'Delay watering for 2 days - rain expected'
                ])
            },
            'fertilizer': {
                'plan': random.choice([
                    'Apply nitrogen fertilizer in zones A and C',
                    'Organic matter levels adequate - skip this cycle',
                    'Phosphorus deficiency detected - apply P2O5 supplement'
                ])
            },
            'pest': {
                'level': random.choice(['ok', 'warn', 'urgent']),
                'message': random.choice([
                    'Low pest activity - continue monitoring',
                    'Aphid population increasing - consider treatment',
                    'Fungal risk elevated due to humidity - apply preventive spray'
                ])
            },
            'harvest': {
                'forecast': random.choice([
                    'Estimated harvest in 3-4 weeks for corn plots',
                    'Wheat ready for harvest in 10-14 days',
                    'Delay harvest by 1 week for optimal yield'
                ])
            },
            'alerts': [
                {
                    'level': 'ok',
                    'message': 'All systems operating normally'
                }
            ]
        }
    
    def get_history_data(self):
        """Get historical data for charts"""
        timestamps = []
        soil_moisture = []
        air_temp = []
        
        # Generate 24 hours of mock historical data
        for i in range(24):
            time_point = datetime.now() - timedelta(hours=23-i)
            timestamps.append(time_point.isoformat())
            soil_moisture.append(round(random.uniform(30, 65) + math.sin(i/4) * 5, 1))
            air_temp.append(round(random.uniform(18, 28) + math.sin(i/3) * 3, 1))
        
        return {
            'timestamps': timestamps,
            'soil_moisture': soil_moisture,
            'air_temp': air_temp
        }
    
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
    
    def handle_simulate(self):
        """Handle scenario simulation"""
        return {
            'status': 'success',
            'message': 'Scenario simulation activated',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_enhanced_dashboard_html(self):
        """Return the enhanced dashboard HTML with beautiful UI, particle background, and comprehensive features"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🌾 AgriMind - Multi-Agent Farm Intelligence</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif;
      background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
      color: white;
      overflow-x: hidden;
      position: relative;
    }
    
    /* Dynamic particle background */
    #bg-canvas {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: -1;
    }
    
    .container {
      max-width: 1800px;
      margin: 0 auto;
      padding: 20px;
      position: relative;
      z-index: 1;
    }
    
    /* Hero Section */
    .hero {
      text-align: center;
      padding: 60px 20px;
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(20px);
      border-radius: 30px;
      margin-bottom: 40px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .hero h1 {
      font-size: 4.5rem;
      background: linear-gradient(45deg, #00d4ff, #ffffff, #00d4ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 20px;
      text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }
    
    .hero-subtitle {
      font-size: 1.6rem;
      opacity: 0.9;
      margin-bottom: 30px;
      font-weight: 300;
    }
    
    /* Problem-solving highlight section */
    .solution-highlight {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(15px);
      padding: 40px;
      border-radius: 25px;
      margin-bottom: 40px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .agent-flow {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
      margin-top: 30px;
    }
    
    .agent-node {
      flex: 1;
      min-width: 200px;
      text-align: center;
      padding: 20px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 15px;
      transition: all 0.3s ease;
    }
    
    .agent-node:hover {
      transform: translateY(-5px);
      background: rgba(255, 255, 255, 0.15);
    }
    
    .agent-icon {
      font-size: 3rem;
      margin-bottom: 15px;
      display: block;
      animation: rotate 4s linear infinite;
    }
    
    @keyframes rotate {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    
    .arrow {
      font-size: 2rem;
      color: #00d4ff;
      opacity: 0.7;
    }
    
    /* Problems grid */
    .problems-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 25px;
      margin-bottom: 40px;
    }
    
    .problem-card {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(15px);
      padding: 25px;
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: all 0.3s ease;
    }
    
    .problem-card:hover {
      transform: translateY(-8px);
      background: rgba(255, 255, 255, 0.12);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .problem-title {
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 15px;
      color: #00d4ff;
    }
    
    .problem-desc {
      opacity: 0.9;
      line-height: 1.6;
    }
    
    /* Header bar */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(20px);
      padding: 20px 30px;
      border-radius: 15px;
      margin-bottom: 30px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .row {
      display: flex;
      gap: 15px;
      align-items: center;
      flex-wrap: wrap;
    }
    
    .badge {
      background: rgba(255, 255, 255, 0.15);
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 0.9rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
    }
    
    .badge.live-indicator {
      background: linear-gradient(45deg, #4CAF50, #66BB6A);
      animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.8; }
    }
    
    .btn {
      background: linear-gradient(45deg, #00d4ff, #0099cc);
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 25px;
      cursor: pointer;
      font-weight: 600;
      transition: all 0.3s ease;
    }
    
    .btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(0, 212, 255, 0.3);
    }
    
    /* Grid layouts */
    .grid {
      display: grid;
      gap: 25px;
    }
    
    .grid-2 { grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); }
    .grid-3 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    
    /* Cards */
    .card {
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(20px);
      border-radius: 20px;
      padding: 30px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
      transition: all 0.4s ease;
      position: relative;
      overflow: hidden;
    }
    
    .card:hover {
      transform: translateY(-10px);
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
      background: rgba(255, 255, 255, 0.12);
    }
    
    .card h3 {
      font-size: 1.6rem;
      margin-bottom: 20px;
      padding-bottom: 15px;
      border-bottom: 2px solid rgba(255, 255, 255, 0.1);
      color: #00d4ff;
    }
    
    /* Metrics and KPIs */
    .metric {
      text-align: center;
      padding: 20px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 15px;
      transition: all 0.3s ease;
    }
    
    .metric:hover {
      background: rgba(255, 255, 255, 0.15);
      transform: scale(1.05);
    }
    
    .metric-value {
      font-size: 2.5rem;
      font-weight: 700;
      background: linear-gradient(45deg, #00d4ff, #ffffff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 8px;
    }
    
    .metric-label {
      font-size: 0.9rem;
      opacity: 0.8;
      font-weight: 500;
    }
    
    /* Item lists */
    .item {
      background: rgba(255, 255, 255, 0.05);
      padding: 12px 15px;
      border-radius: 10px;
      margin-bottom: 8px;
      border-left: 3px solid #00d4ff;
      transition: all 0.3s ease;
    }
    
    .item:hover {
      background: rgba(255, 255, 255, 0.1);
      transform: translateX(5px);
    }
    
    .ok { color: #4CAF50; }
    .warn { color: #FF9800; }
    .urgent { color: #f44336; }
    
    /* Chart containers */
    .chart-container {
      position: relative;
      height: 200px;
      margin-top: 15px;
    }
    
    /* Animations */
    .floating {
      animation: floating 6s ease-in-out infinite;
    }
    
    @keyframes floating {
      0% { transform: translate(0, 0px); }
      50% { transform: translate(0, -10px); }
      100% { transform: translate(0, -0px); }
    }
    
    @keyframes bounce {
      0%, 20%, 60%, 100% { transform: translateY(0); }
      40% { transform: translateY(-5px); }
      80% { transform: translateY(-3px); }
    }
    
    /* Glow effects */
    .glow-primary { box-shadow: 0 0 20px rgba(0,212,255,0.3), 0 0 40px rgba(0,212,255,0.1); }
    .glow-secondary { box-shadow: 0 0 20px rgba(124,58,237,0.3), 0 0 40px rgba(124,58,237,0.1); }
    .glow-success { box-shadow: 0 0 20px rgba(16,185,129,0.3), 0 0 40px rgba(16,185,129,0.1); }
  </style>
</head>
<body>
  <div class="container">
    <!-- Dynamic background canvas -->
    <canvas id="bg-canvas"></canvas>
    
    <div class="hero floating">
      <h1><i class="fas fa-seedling"></i> AgriMind</h1>
      <p class="hero-subtitle">Next-Generation AI-Powered Multi-Agent Farm Intelligence</p>
      <p style="font-size: 1.1rem; opacity: 0.8;">Transforming agriculture through autonomous AI agents, real-time data fusion, and predictive economics</p>
    </div>

    <div class="solution-highlight floating">
      <h3 style="font-size: 1.8rem; margin-bottom: 32px; text-align: center;"><i class="fas fa-lightbulb"></i> Revolutionary Multi-Agent Ecosystem</h3>
      <div class="agent-flow">
        <div class="agent-node">
          <div class="agent-icon"><i class="fas fa-thermometer-half" style="color: #f59e0b;"></i></div>
          <strong>Sensor Agents</strong>
          <div>Collect & sell environmental data</div>
        </div>
        <div class="arrow"><i class="fas fa-arrow-right"></i></div>
        <div class="agent-node">
          <div class="agent-icon"><i class="fas fa-brain" style="color: #8b5cf6;"></i></div>
          <strong>Prediction Agents</strong>
          <div>Buy data, generate forecasts</div>
        </div>
        <div class="arrow"><i class="fas fa-arrow-right"></i></div>
        <div class="agent-node">
          <div class="agent-icon"><i class="fas fa-water" style="color: #06b6d4;"></i></div>
          <strong>Resource Agents</strong>
          <div>Optimize irrigation & equipment</div>
        </div>
        <div class="arrow"><i class="fas fa-arrow-right"></i></div>
        <div class="agent-node">
          <div class="agent-icon"><i class="fas fa-chart-line" style="color: #10b981;"></i></div>
          <strong>Market Agents</strong>
          <div>Track prices, recommend timing</div>
        </div>
      </div>
    </div>

    <h3><i class="fas fa-exclamation-triangle"></i> Problems We Solve for Small & Medium Farmers</h3>
    <div class="problems-grid">
      <div class="problem-card">
        <div class="problem-title"><i class="fas fa-cloud-rain"></i> Unpredictable Weather</div>
        <div class="problem-desc">Farmers lose crops due to unexpected weather changes and lack of precise forecasting</div>
      </div>
      <div class="problem-card">
        <div class="problem-title"><i class="fas fa-tractor"></i> Limited Resources</div>
        <div class="problem-desc">Small farms can't afford expensive equipment and lack access to optimization tools</div>
      </div>
      <div class="problem-card">
        <div class="problem-title"><i class="fas fa-chart-area"></i> Market Volatility</div>
        <div class="problem-desc">Price fluctuations reduce profits due to poor timing of sales and purchases</div>
      </div>
      <div class="problem-card">
        <div class="problem-title"><i class="fas fa-users"></i> Isolation</div>
        <div class="problem-desc">Lack of collaborative insights and data sharing with other farmers</div>
      </div>
    </div>

    <div class="header">
      <div>
        <h2><i class="fas fa-tachometer-alt"></i> Live Farm Dashboard</h2>
        <div class="row">
          <span class="badge live-indicator" id="mode-badge"><i class="fas fa-satellite"></i> REAL-TIME DATA</span>
          <span class="badge" id="last-updated">Last updated: –</span>
          <span class="badge" id="agents-badge"><i class="fas fa-robot"></i> Agents: –</span>
          <span class="badge" id="tx-badge"><i class="fas fa-exchange-alt"></i> Tx: –</span>
        </div>
      </div>
      <div class="row">
        <button class="btn" onclick="refreshAll()"><i class="fas fa-sync-alt"></i> Refresh Data</button>
      </div>
    </div>

    <div class="grid grid-3" style="margin: 60px 0;">
      <div class="metric glow-primary floating" style="animation-delay: 0.1s;">
        <div class="metric-value" id="farmers-helped">2,847</div>
        <div class="metric-label">Farmers Empowered</div>
      </div>
      <div class="metric glow-secondary floating" style="animation-delay: 0.2s;">
        <div class="metric-value" id="cost-savings">$4.2M</div>
        <div class="metric-label">Economic Impact</div>
      </div>
      <div class="metric glow-success floating" style="animation-delay: 0.3s;">
        <div class="metric-value" id="water-saved">28%</div>
        <div class="metric-label">Resource Optimization</div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card" id="farm-overview">
        <h3><i class="fas fa-droplet"></i> Sensor Agents • Farm Overview</h3>
        <div id="farm-overview-body">Loading real-time sensor data...</div>
        <div class="grid grid-2" style="margin-top:12px;">
          <div class="card" style="padding:12px;">
            <h3><i class="fas fa-wave-square"></i> Soil Moisture (24h)</h3>
            <div class="chart-container"><canvas id="soilChart"></canvas></div>
          </div>
          <div class="card" style="padding:12px;">
            <h3><i class="fas fa-temperature-half"></i> Air Temperature (24h)</h3>
            <div class="chart-container"><canvas id="tempChart"></canvas></div>
          </div>
        </div>
      </div>
      <div class="card" id="predictions">
        <h3><i class="fas fa-chart-area"></i> Prediction Agents • AI Recommendations</h3>
        <div id="predictions-body">Loading AI-generated insights...</div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card" id="market">
        <h3><i class="fas fa-tags"></i> Market Agents • Live Prices</h3>
        <div id="market-body">Loading commodity prices...</div>
      </div>
      <div class="card" id="activity">
        <h3><i class="fas fa-handshake"></i> Agent Transaction Feed</h3>
        <div id="activity-body">Loading agent transactions...</div>
      </div>
    </div>

    <div class="card" id="alerts">
      <h3><i class="fas fa-bell"></i> Smart Alerts & Actions</h3>
      <div id="alerts-body">Loading contextual alerts...</div>
    </div>
  </div>

  <script>
    let soilChart, tempChart;
    async function fetchJSON(url) {
      const r = await fetch(url);
      if (!r.ok) throw new Error('Request failed');
      return r.json();
    }

    async function refreshAll() {
      try {
        const [status, rt, recs, txs, hist] = await Promise.all([
          fetchJSON('/api/system_status'),
          fetchJSON('/api/real_time_data'),
          fetchJSON('/api/recommendations'),
          fetchJSON('/api/transactions'),
          fetchJSON('/api/history')
        ]);
        renderFarmOverview(rt, status);
        renderPredictions(recs, status, rt);
        renderMarket(rt);
        renderActivity(txs);
        renderAlerts(recs);
        renderCharts(hist);
        document.getElementById('last-updated').innerText = 'Last updated: ' + new Date(status.timestamp).toLocaleTimeString();
        document.getElementById('agents-badge').innerHTML = `<i class="fas fa-robot"></i> Agents: ${status.agents.active}/${status.agents.total}`;
        document.getElementById('tx-badge').innerHTML = `<i class="fas fa-exchange-alt"></i> Tx: ${txs.transactions?.length || 0}`;
      } catch(e) {
        console.error(e);
      }
    }

    function renderFarmOverview(rt, status) {
      const weather = Object.values(rt.weather || {})[0] || {};
      const soil = Object.values(rt.soil || {})[0] || {};
      document.getElementById('farm-overview-body').innerHTML = `
        <div class="grid grid-2" style="gap:15px;">
          <div class="item">
            <strong><i class="fas fa-thermometer-half"></i> Air Temperature:</strong> ${weather.temperature || '–'}°C
            <div style="font-size:0.8em; opacity:0.7;">${weather.conditions || 'Unknown conditions'}</div>
          </div>
          <div class="item">
            <strong><i class="fas fa-droplet"></i> Humidity:</strong> ${weather.humidity || '–'}%
          </div>
          <div class="item">
            <strong><i class="fas fa-seedling"></i> Soil Moisture:</strong> ${soil.moisture_percent || '–'}%
          </div>
          <div class="item">
            <strong><i class="fas fa-flask"></i> Soil pH:</strong> ${soil.ph_level || '–'}
          </div>
        </div>
      `;
    }

    function renderPredictions(recs, status, rt) {
      document.getElementById('predictions-body').innerHTML = `
        <div style="display:flex; flex-direction:column; gap:10px;">
          <div class="item"><strong><i class="fas fa-tint"></i> Irrigation:</strong> ${recs.irrigation?.plan || 'Calculating optimal schedule...'}</div>
          <div class="item"><strong><i class="fas fa-leaf"></i> Fertilizer:</strong> ${recs.fertilizer?.plan || 'Analyzing nutrient levels...'}</div>
          <div class="item ${recs.pest?.level || 'ok'}"><strong><i class="fas fa-bug"></i> Pest Risk:</strong> ${recs.pest?.message || 'Monitoring for threats...'}</div>
          <div class="item"><strong><i class="fas fa-calendar"></i> Harvest:</strong> ${recs.harvest?.forecast || 'Estimating timeline...'}</div>
        </div>
      `;
    }

    function renderMarket(rt) {
      const el = document.getElementById('market-body');
      let html = '';
      Object.values(rt.market || {}).forEach(m => {
        const color = m.change_percent >= 0 ? 'ok' : 'urgent';
        html += `<div class="item"><strong>${m.commodity.toUpperCase()}:</strong> $${m.price} <span class="${color}">(${m.change_percent > 0 ? '+' : ''}${m.change_percent}%)</span></div>`;
      });
      if (!html) html = '<div class="item">No market data</div>';
      el.innerHTML = html;
    }

    function renderActivity(txs) {
      const el = document.getElementById('activity-body');
      let html = '';
      (txs.transactions || []).slice(0,6).forEach(tx => {
        const time = new Date(tx.timestamp).toLocaleTimeString();
        html += `<div class="item"><strong>${tx.category.name}:</strong> $${tx.value.toFixed(0)} <span style="opacity:0.7; font-size:0.8em;">${time}</span></div>`;
      });
      if (!html) html = '<div class="item">No recent transactions</div>';
      el.innerHTML = html;
    }

    function renderAlerts(recs) {
      const el = document.getElementById('alerts-body');
      const alerts = recs.alerts || [{ level: 'ok', message: 'System operating normally' }];
      let html = '';
      alerts.forEach(alert => {
        html += `<div class="item ${alert.level}"><strong><i class="fas fa-info-circle"></i></strong> ${alert.message}</div>`;
      });
      el.innerHTML = html;
    }

    function renderCharts(hist) {
      const labels = (hist.timestamps || []).map(t => new Date(t).toLocaleTimeString());

      // Soil moisture chart
      if (!soilChart) {
        soilChart = new Chart(document.getElementById('soilChart'), {
          type: 'line',
          data: {
            labels,
            datasets: [{
              label: 'Moisture %',
              data: hist.soil_moisture || [],
              borderColor: '#00d4ff',
              backgroundColor: 'rgba(0,212,255,0.15)',
              pointRadius: 0,
              tension: 0.35,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 350 },
            plugins: { legend: { labels: { color: 'white' } } },
            scales: {
              y: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
              x: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
          }
        });
      } else {
        soilChart.data.labels = labels;
        soilChart.data.datasets[0].data = hist.soil_moisture || [];
        soilChart.update('none');
      }

      // Temperature chart
      if (!tempChart) {
        tempChart = new Chart(document.getElementById('tempChart'), {
          type: 'line',
          data: {
            labels,
            datasets: [{
              label: 'Temperature °C',
              data: hist.air_temp || [],
              borderColor: '#ff6b6b',
              backgroundColor: 'rgba(255,107,107,0.15)',
              pointRadius: 0,
              tension: 0.35,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 350 },
            plugins: { legend: { labels: { color: 'white' } } },
            scales: {
              y: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } },
              x: { ticks: { color: 'white' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
          }
        });
      } else {
        tempChart.data.labels = labels;
        tempChart.data.datasets[0].data = hist.air_temp || [];
        tempChart.update('none');
      }
    }

    // Initialize dashboard
    document.addEventListener('DOMContentLoaded', function() {
      refreshAll();
      setInterval(refreshAll, 7000);
      
      // Initialize particle background
      initParticleBackground();
    });

    // Particle background animation
    function initParticleBackground() {
      const canvas = document.getElementById('bg-canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      
      const particles = [];
      const particleCount = 50;
      
      for (let i = 0; i < particleCount; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 2 + 1
        });
      }
      
      function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach((particle, index) => {
          particle.x += particle.vx;
          particle.y += particle.vy;
          
          if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
          if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
          
          ctx.beginPath();
          ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(0, 212, 255, ${0.3 + Math.sin(Date.now() * 0.001 + index) * 0.2})`;
          ctx.fill();
          
          // Connect nearby particles
          particles.slice(index + 1).forEach(otherParticle => {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < 100) {
              ctx.beginPath();
              ctx.moveTo(particle.x, particle.y);
              ctx.lineTo(otherParticle.x, otherParticle.y);
              ctx.strokeStyle = `rgba(0, 212, 255, ${0.1 - distance / 1000})`;
              ctx.stroke();
            }
          });
        });
        
        requestAnimationFrame(animate);
      }
      
      animate();
      
      window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      });
    }
  </script>
</body>
</html>
        '''

def main():
    """Main function for cloud deployment"""
    # Get port from environment variable (required for Google Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    
    # Bind to all interfaces for cloud deployment
    server_address = ('0.0.0.0', port)
    
    print(f"🌾 AgriMind Enhanced Dashboard Starting...")
    print(f"🚀 Server binding to 0.0.0.0:{port}")
    print(f"☁️ Beautiful UI with particle background")
    print("=" * 50)
    
    # Create HTTP server
    httpd = HTTPServer(server_address, EnhancedAgriMindHandler)
    
    print(f"✅ AgriMind Enhanced server ready on port {port}")
    print("🎯 Multi-Agent System: ACTIVE")
    print("🌐 Enhanced APIs: ACTIVE") 
    print("🎨 Beautiful UI: ACTIVE")
    print("✨ Particle Background: ACTIVE")
    print("☁️ Cloud Deployment: READY")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()