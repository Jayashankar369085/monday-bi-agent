"""Money/currency cleaning and normalization utilities"""

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MoneyCleaner:
    """Handles currency parsing and normalization"""

    @staticmethod
    def clean_currency(value: Any) -> Optional[float]:
        """
        Parse and clean currency values
        
        Args:
            value: Currency value in various formats
            
        Returns:
            Float value or None if parsing fails
        """
        if value is None or value == "":
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

            # Remove currency symbols and other non-numeric characters (except . and -)
            cleaned = re.sub(r'[^\d\.\-,]', '', value)
            # Replace commas with empty string (European format)
            cleaned = cleaned.replace(',', '')

            try:
                return float(cleaned)
            except ValueError:
                logger.warning(f"Could not parse currency: {value}")
                return None

        return None

    @staticmethod
    def format_currency(value: Any, currency: str = "₹", decimals: int = 2) -> Optional[str]:
        """
        Format a value as currency
        
        Args:
            value: Numeric value
            currency: Currency symbol
            decimals: Number of decimal places
            
        Returns:
            Formatted currency string
        """
        num = MoneyCleaner.clean_currency(value)
        if num is not None:
            formatted = f"{num:,.{decimals}f}"
            return f"{currency}{formatted}"
        return None

    @staticmethod
    def standardize_currency(value: Any) -> Optional[float]:
        """
        Standardize currency to a single value
        
        Args:
            value: Currency value
            
        Returns:
            Standardized float value
        """
        return MoneyCleaner.clean_currency(value)

    @staticmethod
    def is_valid_amount(value: Any) -> bool:
        """Check if value is a valid amount"""
        amount = MoneyCleaner.clean_currency(value)
        return amount is not None and amount > 0

    @staticmethod
    def get_amount_range(min_val: Any, max_val: Any) -> Optional[str]:
        """Get formatted range of amounts"""
        min_num = MoneyCleaner.clean_currency(min_val)
        max_num = MoneyCleaner.clean_currency(max_val)
        
        if min_num is not None and max_num is not None:
            return f"₹{min_num:,.0f} - ₹{max_num:,.0f}"
        return None

    @staticmethod
    def calculate_total(values: list) -> float:
        """Calculate total from list of values"""
        total = 0.0
        for value in values:
            amount = MoneyCleaner.clean_currency(value)
            if amount is not None:
                total += amount
        return total

    @staticmethod
    def calculate_average(values: list) -> Optional[float]:
        """Calculate average from list of values"""
        amounts = []
        for value in values:
            amount = MoneyCleaner.clean_currency(value)
            if amount is not None:
                amounts.append(amount)
        
        if amounts:
            return sum(amounts) / len(amounts)
        return None
