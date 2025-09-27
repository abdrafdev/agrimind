"""
AgriMind: Advanced Negotiation Engine
Sophisticated agent negotiation with bidding, counter-offers, and conflict resolution
"""

import asyncio
import json
import math
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger("AgriMind-Negotiation")

class NegotiationStrategy(Enum):
    """Negotiation strategies for agents"""
    COMPETITIVE = "competitive"      # High starting price, slow concessions
    COOPERATIVE = "cooperative"      # Fair starting price, quick agreement
    ADAPTIVE = "adaptive"           # Adjusts based on market conditions
    COLLABORATIVE = "collaborative" # Seeks win-win solutions

class NegotiationStatus(Enum):
    """Status of negotiation sessions"""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    AGREED = "agreed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONFLICT = "conflict"

@dataclass
class Offer:
    """Represents a negotiation offer"""
    id: str
    negotiation_id: str
    sender_id: str
    receiver_id: str
    item_type: str
    quantity: float
    price_per_unit: float
    total_price: float
    conditions: Dict[str, Any]
    timestamp: datetime
    expires_at: datetime
    counter_to: Optional[str] = None  # ID of offer this is countering

@dataclass
class NegotiationSession:
    """Represents a complete negotiation session"""
    id: str
    initiator_id: str
    responder_id: str
    item_type: str
    initial_quantity: float
    status: NegotiationStatus
    offers: List[Offer]
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    final_agreement: Optional[Dict[str, Any]] = None
    conflict_reason: Optional[str] = None

class AdvancedNegotiationEngine:
    """
    Advanced negotiation engine with intelligent bidding and conflict resolution
    """
    
    def __init__(self):
        self.active_negotiations: Dict[str, NegotiationSession] = {}
        self.negotiation_history: List[NegotiationSession] = []
        self.market_intelligence: Dict[str, Dict[str, float]] = {}
        self.agent_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Configure market intelligence with realistic pricing
        self._initialize_market_intelligence()
    
    def _initialize_market_intelligence(self):
        """Initialize market intelligence with historical pricing data"""
        self.market_intelligence = {
            "water_allocation": {
                "base_price": 0.05,  # $/liter
                "seasonal_multiplier": 1.2,
                "scarcity_multiplier": 1.5,
                "quality_premium": 0.02
            },
            "equipment_rental": {
                "base_price": 25.0,  # $/hour
                "demand_multiplier": 1.3,
                "urgency_premium": 15.0,
                "maintenance_discount": 0.1
            },
            "fertilizer_sharing": {
                "base_price": 2.50,  # $/kg
                "organic_premium": 1.8,
                "bulk_discount": 0.15,
                "proximity_discount": 0.1
            },
            "labor_sharing": {
                "base_price": 18.0,  # $/hour
                "skill_premium": 1.4,
                "seasonal_surge": 1.6,
                "experience_bonus": 0.25
            }
        }
    
    def register_agent(self, agent_id: str, agent_type: str, strategy: NegotiationStrategy, 
                      characteristics: Dict[str, Any]):
        """Register an agent with the negotiation engine"""
        self.agent_profiles[agent_id] = {
            "type": agent_type,
            "strategy": strategy,
            "characteristics": characteristics,
            "success_rate": 0.7,  # Default success rate
            "avg_negotiation_time": 300,  # seconds
            "preferred_margin": characteristics.get("preferred_margin", 0.15),
            "risk_tolerance": characteristics.get("risk_tolerance", 0.5),
            "cooperation_level": characteristics.get("cooperation_level", 0.6)
        }
    
    async def initiate_negotiation(
        self, 
        initiator_id: str, 
        responder_id: str, 
        item_type: str, 
        quantity: float,
        initial_price: Optional[float] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Initiate a new negotiation session"""
        
        negotiation_id = str(uuid.uuid4())
        
        # Calculate intelligent initial price if not provided
        if initial_price is None:
            initial_price = self._calculate_intelligent_price(
                initiator_id, item_type, quantity, "initial"
            )
        
        # Create initial offer
        offer_id = str(uuid.uuid4())
        initial_offer = Offer(
            id=offer_id,
            negotiation_id=negotiation_id,
            sender_id=initiator_id,
            receiver_id=responder_id,
            item_type=item_type,
            quantity=quantity,
            price_per_unit=initial_price / quantity,
            total_price=initial_price,
            conditions=conditions or {},
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=30)
        )
        
        # Create negotiation session
        session = NegotiationSession(
            id=negotiation_id,
            initiator_id=initiator_id,
            responder_id=responder_id,
            item_type=item_type,
            initial_quantity=quantity,
            status=NegotiationStatus.INITIATED,
            offers=[initial_offer],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=2)
        )
        
        self.active_negotiations[negotiation_id] = session
        
        logger.info(
            f"🤝 Negotiation initiated: {initiator_id} -> {responder_id} "
            f"for {quantity} {item_type} at ${initial_price:.2f}"
        )
        
        return negotiation_id
    
    async def make_counter_offer(
        self, 
        negotiation_id: str, 
        agent_id: str, 
        counter_price: Optional[float] = None,
        counter_quantity: Optional[float] = None,
        additional_conditions: Optional[Dict[str, Any]] = None
    ) -> Offer:
        """Make a counter-offer in an existing negotiation"""
        
        if negotiation_id not in self.active_negotiations:
            raise ValueError(f"Negotiation {negotiation_id} not found")
        
        session = self.active_negotiations[negotiation_id]
        last_offer = session.offers[-1]
        
        # Determine counter-offer strategy
        if counter_price is None:
            counter_price = self._calculate_counter_offer_price(
                agent_id, session, last_offer
            )
        
        if counter_quantity is None:
            counter_quantity = last_offer.quantity
        
        # Create counter-offer
        offer_id = str(uuid.uuid4())
        counter_offer = Offer(
            id=offer_id,
            negotiation_id=negotiation_id,
            sender_id=agent_id,
            receiver_id=last_offer.sender_id,
            item_type=last_offer.item_type,
            quantity=counter_quantity,
            price_per_unit=counter_price / counter_quantity,
            total_price=counter_price,
            conditions={**last_offer.conditions, **(additional_conditions or {})},
            timestamp=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=20),
            counter_to=last_offer.id
        )
        
        # Update session
        session.offers.append(counter_offer)
        session.updated_at = datetime.now()
        session.status = NegotiationStatus.IN_PROGRESS
        
        logger.info(
            f"💬 Counter-offer: {agent_id} counters with ${counter_price:.2f} "
            f"(was ${last_offer.total_price:.2f})"
        )
        
        # Check if we should auto-accept
        if await self._should_auto_accept(session, counter_offer):
            await self._finalize_agreement(session, counter_offer)
        
        return counter_offer
    
    async def accept_offer(self, negotiation_id: str, agent_id: str, offer_id: str) -> bool:
        """Accept a specific offer"""
        
        if negotiation_id not in self.active_negotiations:
            return False
        
        session = self.active_negotiations[negotiation_id]
        
        # Find the offer
        offer = None
        for o in session.offers:
            if o.id == offer_id:
                offer = o
                break
        
        if not offer or offer.receiver_id != agent_id:
            return False
        
        # Finalize agreement
        await self._finalize_agreement(session, offer)
        return True
    
    async def reject_offer(self, negotiation_id: str, agent_id: str, 
                          reason: Optional[str] = None) -> bool:
        """Reject the current offer"""
        
        if negotiation_id not in self.active_negotiations:
            return False
        
        session = self.active_negotiations[negotiation_id]
        session.status = NegotiationStatus.REJECTED
        session.updated_at = datetime.now()
        session.conflict_reason = reason or "Offer rejected"
        
        # Move to history
        self.negotiation_history.append(session)
        del self.active_negotiations[negotiation_id]
        
        logger.info(f"❌ Negotiation {negotiation_id} rejected by {agent_id}")
        return True
    
    def _calculate_intelligent_price(
        self, 
        agent_id: str, 
        item_type: str, 
        quantity: float, 
        role: str
    ) -> float:
        """Calculate intelligent pricing based on market intelligence and agent profile"""
        
        if item_type not in self.market_intelligence:
            # Fallback for unknown items
            return quantity * 10.0
        
        market_data = self.market_intelligence[item_type]
        base_price = market_data["base_price"] * quantity
        
        # Apply market modifiers
        if "seasonal_multiplier" in market_data:
            base_price *= market_data["seasonal_multiplier"]
        
        # Apply agent-specific adjustments
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            strategy = profile["strategy"]
            
            if strategy == NegotiationStrategy.COMPETITIVE:
                if role == "initial":
                    base_price *= 1.3  # Start high
                else:
                    base_price *= 1.1  # Counter higher
            elif strategy == NegotiationStrategy.COOPERATIVE:
                base_price *= 1.05  # Fair pricing
            elif strategy == NegotiationStrategy.ADAPTIVE:
                # Adjust based on market conditions
                success_rate = profile.get("success_rate", 0.7)
                base_price *= (1.0 + (0.5 - success_rate) * 0.4)
        
        # Add some randomness for realism
        base_price *= (0.95 + random.random() * 0.1)
        
        return round(base_price, 2)
    
    def _calculate_counter_offer_price(
        self, 
        agent_id: str, 
        session: NegotiationSession, 
        last_offer: Offer
    ) -> float:
        """Calculate intelligent counter-offer price"""
        
        original_price = session.offers[0].total_price
        current_price = last_offer.total_price
        
        # Determine negotiation direction
        if len(session.offers) == 1:
            # First counter-offer
            if agent_id in self.agent_profiles:
                profile = self.agent_profiles[agent_id]
                strategy = profile["strategy"]
                
                if strategy == NegotiationStrategy.COMPETITIVE:
                    # Counter with significant reduction
                    counter_price = current_price * 0.7
                elif strategy == NegotiationStrategy.COOPERATIVE:
                    # Counter with moderate reduction
                    counter_price = current_price * 0.85
                elif strategy == NegotiationStrategy.COLLABORATIVE:
                    # Seek middle ground
                    fair_price = self._calculate_fair_market_price(
                        session.item_type, session.initial_quantity
                    )
                    counter_price = (current_price + fair_price) / 2
                else:
                    counter_price = current_price * 0.8
            else:
                counter_price = current_price * 0.8
        else:
            # Subsequent counter-offers - converge gradually
            price_history = [offer.total_price for offer in session.offers]
            
            # Calculate convergence rate based on negotiation progress
            negotiation_age = (datetime.now() - session.created_at).total_seconds()
            max_age = (session.expires_at - session.created_at).total_seconds()
            progress = min(negotiation_age / max_age, 1.0)
            
            # Accelerate convergence as deadline approaches
            convergence_rate = 0.1 + (progress * 0.4)
            
            if len(price_history) >= 2:
                price_diff = abs(price_history[-1] - price_history[-2])
                counter_price = current_price + (price_diff * convergence_rate * 
                                               (1 if current_price < original_price else -1))
            else:
                counter_price = current_price * (1 - convergence_rate)
        
        # Ensure counter-offer is reasonable
        fair_price = self._calculate_fair_market_price(
            session.item_type, session.initial_quantity
        )
        
        # Don't go too far from fair market price
        min_price = fair_price * 0.7
        max_price = fair_price * 1.5
        counter_price = max(min_price, min(max_price, counter_price))
        
        return round(counter_price, 2)
    
    def _calculate_fair_market_price(self, item_type: str, quantity: float) -> float:
        """Calculate fair market price for an item"""
        
        if item_type not in self.market_intelligence:
            return quantity * 10.0
        
        market_data = self.market_intelligence[item_type]
        return market_data["base_price"] * quantity
    
    async def _should_auto_accept(
        self, 
        session: NegotiationSession, 
        offer: Offer
    ) -> bool:
        """Determine if an offer should be automatically accepted"""
        
        # Don't auto-accept the first offer
        if len(session.offers) <= 1:
            return False
        
        fair_price = self._calculate_fair_market_price(offer.item_type, offer.quantity)
        
        # Auto-accept if offer is very close to fair market price
        price_diff_ratio = abs(offer.total_price - fair_price) / fair_price
        
        if price_diff_ratio < 0.05:  # Within 5% of fair price
            return True
        
        # Auto-accept if negotiation is close to expiring and offer is reasonable
        time_remaining = (session.expires_at - datetime.now()).total_seconds()
        if time_remaining < 300:  # Less than 5 minutes remaining
            if price_diff_ratio < 0.15:  # Within 15% of fair price
                return True
        
        # Auto-accept if we've had many rounds and prices are converging
        if len(session.offers) >= 6:
            recent_offers = session.offers[-3:]
            price_variance = max(o.total_price for o in recent_offers) - \
                           min(o.total_price for o in recent_offers)
            
            if price_variance / fair_price < 0.1:  # Prices converging
                return True
        
        return False
    
    async def _finalize_agreement(self, session: NegotiationSession, accepted_offer: Offer):
        """Finalize a negotiation agreement"""
        
        session.status = NegotiationStatus.AGREED
        session.updated_at = datetime.now()
        session.final_agreement = {
            "accepted_offer_id": accepted_offer.id,
            "final_price": accepted_offer.total_price,
            "final_quantity": accepted_offer.quantity,
            "conditions": accepted_offer.conditions,
            "agreement_timestamp": datetime.now().isoformat()
        }
        
        # Update agent success rates
        self._update_agent_success_rates(session)
        
        # Move to history
        self.negotiation_history.append(session)
        del self.active_negotiations[session.id]
        
        logger.info(
            f"✅ Agreement reached: {session.initiator_id} <-> {session.responder_id} "
            f"for {accepted_offer.quantity} {accepted_offer.item_type} "
            f"at ${accepted_offer.total_price:.2f}"
        )
    
    def _update_agent_success_rates(self, session: NegotiationSession):
        """Update agent success rates based on negotiation outcome"""
        
        for agent_id in [session.initiator_id, session.responder_id]:
            if agent_id in self.agent_profiles:
                profile = self.agent_profiles[agent_id]
                current_rate = profile.get("success_rate", 0.7)
                
                # Slowly adjust success rate based on outcome
                if session.status == NegotiationStatus.AGREED:
                    profile["success_rate"] = min(0.95, current_rate + 0.02)
                else:
                    profile["success_rate"] = max(0.2, current_rate - 0.01)
    
    async def cleanup_expired_negotiations(self):
        """Clean up expired negotiations"""
        
        current_time = datetime.now()
        expired_ids = []
        
        for negotiation_id, session in self.active_negotiations.items():
            if current_time > session.expires_at:
                session.status = NegotiationStatus.EXPIRED
                session.updated_at = current_time
                self.negotiation_history.append(session)
                expired_ids.append(negotiation_id)
        
        for expired_id in expired_ids:
            del self.active_negotiations[expired_id]
            logger.info(f"⏰ Negotiation {expired_id} expired")
    
    def get_negotiation_analytics(self) -> Dict[str, Any]:
        """Get analytics about negotiation performance"""
        
        total_negotiations = len(self.negotiation_history) + len(self.active_negotiations)
        successful_negotiations = len([
            s for s in self.negotiation_history 
            if s.status == NegotiationStatus.AGREED
        ])
        
        # Calculate average negotiation time for completed negotiations
        completed_negotiations = [
            s for s in self.negotiation_history 
            if s.status in [NegotiationStatus.AGREED, NegotiationStatus.REJECTED]
        ]
        
        avg_negotiation_time = 0
        if completed_negotiations:
            total_time = sum([
                (s.updated_at - s.created_at).total_seconds()
                for s in completed_negotiations
            ])
            avg_negotiation_time = total_time / len(completed_negotiations)
        
        # Item type success rates
        item_success_rates = {}
        for session in self.negotiation_history:
            item_type = session.item_type
            if item_type not in item_success_rates:
                item_success_rates[item_type] = {"total": 0, "successful": 0}
            
            item_success_rates[item_type]["total"] += 1
            if session.status == NegotiationStatus.AGREED:
                item_success_rates[item_type]["successful"] += 1
        
        # Calculate success rates
        for item_type, data in item_success_rates.items():
            data["success_rate"] = data["successful"] / data["total"] if data["total"] > 0 else 0
        
        return {
            "total_negotiations": total_negotiations,
            "active_negotiations": len(self.active_negotiations),
            "success_rate": successful_negotiations / total_negotiations if total_negotiations > 0 else 0,
            "average_negotiation_time_seconds": avg_negotiation_time,
            "item_type_success_rates": item_success_rates,
            "agent_profiles": len(self.agent_profiles)
        }
    
    def get_active_negotiations_summary(self) -> List[Dict[str, Any]]:
        """Get summary of active negotiations"""
        
        summaries = []
        for session in self.active_negotiations.values():
            last_offer = session.offers[-1] if session.offers else None
            
            summary = {
                "negotiation_id": session.id,
                "item_type": session.item_type,
                "quantity": session.initial_quantity,
                "participants": [session.initiator_id, session.responder_id],
                "status": session.status.value,
                "offers_count": len(session.offers),
                "current_price": last_offer.total_price if last_offer else None,
                "time_remaining": (session.expires_at - datetime.now()).total_seconds(),
                "created_at": session.created_at.isoformat()
            }
            summaries.append(summary)
        
        return summaries

# Global negotiation engine instance
negotiation_engine = AdvancedNegotiationEngine()