"""Cross-board analytics for insights across multiple Monday.com boards"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class CrossBoardAnalytics:
    """Analyze data across multiple Monday.com boards and datasets"""

    @staticmethod
    def correlate_deals_to_workorders(deals: pd.DataFrame, work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Correlate deals to work orders
        
        Args:
            deals: Deals DataFrame
            work_orders: Work orders DataFrame
            
        Returns:
            Correlation analysis
        """
        if deals.empty or work_orders.empty:
            return {}

        correlation = {
            "total_deals": len(deals),
            "total_work_orders": len(work_orders),
            "deal_to_workorder_ratio": 0.0,
            "correlation_strength": "unknown"
        }

        try:
            ratio = len(deals) / max(len(work_orders), 1)
            correlation["deal_to_workorder_ratio"] = round(ratio, 2)

            # Assess correlation strength
            if ratio < 0.3:
                correlation["correlation_strength"] = "loose"
            elif ratio < 1:
                correlation["correlation_strength"] = "moderate"
            else:
                correlation["correlation_strength"] = "tight"

        except Exception as e:
            logger.error(f"Error calculating deal-to-workorder correlation: {str(e)}")

        return correlation

    @staticmethod
    def analyze_sector_consistency(deals: pd.DataFrame, work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze sector distribution consistency across boards
        
        Args:
            deals: Deals DataFrame
            work_orders: Work orders DataFrame
            
        Returns:
            Sector consistency analysis
        """
        consistency = {
            "deal_sectors": {},
            "workorder_sectors": {},
            "sector_alignment": {}
        }

        try:
            # Get sector distribution from deals
            if not deals.empty and "Sector/service" in deals.columns:
                deal_sectors = deals["Sector/service"].value_counts().to_dict()
                consistency["deal_sectors"] = {k: int(v) for k, v in deal_sectors.items() if pd.notna(k)}

            # Get sector distribution from work orders
            if not work_orders.empty and "Sector" in work_orders.columns:
                wo_sectors = work_orders["Sector"].value_counts().to_dict()
                consistency["workorder_sectors"] = {k: int(v) for k, v in wo_sectors.items() if pd.notna(k)}

            # Calculate alignment
            all_sectors = set(consistency["deal_sectors"].keys()) | set(consistency["workorder_sectors"].keys())
            for sector in all_sectors:
                deal_count = consistency["deal_sectors"].get(sector, 0)
                wo_count = consistency["workorder_sectors"].get(sector, 0)
                consistency["sector_alignment"][sector] = {
                    "deals": deal_count,
                    "work_orders": wo_count,
                    "ratio": round(deal_count / max(wo_count, 1), 2)
                }

        except Exception as e:
            logger.error(f"Error analyzing sector consistency: {str(e)}")

        return consistency

    @staticmethod
    def analyze_owner_performance_cross_board(deals: pd.DataFrame, work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze owner/personnel performance across both boards
        
        Args:
            deals: Deals DataFrame
            work_orders: Work orders DataFrame
            
        Returns:
            Cross-board owner performance
        """
        performance = {
            "deal_owners": {},
            "workorder_owners": {},
            "shared_owners": []
        }

        try:
            # Analyze deal owners
            if not deals.empty and "Owner code" in deals.columns:
                owners = deals["Owner code"].value_counts().to_dict()
                for owner, count in owners.items():
                    if pd.notna(owner):
                        performance["deal_owners"][str(owner)] = int(count)

            # Analyze work order owners
            if not work_orders.empty and "BD/KAM Personnel code" in work_orders.columns:
                owners = work_orders["BD/KAM Personnel code"].value_counts().to_dict()
                for owner, count in owners.items():
                    if pd.notna(owner):
                        performance["workorder_owners"][str(owner)] = int(count)

            # Find shared owners
            deal_owner_set = set(performance["deal_owners"].keys())
            wo_owner_set = set(performance["workorder_owners"].keys())
            performance["shared_owners"] = list(deal_owner_set & wo_owner_set)

        except Exception as e:
            logger.error(f"Error analyzing owner performance: {str(e)}")

        return performance

    @staticmethod
    def calculate_pipeline_to_execution_ratio(deals: pd.DataFrame, work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate how well pipeline translates to execution
        
        Args:
            deals: Deals DataFrame
            work_orders: Work orders DataFrame
            
        Returns:
            Pipeline to execution metrics
        """
        metrics = {
            "pipeline_conversion_rate": 0.0,
            "pipeline_value": 0.0,
            "execution_value": 0.0,
            "execution_rate": 0.0
        }

        try:
            # Calculate pipeline size
            if not deals.empty:
                try:
                    pipeline_value = pd.to_numeric(
                        deals.get("Masked Deal value", []), errors='coerce'
                    ).sum()
                    metrics["pipeline_value"] = round(pipeline_value, 2)

                    # Count won deals as converted
                    won_deals = sum(
                        1 for status in deals.get("Deal Status", [])
                        if str(status).lower() in ["won", "project completed"]
                    )
                    total_deals = len(deals)
                    conversion_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
                    metrics["pipeline_conversion_rate"] = round(conversion_rate, 2)
                except:
                    pass

            # Calculate execution metrics
            if not work_orders.empty:
                try:
                    execution_value = pd.to_numeric(
                        work_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), 
                        errors='coerce'
                    ).sum()
                    metrics["execution_value"] = round(execution_value, 2)

                    # Execution rate
                    completed = sum(
                        1 for status in work_orders.get("Execution Status", [])
                        if str(status).lower() in ["completed", "executed until current month"]
                    )
                    total_projects = len(work_orders)
                    execution_rate = (completed / total_projects * 100) if total_projects > 0 else 0
                    metrics["execution_rate"] = round(execution_rate, 2)
                except:
                    pass

        except Exception as e:
            logger.error(f"Error calculating pipeline-to-execution ratio: {str(e)}")

        return metrics

    @staticmethod
    def generate_cross_board_summary(deals: pd.DataFrame, work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive cross-board summary
        
        Args:
            deals: Deals DataFrame
            work_orders: Work orders DataFrame
            
        Returns:
            Cross-board summary
        """
        return {
            "deal_workorder_correlation": CrossBoardAnalytics.correlate_deals_to_workorders(deals, work_orders),
            "sector_consistency": CrossBoardAnalytics.analyze_sector_consistency(deals, work_orders),
            "owner_performance": CrossBoardAnalytics.analyze_owner_performance_cross_board(deals, work_orders),
            "pipeline_execution": CrossBoardAnalytics.calculate_pipeline_to_execution_ratio(deals, work_orders),
            "summary": {
                "total_value_in_deals": len(deals),
                "total_projects_in_execution": len(work_orders),
                "health_status": "balanced" if len(deals) > 0 and len(work_orders) > 0 else "incomplete"
            }
        }

