#!/usr/bin/env python3
"""
AgriMind: Flask Dashboard
Simple web dashboard using Flask for monitoring agent activities
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from threading import Thread, Event

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    from flask import Flask, render_template_string, jsonify
    from flask_socketio import SocketIO, emit
    flask_available = True
except ImportError:
    flask_available = False
    print("Flask not available, creating basic HTTP server instead")

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

# Basic HTTP server fallback
if not flask_available:
    import http.server
    import socketserver
    from urllib.parse import urlparse, parse_qs
    
    class AgriMindHTTPHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>🌾 AgriMind Dashboard</title></head>
                <body style="font-family: Arial; background: #f5f5f5; margin: 40px;">
                    <div style="background: #4CAF50; color: white; padding: 20px; margin: -40px -40px 20px -40px;">
                        <h1>🌾 AgriMind Dashboard</h1>
                        <p>Basic HTTP Dashboard - Auto-refreshing every 10 seconds</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2>System Status (Last Updated: {datetime.now().strftime('%H:%M:%S')})</h2>
                        <p><strong>Total Agents:</strong> {len(message_bus.agents) if message_bus else 0}</p>
                        <p><strong>Message Bus:</strong> {"Connected" if message_bus else "Not Connected"}</p>
                        <p><strong>Config:</strong> {"Loaded" if config_manager else "Not Loaded"}</p>
                    </div>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px;">
                        <h2>Agent Details</h2>
                        {'<p style="color: #999;">No agents connected</p>' if not message_bus or not message_bus.agents else 
                         '<br>'.join([f'<p><strong>{agent_id}:</strong> {type(agent).__name__} - Online</p>' 
                                     for agent_id, agent in message_bus.agents.items()])}
                    </div>
                    
                    <script>
                        // Auto-refresh every 10 seconds
                        setTimeout(function(){{ window.location.reload(); }}, 10000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            elif self.path == '/api/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'total_agents': len(message_bus.agents) if message_bus else 0,
                    'message_bus_connected': message_bus is not None,
                    'config_loaded': config_manager is not None
                }
                self.wfile.write(json.dumps(status).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    def run_basic_server():
        PORT = 8000
        with socketserver.TCPServer(("", PORT), AgriMindHTTPHandler) as httpd:
            print(f"🌾 Basic AgriMind Dashboard running at http://localhost:{PORT}")
            print("📊 Auto-refreshing dashboard (no WebSocket)")
            print("💡 This is a fallback when Flask is not available")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n📱 Dashboard server stopped")

# Flask-based dashboard
else:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'agrimind_dashboard_secret'
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Dashboard HTML template
    DASHBOARD_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌾 AgriMind Dashboard</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #4CAF50; color: white; padding: 20px; margin: -20px -20px 20px -20px; border-radius: 0 0 8px 8px; }
            .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .status { display: inline-block; padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: bold; }
            .online { background: #4CAF50; color: white; }
            .offline { background: #f44336; color: white; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .metric { text-align: center; margin: 10px 0; }
            .metric h3 { margin: 0; color: #4CAF50; font-size: 2.5em; }
            .metric p { margin: 5px 0 0 0; color: #666; }
            .log { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 5px; font-family: monospace; max-height: 300px; overflow-y: auto; }
            .pulse { animation: pulse 2s infinite; }
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌾 AgriMind Real-Time Dashboard</h1>
            <p>Multi-Agent Farm Intelligence Network - Live Monitoring</p>
            <span>Connection: </span><span id="status" class="status pulse offline">Connecting...</span>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📊 System Metrics</h2>
                <div class="metric">
                    <h3 id="total-agents">0</h3>
                    <p>Total Agents</p>
                </div>
                <div class="metric">
                    <h3 id="online-agents">0</h3>
                    <p>Online Agents</p>
                </div>
                <p style="text-align: center; color: #888;">
                    Last Update: <span id="last-update">Never</span>
                </p>
            </div>

            <div class="card">
                <h2>🤖 Active Agents</h2>
                <div id="agent-list" style="min-height: 150px;">
                    <p style="color: #999; text-align: center;">No agents detected</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📝 Live Activity Log</h2>
            <div id="activity-log" class="log" style="min-height: 250px;">
                <div>[INIT] 🌾 AgriMind Dashboard starting...</div>
                <div>[SYSTEM] 📡 Connecting to agent network...</div>
            </div>
        </div>

        <script>
            const socket = io();
            let logCount = 0;

            socket.on('connect', function() {
                document.getElementById('status').textContent = 'Connected';
                document.getElementById('status').className = 'status online';
                addLog('✅ Connected to AgriMind system');
            });

            socket.on('disconnect', function() {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status pulse offline';
                addLog('❌ Connection lost');
            });

            socket.on('system_update', function(data) {
                updateDashboard(data);
            });

            function updateDashboard(data) {
                document.getElementById('total-agents').textContent = data.total_agents || 0;
                document.getElementById('online-agents').textContent = data.online_agents || 0;
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
                const agentList = document.getElementById('agent-list');
                if (data.agents && Object.keys(data.agents).length > 0) {
                    agentList.innerHTML = Object.entries(data.agents).map(([id, info]) => {
                        const statusClass = info.online ? 'online' : 'offline';
                        const statusText = info.online ? 'Online' : 'Offline';
                        return `
                            <div style="display: flex; justify-content: space-between; align-items: center; margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 4px;">
                                <span><strong>${id}</strong><br><small style="color: #666;">${info.type || 'Unknown Type'}</small></span>
                                <span class="status ${statusClass}">${statusText}</span>
                            </div>
                        `;
                    }).join('');
                } else {
                    agentList.innerHTML = '<p style="color: #999; text-align: center;">No agents detected</p>';
                }
                
                addLog(`📊 Update: ${data.total_agents} agents (${data.online_agents} online)`);
            }

            function addLog(message) {
                const log = document.getElementById('activity-log');
                const time = new Date().toLocaleTimeString();
                const entry = document.createElement('div');
                entry.textContent = `[${time}] ${message}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
                
                logCount++;
                if (logCount > 100) {
                    log.removeChild(log.firstChild);
                    logCount--;
                }
            }

            // Request updates every 5 seconds
            setInterval(() => {
                socket.emit('request_update');
            }, 5000);

            // Initial update request
            socket.emit('request_update');
        </script>
    </body>
    </html>
    """

    @app.route('/')
    def dashboard():
        """Serve the main dashboard"""
        return render_template_string(DASHBOARD_TEMPLATE)

    @app.route('/api/status')
    def api_status():
        """API endpoint for system status"""
        return get_system_status()

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"📱 Dashboard client connected")
        emit('system_update', get_system_status())

    @socketio.on('request_update')
    def handle_update_request():
        """Handle update requests from clients"""
        emit('system_update', get_system_status())

    def get_system_status():
        """Get current system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': 0,
            'online_agents': 0,
            'agents': {}
        }
        
        if message_bus and hasattr(message_bus, 'agents'):
            status['total_agents'] = len(message_bus.agents)
            
            online_count = 0
            for agent_id, agent in message_bus.agents.items():
                # Determine if agent is online
                is_online = True  # Default assumption
                if hasattr(agent, 'is_online'):
                    is_online = agent.is_online()
                elif hasattr(agent, 'online'):
                    is_online = agent.online
                
                if is_online:
                    online_count += 1
                
                # Get agent type
                agent_type = "Unknown"
                if hasattr(agent, 'agent_type'):
                    if hasattr(agent.agent_type, 'value'):
                        agent_type = agent.agent_type.value
                    else:
                        agent_type = str(agent.agent_type)
                else:
                    agent_type = type(agent).__name__
                
                status['agents'][agent_id] = {
                    'online': is_online,
                    'type': agent_type,
                    'balance': getattr(agent, 'balance', 0),
                    'transactions': len(getattr(agent, 'transactions', {}))
                }
            
            status['online_agents'] = online_count
        
        return status

    def run_flask_server():
        print("🌾 Starting AgriMind Flask Dashboard...")
        print("📊 Dashboard: http://localhost:8000")
        print("🔗 WebSocket support enabled")
        print("💡 Real-time updates with Flask-SocketIO")
        
        try:
            socketio.run(app, host='127.0.0.1', port=8000, debug=False)
        except KeyboardInterrupt:
            print("\n📱 Dashboard server stopped")

if __name__ == "__main__":
    if flask_available:
        run_flask_server()
    else:
        run_basic_server()