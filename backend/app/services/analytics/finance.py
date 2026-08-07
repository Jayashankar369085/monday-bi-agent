"""Financial analytics including revenue, billing, and collections"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class FinanceAnalytics:
    """Analyze financial metrics from work orders"""

    @staticmethod
    def analyze_revenue_metrics(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze revenue metrics
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Revenue metrics
        """
        if work_orders.empty:
            return {}

        # Total billed
        try:
            total_billed = pd.to_numeric(work_orders.get("Billed Value in Rupees (Excl of GST.) (Masked)", []), errors='coerce').sum()
        except:
            total_billed = 0

        # Total collected
        try:
            total_collected = pd.to_numeric(work_orders.get("Collected Amount in Rupees (Incl of GST.) (Masked)", []), errors='coerce').sum()
        except:
            total_collected = 0

        # Total contract value
        try:
            total_contract_value = pd.to_numeric(work_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
        except:
            total_contract_value = 0

        # Calculate collection rate
        collection_rate = 0
        if total_billed > 0:
            collection_rate = (total_collected / total_billed * 100)

        return {
            "total_contract_value": total_contract_value,
            "total_billed": total_billed,
            "total_collected": total_collected,
            "total_receivable": total_contract_value - total_collected,
            "collection_rate_percentage": round(collection_rate, 2),
            "average_billing_value": total_billed / len(work_orders) if len(work_orders) > 0 else 0,
        }

    @staticmethod
    def analyze_revenue_by_sector(work_orders: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze revenue by sector
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Revenue analysis by sector
        """
        if work_orders.empty:
            return {}

        sectors = work_orders.get("Sector", [])
        if len(sectors) == 0:
            return {}

        result = {}
        for sector in sectors.unique():
            if pd.isna(sector):
                continue

            sector_orders = work_orders[work_orders.get("Sector", []) == sector]
            
            try:
                billed = pd.to_numeric(sector_orders.get("Billed Value in Rupees (Excl of GST.) (Masked)", []), errors='coerce').sum()
                collected = pd.to_numeric(sector_orders.get("Collected Amount in Rupees (Incl of GST.) (Masked)", []), errors='coerce').sum()
            except:
                billed = 0
                collected = 0

            collection_rate = (collected / billed * 100) if billed > 0 else 0

            result[str(sector)] = {
                "total_billed": billed,
                "total_collected": collected,
                "collection_rate": round(collection_rate, 2),
                "outstanding": billed - collected,
                "project_count": len(sector_orders),
            }

        return result

    @staticmethod
    def analyze_billing_status(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze billing status of projects
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Billing status metrics
        """
        if work_orders.empty:
            return {}

        billing_statuses = work_orders.get("Billing Status", [])
        status_counts = billing_statuses.value_counts().to_dict() if len(billing_statuses) > 0 else {}

        # Count projects by billing status
        fully_billed = sum(1 for s in billing_statuses if str(s).lower() in ["fully billed", "billed"])
        partially_billed = sum(1 for s in billing_statuses if str(s).lower() == "partially billed")
        not_billed = sum(1 for s in billing_statuses if str(s).lower() in ["not billed yet", "not billable"])
        update_required = sum(1 for s in billing_statuses if str(s).lower() == "update required")

        return {
            "billing_statuses": status_counts,
            "fully_billed_projects": fully_billed,
            "partially_billed_projects": partially_billed,
            "not_billed_projects": not_billed,
            "billing_status_unknown": update_required,
            "billing_completion_rate": round((fully_billed + partially_billed) / len(work_orders) * 100, 2) if len(work_orders) > 0 else 0,
        }

    @staticmethod
    def analyze_collections(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze collection metrics
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Collection metrics
        """
        if work_orders.empty:
            return {}

        collection_statuses = work_orders.get("Collection status", [])
        status_counts = collection_statuses.value_counts().to_dict() if len(collection_statuses) > 0 else {}

        try:
            total_to_collect = pd.to_numeric(work_orders.get("Amount Receivable (Masked)", []), errors='coerce').sum()
        except:
            total_to_collect = 0

        # Priority accounts
        priority_count = sum(1 for p in work_orders.get("AR Priority account", []) if str(p).lower() == "priority")

        return {
            "collection_statuses": status_counts,
            "total_receivable": total_to_collect,
            "priority_receivables": priority_count,
            "partially_collected": sum(1 for s in collection_statuses if str(s).lower() == "partially collected"),
            "fully_collected": sum(1 for s in collection_statuses if str(s).lower() in ["fully collected", "collected"]),
            "not_collected": sum(1 for s in collection_statuses if pd.isna(s) or str(s) == ""),
        }

    @staticmethod
    def analyze_receivables_aging(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze receivables by age
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Aging analysis
        """
        if work_orders.empty:
            return {}

        today = datetime.now()
        current = 0  # 0-30 days
        thirty_plus = 0  # 30-60 days
        sixty_plus = 0  # 60-90 days
        ninety_plus = 0  # 90+ days

        for idx, row in work_orders.iterrows():
            try:
                invoice_date = pd.to_datetime(row.get("Last invoice date"))
                days_old = (today - invoice_date).days

                if days_old <= 30:
                    current += 1
                elif days_old <= 60:
                    thirty_plus += 1
                elif days_old <= 90:
                    sixty_plus += 1
                else:
                    ninety_plus += 1
            except:
                pass

        total = current + thirty_plus + sixty_plus + ninety_plus

        return {
            "current_0_30_days": current,
            "aging_30_60_days": thirty_plus,
            "aging_60_90_days": sixty_plus,
            "aging_90plus_days": ninety_plus,
            "total_aged_receivables": total,
            "percentage_90plus": round((ninety_plus / total * 100), 2) if total > 0 else 0,
        }

    @staticmethod
    def identify_collection_at_risk(work_orders: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify receivables at risk
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            List of at-risk receivables
        """
        at_risk = []

        for idx, row in work_orders.iterrows():
            project_name = row.get("Deal name masked", f"Project {idx}")
            collection_status = row.get("Collection status", "Unknown")
            is_priority = str(row.get("AR Priority account", "")).lower() == "priority"

            reasons = []

            # Check collection status
            if str(collection_status).lower() == "partially collected" or pd.isna(collection_status):
                reasons.append("Not fully collected")

            # Check if priority account
            if is_priority:
                reasons.append("Priority account")

            # Check invoice age
            try:
                invoice_date = pd.to_datetime(row.get("Last invoice date"))
                days_old = (datetime.now() - invoice_date).days
                if days_old > 90:
                    reasons.append(f"Invoice {days_old} days old")
            except:
                pass

            if reasons:
                try:
                    receivable_amount = float(row.get("Amount Receivable (Masked)", 0))
                except:
                    receivable_amount = 0

                at_risk.append({
                    "project": project_name,
                    "receivable_amount": receivable_amount,
                    "reasons": reasons,
                    "collection_status": collection_status,
                })

        return at_risk

    @staticmethod
    def analyze_margin_by_customer(work_orders: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze margins by customer
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Margin analysis by customer
        """
        if work_orders.empty:
            return {}

        customers = work_orders.get("Customer Name Code", [])
        if len(customers) == 0:
            return {}

        result = {}
        for customer in customers.unique():
            if pd.isna(customer):
                continue

            customer_orders = work_orders[work_orders.get("Customer Name Code", []) == customer]
            
            try:
                contract_value = pd.to_numeric(customer_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
                billed = pd.to_numeric(customer_orders.get("Billed Value in Rupees (Excl of GST.) (Masked)", []), errors='coerce').sum()
            except:
                contract_value = 0
                billed = 0

            margin = billed - contract_value
            margin_percentage = (margin / contract_value * 100) if contract_value > 0 else 0

            result[str(customer)] = {
                "contract_value": contract_value,
                "billed_value": billed,
                "margin": margin,
                "margin_percentage": round(margin_percentage, 2),
                "project_count": len(customer_orders),
            }

        return result
