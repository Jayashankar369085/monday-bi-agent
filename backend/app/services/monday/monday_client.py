"""
Monday.com GraphQL API client for fetching boards and items data.
Handles authentication, caching, and error handling.
"""

import httpx
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class MondayClient:
    """Client for interacting with Monday.com GraphQL API"""

    BASE_URL = "https://api.monday.com/v2"
    CACHE = {}  # Simple in-memory cache
    CACHE_TTL = 300  # 5 minutes default

    def __init__(self, api_token: str, cache_ttl: int = 300):
        """
        Initialize Monday.com client
        
        Args:
            api_token: Monday.com API token
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_token = api_token
        self.cache_ttl = cache_ttl
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }

    def _make_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GraphQL request to Monday.com API
        
        Args:
            query: GraphQL query string
            variables: Query variables
            
        Returns:
            API response data
            
        Raises:
            Exception: If API request fails
        """
        try:
            payload = {
                "query": query,
                "variables": variables or {}
            }
            
            with httpx.Client() as client:
                response = client.post(
                    self.BASE_URL,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    logger.error(f"GraphQL error: {data['errors']}")
                    raise Exception(f"GraphQL error: {data['errors']}")
                
                return data.get("data", {})
        except Exception as e:
            logger.error(f"Monday.com API error: {str(e)}")
            raise

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key"""
        return f"monday_{key}"

    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get item from cache if not expired"""
        cache_key = self._get_cache_key(key)
        if cache_key in self.CACHE:
            entry = self.CACHE[cache_key]
            if datetime.now() < entry["expires"]:
                logger.debug(f"Cache hit for {key}")
                return entry["data"]
            else:
                del self.CACHE[cache_key]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Store item in cache"""
        cache_key = self._get_cache_key(key)
        self.CACHE[cache_key] = {
            "data": data,
            "expires": datetime.now() + timedelta(seconds=self.cache_ttl)
        }

    def get_boards(self) -> List[Dict[str, Any]]:
        """
        Fetch all boards for the user

        Returns:
            List of board objects
        """
        cache_key = "boards"

        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        query = """
        {
            boards {
                id
                name
                state
                type
                created_at
                updated_at
            }
        }
        """

        result = self._make_request(query)
        boards = result.get("boards", [])

        print("\n========== MONDAY BOARDS ==========")
        for board in boards:
            print(f"ID: {board['id']}   NAME: {board['name']}")
        print("===================================\n")

        self._set_cache(cache_key, boards)
        return boards

    def get_board_items(self, board_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Fetch all items from a specific board
        
        Args:
            board_id: Monday.com board ID (as string, will convert to ID type for GraphQL)
            limit: Maximum items to fetch
            
        Returns:
            List of items with all columns
        """
        cache_key = f"board_items_{board_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Use ID type for board_id (Monday API expects ID, not Int)
        query = """
query GetBoardItems($board_id: ID!, $limit: Int!) {
    boards(ids: [$board_id]) {
        items_page(limit: $limit) {
            items {
                id
                name
                created_at
                updated_at
                column_values {
                    id
                    text
                    value
                    type
                    column {
                        title
                    }
                }
            }
        }
    }
}
"""
        
        variables = {
            "board_id": str(board_id),  # Keep as string for ID type
            "limit": limit
        }
        
        logger.debug(f"Fetching items from board: {board_id}")
        logger.debug(f"GraphQL Query: {query}")
        logger.debug(f"Variables: {variables}")
        
        result = self._make_request(query, variables)
        items = []
        
        try:
            boards = result.get("boards", [])
            if boards:
                items_page = boards[0].get("items_page", {})
                items = items_page.get("items", [])
                logger.info(f"Board {board_id}: Fetched {len(items)} items")
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing board items: {str(e)}")
            items = []
        
        self._set_cache(cache_key, items)
        return items

    def get_board_columns(self, board_id: str) -> List[Dict[str, Any]]:
        """
        Fetch column definitions for a board
        
        Args:
            board_id: Monday.com board ID
            
        Returns:
            List of column definitions
        """
        cache_key = f"board_columns_{board_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        query = """
        query GetBoardColumns($board_id: ID!) {
            boards(ids: [$board_id]) {
                columns {
                    id
                    title
                    type
                    settings_str
                }
            }
        }
        """
        
        variables = {"board_id": str(board_id)}  # Keep as string for ID type
        logger.debug(f"Fetching columns for board: {board_id}")
        
        result = self._make_request(query, variables)
        columns = []
        
        try:
            boards = result.get("boards", [])
            if boards:
                columns = boards[0].get("columns", [])
                logger.info(f"Board {board_id}: Found {len(columns)} columns")
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing board columns: {str(e)}")
            columns = []
        
        self._set_cache(cache_key, columns)
        return columns

    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.CACHE.clear()
        logger.info("Cache cleared")

    def search_items(self, board_id: str, query_text: str) -> List[Dict[str, Any]]:
        """
        Search items in a board
        
        Args:
            board_id: Monday.com board ID
            query_text: Search query text
            
        Returns:
            List of matching items
        """
        query = """
        query SearchItems($board_id: ID!, $query_text: String!) {
            items_by_column_values(board_id: $board_id, column_id: "name", column_value: $query_text) {
                id
                name
                column_values {
                    id
                    text
                    value
                    type
                    column {
                        title
                    }
                }
            }
        }
        """
        
        variables = {
            "board_id": str(board_id),  # Keep as string for ID type
            "query_text": query_text
        }
        
        logger.debug(f"Searching items in board {board_id} for: {query_text}")
        
        try:
            result = self._make_request(query, variables)
            items = result.get("items_by_column_values", [])
            logger.info(f"Search found {len(items)} items")
            return items
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
