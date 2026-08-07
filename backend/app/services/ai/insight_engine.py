"""Insight engine for generating business insights from queries and data"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class InsightEngine:
    """Generates business insights from analysis results"""

    @staticmethod
    def extract_key_insights(analysis: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Extract key insights from analysis results
        
        Args:
            analysis: Analysis dictionary with metrics
            limit: Maximum number of insights to extract
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # Extract numerical metrics for insight generation
        for key, value in analysis.items():
            if isinstance(value, (int, float)) and value > 0:
                insights.append({
                    "metric": key.replace("_", " ").title(),
                    "value": value,
                    "type": "numeric"
                })
        
        # Sort by value descending and limit
        insights.sort(key=lambda x: x.get("value", 0), reverse=True)
        return insights[:limit]

    @staticmethod
    def identify_trends(metrics_history: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Identify trends from historical metrics
        
        Args:
            metrics_history: List of metric snapshots over time
            
        Returns:
            Dictionary with trend analysis
        """
        if len(metrics_history) < 2:
            return {"status": "insufficient_data"}
        
        trends = {}
        
        # Compare latest vs previous
        latest = metrics_history[-1]
        previous = metrics_history[-2]
        
        for key in latest:
            if isinstance(latest[key], (int, float)) and isinstance(previous.get(key), (int, float)):
                change = latest[key] - previous[key]
                if change > 0:
                    trends[key] = "increasing"
                elif change < 0:
                    trends[key] = "decreasing"
                else:
                    trends[key] = "stable"
        
        return trends

    @staticmethod
    def calculate_performance_score(metrics: Dict[str, Any]) -> float:
        """
        Calculate overall performance score (0-100)
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            Performance score
        """
        if not metrics:
            return 0.0
        
        scores = []
        
        # Score based on common business metrics
        metric_weights = {
            "win_rate": (50, 1),  # (target_value, weight)
            "completion_rate": (90, 1),
            "collection_rate": (85, 1),
            "on_time_delivery_rate": (95, 1),
        }
        
        for metric_name, (target, weight) in metric_weights.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if isinstance(value, (int, float)):
                    score = min(100, (value / target) * 100) if target > 0 else 0
                    scores.append(score * weight)
        
        # Return average score if any metrics found
        return sum(scores) / len(scores) if scores else 50.0

    @staticmethod
    def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations based on analysis
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for problem areas and suggest actions
        for key, value in analysis.items():
            if isinstance(value, (int, float)):
                if "rate" in key.lower() and value < 50:
                    recommendations.append(f"Improve {key.replace('_', ' ')}: Current {value}% is below target")
                elif "delayed" in key.lower() and value > 5:
                    recommendations.append(f"Address {value} delayed items: Escalate timeline issues")
                elif "at_risk" in key.lower() and value > 0:
                    recommendations.append(f"Manage {value} at-risk items: Proactive intervention needed")
        
        return recommendations[:5]  # Limit to 5 recommendations

