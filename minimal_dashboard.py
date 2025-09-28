#!/usr/bin/env python3
"""
AgriMind: Minimal Real-Time Dashboard
Basic web dashboard for monitoring agent activities
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

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

app = FastAPI(title="AgriMind Dashboard")

# Global state
connected_websockets: List[WebSocket] = []

# Minimal HTML dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🌾 AgriMind Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: #4CAF50; color: white; padding: 20px; margin: -20px -20px 20px -20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status { display: inline-block; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
        .online { background: #4CAF50; color: white; }
        .offline { background: #f44336; color: white; }
        .log { background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 5px; font-family: monospace; height: 200px; overflow-y: auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric { text-align: center; }
        .metric h3 { margin: 0; color: #4CAF50; font-size: 2em; }
        .metric p { margin: 5px 0 0 0; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌾 AgriMind Real-Time Dashboard</h1>
        <span>Status: </span><span id="status" class="status offline">Connecting...</span>
    </div>

    <div class="grid">
        <div class="card">
            <h2>System Status</h2>
            <div class="metric">
                <h3 id="total-agents">0</h3>
                <p>Total Agents</p>
            </div>
            <div class="metric">
                <h3 id="online-agents">0</h3>
                <p>Online Agents</p>
            </div>
            <p>Last Update: <span id="last-update">Never</span></p>
        </div>

        <div class="card">
            <h2>Active Agents</h2>
            <div id="agent-list">
                <p style="color: #999;">No agents connected</p>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>Live System Log</h2>
        <div id="log" class="log">
            <div>[Starting] 🌾 AgriMind Dashboard initialized</div>
            <div>[System] 📡 Waiting for agent connections...</div>
        </div>
    </div>

    <script>
        let socket = null;

        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws`;
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                document.getElementById('status').textContent = 'Connected';
                document.getElementById('status').className = 'status online';
                addLog('✅ Connected to AgriMind system');
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            socket.onclose = function(event) {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status offline';
                addLog('❌ Connection lost, reconnecting...');
                setTimeout(connectWebSocket, 3000);
            };
            
            socket.onerror = function(error) {
                addLog('🚨 WebSocket error occurred');
            };
        }

        function updateDashboard(data) {
            document.getElementById('total-agents').textContent = data.total_agents || 0;
            document.getElementById('online-agents').textContent = data.online_agents || 0;
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            
            const agentList = document.getElementById('agent-list');
            if (data.agents && Object.keys(data.agents).length > 0) {
                agentList.innerHTML = Object.entries(data.agents).map(([id, info]) => 
                    `<p><strong>${id}</strong>: <span class="status ${info.online ? 'online' : 'offline'}">${info.online ? 'Online' : 'Offline'}</span> (${info.type || 'unknown'})</p>`
                ).join('');
            } else {
                agentList.innerHTML = '<p style="color: #999;">No agents connected</p>';
            }
            
            addLog(`📊 System update: ${data.total_agents} agents, ${data.online_agents} online`);
        }

        function addLog(message) {
            const log = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            const entry = document.createElement('div');
            entry.textContent = `[${time}] ${message}`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
            
            // Keep only last 50 entries
            while (log.children.length > 50) {
                log.removeChild(log.firstChild);
            }
        }

        // Start dashboard
        connectWebSocket();
        
        // Periodic ping
        setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'ping'}));
            }
        }, 10000);
    </script>
</body>
</html>
"""

@app.get("/")
async def get_dashboard():
    """Serve the dashboard HTML"""
    return HTMLResponse(content=DASHBOARD_HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    print(f"📱 New dashboard client connected. Total: {len(connected_websockets)}")
    
    try:
        # Send initial data
        await send_system_update(websocket)
        
        while True:
            # Listen for client messages
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    # Respond to ping with current system status
                    await send_system_update(websocket)
            except Exception as e:
                print(f"Error processing client message: {e}")
                break
                
    except WebSocketDisconnect:
        print("📱 Dashboard client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

async def send_system_update(websocket: WebSocket):
    """Send system status update"""
    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": 0,
            "online_agents": 0,
            "agents": {}
        }
        
        # Add agent details if message_bus is available
        if message_bus and hasattr(message_bus, 'agents'):
            data["total_agents"] = len(message_bus.agents)
            
            online_count = 0
            for agent_id, agent in message_bus.agents.items():
                is_online = True  # Default to online for demo
                if hasattr(agent, 'is_online'):
                    is_online = agent.is_online()
                elif hasattr(agent, 'online'):
                    is_online = agent.online
                    
                if is_online:
                    online_count += 1
                    
                agent_type = "unknown"
                if hasattr(agent, 'agent_type'):
                    agent_type = agent.agent_type.value if hasattr(agent.agent_type, 'value') else str(agent.agent_type)
                
                data["agents"][agent_id] = {
                    "online": is_online,
                    "type": agent_type,
                    "balance": getattr(agent, 'balance', 0),
                    "transactions": len(getattr(agent, 'transactions', {}))
                }
            
            data["online_agents"] = online_count
        
        await websocket.send_text(json.dumps(data))
        
    except Exception as e:
        print(f"Error sending system update: {e}")

async def broadcast_updates():
    """Background task to broadcast updates"""
    while True:
        try:
            if connected_websockets:
                disconnected = []
                for websocket in connected_websockets:
                    try:
                        await send_system_update(websocket)
                    except Exception as e:
                        print(f"Error broadcasting: {e}")
                        disconnected.append(websocket)
                
                # Remove disconnected clients
                for ws in disconnected:
                    if ws in connected_websockets:
                        connected_websockets.remove(ws)
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("🌾 Starting AgriMind Minimal Dashboard...")
    print("📊 Dashboard: http://localhost:8000")
    print("🔗 WebSocket: ws://localhost:8000/ws")
    print("💡 Simplified version for easy access")
    
    # Start background broadcast task
    async def startup():
        asyncio.create_task(broadcast_updates())
        print("🚀 Background tasks started")
    
    # Run with startup
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(startup())
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        loop="asyncio"
    )