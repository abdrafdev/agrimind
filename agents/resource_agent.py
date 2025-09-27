"""
AgriMind: Resource Allocation Agent
Negotiates irrigation schedules, fertilizer distribution, and equipment sharing
between farms using collaborative optimization and bidding systems.

Features:
- Resource availability tracking
- Multi-farm irrigation scheduling
- Equipment sharing coordination
- Fertilizer distribution optimization
- Negotiation and conflict resolution
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .base_agent import BaseAgent, AgentType, MessageType, Message
from data_loaders import load_resources_data, DataSourceInfo


class ResourceType(Enum):
    """Types of resources managed by the agent"""
    WATER = "water"
    FERTILIZER = "fertilizer"
    EQUIPMENT = "equipment"
    LABOR = "labor"


class RequestPriority(Enum):
    """Priority levels for resource requests"""
    CRITICAL = "critical"  # Crop failure risk
    HIGH = "high"         # Yield impact
    NORMAL = "normal"     # Optimization
    LOW = "low"          # Nice to have


@dataclass
class ResourceRequest:
    """Represents a request for resources"""
    request_id: str
    farm_id: str
    resource_type: ResourceType
    quantity: float
    start_time: datetime
    duration_hours: float
    priority: RequestPriority
    max_price: float
    metadata: Dict[str, Any]


@dataclass
class ResourceAllocation:
    """Represents an allocated resource"""
    allocation_id: str
    farm_id: str
    resource_type: ResourceType
    quantity: float
    start_time: datetime
    end_time: datetime
    cost: float
    efficiency_score: float  # 0.0 to 1.0


class ResourceAgent(BaseAgent):
    """
    Resource Allocation Agent that manages and coordinates resource sharing
    between multiple farms for optimal utilization
    """
    
    def __init__(
        self, 
        agent_id: str,
        region: str,
        resources_config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id, AgentType.RESOURCE)
        
        self.region = region
        self.resources_config = resources_config or self._default_resources_config()
        
        # Resource tracking
        self.available_resources: Dict[ResourceType, Dict[str, Any]] = {}
        self.resource_requests: Dict[str, ResourceRequest] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.farm_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Scheduling
        self.irrigation_schedule: Dict[datetime, List[str]] = {}  # time -> farm_ids
        self.equipment_schedule: Dict[str, Dict[datetime, str]] = {}  # equipment -> time -> farm
        
        # Pricing
        self.resource_prices = {
            ResourceType.WATER: 0.05,      # per liter
            ResourceType.FERTILIZER: 2.50,  # per kg
            ResourceType.EQUIPMENT: 15.0,   # per hour
            ResourceType.LABOR: 12.0       # per hour
        }
        
        # Initialize resources from dataset or defaults
        self._initialize_resources()
        
        # Subscribe to messages
        self.subscribe(MessageType.RESOURCE_REQUEST, self._handle_resource_request)
        self.subscribe(MessageType.RESOURCE_ALLOCATION, self._handle_allocation_response)
        self.subscribe(MessageType.NEGOTIATION, self._handle_negotiation)
        self.subscribe(MessageType.PREDICTION, self._handle_prediction_update)
        
        self.logger.info(f"Resource agent initialized for region: {region}")

    def _default_resources_config(self) -> Dict[str, Any]:
        """Default resource configuration"""
        return {
            "water": {
                "total_capacity": 10000,  # liters per day
                "peak_hours": [6, 18],    # 6 AM and 6 PM
                "efficiency_bonus": 0.15,  # 15% bonus for peak hours
                "minimum_pressure": 2.0    # bars
            },
            "fertilizer": {
                "types": ["nitrogen", "phosphorus", "potassium"],
                "inventory": {
                    "nitrogen": 500,      # kg
                    "phosphorus": 300,    # kg
                    "potassium": 400      # kg
                },
                "application_rate": 25,   # kg per hour
            },
            "equipment": {
                "tractors": 2,
                "irrigation_pumps": 4,
                "sprayers": 3,
                "harvesters": 1
            },
            "labor": {
                "available_workers": 8,
                "skill_levels": ["basic", "intermediate", "expert"],
                "hourly_rates": {"basic": 10, "intermediate": 12, "expert": 15}
            }
        }

    def _initialize_resources(self):
        """Initialize available resources from dataset first, then configuration fallback"""
        data_source_used = None
        
        # First try to load resources from official dataset
        try:
            resources_data, source_info = load_resources_data()
            
            if resources_data and source_info.source_type == "dataset":
                # Use dataset resources
                self.logger.info(f"💾 Loading resources from dataset: {source_info.source_name} ({source_info.record_count} farms)")
                
                # Aggregate resources from all farms or use first available
                if len(resources_data) > 0:
                    # Use the first farm's resources or aggregate if multiple farms
                    farm_resources = list(resources_data.values())[0]
                    
                    # Water resources
                    if ResourceType.WATER not in self.available_resources:
                        water_data = farm_resources.get('water', {})
                        self.available_resources[ResourceType.WATER] = {
                            "capacity": water_data.get('total_capacity', 10000),
                            "used": 0,
                            "reservations": {},
                            "efficiency_multiplier": 1.0,
                            "source": "dataset"
                        }
                    
                    # Fertilizer resources
                    if ResourceType.FERTILIZER not in self.available_resources:
                        fertilizer_data = farm_resources.get('fertilizer', {})
                        self.available_resources[ResourceType.FERTILIZER] = {
                            "inventory": fertilizer_data.get('inventory', {
                                "nitrogen": 500,
                                "phosphorus": 300,
                                "potassium": 400
                            }),
                            "reservations": {},
                            "source": "dataset"
                        }
                    
                    # Equipment resources
                    if ResourceType.EQUIPMENT not in self.available_resources:
                        equipment_data = farm_resources.get('equipment', {})
                        equipment_units = equipment_data.get('units', {
                            "tractors": 2,
                            "irrigation_pumps": 4,
                            "sprayers": 3,
                            "harvesters": 1
                        })
                        self.available_resources[ResourceType.EQUIPMENT] = {
                            "units": equipment_units,
                            "availability": {unit: True for unit in equipment_units.keys()},
                            "maintenance_schedule": {},
                            "source": "dataset"
                        }
                    
                    # Labor resources
                    if ResourceType.LABOR not in self.available_resources:
                        labor_data = farm_resources.get('labor', {})
                        self.available_resources[ResourceType.LABOR] = {
                            "workers": labor_data.get('workers', 8),
                            "assigned": 0,
                            "skills": labor_data.get('skills', ['basic', 'intermediate', 'expert']),
                            "rates": labor_data.get('rates', {'basic': 10, 'intermediate': 12, 'expert': 15}),
                            "source": "dataset"
                        }
                    
                    data_source_used = f"dataset ({source_info.source_name})"
                    
        except Exception as e:
            self.logger.warning(f"Could not load resources dataset: {e}")
        
        # Fill in any missing resources from configuration defaults
        for resource_name, config in self.resources_config.items():
            resource_type = ResourceType(resource_name)
            
            if resource_type not in self.available_resources:
                if resource_name == "water":
                    self.available_resources[resource_type] = {
                        "capacity": config["total_capacity"],
                        "used": 0,
                        "reservations": {},
                        "efficiency_multiplier": 1.0,
                        "source": "config"
                    }
                elif resource_name == "fertilizer":
                    self.available_resources[resource_type] = {
                        "inventory": config["inventory"].copy(),
                        "reservations": {},
                        "source": "config"
                    }
                elif resource_name == "equipment":
                    self.available_resources[resource_type] = {
                        "units": config.copy(),
                        "availability": {unit: True for unit in config.keys()},
                        "maintenance_schedule": {},
                        "source": "config"
                    }
                elif resource_name == "labor":
                    self.available_resources[resource_type] = {
                        "workers": config["available_workers"],
                        "assigned": 0,
                        "skills": config["skill_levels"],
                        "rates": config["hourly_rates"],
                        "source": "config"
                    }
        
        # Log data sources used
        sources = []
        for resource_type, resource_data in self.available_resources.items():
            source = resource_data.get('source', 'unknown')
            sources.append(f"{resource_type.value}={source}")
        
        if data_source_used:
            self.logger.info(f"💾 ResourceAgent {self.agent_id} loaded resources from {data_source_used}")
        else:
            self.logger.info(f"💾 ResourceAgent {self.agent_id} using configuration defaults")
        
        self.logger.info(f"💾 Resource sources: {', '.join(sources)}")

    async def _handle_resource_request(self, message: Message):
        """Handle incoming resource requests from farms"""
        request_data = message.data
        requester_id = message.sender_id
        
        try:
            # Parse request
            resource_request = ResourceRequest(
                request_id=request_data["request_id"],
                farm_id=requester_id,
                resource_type=ResourceType(request_data["resource_type"]),
                quantity=request_data["quantity"],
                start_time=datetime.fromisoformat(request_data["start_time"]),
                duration_hours=request_data["duration_hours"],
                priority=RequestPriority(request_data.get("priority", "normal")),
                max_price=request_data["max_price"],
                metadata=request_data.get("metadata", {})
            )
            
            # Store request
            self.resource_requests[resource_request.request_id] = resource_request
            
            # Try to allocate immediately
            allocation = await self._attempt_allocation(resource_request)
            
            if allocation:
                # Successful allocation
                self.allocations[allocation.allocation_id] = allocation
                
                # Create transaction
                transaction_id = await self.create_transaction(
                    buyer_id=requester_id,
                    seller_id=self.agent_id,
                    item_type=f"{allocation.resource_type.value}_allocation",
                    quantity=allocation.quantity,
                    price=allocation.cost
                )
                
                # Send allocation response
                await self.send_message(
                    receiver_id=requester_id,
                    message_type=MessageType.RESOURCE_ALLOCATION,
                    data={
                        "status": "allocated",
                        "allocation_id": allocation.allocation_id,
                        "resource_type": allocation.resource_type.value,
                        "quantity": allocation.quantity,
                        "start_time": allocation.start_time.isoformat(),
                        "end_time": allocation.end_time.isoformat(),
                        "cost": allocation.cost,
                        "efficiency_score": allocation.efficiency_score,
                        "transaction_id": transaction_id
                    }
                )
                
                self.logger.info(
                    f"Allocated {allocation.quantity} {allocation.resource_type.value} "
                    f"to {requester_id} for ${allocation.cost:.2f}"
                )
            else:
                # Cannot allocate - try negotiation
                await self._initiate_negotiation(resource_request)
                
        except Exception as e:
            self.logger.error(f"Error handling resource request: {e}")
            
            # Send error response
            await self.send_message(
                receiver_id=requester_id,
                message_type=MessageType.RESOURCE_ALLOCATION,
                data={
                    "status": "error",
                    "request_id": request_data.get("request_id"),
                    "error": str(e)
                }
            )

    async def _attempt_allocation(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Attempt to allocate resources for a request"""
        try:
            resource_type = request.resource_type
            
            if resource_type == ResourceType.WATER:
                return await self._allocate_water(request)
            elif resource_type == ResourceType.FERTILIZER:
                return await self._allocate_fertilizer(request)
            elif resource_type == ResourceType.EQUIPMENT:
                return await self._allocate_equipment(request)
            elif resource_type == ResourceType.LABOR:
                return await self._allocate_labor(request)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in allocation attempt: {e}")
            return None

    async def _allocate_water(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate water resources with irrigation scheduling"""
        water_config = self.resources_config["water"]
        available = self.available_resources[ResourceType.WATER]
        
        # Check if we have enough water capacity
        requested_per_hour = request.quantity / request.duration_hours
        daily_capacity = water_config["total_capacity"]
        
        if requested_per_hour * request.duration_hours > available["capacity"] - available["used"]:
            return None
        
        # Find optimal time slot
        start_time = request.start_time
        end_time = start_time + timedelta(hours=request.duration_hours)
        
        # Check for conflicts in irrigation schedule
        time_slots = []
        current = start_time
        while current < end_time:
            if current in self.irrigation_schedule:
                # Check if adding this farm would exceed capacity
                current_farms = len(self.irrigation_schedule[current])
                if current_farms >= 4:  # Max 4 farms can irrigate simultaneously
                    return None
            time_slots.append(current)
            current += timedelta(hours=1)
        
        # Calculate efficiency score based on timing
        efficiency_score = 1.0
        peak_hours = water_config["peak_hours"]
        
        for hour in range(start_time.hour, end_time.hour):
            if hour in peak_hours:
                efficiency_score += water_config["efficiency_bonus"]
        
        efficiency_score = min(1.0, efficiency_score / request.duration_hours)
        
        # Calculate cost
        base_cost = request.quantity * self.resource_prices[ResourceType.WATER]
        priority_multiplier = self._get_priority_multiplier(request.priority)
        total_cost = base_cost * priority_multiplier
        
        if total_cost > request.max_price:
            return None
        
        # Create allocation
        allocation_id = f"water_{request.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            farm_id=request.farm_id,
            resource_type=ResourceType.WATER,
            quantity=request.quantity,
            start_time=start_time,
            end_time=end_time,
            cost=total_cost,
            efficiency_score=efficiency_score
        )
        
        # Update irrigation schedule
        for time_slot in time_slots:
            if time_slot not in self.irrigation_schedule:
                self.irrigation_schedule[time_slot] = []
            self.irrigation_schedule[time_slot].append(request.farm_id)
        
        # Update available resources
        available["used"] += request.quantity
        
        return allocation

    async def _allocate_fertilizer(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate fertilizer resources"""
        fertilizer_config = self.resources_config["fertilizer"]
        available = self.available_resources[ResourceType.FERTILIZER]
        
        # Determine fertilizer type from metadata
        fertilizer_type = request.metadata.get("fertilizer_type", "nitrogen")
        
        if fertilizer_type not in available["inventory"]:
            return None
        
        if available["inventory"][fertilizer_type] < request.quantity:
            return None
        
        # Calculate delivery time based on application rate
        application_rate = fertilizer_config["application_rate"]
        duration = max(1, request.quantity / application_rate)
        
        start_time = request.start_time
        end_time = start_time + timedelta(hours=duration)
        
        # Calculate cost
        base_cost = request.quantity * self.resource_prices[ResourceType.FERTILIZER]
        
        # Apply distance factor if specified
        distance_km = request.metadata.get("distance_km", 5)
        transport_cost = distance_km * 0.5  # $0.5 per km
        total_cost = base_cost + transport_cost
        
        if total_cost > request.max_price:
            return None
        
        # Create allocation
        allocation_id = f"fertilizer_{request.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            farm_id=request.farm_id,
            resource_type=ResourceType.FERTILIZER,
            quantity=request.quantity,
            start_time=start_time,
            end_time=end_time,
            cost=total_cost,
            efficiency_score=0.9  # High efficiency for fertilizer
        )
        
        # Reserve fertilizer
        available["inventory"][fertilizer_type] -= request.quantity
        if allocation_id not in available["reservations"]:
            available["reservations"][allocation_id] = {}
        available["reservations"][allocation_id] = {
            "type": fertilizer_type,
            "quantity": request.quantity
        }
        
        return allocation

    async def _allocate_equipment(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate equipment resources"""
        equipment_config = self.resources_config["equipment"]
        available = self.available_resources[ResourceType.EQUIPMENT]
        
        # Determine equipment type from metadata
        equipment_type = request.metadata.get("equipment_type", "tractor")
        
        if equipment_type not in available["units"]:
            return None
        
        if available["units"][equipment_type] <= 0:
            return None
        
        # Check equipment schedule
        start_time = request.start_time
        end_time = start_time + timedelta(hours=request.duration_hours)
        
        if equipment_type not in self.equipment_schedule:
            self.equipment_schedule[equipment_type] = {}
        
        # Find available unit
        available_unit = None
        for unit_id in range(available["units"][equipment_type]):
            unit_name = f"{equipment_type}_{unit_id}"
            
            # Check if unit is available during requested time
            conflict = False
            current = start_time
            while current < end_time:
                if current in self.equipment_schedule[equipment_type] and \
                   self.equipment_schedule[equipment_type][current] == unit_name:
                    conflict = True
                    break
                current += timedelta(hours=1)
            
            if not conflict:
                available_unit = unit_name
                break
        
        if not available_unit:
            return None
        
        # Calculate cost
        base_cost = request.duration_hours * self.resource_prices[ResourceType.EQUIPMENT]
        
        # Apply equipment type multiplier
        equipment_multipliers = {
            "tractor": 1.0,
            "harvester": 2.0,
            "sprayer": 1.2,
            "irrigation_pump": 0.8
        }
        multiplier = equipment_multipliers.get(equipment_type, 1.0)
        total_cost = base_cost * multiplier
        
        if total_cost > request.max_price:
            return None
        
        # Create allocation
        allocation_id = f"equipment_{request.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            farm_id=request.farm_id,
            resource_type=ResourceType.EQUIPMENT,
            quantity=1,  # Equipment is binary
            start_time=start_time,
            end_time=end_time,
            cost=total_cost,
            efficiency_score=0.85
        )
        
        # Reserve equipment
        current = start_time
        while current < end_time:
            self.equipment_schedule[equipment_type][current] = available_unit
            current += timedelta(hours=1)
        
        return allocation

    async def _allocate_labor(self, request: ResourceRequest) -> Optional[ResourceAllocation]:
        """Allocate labor resources"""
        labor_config = self.resources_config["labor"]
        available = self.available_resources[ResourceType.LABOR]
        
        # Check if we have enough workers
        required_workers = int(request.quantity)
        if available["workers"] - available["assigned"] < required_workers:
            return None
        
        # Determine skill level needed
        skill_level = request.metadata.get("skill_level", "basic")
        if skill_level not in available["skills"]:
            skill_level = "basic"
        
        # Calculate cost
        hourly_rate = available["rates"][skill_level]
        total_cost = required_workers * request.duration_hours * hourly_rate
        
        if total_cost > request.max_price:
            return None
        
        start_time = request.start_time
        end_time = start_time + timedelta(hours=request.duration_hours)
        
        # Create allocation
        allocation_id = f"labor_{request.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            farm_id=request.farm_id,
            resource_type=ResourceType.LABOR,
            quantity=required_workers,
            start_time=start_time,
            end_time=end_time,
            cost=total_cost,
            efficiency_score=0.8  # Human efficiency varies
        )
        
        # Assign workers
        available["assigned"] += required_workers
        
        return allocation

    def _get_priority_multiplier(self, priority: RequestPriority) -> float:
        """Get cost multiplier based on request priority"""
        multipliers = {
            RequestPriority.CRITICAL: 0.8,  # Discount for critical needs
            RequestPriority.HIGH: 0.9,
            RequestPriority.NORMAL: 1.0,
            RequestPriority.LOW: 1.2       # Premium for low priority
        }
        return multipliers.get(priority, 1.0)

    async def _initiate_negotiation(self, request: ResourceRequest):
        """Initiate negotiation when direct allocation fails"""
        # Find alternative options
        alternatives = await self._find_alternatives(request)
        
        negotiation_data = {
            "request_id": request.request_id,
            "original_request": {
                "resource_type": request.resource_type.value,
                "quantity": request.quantity,
                "start_time": request.start_time.isoformat(),
                "duration_hours": request.duration_hours,
                "max_price": request.max_price
            },
            "alternatives": alternatives,
            "reason": "resource_unavailable"
        }
        
        await self.send_message(
            receiver_id=request.farm_id,
            message_type=MessageType.NEGOTIATION,
            data=negotiation_data
        )

    async def _find_alternatives(self, request: ResourceRequest) -> List[Dict[str, Any]]:
        """Find alternative allocation options"""
        alternatives = []
        
        # Try different time slots
        for hour_offset in [1, 2, 4, 8, 12, 24]:
            alt_start = request.start_time + timedelta(hours=hour_offset)
            alt_request = ResourceRequest(
                request_id=f"{request.request_id}_alt_{hour_offset}",
                farm_id=request.farm_id,
                resource_type=request.resource_type,
                quantity=request.quantity,
                start_time=alt_start,
                duration_hours=request.duration_hours,
                priority=request.priority,
                max_price=request.max_price,
                metadata=request.metadata
            )
            
            allocation = await self._attempt_allocation(alt_request)
            if allocation:
                alternatives.append({
                    "type": "time_shift",
                    "start_time": alt_start.isoformat(),
                    "cost": allocation.cost,
                    "efficiency_score": allocation.efficiency_score
                })
        
        # Try reduced quantity
        if request.resource_type in [ResourceType.WATER, ResourceType.FERTILIZER]:
            for reduction in [0.8, 0.6, 0.4]:
                alt_quantity = request.quantity * reduction
                alt_request = ResourceRequest(
                    request_id=f"{request.request_id}_reduced_{int(reduction*100)}",
                    farm_id=request.farm_id,
                    resource_type=request.resource_type,
                    quantity=alt_quantity,
                    start_time=request.start_time,
                    duration_hours=request.duration_hours,
                    priority=request.priority,
                    max_price=request.max_price,
                    metadata=request.metadata
                )
                
                allocation = await self._attempt_allocation(alt_request)
                if allocation:
                    alternatives.append({
                        "type": "reduced_quantity",
                        "quantity": alt_quantity,
                        "cost": allocation.cost,
                        "efficiency_score": allocation.efficiency_score
                    })
        
        return alternatives

    async def _handle_negotiation(self, message: Message):
        """Handle negotiation responses"""
        negotiation_data = message.data
        requester_id = message.sender_id
        
        if negotiation_data.get("action") == "accept_alternative":
            alt_option = negotiation_data["selected_alternative"]
            original_request_id = negotiation_data["request_id"]
            
            if original_request_id in self.resource_requests:
                original_request = self.resource_requests[original_request_id]
                
                # Create new request based on accepted alternative
                if alt_option["type"] == "time_shift":
                    new_start = datetime.fromisoformat(alt_option["start_time"])
                    modified_request = ResourceRequest(
                        request_id=f"{original_request_id}_accepted",
                        farm_id=original_request.farm_id,
                        resource_type=original_request.resource_type,
                        quantity=original_request.quantity,
                        start_time=new_start,
                        duration_hours=original_request.duration_hours,
                        priority=original_request.priority,
                        max_price=original_request.max_price,
                        metadata=original_request.metadata
                    )
                elif alt_option["type"] == "reduced_quantity":
                    modified_request = ResourceRequest(
                        request_id=f"{original_request_id}_accepted",
                        farm_id=original_request.farm_id,
                        resource_type=original_request.resource_type,
                        quantity=alt_option["quantity"],
                        start_time=original_request.start_time,
                        duration_hours=original_request.duration_hours,
                        priority=original_request.priority,
                        max_price=original_request.max_price,
                        metadata=original_request.metadata
                    )
                
                # Try allocation again
                allocation = await self._attempt_allocation(modified_request)
                if allocation:
                    self.allocations[allocation.allocation_id] = allocation
                    
                    # Send success response
                    await self.send_message(
                        receiver_id=requester_id,
                        message_type=MessageType.RESOURCE_ALLOCATION,
                        data={
                            "status": "allocated",
                            "allocation_id": allocation.allocation_id,
                            "negotiated": True
                        }
                    )

    async def _handle_allocation_response(self, message: Message):
        """Handle responses to allocation offers"""
        response_data = message.data
        allocation_id = response_data.get("allocation_id")
        
        if allocation_id in self.allocations:
            allocation = self.allocations[allocation_id]
            
            if response_data.get("status") == "accepted":
                # Confirm allocation
                await self.complete_transaction(response_data.get("transaction_id"))
                self.logger.info(f"Allocation {allocation_id} confirmed")
            elif response_data.get("status") == "rejected":
                # Release resources
                await self._release_allocation(allocation)
                del self.allocations[allocation_id]
                self.logger.info(f"Allocation {allocation_id} rejected and released")

    async def _handle_prediction_update(self, message: Message):
        """Handle prediction updates that might affect resource planning"""
        prediction_data = message.data
        
        if prediction_data.get("status") == "success":
            prediction = prediction_data["prediction"]
            pred_type = prediction["prediction_type"]
            
            # Adjust resource allocation based on predictions
            if pred_type == "irrigation_need":
                irrigation_need = prediction["value"]
                confidence = prediction["confidence"]
                
                if irrigation_need > 0.8 and confidence > 0.7:
                    # High irrigation need predicted - reserve more water
                    water_available = self.available_resources[ResourceType.WATER]
                    water_available["capacity"] *= 1.2  # Increase capacity temporarily
                    
                    self.logger.info("Increased water capacity due to high irrigation prediction")

    async def _release_allocation(self, allocation: ResourceAllocation):
        """Release resources from a cancelled allocation"""
        if allocation.resource_type == ResourceType.WATER:
            available = self.available_resources[ResourceType.WATER]
            available["used"] -= allocation.quantity
            
            # Remove from irrigation schedule
            current = allocation.start_time
            while current < allocation.end_time:
                if current in self.irrigation_schedule:
                    if allocation.farm_id in self.irrigation_schedule[current]:
                        self.irrigation_schedule[current].remove(allocation.farm_id)
                current += timedelta(hours=1)
                        
        elif allocation.resource_type == ResourceType.FERTILIZER:
            available = self.available_resources[ResourceType.FERTILIZER]
            if allocation.allocation_id in available["reservations"]:
                reservation = available["reservations"][allocation.allocation_id]
                fertilizer_type = reservation["type"]
                available["inventory"][fertilizer_type] += reservation["quantity"]
                del available["reservations"][allocation.allocation_id]
                
        elif allocation.resource_type == ResourceType.EQUIPMENT:
            # Clear equipment schedule
            equipment_type = allocation.metadata.get("equipment_type", "tractor")
            if equipment_type in self.equipment_schedule:
                current = allocation.start_time
                while current < allocation.end_time:
                    if current in self.equipment_schedule[equipment_type]:
                        del self.equipment_schedule[equipment_type][current]
                    current += timedelta(hours=1)
                    
        elif allocation.resource_type == ResourceType.LABOR:
            available = self.available_resources[ResourceType.LABOR]
            available["assigned"] -= allocation.quantity

    async def optimize_allocations(self):
        """Optimize current allocations for better efficiency"""
        # Simple optimization: look for opportunities to consolidate
        water_allocations = [a for a in self.allocations.values() 
                           if a.resource_type == ResourceType.WATER]
        
        # Group by time slots
        time_groups = {}
        for allocation in water_allocations:
            time_key = allocation.start_time.hour
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(allocation)
        
        # Look for optimization opportunities
        for time_key, allocations in time_groups.items():
            if len(allocations) > 1:
                # Calculate total efficiency gain from consolidation
                total_quantity = sum(a.quantity for a in allocations)
                avg_efficiency = sum(a.efficiency_score for a in allocations) / len(allocations)
                
                # If consolidation would improve efficiency, suggest it
                if avg_efficiency < 0.8:
                    self.logger.info(f"Optimization opportunity at {time_key}:00 - consolidate {len(allocations)} allocations")

    async def main_loop(self):
        """Main resource agent logic"""
        # Optimize allocations every hour
        if not hasattr(self, '_last_optimization') or \
           (datetime.now() - self._last_optimization).seconds > 3600:
            
            await self.optimize_allocations()
            self._last_optimization = datetime.now()
        
        # Clean up expired allocations
        await self._cleanup_expired_allocations()

    async def _cleanup_expired_allocations(self):
        """Clean up expired allocations"""
        now = datetime.now()
        expired_allocations = [
            allocation_id for allocation_id, allocation in self.allocations.items()
            if allocation.end_time < now
        ]
        
        for allocation_id in expired_allocations:
            allocation = self.allocations[allocation_id]
            await self._release_allocation(allocation)
            del self.allocations[allocation_id]
            
        if expired_allocations:
            self.logger.info(f"Cleaned up {len(expired_allocations)} expired allocations")

    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        status = self.get_status()
        
        # Resource availability summary
        resource_summary = {}
        for resource_type, data in self.available_resources.items():
            if resource_type == ResourceType.WATER:
                resource_summary["water"] = {
                    "capacity": data["capacity"],
                    "used": data["used"],
                    "available": data["capacity"] - data["used"],
                    "utilization": data["used"] / data["capacity"] if data["capacity"] > 0 else 0
                }
            elif resource_type == ResourceType.FERTILIZER:
                resource_summary["fertilizer"] = {
                    "inventory": data["inventory"],
                    "total_reserved": len(data["reservations"])
                }
            elif resource_type == ResourceType.EQUIPMENT:
                resource_summary["equipment"] = {
                    "units": data["units"],
                    "available_count": sum(1 for avail in data["availability"].values() if avail)
                }
            elif resource_type == ResourceType.LABOR:
                resource_summary["labor"] = {
                    "total_workers": data["workers"],
                    "assigned": data["assigned"],
                    "available": data["workers"] - data["assigned"]
                }
        
        # Current allocations
        allocation_summary = {}
        for allocation_id, allocation in self.allocations.items():
            resource_key = allocation.resource_type.value
            if resource_key not in allocation_summary:
                allocation_summary[resource_key] = []
            
            allocation_summary[resource_key].append({
                "farm_id": allocation.farm_id,
                "quantity": allocation.quantity,
                "start_time": allocation.start_time.isoformat(),
                "end_time": allocation.end_time.isoformat(),
                "cost": allocation.cost,
                "efficiency_score": allocation.efficiency_score
            })
        
        status.update({
            "region": self.region,
            "resource_availability": resource_summary,
            "current_allocations": allocation_summary,
            "resource_prices": {rt.value: price for rt, price in self.resource_prices.items()}
        })
        
        return status


# Helper function to create resource agent
def create_resource_agent(
    agent_id: str,
    region: str
) -> ResourceAgent:
    """Factory function to create a resource agent"""
    return ResourceAgent(agent_id, region)