"""
AgriMind: Collaborative Farm Intelligence Network
Base Agent Framework with Google ADK Integration

This module provides the foundation for all AgriMind agents with:
- Communication capabilities
- Transaction logging and negotiation
- Degraded mode handling for offline operation
- Message passing and state management
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class MessageType(Enum):
    """Types of messages that can be exchanged between agents"""
    DATA_OFFER = "data_offer"
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    NEGOTIATION = "negotiation"
    TRANSACTION = "transaction"
    PREDICTION = "prediction"
    RESOURCE_REQUEST = "resource_request"
    RESOURCE_ALLOCATION = "resource_allocation"
    MARKET_INFO = "market_info"
    HEARTBEAT = "heartbeat"


class AgentType(Enum):
    """Types of agents in the system"""
    SENSOR = "sensor"
    PREDICTION = "prediction"
    RESOURCE = "resource"
    MARKET = "market"


@dataclass
class Message:
    """Standard message format for agent communication"""
    id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    timestamp: datetime
    data: Dict[str, Any]
    ttl: Optional[datetime] = None  # Time to live for the message


@dataclass
class Transaction:
    """Transaction record for agent-to-agent exchanges"""
    id: str
    buyer_id: str
    seller_id: str
    item_type: str
    quantity: float
    price: float
    timestamp: datetime
    status: str  # pending, completed, failed
    metadata: Dict[str, Any]


class BaseAgent:
    """
    Base class for all AgriMind agents
    
    Provides core functionality for:
    - Message handling and communication
    - Transaction processing
    - Degraded mode operation
    - State persistence
    """
    
    def __init__(
        self, 
        agent_id: str, 
        agent_type: AgentType,
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config or {}
        
        # Communication
        self.message_queue: List[Message] = []
        self.subscriptions: Dict[MessageType, List[Callable]] = {}
        
        # Transaction handling
        self.transactions: Dict[str, Transaction] = {}
        self.balance = self.config.get('initial_balance', 1000.0)
        
        # Network and degraded mode
        self.online = True
        self.cached_data = {}
        self.last_online_check = datetime.now()
        
        # State management
        self.state = {}
        self.logger = logging.getLogger(f"Agent-{self.agent_id}")
        
        # Initialize persistence paths
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"{self.agent_type.value} agent {self.agent_id} initialized")

    async def check_connectivity(self) -> bool:
        """
        Check if the agent can connect to external services
        Simulates network connectivity check
        """
        try:
            # In a real implementation, this would ping external APIs
            # For demo purposes, we'll simulate network failures
            import random
            
            # Simulate 95% uptime
            if random.random() < 0.95:
                self.online = True
                self.last_online_check = datetime.now()
                return True
            else:
                self.online = False
                return False
        except Exception as e:
            self.logger.warning(f"Connectivity check failed: {e}")
            self.online = False
            return False

    async def send_message(
        self, 
        receiver_id: str, 
        message_type: MessageType, 
        data: Dict[str, Any],
        ttl_minutes: int = 60
    ) -> str:
        """Send a message to another agent"""
        message_id = str(uuid.uuid4())
        ttl = datetime.now() + timedelta(minutes=ttl_minutes)
        
        message = Message(
            id=message_id,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            timestamp=datetime.now(),
            data=data,
            ttl=ttl
        )
        
        # In degraded mode, store messages locally
        if not self.online:
            await self.store_message_offline(message)
        else:
            await self.deliver_message(message)
        
        self.logger.info(
            f"Sent {message_type.value} message to {receiver_id} "
            f"(online: {self.online})"
        )
        return message_id

    async def deliver_message(self, message: Message):
        """Deliver message to the target agent (simulated)"""
        # In a real system, this would use the Google ADK message broker
        # For this demo, we'll simulate message delivery via a global message bus
        await self.message_bus.deliver(message)

    async def store_message_offline(self, message: Message):
        """Store message for later delivery when back online"""
        offline_file = self.data_dir / f"{self.agent_id}_offline_messages.json"
        
        messages = []
        if offline_file.exists():
            with open(offline_file, 'r') as f:
                messages = json.load(f)
        
        message_dict = asdict(message)
        message_dict['timestamp'] = message.timestamp.isoformat()
        if message.ttl:
            message_dict['ttl'] = message.ttl.isoformat()
        
        messages.append(message_dict)
        
        with open(offline_file, 'w') as f:
            json.dump(messages, f, indent=2)

    async def receive_message(self, message: Message):
        """Process incoming message"""
        # Check if message has expired
        if message.ttl and datetime.now() > message.ttl:
            self.logger.warning(f"Message {message.id} expired, discarding")
            return
        
        self.message_queue.append(message)
        
        # Notify subscribers
        if message.message_type in self.subscriptions:
            for callback in self.subscriptions[message.message_type]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
        
        self.logger.info(
            f"Received {message.message_type.value} message from {message.sender_id}"
        )

    def subscribe(self, message_type: MessageType, callback: Callable):
        """Subscribe to specific message types"""
        if message_type not in self.subscriptions:
            self.subscriptions[message_type] = []
        self.subscriptions[message_type].append(callback)

    async def create_transaction(
        self,
        buyer_id: str,
        seller_id: str,
        item_type: str,
        quantity: float,
        price: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new transaction"""
        transaction_id = str(uuid.uuid4())
        
        transaction = Transaction(
            id=transaction_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_type=item_type,
            quantity=quantity,
            price=price,
            timestamp=datetime.now(),
            status="pending",
            metadata=metadata or {}
        )
        
        self.transactions[transaction_id] = transaction
        
        # Log transaction
        self.logger.info(
            f"Transaction {transaction_id}: {buyer_id} buying {quantity} "
            f"{item_type} from {seller_id} for ${price:.2f}"
        )
        
        return transaction_id

    async def complete_transaction(self, transaction_id: str) -> bool:
        """Complete a transaction"""
        if transaction_id not in self.transactions:
            return False
        
        transaction = self.transactions[transaction_id]
        
        # Process payment (simplified)
        if transaction.buyer_id == self.agent_id:
            self.balance -= transaction.price
        elif transaction.seller_id == self.agent_id:
            self.balance += transaction.price
        
        transaction.status = "completed"
        
        # Save transaction log
        await self.save_transaction_log(transaction)
        
        self.logger.info(f"Transaction {transaction_id} completed")
        return True

    async def save_transaction_log(self, transaction: Transaction):
        """Save transaction to persistent log"""
        log_file = self.logs_dir / f"transactions_{self.agent_id}.json"
        
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        transaction_dict = asdict(transaction)
        transaction_dict['timestamp'] = transaction.timestamp.isoformat()
        
        logs.append(transaction_dict)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    async def get_cached_data(self, key: str, max_age_hours: int = 24) -> Optional[Any]:
        """Retrieve cached data for degraded mode operation"""
        cache_file = self.data_dir / f"{self.agent_id}_cache.pickle"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)
            
            if key not in cache:
                return None
            
            data, timestamp = cache[key]
            
            # Check if data is still fresh
            age = datetime.now() - timestamp
            if age.total_seconds() > max_age_hours * 3600:
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading cached data: {e}")
            return None

    async def cache_data(self, key: str, data: Any):
        """Cache data for offline use"""
        cache_file = self.data_dir / f"{self.agent_id}_cache.pickle"
        
        cache = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cache = pickle.load(f)
            except Exception as e:
                self.logger.error(f"Error loading cache file: {e}")
        
        cache[key] = (data, datetime.now())
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache, f)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")

    async def run_degraded_mode_fallback(self, operation: str) -> Any:
        """
        Execute fallback logic when offline
        This should be overridden by specific agent types
        """
        self.logger.warning(f"Running degraded mode for operation: {operation}")
        
        # Basic fallback logic
        if operation == "irrigation_check":
            return {"recommendation": "check_soil_manually", "confidence": 0.3}
        elif operation == "price_check":
            return {"price": 10.0, "source": "cached_average", "confidence": 0.5}
        
        return None

    async def start(self):
        """Start the agent's main processing loop"""
        self.logger.info(f"Starting {self.agent_type.value} agent {self.agent_id}")
        
        while True:
            try:
                # Check connectivity
                await self.check_connectivity()
                
                # Process message queue
                await self.process_messages()
                
                # Run agent-specific logic
                await self.main_loop()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)

    async def process_messages(self):
        """Process pending messages"""
        processed = []
        
        for message in self.message_queue:
            try:
                await self.handle_message(message)
                processed.append(message)
            except Exception as e:
                self.logger.error(f"Error processing message {message.id}: {e}")
        
        # Remove processed messages
        for msg in processed:
            self.message_queue.remove(msg)

    async def handle_message(self, message: Message):
        """Handle a specific message (to be overridden by subclasses)"""
        self.logger.info(f"Base handler for {message.message_type.value} message")

    async def main_loop(self):
        """Main agent logic loop (to be overridden by subclasses)"""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "online": self.online,
            "balance": self.balance,
            "message_queue_length": len(self.message_queue),
            "transactions_count": len(self.transactions),
            "last_online_check": self.last_online_check.isoformat()
        }


# Global message bus for demo purposes
class MessageBus:
    """Simple message bus for agent communication in demo"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus"""
        self.agents[agent.agent_id] = agent
    
    async def deliver(self, message: Message):
        """Deliver message to target agent"""
        if message.receiver_id in self.agents:
            await self.agents[message.receiver_id].receive_message(message)
        else:
            logging.warning(f"Agent {message.receiver_id} not found for message delivery")


# Global message bus instance
message_bus = MessageBus()

# Add message bus to BaseAgent class
BaseAgent.message_bus = message_bus