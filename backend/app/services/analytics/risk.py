"""Risk analytics for identifying business risks and mitigation opportunities"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class RiskAnalytics:
    """Analyze business risks from operational and financial data"""

    @staticmethod
    def identify_revenue_risks(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify revenue-related risks
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Revenue risk assessment
        """
        if work_orders.empty:
            return {}

        risks = {
            "identified_risks": [],
            "risk_score": 0.0,
            "high_priority": []
        }

        # Check for delayed projects affecting revenue
        try:
            delayed_count = sum(
                1 for status in work_orders.get("Execution Status", [])
                if str(status).lower() in ["paused", "on hold", "stuck"]
            )
            if delayed_count > 0:
                risks["identified_risks"].append({
                    "type": "delayed_projects",
                    "count": delayed_count,
                    "impact": "revenue delay"
                })
        except:
            pass

        # Check for collection issues
        try:
            partial_collection = sum(
                1 for status in work_orders.get("Collection status", [])
                if str(status).lower() == "partially collected" or pd.isna(status)
            )
            if partial_collection > 0:
                risks["high_priority"].append({
                    "type": "collection_risk",
                    "count": partial_collection,
                    "action": "Follow up on outstanding receivables"
                })
        except:
            pass

        # Calculate risk score
        risks["risk_score"] = min(100, len(risks["identified_risks"]) * 20)
        return risks

    @staticmethod
    def identify_pipeline_risks(deals: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify pipeline risks
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            Pipeline risk assessment
        """
        if deals.empty:
            return {}

        risks = {
            "identified_risks": [],
            "risk_score": 0.0,
            "stuck_deals": 0,
            "at_risk_deals": 0
        }

        try:
            # Count deals stuck in early stages
            stuck = sum(
                1 for stage in deals.get("Deal Stage", [])
                if str(stage).lower() in ["a. lead generated", "b. sales qualified leads"]
                and len(deals) > 100  # More than 100 days old assumption
            )
            risks["stuck_deals"] = stuck

            # Count low probability deals
            low_prob = sum(
                1 for prob in deals.get("Closure Probability", [])
                if str(prob).lower() == "low"
            )
            risks["at_risk_deals"] = low_prob

            if stuck > 0:
                risks["identified_risks"].append({
                    "type": "stuck_deals",
                    "count": stuck,
                    "action": "Review and re-engage stalled opportunities"
                })

            if low_prob > 0:
                risks["identified_risks"].append({
                    "type": "low_closure_probability",
                    "count": low_prob,
                    "action": "Increase follow-up on low-probability deals"
                })

        except Exception as e:
            logger.error(f"Error analyzing pipeline risks: {str(e)}")

        risks["risk_score"] = min(100, (risks["stuck_deals"] + risks["at_risk_deals"]) * 10)
        return risks

    @staticmethod
    def identify_operational_risks(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify operational risks
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Operational risk assessment
        """
        if work_orders.empty:
            return {}

        risks = {
            "identified_risks": [],
            "risk_score": 0.0,
            "critical_items": []
        }

        try:
            # Check on-time delivery rate
            on_time = sum(
                1 for status in work_orders.get("Execution Status", [])
                if str(status).lower() in ["completed", "executed until current month"]
            )
            total = len(work_orders)
            on_time_rate = (on_time / total * 100) if total > 0 else 0

            if on_time_rate < 70:
                risks["identified_risks"].append({
                    "type": "low_on_time_delivery",
                    "current_rate": round(on_time_rate, 1),
                    "target_rate": 90,
                    "action": "Improve project timeline management"
                })

            # Check for resource bottlenecks
            bd_personnel = work_orders.get("BD/KAM Personnel code", [])
            if len(bd_personnel) > 0:
                personnel_count = bd_personnel.nunique()
                avg_projects = total / max(personnel_count, 1)
                if avg_projects > 20:
                    risks["identified_risks"].append({
                        "type": "resource_overallocation",
                        "avg_projects_per_person": round(avg_projects, 1),
                        "action": "Consider resource augmentation"
                    })

        except Exception as e:
            logger.error(f"Error analyzing operational risks: {str(e)}")

        risks["risk_score"] = min(100, len(risks["identified_risks"]) * 25)
        return risks

    @staticmethod
    def get_overall_risk_score(revenue_risks: Dict[str, Any], 
                              pipeline_risks: Dict[str, Any], 
                              operational_risks: Dict[str, Any]) -> float:
        """
        Calculate overall business risk score
        
        Args:
            revenue_risks: Revenue risk assessment
            pipeline_risks: Pipeline risk assessment
            operational_risks: Operational risk assessment
            
        Returns:
            Overall risk score (0-100)
        """
        scores = [
            revenue_risks.get("risk_score", 0),
            pipeline_risks.get("risk_score", 0),
            operational_risks.get("risk_score", 0)
        ]
        
        # Average of all risks
        return sum(scores) / len(scores) if scores else 0.0

    @staticmethod
    def generate_risk_report(work_orders: pd.DataFrame, deals: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive risk report
        
        Args:
            work_orders: Work orders DataFrame
            deals: Deals DataFrame
            
        Returns:
            Comprehensive risk report
        """
        revenue_risks = RiskAnalytics.identify_revenue_risks(work_orders)
        pipeline_risks = RiskAnalytics.identify_pipeline_risks(deals)
        operational_risks = RiskAnalytics.identify_operational_risks(work_orders)

        overall_score = RiskAnalytics.get_overall_risk_score(
            revenue_risks, pipeline_risks, operational_risks
        )

        return {
            "overall_risk_score": round(overall_score, 2),
            "risk_level": "high" if overall_score >= 70 else "medium" if overall_score >= 40 else "low",
            "revenue_risks": revenue_risks,
            "pipeline_risks": pipeline_risks,
            "operational_risks": operational_risks,
            "all_critical_items": (
                revenue_risks.get("high_priority", []) +
                pipeline_risks.get("identified_risks", []) +
                operational_risks.get("critical_items", [])
            )[:10]  # Top 10 issues
        }

