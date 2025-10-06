"""
Anomaly Detection Agent for AgriMind
- Requests recent sensor data from the network
- Detects anomalies using robust statistics (IQR) with optional sklearn IsolationForest
- Publishes anomaly alerts via PREDICTION messages
"""
from __future__ import annotations

import asyncio
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from sklearn.ensemble import IsolationForest  # type: ignore
except Exception:
    IsolationForest = None  # Optional

from .base_agent import BaseAgent, AgentType, MessageType, Message


@dataclass
class AnomalyRecord:
    sensor_type: str
    value: float
    timestamp: datetime
    method: str
    score: float


class AnomalyDetectionAgent(BaseAgent):
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, AgentType.PREDICTION, config=config)
        self.recent_data: Dict[str, List[Dict[str, Any]]] = {}
        self.anomalies: List[AnomalyRecord] = []

        # Listen for data responses
        self.subscribe(MessageType.DATA_RESPONSE, self._handle_data_response)

    async def scan_for_anomalies(self):
        # Request small batches of common sensor data types
        for sensor_type in ["soil_moisture", "temperature", "humidity"]:
            await self.send_message(
                receiver_id="broadcast",
                message_type=MessageType.DATA_REQUEST,
                data={"sensor_type": sensor_type, "count": 5, "max_price_per_unit": 0.0},
            )
        # Give time for responses in the demo
        await asyncio.sleep(0.5)
        # Run detection
        await self._detect_all()

    async def _handle_data_response(self, message: Message):
        data = message.data
        if data.get("status") != "approved":
            return
        for reading in data.get("data", []):
            st = reading.get("sensor_type")
            if not st:
                continue
            self.recent_data.setdefault(st, []).append(
                {
                    "value": float(reading.get("value", 0.0)),
                    "timestamp": datetime.fromisoformat(reading.get("timestamp", datetime.now().isoformat())),
                    "source": reading.get("source", "unknown"),
                }
            )

    async def _detect_all(self):
        for sensor_type, items in list(self.recent_data.items()):
            if len(items) < 5:
                continue
            values = [it["value"] for it in items][-20:]
            # IQR-based detection
            try:
                q1 = statistics.quantiles(values, n=4)[0]
                q3 = statistics.quantiles(values, n=4)[2]
                iqr = max(1e-9, q3 - q1)
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                latest = values[-1]
                if latest < lower or latest > upper:
                    score = abs(latest - (q1 + q3) / 2) / iqr
                    await self._record_and_publish(sensor_type, latest, "iqr", score)
                    continue
            except Exception:
                pass

            # Optional IsolationForest if available and enough points
            if IsolationForest and len(values) >= 10:
                try:
                    import numpy as np  # type: ignore

                    model = IsolationForest(n_estimators=50, contamination=0.1, random_state=42)
                    preds = model.fit_predict(np.array(values).reshape(-1, 1))
                    latest_pred = preds[-1]
                    if latest_pred == -1:
                        # anomaly
                        await self._record_and_publish(sensor_type, values[-1], "isolation_forest", 1.0)
                except Exception:
                    pass

    async def _record_and_publish(self, sensor_type: str, value: float, method: str, score: float):
        rec = AnomalyRecord(sensor_type=sensor_type, value=value, timestamp=datetime.now(), method=method, score=score)
        self.anomalies.append(rec)
        self.logger.warning(f"🚨 Anomaly detected: {sensor_type}={value:.3f} via {method} (score={score:.2f})")
        await self.send_message(
            receiver_id="broadcast",
            message_type=MessageType.PREDICTION,
            data={
                "status": "success",
                "prediction": {
                    "prediction_type": "anomaly_alert",
                    "value": score,
                    "confidence": min(1.0, 0.5 + score * 0.1),
                    "timestamp": datetime.now().isoformat(),
                    "valid_until": (datetime.now() + timedelta(hours=1)).isoformat(),
                    "metadata": {"sensor_type": sensor_type, "method": method, "value": value},
                },
            },
        )

    async def main_loop(self):
        # Periodically request data and scan
        if not hasattr(self, "_last_scan") or (datetime.now() - self._last_scan).seconds > 300:
            await self.scan_for_anomalies()
            self._last_scan = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        st = super().get_status()
        st.update({
            "anomalies_count": len(self.anomalies),
            "recent_anomalies": [
                {"sensor_type": a.sensor_type, "value": a.value, "method": a.method, "timestamp": a.timestamp.isoformat()}
                for a in self.anomalies[-5:]
            ],
        })
        return st


def create_anomaly_detection_agent(agent_id: str) -> AnomalyDetectionAgent:
    return AnomalyDetectionAgent(agent_id)
