"""
AgriMind: Comprehensive System Evaluator
Performance tracking, efficiency metrics, and system optimization indicators
"""

import asyncio
import json
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import statistics
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.base_agent import message_bus, MessageType, AgentType
from agents.negotiation_engine import negotiation_engine

logger = logging.getLogger("AgriMind-Evaluator")

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    agent_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class SystemSnapshot:
    """System state snapshot for trend analysis"""
    timestamp: datetime
    total_agents: int
    online_agents: int
    total_transactions: int
    total_messages: int
    system_load: float
    response_time_avg: float
    success_rate: float
    data_freshness_score: float

@dataclass
class AgentEfficiencyReport:
    """Agent efficiency analysis"""
    agent_id: str
    agent_type: str
    transaction_success_rate: float
    avg_response_time: float
    data_quality_score: float
    collaboration_score: float
    resource_utilization: float
    profitability_score: float
    recommendations: List[str]

class AgriMindEvaluator:
    """
    Comprehensive system evaluator for AgriMind
    Tracks performance, efficiency, and optimization opportunities
    """
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.system_snapshots: List[SystemSnapshot] = []
        self.evaluation_start_time = datetime.now()
        self.benchmark_data = {}
        
        # Performance tracking
        self.response_times = []
        self.transaction_times = []
        self.error_counts = {"critical": 0, "warning": 0, "info": 0}
        
        # Efficiency tracking
        self.agent_activity_log = {}
        self.resource_usage_log = {}
        self.collaboration_matrix = {}
        
        # Load benchmark data
        self._initialize_benchmarks()
    
    def _initialize_benchmarks(self):
        """Initialize performance benchmarks for comparison"""
        self.benchmark_data = {
            "response_time_targets": {
                "sensor_data_collection": 2.0,  # seconds
                "prediction_generation": 5.0,   # seconds
                "resource_allocation": 3.0,     # seconds
                "market_operations": 1.5,       # seconds
                "negotiation_round": 10.0       # seconds
            },
            "success_rate_targets": {
                "data_transactions": 0.95,
                "predictions": 0.90,
                "resource_allocations": 0.85,
                "negotiations": 0.80,
                "system_uptime": 0.99
            },
            "efficiency_targets": {
                "agent_utilization": 0.75,
                "data_freshness": 0.90,
                "collaboration_score": 0.80,
                "cost_efficiency": 0.85
            }
        }
    
    def record_metric(
        self, 
        name: str, 
        value: float, 
        unit: str, 
        category: str,
        agent_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            category=category,
            agent_id=agent_id,
            details=details
        )
        self.metrics_history.append(metric)
        
        # Keep only last 10000 metrics to prevent memory issues
        if len(self.metrics_history) > 10000:
            self.metrics_history = self.metrics_history[-5000:]
    
    def record_response_time(self, operation: str, duration: float, agent_id: str):
        """Record operation response time"""
        self.response_times.append({
            "operation": operation,
            "duration": duration,
            "agent_id": agent_id,
            "timestamp": datetime.now()
        })
        
        # Track agent activity
        if agent_id not in self.agent_activity_log:
            self.agent_activity_log[agent_id] = []
        
        self.agent_activity_log[agent_id].append({
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now()
        })
        
        self.record_metric(
            name=f"{operation}_response_time",
            value=duration,
            unit="seconds",
            category="performance",
            agent_id=agent_id
        )
    
    def record_transaction(
        self, 
        transaction_type: str, 
        duration: float, 
        success: bool,
        buyer_id: str, 
        seller_id: str,
        value: float
    ):
        """Record transaction metrics"""
        self.transaction_times.append({
            "type": transaction_type,
            "duration": duration,
            "success": success,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "value": value,
            "timestamp": datetime.now()
        })
        
        # Update collaboration matrix
        if buyer_id not in self.collaboration_matrix:
            self.collaboration_matrix[buyer_id] = {}
        if seller_id not in self.collaboration_matrix[buyer_id]:
            self.collaboration_matrix[buyer_id][seller_id] = {"count": 0, "total_value": 0.0}
        
        self.collaboration_matrix[buyer_id][seller_id]["count"] += 1
        self.collaboration_matrix[buyer_id][seller_id]["total_value"] += value
        
        self.record_metric(
            name=f"{transaction_type}_transaction_time",
            value=duration,
            unit="seconds",
            category="transactions",
            details={
                "success": success,
                "buyer_id": buyer_id,
                "seller_id": seller_id,
                "value": value
            }
        )
    
    def record_error(self, severity: str, message: str, agent_id: Optional[str] = None):
        """Record system errors"""
        if severity in self.error_counts:
            self.error_counts[severity] += 1
        
        self.record_metric(
            name="system_error",
            value=1.0,
            unit="count",
            category="reliability",
            agent_id=agent_id,
            details={"severity": severity, "message": message}
        )
    
    def take_system_snapshot(self) -> SystemSnapshot:
        """Take a comprehensive system snapshot"""
        # Get current system state
        agent_stats = message_bus.get_agent_stats()
        
        # Calculate metrics
        avg_response_time = 0.0
        if self.response_times:
            recent_responses = [
                r["duration"] for r in self.response_times[-100:]  # Last 100 operations
            ]
            avg_response_time = statistics.mean(recent_responses) if recent_responses else 0.0
        
        success_rate = self._calculate_current_success_rate()
        data_freshness = self._calculate_data_freshness_score()
        system_load = self._calculate_system_load()
        
        snapshot = SystemSnapshot(
            timestamp=datetime.now(),
            total_agents=agent_stats.get("total_agents", 0),
            online_agents=agent_stats.get("online_agents", 0),
            total_transactions=len(self.transaction_times),
            total_messages=agent_stats.get("total_messages_broadcast", 0),
            system_load=system_load,
            response_time_avg=avg_response_time,
            success_rate=success_rate,
            data_freshness_score=data_freshness
        )
        
        self.system_snapshots.append(snapshot)
        
        # Keep only last 1000 snapshots
        if len(self.system_snapshots) > 1000:
            self.system_snapshots = self.system_snapshots[-500:]
        
        return snapshot
    
    def _calculate_current_success_rate(self) -> float:
        """Calculate current system success rate"""
        if not self.transaction_times:
            return 1.0
        
        recent_transactions = self.transaction_times[-100:]  # Last 100 transactions
        if not recent_transactions:
            return 1.0
        
        successful = sum(1 for t in recent_transactions if t["success"])
        return successful / len(recent_transactions)
    
    def _calculate_data_freshness_score(self) -> float:
        """Calculate data freshness score"""
        current_time = datetime.now()
        freshness_scores = []
        
        for agent_id, activities in self.agent_activity_log.items():
            if not activities:
                continue
            
            last_activity = max(activities, key=lambda x: x["timestamp"])
            time_diff = (current_time - last_activity["timestamp"]).total_seconds()
            
            # Fresher data gets higher score (exponential decay)
            freshness = math.exp(-time_diff / 300)  # 5-minute half-life
            freshness_scores.append(freshness)
        
        return statistics.mean(freshness_scores) if freshness_scores else 0.0
    
    def _calculate_system_load(self) -> float:
        """Calculate current system load"""
        # Simple load calculation based on recent activity
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=1)
        
        recent_operations = [
            r for r in self.response_times
            if r["timestamp"] > recent_cutoff
        ]
        
        # Normalize to 0-1 scale (100 operations per minute = load 1.0)
        return min(1.0, len(recent_operations) / 100.0)
    
    def generate_agent_efficiency_report(self, agent_id: str) -> AgentEfficiencyReport:
        """Generate comprehensive efficiency report for an agent"""
        if agent_id not in message_bus.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = message_bus.agents[agent_id]
        agent_activities = self.agent_activity_log.get(agent_id, [])
        
        # Calculate metrics
        transaction_success_rate = self._calculate_agent_transaction_success_rate(agent_id)
        avg_response_time = self._calculate_agent_avg_response_time(agent_id)
        data_quality_score = self._calculate_agent_data_quality_score(agent_id)
        collaboration_score = self._calculate_agent_collaboration_score(agent_id)
        resource_utilization = self._calculate_agent_resource_utilization(agent_id)
        profitability_score = self._calculate_agent_profitability_score(agent_id)
        
        recommendations = self._generate_agent_recommendations(
            agent_id, transaction_success_rate, avg_response_time,
            data_quality_score, collaboration_score, resource_utilization
        )
        
        return AgentEfficiencyReport(
            agent_id=agent_id,
            agent_type=agent.agent_type.value,
            transaction_success_rate=transaction_success_rate,
            avg_response_time=avg_response_time,
            data_quality_score=data_quality_score,
            collaboration_score=collaboration_score,
            resource_utilization=resource_utilization,
            profitability_score=profitability_score,
            recommendations=recommendations
        )
    
    def _calculate_agent_transaction_success_rate(self, agent_id: str) -> float:
        """Calculate transaction success rate for an agent"""
        agent_transactions = [
            t for t in self.transaction_times
            if t["buyer_id"] == agent_id or t["seller_id"] == agent_id
        ]
        
        if not agent_transactions:
            return 1.0
        
        successful = sum(1 for t in agent_transactions if t["success"])
        return successful / len(agent_transactions)
    
    def _calculate_agent_avg_response_time(self, agent_id: str) -> float:
        """Calculate average response time for an agent"""
        agent_responses = [
            r["duration"] for r in self.response_times
            if r["agent_id"] == agent_id
        ]
        
        return statistics.mean(agent_responses) if agent_responses else 0.0
    
    def _calculate_agent_data_quality_score(self, agent_id: str) -> float:
        """Calculate data quality score for an agent"""
        # This is a simplified metric - in practice would analyze data accuracy,
        # completeness, timeliness, etc.
        agent_metrics = [
            m for m in self.metrics_history
            if m.agent_id == agent_id and m.category == "data_quality"
        ]
        
        if not agent_metrics:
            return 0.8  # Default score
        
        quality_scores = [m.value for m in agent_metrics]
        return statistics.mean(quality_scores)
    
    def _calculate_agent_collaboration_score(self, agent_id: str) -> float:
        """Calculate collaboration score for an agent"""
        # Score based on number of unique trading partners and transaction volume
        unique_partners = set()
        total_interactions = 0
        
        if agent_id in self.collaboration_matrix:
            for partner, data in self.collaboration_matrix[agent_id].items():
                unique_partners.add(partner)
                total_interactions += data["count"]
        
        # Also check incoming transactions
        for buyer_id, partners in self.collaboration_matrix.items():
            if agent_id in partners:
                unique_partners.add(buyer_id)
                total_interactions += partners[agent_id]["count"]
        
        # Normalize scores
        partner_score = min(1.0, len(unique_partners) / 5.0)  # Max 5 partners
        interaction_score = min(1.0, total_interactions / 50.0)  # Max 50 interactions
        
        return (partner_score + interaction_score) / 2.0
    
    def _calculate_agent_resource_utilization(self, agent_id: str) -> float:
        """Calculate resource utilization for an agent"""
        if agent_id not in message_bus.agents:
            return 0.0
        
        agent = message_bus.agents[agent_id]
        
        # Simple utilization based on activity level
        agent_activities = self.agent_activity_log.get(agent_id, [])
        current_time = datetime.now()
        recent_activities = [
            a for a in agent_activities
            if (current_time - a["timestamp"]).total_seconds() < 3600  # Last hour
        ]
        
        # Normalize to expected activity level per agent type
        expected_activities = {
            AgentType.SENSOR: 20,      # 20 activities per hour
            AgentType.PREDICTION: 15,  # 15 activities per hour
            AgentType.RESOURCE: 10,    # 10 activities per hour
            AgentType.MARKET: 8        # 8 activities per hour
        }
        
        expected = expected_activities.get(agent.agent_type, 10)
        return min(1.0, len(recent_activities) / expected)
    
    def _calculate_agent_profitability_score(self, agent_id: str) -> float:
        """Calculate profitability score for an agent"""
        if agent_id not in message_bus.agents:
            return 0.0
        
        agent = message_bus.agents[agent_id]
        
        # Calculate net profit from transactions
        total_income = 0.0
        total_expenses = 0.0
        
        for transaction in self.transaction_times:
            if transaction["seller_id"] == agent_id:
                total_income += transaction["value"]
            elif transaction["buyer_id"] == agent_id:
                total_expenses += transaction["value"]
        
        if total_income + total_expenses == 0:
            return 0.5  # Neutral score if no transactions
        
        net_profit = total_income - total_expenses
        profit_margin = net_profit / (total_income + total_expenses)
        
        # Normalize to 0-1 score
        return max(0.0, min(1.0, (profit_margin + 1.0) / 2.0))
    
    def _generate_agent_recommendations(
        self,
        agent_id: str,
        transaction_success_rate: float,
        avg_response_time: float,
        data_quality_score: float,
        collaboration_score: float,
        resource_utilization: float
    ) -> List[str]:
        """Generate optimization recommendations for an agent"""
        recommendations = []
        
        if transaction_success_rate < 0.8:
            recommendations.append(
                "Improve transaction success rate by enhancing negotiation strategies"
            )
        
        if avg_response_time > 5.0:
            recommendations.append(
                "Optimize response time by implementing more efficient data processing"
            )
        
        if data_quality_score < 0.7:
            recommendations.append(
                "Enhance data quality through better sensor calibration and validation"
            )
        
        if collaboration_score < 0.6:
            recommendations.append(
                "Increase collaboration by engaging with more trading partners"
            )
        
        if resource_utilization < 0.5:
            recommendations.append(
                "Improve resource utilization by increasing activity frequency"
            )
        elif resource_utilization > 0.9:
            recommendations.append(
                "Consider load balancing to prevent resource over-utilization"
            )
        
        if not recommendations:
            recommendations.append("Agent performance is optimal - maintain current strategies")
        
        return recommendations
    
    def generate_system_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive system performance report"""
        current_snapshot = self.take_system_snapshot()
        
        # Calculate trends
        performance_trends = self._calculate_performance_trends()
        
        # Benchmark comparisons
        benchmark_comparison = self._compare_against_benchmarks()
        
        # Top performing agents
        top_agents = self._identify_top_performing_agents()
        
        # System recommendations
        system_recommendations = self._generate_system_recommendations()
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "evaluation_period": {
                "start": self.evaluation_start_time.isoformat(),
                "duration_hours": (datetime.now() - self.evaluation_start_time).total_seconds() / 3600
            },
            "current_status": {
                "total_agents": current_snapshot.total_agents,
                "online_agents": current_snapshot.online_agents,
                "system_load": current_snapshot.system_load,
                "success_rate": current_snapshot.success_rate,
                "avg_response_time": current_snapshot.response_time_avg,
                "data_freshness": current_snapshot.data_freshness_score
            },
            "performance_trends": performance_trends,
            "benchmark_comparison": benchmark_comparison,
            "top_performing_agents": top_agents,
            "system_recommendations": system_recommendations,
            "total_metrics_collected": len(self.metrics_history),
            "total_transactions_processed": len(self.transaction_times),
            "error_summary": self.error_counts
        }
        
        return report
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(self.system_snapshots) < 2:
            return {"status": "insufficient_data"}
        
        recent_snapshots = self.system_snapshots[-10:]  # Last 10 snapshots
        
        # Calculate trends
        response_time_trend = self._calculate_metric_trend(
            [s.response_time_avg for s in recent_snapshots]
        )
        
        success_rate_trend = self._calculate_metric_trend(
            [s.success_rate for s in recent_snapshots]
        )
        
        system_load_trend = self._calculate_metric_trend(
            [s.system_load for s in recent_snapshots]
        )
        
        return {
            "response_time": {
                "trend": response_time_trend,
                "current": recent_snapshots[-1].response_time_avg,
                "change_percent": self._calculate_percent_change(
                    recent_snapshots[0].response_time_avg,
                    recent_snapshots[-1].response_time_avg
                )
            },
            "success_rate": {
                "trend": success_rate_trend,
                "current": recent_snapshots[-1].success_rate,
                "change_percent": self._calculate_percent_change(
                    recent_snapshots[0].success_rate,
                    recent_snapshots[-1].success_rate
                )
            },
            "system_load": {
                "trend": system_load_trend,
                "current": recent_snapshots[-1].system_load,
                "change_percent": self._calculate_percent_change(
                    recent_snapshots[0].system_load,
                    recent_snapshots[-1].system_load
                )
            }
        }
    
    def _calculate_metric_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a metric"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression to determine trend
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_percent_change(self, old_value: float, new_value: float) -> float:
        """Calculate percent change between two values"""
        if old_value == 0:
            return 0.0 if new_value == 0 else 100.0
        
        return ((new_value - old_value) / old_value) * 100.0
    
    def _compare_against_benchmarks(self) -> Dict[str, Any]:
        """Compare current performance against benchmarks"""
        if not self.system_snapshots:
            return {"status": "no_data"}
        
        current = self.system_snapshots[-1]
        
        comparisons = {}
        
        # Response time comparison
        avg_response_time = current.response_time_avg
        response_time_target = statistics.mean(self.benchmark_data["response_time_targets"].values())
        
        comparisons["response_time"] = {
            "current": avg_response_time,
            "target": response_time_target,
            "performance": "good" if avg_response_time <= response_time_target else "needs_improvement",
            "percent_difference": self._calculate_percent_change(response_time_target, avg_response_time)
        }
        
        # Success rate comparison
        success_rate_target = self.benchmark_data["success_rate_targets"]["system_uptime"]
        
        comparisons["success_rate"] = {
            "current": current.success_rate,
            "target": success_rate_target,
            "performance": "good" if current.success_rate >= success_rate_target else "needs_improvement",
            "percent_difference": self._calculate_percent_change(success_rate_target, current.success_rate)
        }
        
        return comparisons
    
    def _identify_top_performing_agents(self) -> List[Dict[str, Any]]:
        """Identify top performing agents"""
        agent_scores = []
        
        for agent_id in message_bus.agents.keys():
            try:
                efficiency_report = self.generate_agent_efficiency_report(agent_id)
                
                # Calculate composite score
                composite_score = (
                    efficiency_report.transaction_success_rate * 0.25 +
                    (1.0 - min(1.0, efficiency_report.avg_response_time / 10.0)) * 0.20 +
                    efficiency_report.data_quality_score * 0.20 +
                    efficiency_report.collaboration_score * 0.20 +
                    efficiency_report.profitability_score * 0.15
                )
                
                agent_scores.append({
                    "agent_id": agent_id,
                    "agent_type": efficiency_report.agent_type,
                    "composite_score": composite_score,
                    "transaction_success_rate": efficiency_report.transaction_success_rate,
                    "collaboration_score": efficiency_report.collaboration_score,
                    "profitability_score": efficiency_report.profitability_score
                })
            except Exception as e:
                logger.error(f"Error evaluating agent {agent_id}: {e}")
        
        # Sort by composite score
        agent_scores.sort(key=lambda x: x["composite_score"], reverse=True)
        
        return agent_scores[:5]  # Top 5 agents
    
    def _generate_system_recommendations(self) -> List[str]:
        """Generate system-wide optimization recommendations"""
        recommendations = []
        
        if not self.system_snapshots:
            return ["Insufficient data for recommendations"]
        
        current = self.system_snapshots[-1]
        
        if current.success_rate < 0.9:
            recommendations.append("Improve system reliability through better error handling")
        
        if current.response_time_avg > 3.0:
            recommendations.append("Optimize system performance through caching and load balancing")
        
        if current.system_load > 0.8:
            recommendations.append("Consider scaling up resources to handle high system load")
        
        if current.data_freshness_score < 0.7:
            recommendations.append("Implement more frequent data collection cycles")
        
        # Analyze agent distribution
        agent_types = {}
        for agent in message_bus.agents.values():
            agent_type = agent.agent_type.value
            agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
        
        if agent_types.get("sensor", 0) < 3:
            recommendations.append("Consider adding more sensor agents for better data coverage")
        
        if not recommendations:
            recommendations.append("System performance is optimal - maintain current configuration")
        
        return recommendations
    
    def export_metrics_to_file(self, filepath: str):
        """Export all collected metrics to a JSON file"""
        export_data = {
            "evaluation_period": {
                "start": self.evaluation_start_time.isoformat(),
                "end": datetime.now().isoformat()
            },
            "metrics": [asdict(metric) for metric in self.metrics_history],
            "system_snapshots": [asdict(snapshot) for snapshot in self.system_snapshots],
            "transaction_history": self.transaction_times,
            "collaboration_matrix": self.collaboration_matrix,
            "error_counts": self.error_counts
        }
        
        # Convert datetime objects to ISO format
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=convert_datetime)
        
        logger.info(f"Metrics exported to {filepath}")

# Global evaluator instance
agrimind_evaluator = AgriMindEvaluator()