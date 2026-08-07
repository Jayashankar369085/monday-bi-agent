"""Extract business entities from queries and data"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract entities like sectors, customers, deal names from queries"""

    # Entity patterns
    NUMERIC_PATTERN = r'\d+(?:\.\d+)?'
    CURRENCY_PATTERN = r'₹?\d+(?:,\d{3})*(?:\.\d+)?'
    PERCENTAGE_PATTERN = r'\d+(?:\.\d+)?%'

    SECTORS = [
        "mining", "renewables", "powerline", "railways", "construction",
        "dsp", "others", "tender", "security", "aviation", "manufacturing"
    ]

    METRICS = [
        "revenue", "deal", "customer", "project", "work order", "pipeline",
        "collection", "billing", "margin", "growth", "capacity"
    ]

    @staticmethod
    def extract_sectors(query: str) -> List[str]:
        """
        Extract sector names from query
        
        Args:
            query: User query
            
        Returns:
            List of mentioned sectors
        """
        query_lower = query.lower()
        found = []

        for sector in EntityExtractor.SECTORS:
            if sector in query_lower:
                found.append(sector)

        return found

    @staticmethod
    def extract_metrics(query: str) -> List[str]:
        """Extract business metrics from query"""
        query_lower = query.lower()
        found = []

        for metric in EntityExtractor.METRICS:
            if metric in query_lower:
                found.append(metric)

        return found

    @staticmethod
    def extract_numbers(query: str) -> List[float]:
        """Extract numeric values from query"""
        matches = re.findall(EntityExtractor.NUMERIC_PATTERN, query)
        return [float(m) for m in matches]

    @staticmethod
    def extract_currency_amounts(query: str) -> List[float]:
        """Extract currency amounts from query"""
        matches = re.findall(EntityExtractor.CURRENCY_PATTERN, query)
        amounts = []

        for match in matches:
            # Remove currency symbols and commas
            clean = match.replace('₹', '').replace(',', '')
            try:
                amounts.append(float(clean))
            except ValueError:
                pass

        return amounts

    @staticmethod
    def extract_percentages(query: str) -> List[float]:
        """Extract percentage values from query"""
        matches = re.findall(EntityExtractor.PERCENTAGE_PATTERN, query)
        percentages = []

        for match in matches:
            try:
                value = float(match.replace('%', ''))
                percentages.append(value)
            except ValueError:
                pass

        return percentages

    @staticmethod
    def extract_entities(query: str) -> Dict[str, Any]:
        """
        Extract all entities from query
        
        Args:
            query: User query
            
        Returns:
            Dict with extracted entities
        """
        sectors = EntityExtractor.extract_sectors(query)
        metrics = EntityExtractor.extract_metrics(query)
        numbers = EntityExtractor.extract_numbers(query)
        amounts = EntityExtractor.extract_currency_amounts(query)
        percentages = EntityExtractor.extract_percentages(query)

        # Extract time references
        time_refs = EntityExtractor._extract_time_references(query)

        return {
            "sectors": sectors,
            "metrics": metrics,
            "numbers": numbers,
            "amounts": amounts,
            "percentages": percentages,
            "time_references": time_refs,
        }

    @staticmethod
    def _extract_time_references(query: str) -> List[str]:
        """Extract time period references"""
        time_keywords = [
            "today", "yesterday", "this week", "last week", "this month",
            "last month", "this quarter", "last quarter", "this year",
            "last year", "ytd", "monthly", "quarterly", "annually",
            "daily", "weekly", "q1", "q2", "q3", "q4", "january", "february",
            "march", "april", "may", "june", "july", "august", "september",
            "october", "november", "december", "2024", "2025", "2026"
        ]

        query_lower = query.lower()
        found = []

        for keyword in time_keywords:
            if keyword in query_lower:
                found.append(keyword)

        return found

    @staticmethod
    def extract_comparison_entities(query: str) -> Tuple[List[str], List[str]]:
        """
        Extract entities being compared
        
        Args:
            query: User query
            
        Returns:
            Tuple of (left_entities, right_entities)
        """
        # Split by comparison keywords
        comparison_keywords = ["vs", "versus", "compared to", "vs.", "against"]

        for keyword in comparison_keywords:
            if keyword in query.lower():
                parts = query.lower().split(keyword)
                if len(parts) == 2:
                    left = EntityExtractor.extract_sectors(parts[0])
                    right = EntityExtractor.extract_sectors(parts[1])
                    return left or EntityExtractor.extract_metrics(parts[0]), right or EntityExtractor.extract_metrics(parts[1])

        return [], []

    @staticmethod
    def extract_data_entities(data_items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract unique entities from data items
        
        Args:
            data_items: List of data dictionaries
            
        Returns:
            Dict with unique values for key fields
        """
        entities = {
            "customers": set(),
            "sectors": set(),
            "statuses": set(),
            "deal_stages": set(),
            "work_types": set(),
        }

        for item in data_items:
            # Extract customer/deal name
            if "Deal name masked" in item or "name" in item:
                customer = item.get("Deal name masked") or item.get("name")
                if customer:
                    entities["customers"].add(str(customer))

            # Extract sector
            if "Sector" in item:
                sector = item.get("Sector")
                if sector:
                    entities["sectors"].add(str(sector))

            # Extract status
            if "Deal Status" in item:
                status = item.get("Deal Status")
                if status:
                    entities["statuses"].add(str(status))

            if "Execution Status" in item:
                status = item.get("Execution Status")
                if status:
                    entities["statuses"].add(str(status))

            # Extract deal stage
            if "Deal Stage" in item:
                stage = item.get("Deal Stage")
                if stage:
                    entities["deal_stages"].add(str(stage))

            # Extract work type
            if "Type of Work" in item:
                work_type = item.get("Type of Work")
                if work_type:
                    entities["work_types"].add(str(work_type))

        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in entities.items()}
