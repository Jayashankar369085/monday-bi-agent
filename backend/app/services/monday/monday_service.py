"""
Monday service for fetching and managing board data.
Integrates MondayClient and provides high-level data access methods.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from .monday_client import MondayClient

logger = logging.getLogger(__name__)


class MondayService:
    """Service layer for Monday.com board operations"""

    WORK_ORDERS_BOARD_NAME = "Work Orders"
    DEALS_BOARD_NAME = "Deals"

    # Column name mapping: Monday column names -> Standard names
    COLUMN_MAPPING = {
        # Status columns
        "status": ["status", "stage", "progress"],
        "status_col": ["status", "stage", "progress"],
        
        # Value/Revenue columns
        "value": ["value", "amount", "price", "revenue", "deal value"],
        "deal value": ["value", "amount", "price", "revenue", "deal value"],
        
        # Timeline columns
        "timeline": ["timeline", "dates", "deadline", "due date"],
        "due date": ["timeline", "dates", "deadline", "due date"],
        
        # Owner/Person
        "owner": ["owner", "assigned to", "person", "owner_name"],
        "assigned to": ["owner", "assigned to", "person", "owner_name"],
        
        # Project/Name
        "project": ["project", "name", "title"],
        "name": ["project", "name", "title"],
    }

    def __init__(self, client: MondayClient):
        """
        Initialize Monday service
        
        Args:
            client: MondayClient instance
        """
        self.client = client
        self._board_cache = None
        self._work_orders_board_id = None
        self._deals_board_id = None
        self._work_orders_columns = None
        self._deals_columns = None

    def _find_board_by_name(self, name: str) -> Optional[str]:
        """Find board ID by name"""
        boards = self.client.get_boards()
        logger.info(f"Available boards: {[b['name'] for b in boards]}")
        
        for board in boards:
            if board.get("name", "").lower() == name.lower():
                board_id = str(board.get("id"))
                logger.info(f"Found board '{name}' with ID: {board_id}")
                return board_id
        
        logger.warning(f"Board '{name}' not found")
        return None

    def get_work_orders_board_id(self) -> Optional[str]:
        """Get work orders board ID"""
        if self._work_orders_board_id:
            return self._work_orders_board_id
        
        self._work_orders_board_id = self._find_board_by_name(self.WORK_ORDERS_BOARD_NAME)
        return self._work_orders_board_id

    def get_deals_board_id(self) -> Optional[str]:
        """Get deals board ID"""
        if self._deals_board_id:
            return self._deals_board_id
        
        self._deals_board_id = self._find_board_by_name(self.DEALS_BOARD_NAME)
        return self._deals_board_id

    def get_work_orders(self) -> List[Dict[str, Any]]:
        """Fetch all work orders"""
        board_id = self.get_work_orders_board_id()
        if not board_id:
            logger.warning(f"Board '{self.WORK_ORDERS_BOARD_NAME}' not found")
            return []
        
        items = self.client.get_board_items(board_id)
        logger.info(f"Fetched {len(items)} work orders from board {board_id}")
        return items

    def get_deals(self) -> List[Dict[str, Any]]:
        """Fetch all deals"""
        board_id = self.get_deals_board_id()
        if not board_id:
            logger.warning(f"Board '{self.DEALS_BOARD_NAME}' not found")
            return []
        
        items = self.client.get_board_items(board_id)
        logger.info(f"Fetched {len(items)} deals from board {board_id}")
        return items

    def _map_column_name(self, column_title: str) -> str:
        """
        Map Monday.com column names to standard names.
        If no mapping exists, return the original name.
        
        Args:
            column_title: Original column title from Monday
            
        Returns:
            Mapped or original column name
        """
        lower_title = column_title.lower()
        
        for standard_name, aliases in self.COLUMN_MAPPING.items():
            if lower_title in aliases:
                logger.debug(f"Mapped '{column_title}' to '{standard_name}'")
                return standard_name
        
        logger.debug(f"No mapping found for '{column_title}', keeping original")
        return column_title

    def get_work_orders_dataframe(self) -> pd.DataFrame:
        """
        Get work orders as a pandas DataFrame for analysis
        
        Returns:
            DataFrame with normalized work order data
        """
        items = self.get_work_orders()
        df = self._normalize_items_to_dataframe(items)
        logger.info(f"Work orders DataFrame shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        return df

    def get_deals_dataframe(self) -> pd.DataFrame:
        """
        Get deals as a pandas DataFrame for analysis
        
        Returns:
            DataFrame with normalized deal data
        """
        items = self.get_deals()
        df = self._normalize_items_to_dataframe(items)
        logger.info(f"Deals DataFrame shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        return df

    def _normalize_items_to_dataframe(self, items: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert Monday.com items to pandas DataFrame with automatic column mapping
        
        Args:
            items: List of items from Monday.com
            
        Returns:
            Normalized DataFrame with mapped column names
        """
        if not items:
            logger.warning("No items to normalize")
            return pd.DataFrame()

        data = []
        for item in items:
            row = {
                "id": item.get("id"),
                "name": item.get("name"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }
            
            # Extract column values with automatic mapping
            for col_val in item.get("column_values", []):
                col_id = col_val.get("id")
                column = col_val.get("column", {})
                col_title = column.get("title", col_id)
                # Use text if available, otherwise use value
                col_data = col_val.get("text") or col_val.get("value")
                
                # Map column name to standard name
                mapped_name = self._map_column_name(col_title)
                row[mapped_name] = col_data
            
            data.append(row)

        df = pd.DataFrame(data)
        print("\n========== DATAFRAME ==========")
        print(df.columns.tolist())
        print("===============================\n")
        logger.info(f"Normalized {len(data)} items into DataFrame")
        return df

    def get_board_items_raw(self, board_id: str) -> List[Dict[str, Any]]:
        """Get raw board items without processing"""
        return self.client.get_board_items(board_id)

    def search_work_orders(self, query: str) -> List[Dict[str, Any]]:
        """Search work orders"""
        board_id = self.get_work_orders_board_id()
        if not board_id:
            return []
        items = self.client.search_items(board_id, query)
        logger.info(f"Search for '{query}' found {len(items)} work orders")
        return items

    def search_deals(self, query: str) -> List[Dict[str, Any]]:
        """Search deals"""
        board_id = self.get_deals_board_id()
        if not board_id:
            return []
        items = self.client.search_items(board_id, query)
        logger.info(f"Search for '{query}' found {len(items)} deals")
        return items

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.client.clear_cache()
        self._board_cache = None
        logger.info("Cache cleared")
