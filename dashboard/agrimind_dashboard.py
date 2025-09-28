"""
AgriMind: Real-Time Dashboard
Web-based dashboard for monitoring agent activities, transactions, and system health
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

# Import AgriMind components
from agents.base_agent import message_bus, MessageType, AgentType
from config.config import get_config_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgriMind-Dashboard")

app = FastAPI(title="AgriMind Dashboard", description="Real-time farm intelligence monitoring")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class AgentStatus(BaseModel):
    agent_id: str
    agent_type: str
    online: bool
    balance: float
    message_queue_length: int
    transactions_count: int
    last_activity: str

class SystemMetrics(BaseModel):
    total_agents: int
    online_agents: int
    total_transactions: int
    total_messages: int
    system_uptime: str
    data_sources_active: int

class TransactionData(BaseModel):
    transaction_id: str
    buyer_id: str
    seller_id: str
    item_type: str
    quantity: float
    price: float
    timestamp: str
    status: str

# Global state
connected_websockets: List[WebSocket] = []
dashboard_data = {
    "agents": {},
    "transactions": [],
    "messages": [],
    "system_metrics": {},
    "alerts": []
}

# Dashboard HTML page
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌾 AgriMind Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .agent-card { transition: all 0.3s ease; }
        .agent-card:hover { transform: scale(1.02); }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <header class="bg-green-600 text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">🌾 AgriMind: Collaborative Farm Intelligence</h1>
            <div class="flex items-center space-x-4">
                <span id="connection-status" class="px-3 py-1 bg-red-500 rounded-full text-sm">Disconnected</span>
                <span id="last-update" class="text-sm opacity-75">Never</span>
            </div>
        </div>
    </header>

    <main class="container mx-auto p-6">
        <!-- System Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Total Agents</h3>
                <p id="total-agents" class="text-3xl font-bold text-green-600">0</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Online Agents</h3>
                <p id="online-agents" class="text-3xl font-bold text-blue-600">0</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Transactions</h3>
                <p id="total-transactions" class="text-3xl font-bold text-purple-600">0</p>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-2">Messages</h3>
                <p id="total-messages" class="text-3xl font-bold text-yellow-600">0</p>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Agent Activity</h3>
                <canvas id="agentActivityChart" width="400" height="200"></canvas>
            </div>
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h3 class="text-lg font-semibold text-gray-700 mb-4">Transaction Volume</h3>
                <canvas id="transactionChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- Agents Grid -->
        <div class="bg-white p-6 rounded-lg shadow-md mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Active Agents</h3>
            <div id="agents-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                <!-- Agent cards will be populated here -->
            </div>
        </div>

        <!-- Recent Transactions -->
        <div class="bg-white p-6 rounded-lg shadow-md mb-8">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">Recent Transactions</h3>
            <div class="overflow-x-auto">
                <table class="min-w-full table-auto">
                    <thead>
                        <tr class="bg-gray-50">
                            <th class="px-4 py-2 text-left">Time</th>
                            <th class="px-4 py-2 text-left">Buyer</th>
                            <th class="px-4 py-2 text-left">Seller</th>
                            <th class="px-4 py-2 text-left">Item</th>
                            <th class="px-4 py-2 text-left">Quantity</th>
                            <th class="px-4 py-2 text-left">Price</th>
                            <th class="px-4 py-2 text-left">Status</th>
                        </tr>
                    </thead>
                    <tbody id="transactions-table">
                        <!-- Transactions will be populated here -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- System Alerts -->
        <div class="bg-white p-6 rounded-lg shadow-md">
            <h3 class="text-lg font-semibold text-gray-700 mb-4">System Alerts</h3>
            <div id="alerts-container" class="space-y-2">
                <!-- Alerts will be populated here -->
            </div>
        </div>
    </main>

    <script>
        let socket = null;
        let agentActivityChart = null;
        let transactionChart = null;

        // Initialize dashboard
        function initDashboard() {
            connectWebSocket();
            initCharts();
        }

        // WebSocket connection
        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws`;
            socket = new WebSocket(wsUrl);

            socket.onopen = function(event) {
                console.log('Connected to AgriMind Dashboard');
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').className = 'px-3 py-1 bg-green-500 rounded-full text-sm';
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            };

            socket.onclose = function(event) {
                console.log('Disconnected from AgriMind Dashboard');
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').className = 'px-3 py-1 bg-red-500 rounded-full text-sm';
                
                // Reconnect after 5 seconds
                setTimeout(connectWebSocket, 5000);
            };

            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        // Initialize charts
        function initCharts() {
            const ctx1 = document.getElementById('agentActivityChart').getContext('2d');
            agentActivityChart = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Sensor', 'Prediction', 'Resource', 'Market'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#10B981', '#3B82F6', '#8B5CF6', '#F59E0B']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            const ctx2 = document.getElementById('transactionChart').getContext('2d');
            transactionChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Transactions per Minute',
                        data: [],
                        borderColor: '#8B5CF6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Update dashboard with new data
        function updateDashboard(data) {
            updateMetrics(data.system_metrics);
            updateAgents(data.agents);
            updateTransactions(data.transactions);
            updateCharts(data);
            updateAlerts(data.alerts);
        }

        // Update system metrics
        function updateMetrics(metrics) {
            if (!metrics) return;
            
            document.getElementById('total-agents').textContent = metrics.total_agents || 0;
            document.getElementById('online-agents').textContent = metrics.online_agents || 0;
            document.getElementById('total-transactions').textContent = metrics.total_transactions || 0;
            document.getElementById('total-messages').textContent = metrics.total_messages || 0;
        }

        // Update agents display
        function updateAgents(agents) {
            if (!agents) return;

            const grid = document.getElementById('agents-grid');
            grid.innerHTML = '';

            Object.values(agents).forEach(agent => {
                const card = document.createElement('div');
                card.className = `agent-card p-4 border rounded-lg ${agent.online ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`;
                
                const statusColor = agent.online ? 'text-green-600' : 'text-red-600';
                const statusIcon = agent.online ? '🟢' : '🔴';
                
                card.innerHTML = `
                    <div class="flex justify-between items-center mb-2">
                        <h4 class="font-semibold">${agent.agent_id}</h4>
                        <span class="${statusColor}">${statusIcon}</span>
                    </div>
                    <p class="text-sm text-gray-600 mb-2">${agent.agent_type}</p>
                    <div class="text-xs text-gray-500">
                        <p>Balance: $${agent.balance?.toFixed(2) || 0}</p>
                        <p>Messages: ${agent.message_queue_length || 0}</p>
                        <p>Transactions: ${agent.transactions_count || 0}</p>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        // Update transactions table
        function updateTransactions(transactions) {
            if (!transactions) return;

            const tbody = document.getElementById('transactions-table');
            tbody.innerHTML = '';

            transactions.slice(-10).reverse().forEach(transaction => {
                const row = document.createElement('tr');
                row.className = 'border-b hover:bg-gray-50';
                
                const statusClass = transaction.status === 'completed' ? 'text-green-600' : 'text-yellow-600';
                
                row.innerHTML = `
                    <td class="px-4 py-2">${new Date(transaction.timestamp).toLocaleTimeString()}</td>
                    <td class="px-4 py-2">${transaction.buyer_id}</td>
                    <td class="px-4 py-2">${transaction.seller_id}</td>
                    <td class="px-4 py-2">${transaction.item_type}</td>
                    <td class="px-4 py-2">${transaction.quantity}</td>
                    <td class="px-4 py-2">$${transaction.price?.toFixed(2) || 0}</td>
                    <td class="px-4 py-2 ${statusClass}">${transaction.status}</td>
                `;
                tbody.appendChild(row);
            });
        }

        // Update charts
        function updateCharts(data) {
            // Update agent activity chart
            if (data.agents && agentActivityChart) {
                const agentTypes = { sensor: 0, prediction: 0, resource: 0, market: 0 };
                Object.values(data.agents).forEach(agent => {
                    if (agentTypes.hasOwnProperty(agent.agent_type)) {
                        agentTypes[agent.agent_type]++;
                    }
                });

                agentActivityChart.data.datasets[0].data = [
                    agentTypes.sensor, agentTypes.prediction, 
                    agentTypes.resource, agentTypes.market
                ];
                agentActivityChart.update();
            }

            // Update transaction chart (simplified)
            if (data.transactions && transactionChart) {
                const now = new Date();
                const label = now.toLocaleTimeString();
                
                transactionChart.data.labels.push(label);
                transactionChart.data.datasets[0].data.push(data.transactions.length);
                
                // Keep only last 20 points
                if (transactionChart.data.labels.length > 20) {
                    transactionChart.data.labels.shift();
                    transactionChart.data.datasets[0].data.shift();
                }
                
                transactionChart.update();
            }
        }

        // Update alerts
        function updateAlerts(alerts) {
            if (!alerts) return;

            const container = document.getElementById('alerts-container');
            container.innerHTML = '';

            if (alerts.length === 0) {
                container.innerHTML = '<p class="text-gray-500">No active alerts</p>';
                return;
            }

            alerts.forEach(alert => {
                const alertDiv = document.createElement('div');
                alertDiv.className = `p-3 border-l-4 ${getAlertClass(alert.severity)} bg-gray-50`;
                alertDiv.innerHTML = `
                    <div class="flex justify-between">
                        <span class="font-semibold">${alert.title}</span>
                        <span class="text-sm text-gray-500">${new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p class="text-sm mt-1">${alert.message}</p>
                `;
                container.appendChild(alertDiv);
            });
        }

        // Get alert CSS class based on severity
        function getAlertClass(severity) {
            switch (severity) {
                case 'error': return 'border-red-500';
                case 'warning': return 'border-yellow-500';
                case 'info': return 'border-blue-500';
                default: return 'border-gray-500';
            }
        }

        // Initialize dashboard when page loads
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard page"""
    return HTMLResponse(content=DASHBOARD_HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        # Send initial data
        await websocket.send_text(json.dumps(dashboard_data))
        
        # Keep connection alive
        while True:
            await asyncio.sleep(1)  # Wait for updates
            
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)

@app.get("/api/agents")
async def get_agents():
    """Get all agent statuses"""
    agents = {}
    for agent_id, agent in message_bus.agents.items():
        agents[agent_id] = agent.get_status()
    return agents

@app.get("/api/system/stats")
async def get_system_stats():
    """Get system statistics"""
    stats = message_bus.get_agent_stats()
    
    # Add transaction stats
    total_transactions = 0
    for agent in message_bus.agents.values():
        total_transactions += len(agent.transactions)
    
    stats.update({
        "total_transactions": total_transactions,
        "uptime": "N/A",  # Would calculate from start time
        "data_sources_active": 4  # Mock for now
    })
    
    return stats

@app.get("/api/transactions")
async def get_transactions():
    """Get recent transactions"""
    transactions = []
    for agent in message_bus.agents.values():
        for transaction in agent.transactions.values():
            transactions.append({
                "transaction_id": transaction.id,
                "buyer_id": transaction.buyer_id,
                "seller_id": transaction.seller_id,
                "item_type": transaction.item_type,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "timestamp": transaction.timestamp.isoformat(),
                "status": transaction.status
            })
    
    # Sort by timestamp, most recent first
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    return transactions[:20]  # Return last 20 transactions

@app.get("/api/marketplace")
async def get_marketplace():
    """Get marketplace data"""
    return message_bus.get_marketplace_data()

@app.post("/api/alerts")
async def create_alert(title: str, message: str, severity: str = "info"):
    """Create a system alert"""
    alert = {
        "title": title,
        "message": message,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    
    dashboard_data["alerts"].append(alert)
    
    # Keep only last 50 alerts
    if len(dashboard_data["alerts"]) > 50:
        dashboard_data["alerts"] = dashboard_data["alerts"][-50:]
    
    # Broadcast to all connected clients
    await broadcast_update()
    
    return {"status": "success", "alert": alert}

async def update_dashboard_data():
    """Update dashboard data from message bus and agents"""
    # Get agent data
    agents = {}
    total_transactions = 0
    
    for agent_id, agent in message_bus.agents.items():
        agents[agent_id] = agent.get_status()
        total_transactions += len(agent.transactions)
    
    # Get system metrics
    system_stats = message_bus.get_agent_stats()
    system_metrics = {
        "total_agents": system_stats.get("total_agents", 0),
        "online_agents": system_stats.get("online_agents", 0),
        "total_transactions": total_transactions,
        "total_messages": system_stats.get("total_messages_broadcast", 0),
        "uptime": "N/A"  # Would calculate from start time
    }
    
    # Get transactions
    transactions = []
    for agent in message_bus.agents.values():
        for transaction in agent.transactions.values():
            transactions.append({
                "transaction_id": transaction.id,
                "buyer_id": transaction.buyer_id,
                "seller_id": transaction.seller_id,
                "item_type": transaction.item_type,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "timestamp": transaction.timestamp.isoformat(),
                "status": transaction.status
            })
    
    # Update global dashboard data
    dashboard_data.update({
        "agents": agents,
        "system_metrics": system_metrics,
        "transactions": sorted(transactions, key=lambda x: x["timestamp"], reverse=True)[:50],
        "messages": []  # Would collect from message bus
    })

async def broadcast_update():
    """Broadcast dashboard updates to all connected WebSocket clients"""
    if not connected_websockets:
        return
    
    await update_dashboard_data()
    
    # Send to all connected clients
    disconnected = []
    for websocket in connected_websockets:
        try:
            await websocket.send_text(json.dumps(dashboard_data))
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        connected_websockets.remove(ws)

async def dashboard_updater():
    """Background task to update dashboard periodically"""
    while True:
        try:
            await broadcast_update()
            await asyncio.sleep(2)  # Update every 2 seconds
        except Exception as e:
            logger.error(f"Dashboard update error: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    # Start dashboard updater
    asyncio.create_task(dashboard_updater())
    logger.info("🌾 AgriMind Dashboard started!")

if __name__ == "__main__":
    # Ensure dashboard directory exists
    Path("dashboard").mkdir(exist_ok=True)
    
    print("🌾 Starting AgriMind Real-Time Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔗 WebSocket endpoint: ws://localhost:8000/ws")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False
    )
