"""
AgriMind: Market Agent
Tracks crop prices, demand patterns, and connects farmers with buyers.
Recommends optimal selling times and facilitates transactions.

Features:
- Real-time price tracking with mock/API data
- Demand forecasting
- Buyer-seller matching
- Market trend analysis
- Degraded mode with cached prices
"""

import asyncio
import random
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from .base_agent import BaseAgent, AgentType, MessageType, Message
from data_loaders import load_market_data, DataSourceInfo


class CropType(Enum):
    """Types of crops handled by the market"""
    TOMATOES = "tomatoes"
    CORN = "corn"
    WHEAT = "wheat"
    SOYBEANS = "soybeans"
    LETTUCE = "lettuce"
    CARROTS = "carrots"
    PEPPERS = "peppers"


class MarketTrend(Enum):
    """Market trend directions"""
    BULLISH = "bullish"    # Rising prices
    BEARISH = "bearish"    # Falling prices
    STABLE = "stable"      # Sideways movement
    VOLATILE = "volatile"  # High fluctuation


@dataclass
class PriceData:
    """Represents market price information"""
    crop_type: CropType
    price: float          # Price per kg
    timestamp: datetime
    volume: int           # Quantity traded
    trend: MarketTrend
    quality_grade: str    # A, B, C grade
    source: str          # API, mock, cached
    confidence: float    # 0.0 to 1.0


@dataclass
class MarketDemand:
    """Represents demand information"""
    crop_type: CropType
    quantity_needed: int  # kg
    max_price: float
    deadline: datetime
    buyer_id: str
    quality_requirements: Dict[str, Any]
    location: str


@dataclass
class SellOffer:
    """Represents a sell offer from a farmer"""
    offer_id: str
    farmer_id: str
    crop_type: CropType
    quantity: int         # kg
    asking_price: float
    quality_grade: str
    harvest_date: datetime
    expiry_date: datetime
    location: str
    metadata: Dict[str, Any]


class MarketAgent(BaseAgent):
    """
    Market Agent that tracks crop prices, analyzes trends, and facilitates
    connections between farmers and buyers
    """
    
    def __init__(
        self, 
        agent_id: str,
        region: str,
        market_config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(agent_id, AgentType.MARKET)
        
        self.region = region
        self.market_config = market_config or self._default_market_config()
        
        # Market data
        self.price_history: Dict[CropType, List[PriceData]] = {}
        self.demand_requests: Dict[str, MarketDemand] = {}
        self.sell_offers: Dict[str, SellOffer] = {}
        self.completed_trades: List[Dict[str, Any]] = []
        
        # Market analysis
        self.trend_analysis: Dict[CropType, Dict[str, Any]] = {}
        self.seasonal_patterns: Dict[CropType, Dict[str, float]] = {}
        
        # Buyer network
        self.registered_buyers: Dict[str, Dict[str, Any]] = {}
        self.buyer_preferences: Dict[str, Dict[str, Any]] = {}
        
        # Initialize market data
        self._initialize_market_data()
        
        # Subscribe to messages
        self.subscribe(MessageType.MARKET_INFO, self._handle_market_request)
        self.subscribe(MessageType.NEGOTIATION, self._handle_trade_negotiation)
        self.subscribe(MessageType.PREDICTION, self._handle_harvest_prediction)
        
        self.logger.info(f"Market agent initialized for region: {region}")

    def _default_market_config(self) -> Dict[str, Any]:
        """Default market configuration"""
        return {
            "crops": {
                "tomatoes": {"base_price": 3.50, "volatility": 0.15, "seasonality": 0.3},
                "corn": {"base_price": 0.85, "volatility": 0.10, "seasonality": 0.2},
                "wheat": {"base_price": 0.65, "volatility": 0.08, "seasonality": 0.15},
                "soybeans": {"base_price": 1.20, "volatility": 0.12, "seasonality": 0.25},
                "lettuce": {"base_price": 2.80, "volatility": 0.20, "seasonality": 0.4},
                "carrots": {"base_price": 1.50, "volatility": 0.12, "seasonality": 0.2},
                "peppers": {"base_price": 4.20, "volatility": 0.18, "seasonality": 0.35}
            },
            "quality_multipliers": {
                "A": 1.2,  # Premium grade
                "B": 1.0,  # Standard grade
                "C": 0.8   # Lower grade
            },
            "commission_rate": 0.03,  # 3% commission
            "update_interval": 300,   # 5 minutes
            "trend_window": 24        # Hours for trend analysis
        }

    def _initialize_market_data(self):
        """Initialize market data from dataset first, then mock data fallback"""
        data_source_used = []
        
        # First try to load market data from official dataset
        try:
            market_df, source_info = load_market_data(days_back=60)
            
            if not market_df.empty and source_info.source_type == "dataset":
                self.logger.info(f"📈 Loading market data from dataset: {source_info.source_name} ({len(market_df)} records)")
                
                # Group data by crop and convert to PriceData objects
                if 'crop' in market_df.columns and 'price' in market_df.columns:
                    for crop_name in market_df['crop'].unique():
                        try:
                            crop_type = CropType(crop_name.lower())
                        except ValueError:
                            self.logger.warning(f"Unknown crop type in dataset: {crop_name}")
                            continue
                        
                        crop_data = market_df[market_df['crop'].str.lower() == crop_name.lower()]
                        self.price_history[crop_type] = []
                        
                        for _, row in crop_data.iterrows():
                            try:
                                price_data = PriceData(
                                    crop_type=crop_type,
                                    price=float(row['price']),
                                    timestamp=pd.to_datetime(row['date']) if 'date' in row else datetime.now(),
                                    volume=int(row.get('volume', random.randint(100, 1000))),
                                    trend=self._determine_trend_from_data(crop_data, row.name),
                                    quality_grade=str(row.get('quality_grade', 'B')),
                                    source="dataset",
                                    confidence=0.9
                                )
                                self.price_history[crop_type].append(price_data)
                            except Exception as e:
                                self.logger.warning(f"Error processing market record: {e}")
                                continue
                        
                        if self.price_history[crop_type]:
                            data_source_used.append(f"{crop_type.value} dataset ({len(self.price_history[crop_type])} records)")
        
        except Exception as e:
            self.logger.warning(f"Could not load market dataset: {e}")
        
        # Fill in missing crops with mock data from configuration
        for crop_name in self.market_config["crops"]:
            crop_type = CropType(crop_name)
            
            if crop_type not in self.price_history or not self.price_history[crop_type]:
                self.price_history[crop_type] = []
                
                # Generate mock historical data
                base_price = self.market_config["crops"][crop_name]["base_price"]
                volatility = self.market_config["crops"][crop_name]["volatility"]
                
                # Create some historical data
                for hours_ago in range(48, 0, -1):
                    timestamp = datetime.now() - timedelta(hours=hours_ago)
                    price_variation = random.uniform(-volatility, volatility)
                    price = base_price * (1 + price_variation)
                    
                    price_data = PriceData(
                        crop_type=crop_type,
                        price=price,
                        timestamp=timestamp,
                        volume=random.randint(100, 1000),
                        trend=MarketTrend.STABLE,
                        quality_grade="B",
                        source="mock",
                        confidence=0.7
                    )
                    
                    self.price_history[crop_type].append(price_data)
                
                data_source_used.append(f"{crop_type.value} mock (48 records)")
        
        # Log data sources used
        if data_source_used:
            self.logger.info(f"📈 MarketAgent {self.agent_id} data sources: {'; '.join(data_source_used)}")
        
        # Initialize mock buyers
        self._initialize_mock_buyers()

    def _determine_trend_from_data(self, crop_data: pd.DataFrame, current_index: int) -> MarketTrend:
        """Determine market trend from price data"""
        try:
            if len(crop_data) < 3:
                return MarketTrend.STABLE
            
            # Get a window around current price
            start_idx = max(0, current_index - 2)
            end_idx = min(len(crop_data), current_index + 3)
            window = crop_data.iloc[start_idx:end_idx]
            
            if 'price' not in window.columns:
                return MarketTrend.STABLE
            
            prices = window['price'].values
            if len(prices) < 2:
                return MarketTrend.STABLE
            
            # Calculate trend based on price changes
            price_changes = []
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1]
                price_changes.append(change)
            
            if not price_changes:
                return MarketTrend.STABLE
            
            avg_change = sum(price_changes) / len(price_changes)
            volatility = max(price_changes) - min(price_changes)
            
            # Determine trend
            if volatility > 0.15:  # High volatility
                return MarketTrend.VOLATILE
            elif avg_change > 0.05:  # Rising trend
                return MarketTrend.BULLISH
            elif avg_change < -0.05:  # Falling trend
                return MarketTrend.BEARISH
            else:
                return MarketTrend.STABLE
                
        except Exception as e:
            self.logger.warning(f"Error determining trend: {e}")
            return MarketTrend.STABLE

    def _initialize_mock_buyers(self):
        """Initialize mock buyer profiles"""
        mock_buyers = [
            {
                "buyer_id": "grocery_chain_1",
                "name": "Fresh Market Co.",
                "type": "retail_chain",
                "preferred_crops": ["tomatoes", "lettuce", "carrots"],
                "min_quality": "B",
                "typical_volume": 500,  # kg per order
                "payment_terms": "net_30"
            },
            {
                "buyer_id": "restaurant_group",
                "name": "Farm-to-Table Restaurants",
                "type": "restaurant",
                "preferred_crops": ["tomatoes", "peppers", "lettuce"],
                "min_quality": "A",
                "typical_volume": 100,
                "payment_terms": "net_15"
            },
            {
                "buyer_id": "food_processor",
                "name": "Valley Processing Inc.",
                "type": "processor",
                "preferred_crops": ["corn", "wheat", "soybeans"],
                "min_quality": "C",
                "typical_volume": 2000,
                "payment_terms": "net_45"
            },
            {
                "buyer_id": "export_company",
                "name": "Global Agri Exports",
                "type": "exporter",
                "preferred_crops": ["wheat", "soybeans", "corn"],
                "min_quality": "B",
                "typical_volume": 5000,
                "payment_terms": "letter_of_credit"
            }
        ]
        
        for buyer in mock_buyers:
            self.registered_buyers[buyer["buyer_id"]] = buyer
            self.buyer_preferences[buyer["buyer_id"]] = {
                "crops": buyer["preferred_crops"],
                "quality": buyer["min_quality"],
                "volume": buyer["typical_volume"]
            }

    async def update_market_prices(self):
        """Update market prices with new data"""
        for crop_type in self.price_history:
            try:
                if self.online:
                    # Try to get real market data
                    price_data = await self._fetch_real_price_data(crop_type)
                    if price_data is None:
                        # Fallback to mock data
                        price_data = self._generate_mock_price_data(crop_type)
                else:
                    # Degraded mode
                    price_data = await self._get_degraded_price_data(crop_type)
                
                if price_data:
                    self.price_history[crop_type].append(price_data)
                    
                    # Keep only recent data (last 7 days)
                    cutoff = datetime.now() - timedelta(days=7)
                    self.price_history[crop_type] = [
                        p for p in self.price_history[crop_type]
                        if p.timestamp > cutoff
                    ]
                    
                    # Cache for degraded mode
                    await self.cache_data(f"price_{crop_type.value}", price_data)
                    
                    # Update trend analysis
                    await self._update_trend_analysis(crop_type)
                    
            except Exception as e:
                self.logger.error(f"Error updating prices for {crop_type.value}: {e}")

    async def _fetch_real_price_data(self, crop_type: CropType) -> Optional[PriceData]:
        """Fetch real market data from external APIs (simulated)"""
        # In a real implementation, this would call actual market data APIs
        # For demo purposes, we'll simulate API failures and responses
        
        if random.random() < 0.1:  # 10% chance of API failure
            raise Exception("Market API temporarily unavailable")
        
        # Simulate API response
        base_price = self.market_config["crops"][crop_type.value]["base_price"]
        volatility = self.market_config["crops"][crop_type.value]["volatility"]
        
        # Add some market forces simulation
        market_factors = self._simulate_market_factors(crop_type)
        price_change = market_factors["supply_demand"] + market_factors["seasonal"]
        
        new_price = base_price * (1 + price_change)
        
        return PriceData(
            crop_type=crop_type,
            price=new_price,
            timestamp=datetime.now(),
            volume=random.randint(200, 1500),
            trend=self._determine_trend(crop_type),
            quality_grade="B",
            source="market_api",
            confidence=0.9
        )

    def _simulate_market_factors(self, crop_type: CropType) -> Dict[str, float]:
        """Simulate various market factors affecting prices"""
        # Supply and demand simulation
        supply_demand = random.uniform(-0.1, 0.1)
        
        # Seasonal factors
        month = datetime.now().month
        seasonality = self.market_config["crops"][crop_type.value]["seasonality"]
        
        # Simple seasonal pattern (peak in summer for most crops)
        seasonal_factor = 0
        if crop_type in [CropType.TOMATOES, CropType.LETTUCE, CropType.PEPPERS]:
            # Summer crops - higher prices in winter
            seasonal_factor = seasonality * (6 - abs(month - 6)) / 6
        elif crop_type in [CropType.CORN, CropType.WHEAT, CropType.SOYBEANS]:
            # Fall harvest crops - higher prices before harvest
            seasonal_factor = seasonality * (3 - abs(month - 9)) / 3
        
        # Weather impact (random)
        weather_impact = random.uniform(-0.05, 0.05)
        
        return {
            "supply_demand": supply_demand,
            "seasonal": seasonal_factor,
            "weather": weather_impact
        }

    def _generate_mock_price_data(self, crop_type: CropType) -> PriceData:
        """Generate realistic mock price data"""
        # Get latest price for trend continuation
        latest_prices = [p.price for p in self.price_history[crop_type][-5:]]
        if latest_prices:
            latest_price = latest_prices[-1]
            # Add some trend momentum
            trend_momentum = sum(latest_prices[-3:]) - sum(latest_prices[-5:-2]) if len(latest_prices) >= 5 else 0
            trend_factor = trend_momentum / len(latest_prices) * 0.1
        else:
            latest_price = self.market_config["crops"][crop_type.value]["base_price"]
            trend_factor = 0
        
        volatility = self.market_config["crops"][crop_type.value]["volatility"]
        price_change = random.uniform(-volatility, volatility) + trend_factor
        new_price = max(0.1, latest_price * (1 + price_change))
        
        return PriceData(
            crop_type=crop_type,
            price=new_price,
            timestamp=datetime.now(),
            volume=random.randint(150, 800),
            trend=self._determine_trend(crop_type),
            quality_grade="B",
            source="mock_data",
            confidence=0.7
        )

    async def _get_degraded_price_data(self, crop_type: CropType) -> Optional[PriceData]:
        """Get price data in degraded mode"""
        # Try cached data first
        cached_price = await self.get_cached_data(f"price_{crop_type.value}", max_age_hours=6)
        if cached_price:
            cached_price.timestamp = datetime.now()
            cached_price.source += "_cached"
            cached_price.confidence *= 0.6
            return cached_price
        
        # Fall back to rule-based price estimation
        self.logger.warning(f"Using rule-based price estimation for {crop_type.value}")
        
        base_price = self.market_config["crops"][crop_type.value]["base_price"]
        # Conservative estimate with seasonal adjustment
        seasonal_adjustment = self._get_seasonal_adjustment(crop_type)
        estimated_price = base_price * (1 + seasonal_adjustment)
        
        return PriceData(
            crop_type=crop_type,
            price=estimated_price,
            timestamp=datetime.now(),
            volume=300,  # Conservative volume estimate
            trend=MarketTrend.STABLE,
            quality_grade="B",
            source="rule_based",
            confidence=0.4
        )

    def _get_seasonal_adjustment(self, crop_type: CropType) -> float:
        """Get seasonal price adjustment"""
        month = datetime.now().month
        seasonality = self.market_config["crops"][crop_type.value]["seasonality"]
        
        # Simple seasonal patterns
        if crop_type in [CropType.TOMATOES, CropType.LETTUCE]:
            # Higher prices in winter months
            if month in [12, 1, 2]:
                return seasonality * 0.3
            elif month in [6, 7, 8]:
                return -seasonality * 0.2
        elif crop_type in [CropType.CORN, CropType.WHEAT]:
            # Higher prices before harvest season
            if month in [7, 8]:
                return seasonality * 0.2
            elif month in [10, 11]:
                return -seasonality * 0.3
        
        return 0.0

    def _determine_trend(self, crop_type: CropType) -> MarketTrend:
        """Determine current market trend based on recent price history"""
        recent_prices = [p.price for p in self.price_history[crop_type][-10:]]
        
        if len(recent_prices) < 5:
            return MarketTrend.STABLE
        
        # Calculate price changes
        price_changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]
        avg_change = sum(price_changes) / len(price_changes)
        volatility = sum(abs(change) for change in price_changes) / len(price_changes)
        
        # Determine trend
        if volatility > avg_change * 3:
            return MarketTrend.VOLATILE
        elif avg_change > 0.02:
            return MarketTrend.BULLISH
        elif avg_change < -0.02:
            return MarketTrend.BEARISH
        else:
            return MarketTrend.STABLE

    async def _update_trend_analysis(self, crop_type: CropType):
        """Update trend analysis for a crop type"""
        prices = self.price_history[crop_type]
        if len(prices) < 10:
            return
        
        # Calculate various metrics
        recent_prices = [p.price for p in prices[-24:]]  # Last 24 hours
        
        if len(recent_prices) >= 24:
            current_price = recent_prices[-1]
            day_ago_price = recent_prices[0]
            
            price_change_24h = (current_price - day_ago_price) / day_ago_price
            avg_volume = sum(p.volume for p in prices[-24:]) / len(prices[-24:])
            
            # Support and resistance levels
            recent_highs = [max(recent_prices[i:i+6]) for i in range(0, len(recent_prices)-5, 6)]
            recent_lows = [min(recent_prices[i:i+6]) for i in range(0, len(recent_prices)-5, 6)]
            
            resistance_level = max(recent_highs) if recent_highs else current_price
            support_level = min(recent_lows) if recent_lows else current_price
            
            self.trend_analysis[crop_type] = {
                "current_price": current_price,
                "price_change_24h": price_change_24h,
                "trend": self._determine_trend(crop_type).value,
                "support_level": support_level,
                "resistance_level": resistance_level,
                "avg_volume": avg_volume,
                "volatility": self._calculate_volatility(recent_prices),
                "recommendation": self._generate_price_recommendation(crop_type)
            }

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility"""
        if len(prices) < 2:
            return 0.0
        
        changes = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        mean_change = sum(changes) / len(changes)
        variance = sum((change - mean_change) ** 2 for change in changes) / len(changes)
        return variance ** 0.5

    def _generate_price_recommendation(self, crop_type: CropType) -> Dict[str, Any]:
        """Generate buy/sell recommendations"""
        if crop_type not in self.trend_analysis:
            return {"action": "hold", "confidence": 0.5}
        
        analysis = self.trend_analysis[crop_type]
        current_price = analysis["current_price"]
        price_change = analysis["price_change_24h"]
        trend = analysis["trend"]
        
        # Simple recommendation logic
        if trend == "bullish" and price_change > 0.05:
            return {"action": "buy", "confidence": 0.8, "reason": "strong_upward_trend"}
        elif trend == "bearish" and price_change < -0.05:
            return {"action": "sell", "confidence": 0.8, "reason": "strong_downward_trend"}
        elif trend == "volatile":
            return {"action": "wait", "confidence": 0.6, "reason": "high_volatility"}
        else:
            # Check seasonal factors
            seasonal_adj = self._get_seasonal_adjustment(crop_type)
            if seasonal_adj > 0.1:
                return {"action": "hold_for_season", "confidence": 0.7, "reason": "seasonal_upside"}
            else:
                return {"action": "hold", "confidence": 0.5, "reason": "stable_market"}

    async def _handle_market_request(self, message: Message):
        """Handle market information requests"""
        request_data = message.data
        requester_id = message.sender_id
        
        request_type = request_data.get("request_type")
        
        if request_type == "price_quote":
            crop_type = CropType(request_data["crop_type"])
            quality = request_data.get("quality", "B")
            
            # Get latest price
            if crop_type in self.price_history and self.price_history[crop_type]:
                latest_price = self.price_history[crop_type][-1]
                
                # Adjust for quality
                quality_multiplier = self.market_config["quality_multipliers"].get(quality, 1.0)
                adjusted_price = latest_price.price * quality_multiplier
                
                response_data = {
                    "request_type": "price_quote",
                    "crop_type": crop_type.value,
                    "price": adjusted_price,
                    "quality": quality,
                    "timestamp": latest_price.timestamp.isoformat(),
                    "trend": latest_price.trend.value,
                    "confidence": latest_price.confidence,
                    "recommendation": self.trend_analysis.get(crop_type, {}).get("recommendation", {})
                }
            else:
                response_data = {
                    "request_type": "price_quote",
                    "error": "No price data available",
                    "crop_type": crop_type.value
                }
            
        elif request_type == "market_analysis":
            crop_type = CropType(request_data["crop_type"])
            
            if crop_type in self.trend_analysis:
                response_data = {
                    "request_type": "market_analysis",
                    "crop_type": crop_type.value,
                    "analysis": self.trend_analysis[crop_type]
                }
            else:
                response_data = {
                    "request_type": "market_analysis",
                    "error": "No analysis available",
                    "crop_type": crop_type.value
                }
        
        elif request_type == "buyer_matching":
            crop_type = CropType(request_data["crop_type"])
            quantity = request_data["quantity"]
            quality = request_data.get("quality", "B")
            
            matches = await self._find_buyer_matches(crop_type, quantity, quality)
            response_data = {
                "request_type": "buyer_matching",
                "crop_type": crop_type.value,
                "matches": matches
            }
        
        elif request_type == "sell_offer":
            # Register sell offer
            offer = SellOffer(
                offer_id=f"offer_{requester_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                farmer_id=requester_id,
                crop_type=CropType(request_data["crop_type"]),
                quantity=request_data["quantity"],
                asking_price=request_data["asking_price"],
                quality_grade=request_data.get("quality_grade", "B"),
                harvest_date=datetime.fromisoformat(request_data["harvest_date"]),
                expiry_date=datetime.fromisoformat(request_data.get("expiry_date", 
                    (datetime.now() + timedelta(days=30)).isoformat())),
                location=request_data.get("location", "unknown"),
                metadata=request_data.get("metadata", {})
            )
            
            self.sell_offers[offer.offer_id] = offer
            
            # Try to match with existing demand
            matches = await self._match_with_demand(offer)
            
            response_data = {
                "request_type": "sell_offer",
                "offer_id": offer.offer_id,
                "status": "registered",
                "potential_matches": len(matches)
            }
            
            # Notify potential buyers
            for match in matches:
                await self._notify_buyer_of_match(match, offer)
        
        else:
            response_data = {
                "error": "Unknown request type",
                "request_type": request_type
            }
        
        # Send response
        await self.send_message(
            receiver_id=requester_id,
            message_type=MessageType.MARKET_INFO,
            data=response_data
        )

    async def _find_buyer_matches(self, crop_type: CropType, quantity: int, quality: str) -> List[Dict[str, Any]]:
        """Find potential buyers for a crop"""
        matches = []
        
        for buyer_id, buyer_info in self.registered_buyers.items():
            preferences = self.buyer_preferences.get(buyer_id, {})
            
            # Check if buyer is interested in this crop
            if crop_type.value in preferences.get("crops", []):
                # Check quality requirements
                min_quality = preferences.get("quality", "C")
                quality_order = {"A": 3, "B": 2, "C": 1}
                
                if quality_order.get(quality, 1) >= quality_order.get(min_quality, 1):
                    # Calculate match score
                    typical_volume = preferences.get("volume", 100)
                    volume_match = min(1.0, typical_volume / quantity) if quantity > 0 else 1.0
                    
                    # Get current price for this crop
                    current_price = 0
                    if crop_type in self.price_history and self.price_history[crop_type]:
                        current_price = self.price_history[crop_type][-1].price
                    
                    match_score = volume_match * 0.7 + (1.0 if quality == min_quality else 0.5) * 0.3
                    
                    matches.append({
                        "buyer_id": buyer_id,
                        "buyer_name": buyer_info["name"],
                        "buyer_type": buyer_info["type"],
                        "match_score": match_score,
                        "typical_volume": typical_volume,
                        "payment_terms": buyer_info["payment_terms"],
                        "suggested_price": current_price
                    })
        
        # Sort by match score
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:5]  # Return top 5 matches

    async def _match_with_demand(self, offer: SellOffer) -> List[Dict[str, Any]]:
        """Match sell offer with existing demand requests"""
        matches = []
        
        for demand_id, demand in self.demand_requests.items():
            if (demand.crop_type == offer.crop_type and 
                demand.quantity >= offer.quantity and
                demand.max_price >= offer.asking_price and
                demand.deadline > offer.harvest_date):
                
                quality_req = demand.quality_requirements.get("min_grade", "C")
                quality_order = {"A": 3, "B": 2, "C": 1}
                
                if quality_order.get(offer.quality_grade, 1) >= quality_order.get(quality_req, 1):
                    match_score = (
                        0.4 * (min(demand.quantity, offer.quantity) / max(demand.quantity, offer.quantity)) +
                        0.4 * (min(demand.max_price, offer.asking_price) / max(demand.max_price, offer.asking_price)) +
                        0.2 * (1.0 if offer.quality_grade == quality_req else 0.7)
                    )
                    
                    matches.append({
                        "demand_id": demand_id,
                        "buyer_id": demand.buyer_id,
                        "match_score": match_score,
                        "demand": asdict(demand)
                    })
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches

    async def _notify_buyer_of_match(self, match: Dict[str, Any], offer: SellOffer):
        """Notify buyer of a potential match"""
        buyer_id = match["buyer_id"]
        
        notification_data = {
            "notification_type": "crop_available",
            "offer_id": offer.offer_id,
            "crop_type": offer.crop_type.value,
            "quantity": offer.quantity,
            "quality_grade": offer.quality_grade,
            "asking_price": offer.asking_price,
            "harvest_date": offer.harvest_date.isoformat(),
            "location": offer.location,
            "match_score": match["match_score"],
            "farmer_id": offer.farmer_id
        }
        
        await self.send_message(
            receiver_id=buyer_id,
            message_type=MessageType.MARKET_INFO,
            data=notification_data
        )

    async def _handle_trade_negotiation(self, message: Message):
        """Handle trade negotiations between buyers and sellers"""
        negotiation_data = message.data
        negotiator_id = message.sender_id
        
        if negotiation_data.get("action") == "make_offer":
            offer_id = negotiation_data["offer_id"]
            bid_price = negotiation_data["bid_price"]
            quantity = negotiation_data.get("quantity")
            
            if offer_id in self.sell_offers:
                sell_offer = self.sell_offers[offer_id]
                
                # Calculate commission
                commission_rate = self.market_config["commission_rate"]
                commission = bid_price * quantity * commission_rate
                
                # Create transaction
                transaction_id = await self.create_transaction(
                    buyer_id=negotiator_id,
                    seller_id=sell_offer.farmer_id,
                    item_type=f"{sell_offer.crop_type.value}_trade",
                    quantity=quantity or sell_offer.quantity,
                    price=bid_price * (quantity or sell_offer.quantity)
                )
                
                # Notify farmer
                await self.send_message(
                    receiver_id=sell_offer.farmer_id,
                    message_type=MessageType.NEGOTIATION,
                    data={
                        "action": "bid_received",
                        "offer_id": offer_id,
                        "buyer_id": negotiator_id,
                        "bid_price": bid_price,
                        "quantity": quantity or sell_offer.quantity,
                        "commission": commission,
                        "transaction_id": transaction_id
                    }
                )

    async def _handle_harvest_prediction(self, message: Message):
        """Handle harvest timing predictions to inform market planning"""
        prediction_data = message.data
        
        if (prediction_data.get("status") == "success" and 
            prediction_data["prediction"]["prediction_type"] == "harvest_timing"):
            
            farmer_id = message.sender_id
            days_to_harvest = prediction_data["prediction"]["value"]
            confidence = prediction_data["prediction"]["confidence"]
            
            # Update supply forecasts
            if confidence > 0.6:
                harvest_date = datetime.now() + timedelta(days=days_to_harvest)
                
                self.logger.info(
                    f"Updated harvest forecast: {farmer_id} expects harvest in {days_to_harvest:.0f} days"
                )
                
                # This could trigger demand matching or price adjustments

    async def generate_market_report(self) -> Dict[str, Any]:
        """Generate comprehensive market report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
            "market_summary": {},
            "price_trends": {},
            "trade_volume": {},
            "active_offers": len(self.sell_offers),
            "registered_buyers": len(self.registered_buyers),
            "completed_trades_today": len([
                t for t in self.completed_trades 
                if datetime.fromisoformat(t["timestamp"]).date() == datetime.now().date()
            ])
        }
        
        for crop_type, prices in self.price_history.items():
            if prices:
                latest_price = prices[-1]
                day_ago_prices = [p for p in prices if (datetime.now() - p.timestamp).days <= 1]
                
                if day_ago_prices:
                    price_change = ((latest_price.price - day_ago_prices[0].price) / 
                                  day_ago_prices[0].price * 100)
                else:
                    price_change = 0
                
                report["market_summary"][crop_type.value] = {
                    "current_price": latest_price.price,
                    "price_change_24h": price_change,
                    "trend": latest_price.trend.value,
                    "volume": latest_price.volume
                }
                
                if crop_type in self.trend_analysis:
                    report["price_trends"][crop_type.value] = self.trend_analysis[crop_type]
        
        return report

    async def main_loop(self):
        """Main market agent logic"""
        # Update prices every 5 minutes
        if not hasattr(self, '_last_price_update') or \
           (datetime.now() - self._last_price_update).seconds > 300:
            
            await self.update_market_prices()
            self._last_price_update = datetime.now()
        
        # Generate market report every hour
        if not hasattr(self, '_last_report') or \
           (datetime.now() - self._last_report).seconds > 3600:
            
            report = await self.generate_market_report()
            await self.cache_data("market_report", report)
            self._last_report = datetime.now()
            
            self.logger.info("Generated hourly market report")

    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status"""
        status = self.get_status()
        
        # Current prices
        current_prices = {}
        for crop_type, prices in self.price_history.items():
            if prices:
                latest = prices[-1]
                current_prices[crop_type.value] = {
                    "price": latest.price,
                    "timestamp": latest.timestamp.isoformat(),
                    "trend": latest.trend.value,
                    "confidence": latest.confidence
                }
        
        # Market activity
        market_activity = {
            "active_sell_offers": len(self.sell_offers),
            "registered_buyers": len(self.registered_buyers),
            "completed_trades_total": len(self.completed_trades)
        }
        
        status.update({
            "region": self.region,
            "current_prices": current_prices,
            "market_activity": market_activity,
            "trend_analysis": {k.value: v for k, v in self.trend_analysis.items()}
        })
        
        return status


# Helper function to create market agent
def create_market_agent(
    agent_id: str,
    region: str
) -> MarketAgent:
    """Factory function to create a market agent"""
    return MarketAgent(agent_id, region)