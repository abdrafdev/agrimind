#!/usr/bin/env python3
"""
AgriMind: Simple Real-Time Dashboard
Simplified web dashboard for monitoring agent activities
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
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import AgriMind components
try:
    from agents.base_agent import message_bus
    from config.config import get_config_manager
    config_manager = get_config_manager()
except ImportError as e:
    print(f"Warning: Could not import AgriMind components: {e}")
    message_bus = None
    config_manager = None

app = FastAPI(title="AgriMind Dashboard")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
connected_websockets: List[WebSocket] = []

# Simple HTML dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🌾 AgriMind Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <header class="bg-green-600 text-white p-4">
        <h1 class="text-2xl font-bold">🌾 AgriMind Real-Time Dashboard</h1>
        <div id="status" class="mt-2">
            Status: <span id="connection-status" class="pulse bg-red-500 px-2 py-1 rounded">Connecting...</span>
        </div>
    </header>

    <main class="container mx-auto p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded shadow">
                <h3 class="font-bold text-gray-700">System Status</h3>
                <div id="system-info" class="mt-4">
                    <p>Total Agents: <span id="total-agents" class="font-bold text-green-600">0</span></p>
                    <p>Online Agents: <span id="online-agents" class="font-bold text-blue-600">0</span></p>
                    <p>Last Update: <span id="last-update" class="text-gray-500">Never</span></p>
                </div>
            </div>
            
            <div class="bg-white p-6 rounded shadow">
                <h3 class="font-bold text-gray-700">Agent Activity</h3>
                <div id="agent-activity" class="mt-4 space-y-2">
                    <!-- Agent info will appear here -->
                </div>
            </div>
            
            <div class="bg-white p-6 rounded shadow">
                <h3 class="font-bold text-gray-700">Recent Messages</h3>
                <div id="messages" class="mt-4 space-y-1 text-sm">
                    <!-- Messages will appear here -->
                </div>
            </div>
        </div>

        <div class="bg-white p-6 rounded shadow">
            <h3 class="font-bold text-gray-700 mb-4">Live System Log</h3>
            <div id="live-log" class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
                <div>🌾 AgriMind Dashboard initialized...</div>
                <div>📡 Waiting for agent connections...</div>
            </div>
        </div>
    </main>

    <script>
        let socket = null;
        let messageCount = 0;

        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws`;
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function(event) {
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').className = 'bg-green-500 px-2 py-1 rounded';
                addLogMessage('✅ Connected to AgriMind system');
            };
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            socket.onclose = function(event) {
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').className = 'pulse bg-red-500 px-2 py-1 rounded';
                addLogMessage('❌ Connection lost, attempting to reconnect...');
                setTimeout(connectWebSocket, 3000);
            };
            
            socket.onerror = function(error) {
                addLogMessage('🚨 WebSocket error: ' + error);
            };
        }

        function updateDashboard(data) {
            // Update system metrics
            document.getElementById('total-agents').textContent = data.total_agents || 0;
            document.getElementById('online-agents').textContent = data.online_agents || 0;
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            
            // Update agent activity
            const agentActivity = document.getElementById('agent-activity');
            if (data.agents && Object.keys(data.agents).length > 0) {
                agentActivity.innerHTML = Object.entries(data.agents).map(([id, info]) => 
                    `<div class="flex justify-between">
                        <span class="text-sm">${id}:</span>
                        <span class="text-xs ${info.online ? 'text-green-600' : 'text-red-600'}">${info.online ? '🟢 Online' : '🔴 Offline'}</span>
                    </div>`
                ).join('');
            }
            
            // Add message to log
            addLogMessage(`📊 System update: ${data.total_agents} agents, ${data.online_agents} online`);
        }

        function addLogMessage(message) {
            const logDiv = document.getElementById('live-log');
            const time = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.textContent = `[${time}] ${message}`;
            logDiv.appendChild(logEntry);
            logDiv.scrollTop = logDiv.scrollHeight;
            
            messageCount++;
            if (messageCount > 100) {
                logDiv.removeChild(logDiv.firstChild);
                messageCount--;
            }
        }

        // Initialize dashboard
        connectWebSocket();
        
        // Send periodic status updates
        setInterval(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({type: 'ping', timestamp: Date.now()}));
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
    
    try:
        # Send initial data
        await send_system_update(websocket)
        
        while True:
            # Listen for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                # Respond to ping with current system status
                await send_system_update(websocket)
                
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

async def send_system_update(websocket: WebSocket):
    """Send system status update"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "total_agents": len(message_bus.agents) if message_bus else 0,
        "online_agents": len([a for a in message_bus.agents.values() if a.is_online()]) if message_bus else 0,
        "agents": {}
    }
    
    # Add agent details if available
    if message_bus:
        for agent_id, agent in message_bus.agents.items():
            data["agents"][agent_id] = {
                "online": agent.is_online(),
                "type": agent.agent_type.value if hasattr(agent.agent_type, 'value') else str(agent.agent_type),
                "balance": getattr(agent, 'balance', 0),
                "transactions": len(getattr(agent, 'transactions', {}))
            }
    
    try:
        await websocket.send_text(json.dumps(data))
    except Exception as e:
        print(f"Error sending update: {e}")

async def broadcast_updates():
    """Background task to broadcast updates to all connected clients"""
    while True:
        try:
            if connected_websockets:
                disconnected = []
                for websocket in connected_websockets:
                    try:
                        await send_system_update(websocket)
                    except Exception as e:
                        print(f"Error broadcasting to client: {e}")
                        disconnected.append(websocket)
                
                # Remove disconnected clients
                for ws in disconnected:
                    if ws in connected_websockets:
                        connected_websockets.remove(ws)
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"Broadcast error: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(broadcast_updates())
    print("🌾 AgriMind Simple Dashboard started!")

if __name__ == "__main__":
    print("🌾 Starting AgriMind Simple Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔗 WebSocket endpoint: ws://localhost:8000/ws")
    print("💡 This is a simplified version for demonstration")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )