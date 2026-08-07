"""Sales pipeline and deal analytics"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class SalesAnalytics:
    """Analyze sales deals and pipeline"""

    @staticmethod
    def analyze_pipeline_health(deals: pd.DataFrame) -> Dict[str, Any]:
        print("\n========== DEAL COLUMN NAMES ==========")
        for col in deals.columns:
            print(col)
        print("=======================================")
        """
        Analyze overall pipeline health
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            Pipeline health metrics
        """
        if deals.empty:
            return {}

        # Count deals by status
        deal_statuses = deals.get("Deal Status", [])
        status_counts = deal_statuses.value_counts().to_dict() if len(deal_statuses) > 0 else {}

        # Calculate total deal value
        try:
            total_value = pd.to_numeric(deals.get("Masked Deal value", []), errors='coerce').sum()
        except:
            total_value = 0

        # Average deal size
        try:
            avg_deal_size = pd.to_numeric(deals.get("Masked Deal value", []), errors='coerce').mean()
        except:
            avg_deal_size = 0

        # Deal stages
        stages = deals.get("Deal Stage", [])
        stage_dist = stages.value_counts().to_dict() if len(stages) > 0 else {}

        # Win rate (if we can detect)
        won_deals = sum(1 for status in deal_statuses if str(status).lower() in ["won", "project completed"])
        total_deals = len(deal_statuses)
        win_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0

        return {
            "total_deals": total_deals,
            "total_pipeline_value": total_value,
            "average_deal_size": avg_deal_size,
            "deal_statuses": status_counts,
            "deal_stages": stage_dist,
            "win_rate_percentage": round(win_rate, 2),
            "open_deals": sum(1 for status in deal_statuses if str(status).lower() == "open"),
            "closed_deals": sum(1 for status in deal_statuses if str(status).lower() in ["won", "closed", "project completed"]),
            "lost_deals": sum(1 for status in deal_statuses if str(status).lower() in ["dead", "lost", "project lost"]),
        }

    @staticmethod
    def analyze_pipeline_by_sector(deals: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze pipeline broken down by sector
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            Pipeline analysis by sector
        """
        if deals.empty:
            return {}

        sectors = deals.get("Sector/service", [])
        if len(sectors) == 0:
            return {}

        result = {}
        for sector in sectors.unique():
            if pd.isna(sector):
                continue

            sector_deals = deals[deals.get("Sector/service", []) == sector]
            
            try:
                sector_value = pd.to_numeric(sector_deals.get("Masked Deal value", []), errors='coerce').sum()
            except:
                sector_value = 0

            won = sum(1 for status in sector_deals.get("Deal Status", []) if str(status).lower() in ["won", "project completed"])
            total = len(sector_deals)

            result[str(sector)] = {
                "deal_count": total,
                "total_value": sector_value,
                "average_value": sector_value / total if total > 0 else 0,
                "win_count": won,
                "win_rate": (won / total * 100) if total > 0 else 0,
            }

        return result

    @staticmethod
    def analyze_deals_by_stage(deals: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze deals progression through sales stages
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            Stage-wise analysis
        """
        if deals.empty:
            return {}

        stages = deals.get("Deal Stage", [])
        if len(stages) == 0:
            return {}

        result = {}
        for stage in stages.unique():
            if pd.isna(stage):
                continue

            stage_deals = deals[deals.get("Deal Stage", []) == stage]
            
            try:
                stage_value = pd.to_numeric(stage_deals.get("Masked Deal value", []), errors='coerce').sum()
            except:
                stage_value = 0

            result[str(stage)] = {
                "deal_count": len(stage_deals),
                "total_value": stage_value,
                "average_value": stage_value / len(stage_deals) if len(stage_deals) > 0 else 0,
            }

        return result

    @staticmethod
    def identify_at_risk_deals(deals: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify deals at risk of being lost
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            List of at-risk deals
        """
        at_risk = []

        for idx, row in deals.iterrows():
            deal_name = row.get("Deal Name", f"Deal {idx}")
            stage = row.get("Deal Stage", "Unknown")
            status = row.get("Deal Status", "Open")
            close_prob = row.get("Closure Probability", "Medium")

            # Flags for at-risk
            is_at_risk = False
            reasons = []

            # Check probability
            if str(close_prob).lower() == "low":
                is_at_risk = True
                reasons.append("Low closure probability")

            # Check if stuck in early stage
            if str(stage).lower() in ["a. lead generated", "b. sales qualified leads"] and status == "On Hold":
                is_at_risk = True
                reasons.append("Stuck in early stage")

            # Check for old created dates
            if "Created Date" in row:
                try:
                    created = pd.to_datetime(row.get("Created Date"))
                    days_old = (datetime.now() - created).days
                    if days_old > 180:  # More than 6 months
                        is_at_risk = True
                        reasons.append(f"No progress in {days_old} days")
                except:
                    pass

            if is_at_risk and reasons:
                at_risk.append({
                    "deal_name": deal_name,
                    "stage": stage,
                    "status": status,
                    "reasons": reasons,
                })

        return at_risk

    @staticmethod
    def forecast_quarterly_revenue(deals: pd.DataFrame, quarter: Optional[str] = None) -> Dict[str, Any]:
        """
        Forecast revenue based on pipeline
        
        Args:
            deals: Deals DataFrame
            quarter: Target quarter (e.g., 'Q1 2025')
            
        Returns:
            Revenue forecast
        """
        if deals.empty:
            return {}

        # Filter to open/active deals
        deal_statuses = deals.get("Deal Status", [])
        open_deals = deals[deal_statuses.isin(["Open", "On Hold"])]

        if open_deals.empty:
            return {}

        try:
            total_value = pd.to_numeric(open_deals.get("Masked Deal value", []), errors='coerce').sum()
        except:
            total_value = 0

        # Simple forecast: count probable closes based on closure probability
        conservative_value = 0
        base_value = 0

        for idx, row in open_deals.iterrows():
            try:
                deal_value = float(row.get("Masked Deal value", 0))
                close_prob = row.get("Closure Probability", "Medium")

                base_value += deal_value

                # Estimate based on probability
                if str(close_prob).lower() == "high":
                    conservative_value += deal_value * 0.7
                elif str(close_prob).lower() == "medium":
                    conservative_value += deal_value * 0.4
                else:  # Low
                    conservative_value += deal_value * 0.1
            except:
                pass

        return {
            "total_pipeline_value": total_value,
            "conservative_forecast": round(conservative_value, 2),
            "aggressive_forecast": round(conservative_value * 1.3, 2),
            "realistic_forecast": round(conservative_value, 2),
        }

    @staticmethod
    def get_owner_performance(deals: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze performance by deal owner/KAM
        
        Args:
            deals: Deals DataFrame
            
        Returns:
            Owner performance metrics
        """
        if deals.empty:
            return {}

        owners = deals.get("Owner code", [])
        if len(owners) == 0:
            return {}

        result = {}
        for owner in owners.unique():
            if pd.isna(owner):
                continue

            owner_deals = deals[deals.get("Owner code", []) == owner]
            
            try:
                owner_value = pd.to_numeric(owner_deals.get("Masked Deal value", []), errors='coerce').sum()
            except:
                owner_value = 0

            won = sum(1 for status in owner_deals.get("Deal Status", []) if str(status).lower() in ["won", "project completed"])
            total = len(owner_deals)

            result[str(owner)] = {
                "total_deals": total,
                "total_value": owner_value,
                "average_value": owner_value / total if total > 0 else 0,
                "won_deals": won,
                "win_rate": (won / total * 100) if total > 0 else 0,
            }

        return result
