"""Date cleaning and normalization utilities"""

import logging
from datetime import datetime
from typing import Any, Optional
import re

logger = logging.getLogger(__name__)


class DateCleaner:
    """Handles date parsing and normalization from various formats"""

    # Common date formats
    DATE_FORMATS = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
    ]

    @staticmethod
    def clean_date(value: Any) -> Optional[datetime]:
        """
        Parse and clean a date value
        
        Args:
            value: Date value in various formats
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not value or value == "":
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

            # Try each format
            for fmt in DateCleaner.DATE_FORMATS:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

            # Try ISO format
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass

            logger.warning(f"Could not parse date: {value}")
            return None

        return None

    @staticmethod
    def format_date(value: Any, fmt: str = "%Y-%m-%d") -> Optional[str]:
        """
        Format a date value to a standard format
        
        Args:
            value: Date value
            fmt: Target format string
            
        Returns:
            Formatted date string or None
        """
        dt = DateCleaner.clean_date(value)
        if dt:
            return dt.strftime(fmt)
        return None

    @staticmethod
    def get_month_year(value: Any) -> Optional[str]:
        """Get month-year from date"""
        dt = DateCleaner.clean_date(value)
        if dt:
            return dt.strftime("%B %Y")
        return None

    @staticmethod
    def is_past_date(value: Any) -> bool:
        """Check if date is in the past"""
        dt = DateCleaner.clean_date(value)
        if dt:
            return dt < datetime.now()
        return False

    @staticmethod
    def is_future_date(value: Any) -> bool:
        """Check if date is in the future"""
        dt = DateCleaner.clean_date(value)
        if dt:
            return dt > datetime.now()
        return False

    @staticmethod
    def get_quarter_from_date(value: Any) -> Optional[str]:
        """Get quarter and year from date"""
        dt = DateCleaner.clean_date(value)
        if dt:
            quarter = (dt.month - 1) // 3 + 1
            return f"Q{quarter} {dt.year}"
        return None
