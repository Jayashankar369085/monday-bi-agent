"""Intelligent column mapper for handling different DataFrame column names"""

import logging
from typing import Optional, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class ColumnMapper:
    """Maps various column name variations to standard names"""
    
    # Known column mappings with aliases
    COLUMN_ALIASES = {
        # Revenue/Amount columns
        'revenue': ['revenue', 'total revenue', 'amount', 'value', 'total amount', 
                   'Amount in Rupees (Excl of GST) (Masked)', 'amount in rupees', 'deal value'],
        
        # Status columns
        'status': ['status', 'execution status', 'deal status', 'stage', 'progress', 'state'],
        
        # Name/Title columns
        'name': ['name', 'deal name', 'deal name masked', 'title', 'project name', 'work order'],
        
        # Date columns
        'date': ['date', 'created at', 'created_at', 'updated at', 'updated_at', 
                'probable end date', 'deadline', 'due date'],
        
        # Sector columns
        'sector': ['sector', 'vertical', 'segment', 'industry', 'sector/service', 'service'],
        
        # Completion/Status columns
        'completion': ['completed', 'completion', 'execution status', 'delivered', 
                      'delivered date', 'delivery date'],
        
        # Personnel/Owner columns
        'owner': ['owner', 'assigned to', 'owner code', 'bd/kam personnel code', 'personnel', 
                 'person'],
        
        # ID columns
        'id': ['id', 'item id', 'order id', 'deal id', 'project id'],
    }
    
    @staticmethod
    def find_column(df: pd.DataFrame, target: str) -> Optional[str]:
        """
        Find a column in DataFrame by target name (with fallback to aliases)
        
        Args:
            df: DataFrame to search
            target: Target column name (e.g., 'revenue', 'status')
            
        Returns:
            Actual column name if found, None otherwise
        """
        if df.empty:
            return None
        
        columns = list(df.columns)
        target_lower = target.lower()
        
        # Exact match first
        for col in columns:
            if col.lower() == target_lower:
                logger.debug(f"Exact match found: {target} -> {col}")
                return col
        
        # Alias match
        if target_lower in ColumnMapper.COLUMN_ALIASES:
            aliases = ColumnMapper.COLUMN_ALIASES[target_lower]
            for alias in aliases:
                for col in columns:
                    if col.lower() == alias.lower():
                        logger.debug(f"Alias match found: {target} -> {col} (via {alias})")
                        return col
        
        # Fuzzy match - contains
        for alias_list in ColumnMapper.COLUMN_ALIASES.values():
            for alias in alias_list:
                for col in columns:
                    if alias.lower() in col.lower() or col.lower() in alias.lower():
                        logger.debug(f"Fuzzy match found: {target} -> {col} (via {alias})")
                        return col
        
        logger.warning(f"No column match found for {target}. Available: {columns}")
        return None
    
    @staticmethod
    def get_column_value(row: pd.Series, possible_names: List[str]) -> any:
        """
        Get value from row using multiple possible column names
        
        Args:
            row: DataFrame row
            possible_names: List of possible column names to try
            
        Returns:
            Value if found, None otherwise
        """
        for name in possible_names:
            if name in row.index:
                return row[name]
        return None
    
    @staticmethod
    def get_numeric_value(row: pd.Series, possible_names: List[str], default=0) -> float:
        """
        Get numeric value from row, trying multiple column names
        
        Args:
            row: DataFrame row
            possible_names: List of possible column names
            default: Default value if not found
            
        Returns:
            Numeric value
        """
        for name in possible_names:
            if name in row.index:
                try:
                    val = row[name]
                    if pd.notna(val):
                        return float(val)
                except (ValueError, TypeError):
                    continue
        return default
    
    @staticmethod
    def print_columns(df: pd.DataFrame, name: str = "DataFrame") -> None:
        """
        Print all columns in a DataFrame for debugging
        
        Args:
            df: DataFrame to inspect
            name: Name of the DataFrame for logging
        """
        if df.empty:
            logger.info(f"{name}: Empty")
        else:
            logger.info(f"{name} ({len(df)} rows, {len(df.columns)} columns):")
            logger.info(f"  Columns: {list(df.columns)}")
