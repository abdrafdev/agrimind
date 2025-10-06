"""
Advisor Agent for AgriMind
- Listens to predictions and market info
- Synthesizes farm-level recommendations
- Can request on-demand predictions
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentType, MessageType, Message


@dataclass
class Advice:
    kind: str
    message: str
    confidence: float
    timestamp: datetime


class AdvisorAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentType.PREDICTION, config=config)
        self.advices: List[Advice] = []
        self.subscribe(MessageType.PREDICTION, self._handle_prediction)
        self.subscribe(MessageType.MARKET_INFO, self._handle_market)

    async def _handle_prediction(self, message: Message):
        data = message.data
        if data.get("status") != "success":
            return
        pred = data.get("prediction", {})
        ptype = pred.get("prediction_type")
        value = pred.get("value")
        conf = float(pred.get("confidence", 0.5))
        if ptype == "irrigation_need":
            if value >= 0.85:
                self._add_advice("irrigation", "Schedule immediate irrigation (high need)", min(1.0, conf * 0.9))
            elif value >= 0.6:
                self._add_advice("irrigation", "Irrigate within 24 hours", conf)
            else:
                self._add_advice("irrigation", "Irrigation not urgent; monitor conditions", conf * 0.8)
        elif ptype == "pest_risk":
            if value >= 0.7:
                self._add_advice("pest", "High pest risk: apply preventive treatment", min(1.0, conf * 0.9))
            elif value >= 0.4:
                self._add_advice("pest", "Moderate pest risk: increase scouting frequency", conf)
        elif ptype == "harvest_timing":
            days = int(value)
            if days <= 10:
                self._add_advice("harvest", f"Prepare for harvest in {days} days", conf)
        elif ptype == "anomaly_alert":
            meta = pred.get("metadata", {})
            s = meta.get("sensor_type", "sensor")
            self._add_advice("anomaly", f"Investigate {s} anomaly", conf)

    async def _handle_market(self, message: Message):
        data = message.data
        # Recognize price_quote responses
        if data.get("request_type") == "price_quote" and "price" in data:
            price = data.get("price", 0.0)
            crop = data.get("crop_type", "unknown")
            rec = data.get("recommendation", {})
            action = rec.get("action", "hold")
            self._add_advice("market", f"{crop}: ${price:.2f}/kg — recommended action: {action}")

    def _add_advice(self, kind: str, message: str, confidence: float = 0.6):
        adv = Advice(kind=kind, message=message, confidence=confidence, timestamp=datetime.now())
        self.advices.append(adv)
        self.logger.info(f"🧭 Advice[{kind}]: {message} (conf={confidence:.2f})")

    async def request_market_quote(self, crop: str = "tomatoes", quality: str = "B"):
        await self.send_message(
            receiver_id="broadcast",
            message_type=MessageType.MARKET_INFO,
            data={"request_type": "price_quote", "crop_type": crop, "quality": quality},
        )

    async def main_loop(self):
        # Periodically request a market quote for awareness
        if not hasattr(self, "_last_quote") or (datetime.now() - self._last_quote).seconds > 600:
            await self.request_market_quote()
            self._last_quote = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        st = super().get_status()
        st.update(
            {
                "advices": [
                    {"kind": a.kind, "message": a.message, "confidence": a.confidence, "timestamp": a.timestamp.isoformat()}
                    for a in self.advices[-10:]
                ]
            }
        )
        return st


def create_advisor_agent(agent_id: str) -> AdvisorAgent:
    return AdvisorAgent(agent_id)
