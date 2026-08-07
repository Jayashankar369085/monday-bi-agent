"""Data validation and quality checking utilities"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates and checks data quality"""

    @staticmethod
    def validate_required_fields(item: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if required fields are present and non-empty
        
        Args:
            item: Data item
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        missing = []
        for field in required_fields:
            value = item.get(field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing.append(field)
        
        return len(missing) == 0, missing

    @staticmethod
    def get_data_quality_score(item: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0-100)
        
        Args:
            item: Data item
            
        Returns:
            Quality score as percentage
        """
        if not item:
            return 0.0

        total_fields = len(item)
        if total_fields == 0:
            return 0.0

        non_null_fields = sum(1 for v in item.values() if v is not None and v != "")
        return (non_null_fields / total_fields) * 100

    @staticmethod
    def get_missing_fields_count(item: Dict[str, Any]) -> int:
        """Count missing/null fields"""
        return sum(1 for v in item.values() if v is None or v == "")

    @staticmethod
    def identify_data_quality_issues(item: Dict[str, Any]) -> List[str]:
        """
        Identify common data quality issues
        
        Args:
            item: Data item
            
        Returns:
            List of identified issues
        """
        issues = []

        # Check for empty values
        null_count = sum(1 for v in item.values() if v is None or v == "")
        if null_count > len(item) * 0.5:
            issues.append(f"High number of empty fields ({null_count}/{len(item)})")

        # Check for duplicate-like patterns
        for key, value in item.items():
            if isinstance(value, str):
                # Check for masked/placeholder data
                if "masked" in value.lower() or "update required" in value.lower():
                    issues.append(f"Masked or incomplete data in '{key}'")

                # Check for error values
                if "error" in value.lower():
                    issues.append(f"Error value found in '{key}': {value}")

        return issues

    @staticmethod
    def filter_valid_items(items: List[Dict[str, Any]], min_quality_score: float = 30) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Filter items by quality threshold
        
        Args:
            items: List of data items
            min_quality_score: Minimum quality score (0-100)
            
        Returns:
            Tuple of (valid_items, filtered_out_items)
        """
        valid_items = []
        filtered_out = []

        for item in items:
            score = DataValidator.get_data_quality_score(item)
            if score >= min_quality_score:
                valid_items.append(item)
            else:
                filtered_out.append(f"Item skipped (quality: {score:.0f}%)")

        return valid_items, filtered_out

    @staticmethod
    def validate_numeric_range(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
        """
        Validate numeric value is within range
        
        Args:
            value: Value to validate
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            True if valid, False otherwise
        """
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def sanitize_string(value: Any) -> Optional[str]:
        """
        Sanitize string value
        
        Args:
            value: String value
            
        Returns:
            Sanitized string or None
        """
        if not value:
            return None

        if not isinstance(value, str):
            value = str(value)

        # Strip whitespace
        value = value.strip()

        # Remove extra whitespace
        value = " ".join(value.split())

        return value if value else None

    @staticmethod
    def compare_data_quality(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze data quality across items
        
        Args:
            items: List of data items
            
        Returns:
            Quality analysis report
        """
        if not items:
            return {
                "total_items": 0,
                "avg_quality_score": 0,
                "items_with_issues": 0,
                "common_issues": []
            }

        scores = [DataValidator.get_data_quality_score(item) for item in items]
        all_issues = []
        
        for item in items:
            all_issues.extend(DataValidator.identify_data_quality_issues(item))

        items_with_issues = sum(1 for item in items if DataValidator.identify_data_quality_issues(item))

        # Count common issues
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_items": len(items),
            "avg_quality_score": sum(scores) / len(scores) if scores else 0,
            "items_with_issues": items_with_issues,
            "common_issues": [{"issue": issue, "count": count} for issue, count in common_issues],
            "quality_distribution": {
                "excellent": sum(1 for s in scores if s >= 90),
                "good": sum(1 for s in scores if 70 <= s < 90),
                "fair": sum(1 for s in scores if 50 <= s < 70),
                "poor": sum(1 for s in scores if s < 50),
            }
        }
