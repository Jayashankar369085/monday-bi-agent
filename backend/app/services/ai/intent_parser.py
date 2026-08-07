"""Intent parsing for business queries using keyword matching and LLM"""

import logging
import re
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    """Possible query intents"""
    REVENUE_ANALYSIS = "revenue_analysis"
    PIPELINE_HEALTH = "pipeline_health"
    SECTORAL_PERFORMANCE = "sectoral_performance"
    DEAL_STATUS = "deal_status"
    WORK_ORDER_STATUS = "work_order_status"
    FORECASTING = "forecasting"
    OPERATIONAL_METRICS = "operational_metrics"
    CUSTOMER_ANALYSIS = "customer_analysis"
    COLLECTION_ANALYSIS = "collection_analysis"
    BILLING_ANALYSIS = "billing_analysis"
    COMPARISON = "comparison"
    TREND_ANALYSIS = "trend_analysis"
    UNKNOWN = "unknown"


class IntentParser:
    """Parse user queries to identify business intent"""

    # Keyword mappings for intent detection
    INTENT_KEYWORDS = {
        QueryIntent.REVENUE_ANALYSIS: [
            "revenue", "income", "earnings", "profit", "total amount", "billed",
            "collection", "collected", "turnover", "sales", "financial", "money",
            "summary"  # Generic summary queries map to revenue
        ],
        QueryIntent.PIPELINE_HEALTH: [
            "pipeline", "deals", "forecast", "funnel", "opportunity", "prospects",
            "closing", "win rate", "deal status", "deal", "sales pipeline",
            "health"  # "health" keyword
        ],
        QueryIntent.SECTORAL_PERFORMANCE: [
            "sector", "vertical", "segment", "industry", "mining", "renewables",
            "powerline", "railways", "construction", "performance by sector"
        ],
        QueryIntent.DEAL_STATUS: [
            "deal", "status", "stage", "progress", "won", "lost", "open",
            "closed", "negotiation", "deals"
        ],
        QueryIntent.WORK_ORDER_STATUS: [
            "work order", "project", "execution", "delivery", "completion",
            "timeline", "schedule", "work orders", "projects", "how many"
        ],
        QueryIntent.FORECASTING: [
            "forecast", "predict", "estimate", "projection", "expected",
            "outlook", "anticipated"
        ],
        QueryIntent.OPERATIONAL_METRICS: [
            "metrics", "kpi", "performance", "efficiency", "utilization",
            "capacity", "throughput", "delayed", "delay", "overdue", "late",
            "pending", "behind schedule", "stalled", "completed", "completion",
            "leadership", "update"
        ],
        QueryIntent.CUSTOMER_ANALYSIS: [
            "customer", "client", "account", "customer base", "accounts",
            "customer concentration"
        ],
        QueryIntent.COLLECTION_ANALYSIS: [
            "collection", "collected", "payment", "receivable", "ar",
            "outstanding", "dues", "collections"
        ],
        QueryIntent.BILLING_ANALYSIS: [
            "billing", "billed", "invoice", "bill", "billings", "amounts"
        ],
        QueryIntent.COMPARISON: [
            "compare", "vs", "versus", "difference", "similar", "like",
            "between", "against", "relative"
        ],
        QueryIntent.TREND_ANALYSIS: [
            "trend", "growth", "increase", "decrease", "change", "over time",
            "monthly", "quarterly", "historical", "trends"
        ],
    }
    
    # Intent patterns for specific query structures
    INTENT_PATTERNS = {
        "how many.*work order": QueryIntent.WORK_ORDER_STATUS.value,
        "how many.*deal": QueryIntent.DEAL_STATUS.value,
        "show me.*revenue": QueryIntent.REVENUE_ANALYSIS.value,
        "show me.*delay": QueryIntent.OPERATIONAL_METRICS.value,
        "what is.*health": QueryIntent.PIPELINE_HEALTH.value,
        "generate.*leadership": QueryIntent.OPERATIONAL_METRICS.value,
        "generate.*update": QueryIntent.OPERATIONAL_METRICS.value,
        "what data.*access": QueryIntent.OPERATIONAL_METRICS.value,
        "what data.*available": QueryIntent.OPERATIONAL_METRICS.value,
    }

    # Sector keywords
    SECTORS = [
        "mining", "renewables", "renewable energy", "powerline", "power",
        "railways", "rail", "construction", "dsp", "others", "security"
    ]

    # Time period keywords
    TIME_PERIODS = [
        "this quarter", "q1", "q2", "q3", "q4", "month", "year",
        "ytd", "this year", "last quarter", "last month", "last year",
        "daily", "weekly", "monthly", "quarterly", "annually"
    ]

    @staticmethod
    def parse_intent(query: str) -> Dict[str, Any]:
        """
        Parse query to extract intent and entities
        
        Args:
            query: User query
            
        Returns:
            Dict with intent, entities, and confidence
        """
        query_lower = query.lower()

        # First, try pattern-based matching for specific query structures
        primary_intent = None
        pattern_matched = False
        
        for pattern, intent_value in IntentParser.INTENT_PATTERNS.items():
            if re.search(pattern, query_lower):
                primary_intent = intent_value
                pattern_matched = True
                logger.debug(f"Pattern matched '{pattern}' -> {intent_value}")
                break

        # If no pattern match, use keyword-based matching
        if not pattern_matched:
            intent_scores = {}
            for intent, keywords in IntentParser.INTENT_KEYWORDS.items():
                score = sum(1 for keyword in keywords if keyword in query_lower)
                if score > 0:
                    intent_scores[intent] = score

            # Get primary intent - any recognized intent passes through
            if intent_scores:
                primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0].value
            else:
                primary_intent = QueryIntent.UNKNOWN.value
        
        # Calculate confidence
        if primary_intent != QueryIntent.UNKNOWN.value:
            confidence = 0.9  # High confidence for recognized intents
        else:
            confidence = 0.0

        # Extract entities
        sectors = IntentParser._extract_sectors(query_lower)
        time_period = IntentParser._extract_time_period(query_lower)
        is_comparison = IntentParser._detect_comparison(query_lower)

        return {
            "intent": primary_intent,
            "confidence": confidence,
            "sectors": sectors,
            "time_period": time_period,
            "is_comparison": is_comparison,
            "original_query": query
        }

    @staticmethod
    def _extract_sectors(query_lower: str) -> List[str]:
        """Extract mentioned sectors from query"""
        mentioned = []
        for sector in IntentParser.SECTORS:
            if sector in query_lower:
                mentioned.append(sector)
        return mentioned

    @staticmethod
    def _extract_time_period(query_lower: str) -> Optional[str]:
        """Extract time period from query"""
        for period in IntentParser.TIME_PERIODS:
            if period in query_lower:
                return period
        return None

    @staticmethod
    def _detect_comparison(query_lower: str) -> bool:
        """Detect if query is asking for comparison"""
        comparison_keywords = ["vs", "versus", "compare", "vs", "compared to", "versus", "between"]
        return any(keyword in query_lower for keyword in comparison_keywords)

    @staticmethod
    def needs_clarification(parsed: Dict[str, Any]) -> Optional[str]:
        """
        Determine if query needs clarification
        
        Only UNKNOWN intents require clarification.
        All recognized intents pass through to analytics.
        
        Args:
            parsed: Parsed query dict
            
        Returns:
            Clarification question or None
        """
        intent = parsed.get("intent")

        # ONLY ask clarification for truly unknown queries
        if intent == QueryIntent.UNKNOWN.value:
            return "Could you please provide more details about what you're looking for? Are you interested in revenue, pipeline health, or operational metrics?"

        # All recognized intents pass through to analytics pipeline
        return None
