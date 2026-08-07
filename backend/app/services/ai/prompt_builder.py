"""Build context-aware prompts for the LLM"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Build prompts with business context"""

    @staticmethod
    def build_analysis_prompt(
        query: str,
        intent: str,
        context: Dict[str, Any],
        analysis_results: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for analysis interpretation
        
        Args:
            query: Original user query
            intent: Detected intent
            context: Business context
            analysis_results: Results from analytics
            
        Returns:
            Formatted prompt for LLM
        """
        prompt = f"""You are a business intelligence analyst for Skylark Drones. 
        
User Query: {query}

Analysis Type: {intent}

Business Context:
{PromptBuilder._format_context(context)}

Analysis Results:
{PromptBuilder._format_analysis(analysis_results)}

Instructions:
1. Provide a clear, business-focused answer to the user's query
2. Highlight key metrics and trends
3. Identify risks or opportunities
4. Suggest actionable insights
5. Note any data quality issues or gaps
6. Keep response concise but comprehensive (2-3 paragraphs)

Provide your analysis:"""
        
        return prompt

    @staticmethod
    def build_comparison_prompt(
        query: str,
        entity1: str,
        entity2: str,
        data1: Dict[str, Any],
        data2: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for comparison analysis
        
        Args:
            query: Original query
            entity1: First entity to compare
            entity2: Second entity to compare
            data1: Data for entity1
            data2: Data for entity2
            
        Returns:
            Formatted comparison prompt
        """
        prompt = f"""You are a business analyst comparing business entities.

User Query: {query}

Comparing: {entity1} vs {entity2}

{entity1} Metrics:
{PromptBuilder._format_analysis(data1)}

{entity2} Metrics:
{PromptBuilder._format_analysis(data2)}

Instructions:
1. Provide a head-to-head comparison
2. Highlight where each entity excels or underperforms
3. Provide percentage differences where applicable
4. Give a brief recommendation or assessment
5. Keep response focused (2-3 paragraphs)

Provide your comparison:"""
        
        return prompt

    @staticmethod
    def build_forecast_prompt(
        query: str,
        historical_data: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for forecast interpretation
        
        Args:
            query: Original query
            historical_data: Historical metrics
            forecast: Forecast data
            
        Returns:
            Formatted forecast prompt
        """
        prompt = f"""You are a business forecasting analyst.

User Query: {query}

Historical Data:
{PromptBuilder._format_analysis(historical_data)}

Forecast:
{PromptBuilder._format_analysis(forecast)}

Instructions:
1. Interpret the forecast in business context
2. Explain key assumptions
3. Highlight risks and opportunities
4. Suggest confidence level (High/Medium/Low)
5. Provide actionable recommendations
6. Keep response focused (2-3 paragraphs)

Provide your forecast analysis:"""
        
        return prompt

    @staticmethod
    def build_clarification_prompt(query: str, issues: List[str]) -> str:
        """
        Build a prompt for clarifying ambiguous queries
        
        Args:
            query: Original query
            issues: Issues with query interpretation
            
        Returns:
            Clarification prompt
        """
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        prompt = f"""The user asked: "{query}"

Issues with interpretation:
{issues_text}

Suggest 2-3 clarifying questions to better understand what the user is asking for.
Format as a numbered list."""
        
        return prompt

    @staticmethod
    def _format_context(context: Dict[str, Any]) -> str:
        """Format business context for prompt"""
        lines = []
        
        if context.get("sectors"):
            lines.append(f"Sectors: {', '.join(context['sectors'])}")
        
        if context.get("time_period"):
            lines.append(f"Time Period: {context['time_period']}")
        
        if context.get("data_quality_score"):
            lines.append(f"Data Quality: {context['data_quality_score']:.0f}%")
        
        if context.get("total_records"):
            lines.append(f"Records Analyzed: {context['total_records']}")
        
        return "\n".join(lines) if lines else "No specific context"

    @staticmethod
    def _format_analysis(analysis: Dict[str, Any], indent: int = 0) -> str:
        """Format analysis results for prompt"""
        lines = []
        prefix = "  " * indent
        
        for key, value in analysis.items():
            # Skip complex nested objects
            if isinstance(value, dict) and len(str(value)) > 200:
                lines.append(f"{prefix}{key.replace('_', ' ').title()}: [Complex data]")
            elif isinstance(value, (list, tuple)) and len(value) > 5:
                lines.append(f"{prefix}{key.replace('_', ' ').title()}: {len(value)} items")
            elif isinstance(value, float):
                lines.append(f"{prefix}{key.replace('_', ' ').title()}: {value:.2f}")
            elif isinstance(value, dict):
                lines.append(f"{prefix}{key.replace('_', ' ').title()}:")
                for subkey, subvalue in list(value.items())[:5]:
                    if isinstance(subvalue, float):
                        lines.append(f"{prefix}  {subkey}: {subvalue:.2f}")
                    else:
                        lines.append(f"{prefix}  {subkey}: {subvalue}")
                if len(value) > 5:
                    lines.append(f"{prefix}  ... and {len(value) - 5} more items")
            else:
                lines.append(f"{prefix}{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines) if lines else "No analysis data"

    @staticmethod
    def build_leadership_update_prompt(
        work_orders_analysis: Dict[str, Any],
        deals_analysis: Dict[str, Any],
        sector_performance: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for generating leadership update
        
        Args:
            work_orders_analysis: Work orders metrics
            deals_analysis: Deals/pipeline metrics
            sector_performance: Sector-wise performance
            
        Returns:
            Leadership update prompt
        """
        prompt = f"""You are preparing an executive dashboard summary for leadership.

Business Metrics:

Work Orders & Operations:
{PromptBuilder._format_analysis(work_orders_analysis)}

Sales Pipeline:
{PromptBuilder._format_analysis(deals_analysis)}

Sector Performance:
{PromptBuilder._format_analysis(sector_performance)}

Generate a concise executive summary (300 words max) including:
1. Key Performance Indicators (top 3-4 metrics)
2. Status Summary (operations, sales, finances)
3. Risks or Concerns (if any)
4. Opportunities or Recommendations (if any)

Format as:
## Executive Summary
[Content]

## Key Metrics
- Metric 1: Value
- Metric 2: Value
- etc.

## Status & Recommendations
[2-3 sentences]

Generate the leadership update:"""
        
        return prompt
