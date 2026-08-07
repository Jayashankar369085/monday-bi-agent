"""Operational analytics for work orders and project execution"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OperationsAnalytics:
    """Analyze work orders and project execution"""

    @staticmethod
    def analyze_project_execution(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze project execution status
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Execution metrics
        """
        if work_orders.empty:
            return {}

        statuses = work_orders.get("Execution Status", [])
        status_counts = statuses.value_counts().to_dict() if len(statuses) > 0 else {}

        completion_rate = 0
        if len(statuses) > 0:
            completed = sum(1 for s in statuses if str(s).lower() in ["completed", "executed until current month"])
            completion_rate = (completed / len(statuses) * 100)

        # Calculate total project value
        try:
            total_value = pd.to_numeric(work_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
        except:
            total_value = 0

        return {
            "total_projects": len(work_orders),
            "total_project_value": total_value,
            "execution_statuses": status_counts,
            "completion_rate": round(completion_rate, 2),
            "completed_projects": sum(1 for s in statuses if str(s).lower() == "completed"),
            "ongoing_projects": sum(1 for s in statuses if str(s).lower() == "ongoing" or str(s).lower() == "executed until current month"),
            "not_started_projects": sum(1 for s in statuses if str(s).lower() == "not started"),
            "paused_projects": sum(1 for s in statuses if str(s).lower() in ["paused", "pause / struck", "stuck"]),
        }

    @staticmethod
    def analyze_operational_by_sector(work_orders: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze operations by sector
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Sector-wise operational metrics
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
                sector_value = pd.to_numeric(sector_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
            except:
                sector_value = 0

            completed = sum(1 for status in sector_orders.get("Execution Status", []) if str(status).lower() in ["completed", "executed until current month"])
            total = len(sector_orders)

            result[str(sector)] = {
                "project_count": total,
                "total_value": sector_value,
                "average_value": sector_value / total if total > 0 else 0,
                "completed_count": completed,
                "completion_rate": (completed / total * 100) if total > 0 else 0,
            }

        return result

    @staticmethod
    def analyze_timeline_performance(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze project delivery timeline performance
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Timeline metrics
        """
        if work_orders.empty:
            return {}

        on_time = 0
        delayed = 0
        not_completed = 0

        for idx, row in work_orders.iterrows():
            try:
                probable_end = pd.to_datetime(row.get("Probable End Date"))
                delivery_date = row.get("Data Delivery Date")
                
                if delivery_date:
                    delivery_date = pd.to_datetime(delivery_date)
                    if delivery_date <= probable_end:
                        on_time += 1
                    else:
                        delayed += 1
                else:
                    # Not yet delivered
                    not_completed += 1
            except:
                pass

        total = on_time + delayed + not_completed
        on_time_rate = (on_time / total * 100) if total > 0 else 0

        return {
            "total_projects_analyzed": total,
            "on_time_projects": on_time,
            "delayed_projects": delayed,
            "not_delivered": not_completed,
            "on_time_delivery_rate": round(on_time_rate, 2),
        }

    @staticmethod
    def identify_delayed_projects(work_orders: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identify projects that are delayed
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            List of delayed projects
        """
        delayed_projects = []

        for idx, row in work_orders.iterrows():
            project_name = row.get("Deal name masked", f"Project {idx}")
            status = row.get("Execution Status", "Unknown")

            try:
                probable_end = pd.to_datetime(row.get("Probable End Date"))
                today = datetime.now()

                # Check if project should be completed but isn't
                if str(status).lower() not in ["completed", "executed until current month"] and probable_end < today:
                    delivery_date = row.get("Data Delivery Date")
                    if delivery_date:
                        delivery_date = pd.to_datetime(delivery_date)
                        days_late = (delivery_date - probable_end).days
                    else:
                        days_late = (today - probable_end).days

                    delayed_projects.append({
                        "project_name": project_name,
                        "status": status,
                        "probable_end_date": probable_end.strftime("%Y-%m-%d"),
                        "days_overdue": days_late,
                        "sector": row.get("Sector", "Unknown"),
                    })
            except:
                pass

        return delayed_projects

    @staticmethod
    def get_team_workload(work_orders: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze team workload distribution
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Team workload metrics
        """
        if work_orders.empty:
            return {}

        bd_personnel = work_orders.get("BD/KAM Personnel code", [])
        if len(bd_personnel) == 0:
            return {}

        result = {}
        for person in bd_personnel.unique():
            if pd.isna(person):
                continue

            person_orders = work_orders[work_orders.get("BD/KAM Personnel code", []) == person]
            
            try:
                person_value = pd.to_numeric(person_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
            except:
                person_value = 0

            completed = sum(1 for status in person_orders.get("Execution Status", []) if str(status).lower() == "completed")
            total = len(person_orders)

            result[str(person)] = {
                "assigned_projects": total,
                "total_value": person_value,
                "average_value": person_value / total if total > 0 else 0,
                "completed_projects": completed,
                "completion_rate": (completed / total * 100) if total > 0 else 0,
            }

        return result

    @staticmethod
    def analyze_project_types(work_orders: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Analyze projects by type of work
        
        Args:
            work_orders: Work orders DataFrame
            
        Returns:
            Analysis by work type
        """
        if work_orders.empty:
            return {}

        work_types = work_orders.get("Type of Work", [])
        if len(work_types) == 0:
            return {}

        result = {}
        for work_type in work_types.unique():
            if pd.isna(work_type):
                continue

            type_orders = work_orders[work_orders.get("Type of Work", []) == work_type]
            
            try:
                type_value = pd.to_numeric(type_orders.get("Amount in Rupees (Excl of GST) (Masked)", []), errors='coerce').sum()
            except:
                type_value = 0

            completed = sum(1 for status in type_orders.get("Execution Status", []) if str(status).lower() == "completed")
            total = len(type_orders)

            result[str(work_type)] = {
                "project_count": total,
                "total_value": type_value,
                "average_value": type_value / total if total > 0 else 0,
                "completed_count": completed,
                "completion_rate": (completed / total * 100) if total > 0 else 0,
            }

        return result
