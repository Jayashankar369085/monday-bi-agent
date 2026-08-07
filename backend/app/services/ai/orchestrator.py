"""Main orchestrator for BI agent - coordinates all services"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd

from .intent_parser import IntentParser
from .entity_extractor import EntityExtractor
from .prompt_builder import PromptBuilder
from .openai_client import OpenAIClient
from ..monday.monday_service import MondayService
from ..cleaner.date_cleaner import DateCleaner
from ..cleaner.money_cleaner import MoneyCleaner
from ..cleaner.enum_cleaner import EnumCleaner
from ..cleaner.validator import DataValidator
from ..analytics.sales import SalesAnalytics
from ..analytics.operations import OperationsAnalytics
from ..analytics.finance import FinanceAnalytics
from ...utils.serializer import convert_numpy_types

logger = logging.getLogger(__name__)


class BIOrchestrator:
    """Orchestrates all BI agent services"""

    def __init__(self, monday_service: MondayService, openai_client: OpenAIClient):
        """
        Initialize orchestrator
        
        Args:
            monday_service: MondayService instance
            openai_client: OpenAIClient instance
        """
        self.monday_service = monday_service
        self.openai_client = openai_client
        self._work_orders_cache = None
        self._deals_cache = None
        self._work_orders_df = None
        self._deals_df = None

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query end-to-end
        
        Args:
            query: User query
            
        Returns:
            Response dict with answer and metadata
        """
        try:
            logger.info(f"Processing query: {query}")

            # Parse intent
            parsed = IntentParser.parse_intent(query)
            logger.info(f"Parsed intent: {parsed.get('intent')}")

            # Extract entities
            entities = EntityExtractor.extract_entities(query)
            logger.debug(f"Extracted entities: {entities}")

            # Check if clarification needed
            clarification_needed = IntentParser.needs_clarification(parsed)
            if clarification_needed:
                return {
                    "status": "clarification_needed",
                    "message": clarification_needed,
                    "answer": clarification_needed,
                    "parsed_intent": parsed,
                    "extracted_entities": entities,
                }

            # Load data - CRITICAL: must load before analyzing
            work_orders_df = self._get_work_orders_df()
            deals_df = self._get_deals_df()
            
            logger.info(f"Loaded: {len(work_orders_df)} work orders, {len(deals_df)} deals")

            if work_orders_df.empty and deals_df.empty:
                error_msg = "Unable to fetch data from monday.com. Please check API configuration."
                return {
                    "status": "error",
                    "message": error_msg,
                    "answer": error_msg,
                }
            # Route to appropriate analysis - Pass DataFrames explicitly
            # Handle leadership report requests first
            query_lower = query.lower()

            if any(keyword in query_lower for keyword in [
                "leadership",
                "leadership report",
                "leadership update",
                "executive summary",
                "executive report"
            ]):
                report = self.generate_leadership_update()
                return {
                    "status": "success",
                    "intent": "leadership_update",
                    "answer": report["report"],
                    "report": report["report"]
                }

            # Route to appropriate analysis - Pass DataFrames explicitly
            intent = parsed.get("intent")
            
            if intent == "revenue_analysis":
                return self._handle_revenue_query(query, work_orders_df, deals_df, parsed)
            elif intent == "pipeline_health":
                return self._handle_pipeline_query(query, deals_df, parsed)
            elif intent == "sectoral_performance":
                return self._handle_sectoral_query(query, work_orders_df, deals_df, parsed)
            elif intent == "operational_metrics":
                return self._handle_operational_query(query, work_orders_df, parsed)
            elif intent == "comparison":
                return self._handle_comparison_query(query, work_orders_df, deals_df, entities)
            elif intent == "work_order_status":
                count = len(work_orders_df)
                return {
                    "status": "success",
                    "intent": "work_order_status",
                    "answer": f"There are {count} work orders in the system.",
                }
            elif intent == "deal_status":
                count = len(deals_df)
                return {
                    "status": "success",
                    "intent": "deal_status",
                    "answer": f"There are {count} deals in the pipeline.",
                }
            else:
                return self._handle_general_query(query, work_orders_df, deals_df, parsed)
        
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}", exc_info=True)
            error_msg = f"An error occurred while processing your query"
            return {
                "status": "error",
                "answer": error_msg,
            }
    

    def _get_work_orders_df(self) -> pd.DataFrame:
        """Get work orders DataFrame with caching"""
        if self._work_orders_df is None:
            try:
                items = self.monday_service.get_work_orders()
                self._work_orders_df = self.monday_service._normalize_items_to_dataframe(items)
                logger.info(f"Loaded {len(self._work_orders_df)} work orders from Monday.com")
            except Exception as e:
                logger.error(f"Error loading work orders: {str(e)}")
                self._work_orders_df = pd.DataFrame()
        return self._work_orders_df

    def _get_deals_df(self) -> pd.DataFrame:
        """Get deals DataFrame with caching"""
        if self._deals_df is None:
            try:
                items = self.monday_service.get_deals()
                self._deals_df = self.monday_service._normalize_items_to_dataframe(items)
                logger.info(f"Loaded {len(self._deals_df)} deals from Monday.com")
            except Exception as e:
                logger.error(f"Error loading deals: {str(e)}")
                self._deals_df = pd.DataFrame()
        return self._deals_df

    def _handle_revenue_query(self, query: str, work_orders: pd.DataFrame, deals: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Handle revenue analysis query"""
        try:
            analysis = FinanceAnalytics.analyze_revenue_metrics(work_orders)
            sector_analysis = FinanceAnalytics.analyze_revenue_by_sector(work_orders)
            
            analysis["by_sector"] = sector_analysis
            
            # Build analytics-based response
            # Build Top 5 sectors

            if deals_by_sector:
                top5 = sorted(
                    deals_by_sector.items(),
                    key=lambda x: x[1]["deal_count"],
                    reverse=True
                )[:5]

                sector_summary = "Top 5 Sectors by Deal Count:\n\n"

                for i, (sector, data) in enumerate(top5, 1):
                    sector_summary += (
                        f"{i}. {sector}\n"
                        f"   Deals: {data['deal_count']}\n"
                        f"   Pipeline Value: ₹{data['total_value']:,.0f}\n"
                        f"   Win Rate: {data['win_rate']:.1f}%\n\n"
                    )
            else:
                sector_summary = "No sector data available."
            prompt = PromptBuilder.build_analysis_prompt(
                query, "revenue_analysis", {}, analysis
            )
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use analytics summary
            answer = ai_answer if ai_answer else revenue_summary

            return {
                "status": "success",
                "intent": "revenue_analysis",
                "answer": answer,
                "analysis": convert_numpy_types(analysis),
            }
        except Exception as e:
            logger.error(f"Revenue query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"Revenue Analysis: {len(work_orders)} projects loaded",
            }

    def _handle_pipeline_query(self, query: str, deals: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Handle pipeline health query"""
        try:
            analysis = SalesAnalytics.analyze_pipeline_health(deals)
            sector_analysis = SalesAnalytics.analyze_pipeline_by_sector(deals)
            stage_analysis = SalesAnalytics.analyze_deals_by_stage(deals)
            
            analysis["by_sector"] = sector_analysis
            analysis["by_stage"] = stage_analysis

            at_risk_deals = SalesAnalytics.identify_at_risk_deals(deals)
            if at_risk_deals:
                analysis["at_risk_deals"] = at_risk_deals[:5]

            # Build analytics-based response
            total_deals = analysis.get('total_deals', 0)
            avg_size = analysis.get('average_deal_size', 0)
            total_value = analysis.get('total_pipeline_value', 0)
            win_rate = analysis.get('win_rate_percentage', 0)
            open_deals = analysis.get('open_deals', 0)
            closed_deals = analysis.get('closed_deals', 0)
            
            pipeline_summary = f"""Pipeline Health:

Total Deals: {total_deals}
Average Deal Size: ₹{avg_size:,.0f}
Total Pipeline Value: ₹{total_value:,.0f}
Win Rate: {win_rate:.1f}%

Status Breakdown:
- Open: {open_deals}
- Closed: {closed_deals}
- Lost: {analysis.get('lost_deals', 0)}"""

            prompt = PromptBuilder.build_analysis_prompt(
                query, "pipeline_health", {}, analysis
            )
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use analytics summary
            answer = ai_answer if ai_answer else pipeline_summary
            
            return {
                "status": "success",
                "intent": "pipeline_health",
                "answer": answer,
                "analysis": convert_numpy_types(analysis),
            }
        except Exception as e:
            logger.error(f"Pipeline query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"Pipeline Health: {len(deals)} deals loaded",
            }

    def _handle_sectoral_query(self, query: str, work_orders: pd.DataFrame, deals: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Handle sectoral performance query"""
        try:
            sectors = parsed.get("sectors", [])
            
            # Get all sector analyses
            ops_by_sector = OperationsAnalytics.analyze_operational_by_sector(work_orders)
            finance_by_sector = FinanceAnalytics.analyze_revenue_by_sector(work_orders)
            deals_by_sector = SalesAnalytics.analyze_pipeline_by_sector(deals)

            combined_analysis = {
                "query": query,
                "operations": ops_by_sector,
                "finance": finance_by_sector,
                "pipeline": deals_by_sector,
            }

            # Build analytics-based response
            sector_count = len(ops_by_sector) if ops_by_sector else len(finance_by_sector)
            sector_summary = f"""Sector Analysis:

Total Sectors Analyzed: {sector_count}
Work Orders by Sector: {len(work_orders)}
Deals by Sector: {len(deals)}"""

            prompt = PromptBuilder.build_analysis_prompt(
                query, "sectoral_performance", {"sectors": sectors}, combined_analysis
            )
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use analytics summary
            answer = ai_answer if ai_answer else sector_summary
            
            return {
                "status": "success",
                "intent": "sectoral_performance",
                "answer": answer,
                "analysis": convert_numpy_types(combined_analysis),
            }
        except Exception as e:
            logger.error(f"Sectoral query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"Sector Analysis: {len(work_orders)} work orders analyzed",
            }

    def _handle_operational_query(self, query: str, work_orders: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Handle operational metrics query"""
        try:
            analysis = OperationsAnalytics.analyze_project_execution(work_orders)
            sector_analysis = OperationsAnalytics.analyze_operational_by_sector(work_orders)
            timeline_analysis = OperationsAnalytics.analyze_timeline_performance(work_orders)
            
            analysis["by_sector"] = sector_analysis
            analysis["timeline"] = timeline_analysis

            delayed = OperationsAnalytics.identify_delayed_projects(work_orders)
            if delayed:
                analysis["delayed_projects"] = delayed[:3]

            # Build analytics-based response
            total_projects = analysis.get('total_projects', 0)
            completion_rate = analysis.get('completion_rate', 0)
            completed = analysis.get('completed_projects', 0)
            delayed_count = len(delayed) if delayed else 0
            
            ops_summary = f"""Operational Metrics:

Total Projects: {total_projects}
Completion Rate: {completion_rate:.1f}%
Completed: {completed}
Delayed: {delayed_count}
Ongoing: {analysis.get('ongoing_projects', 0)}"""

            prompt = PromptBuilder.build_analysis_prompt(
                query, "operational_metrics", {}, analysis
            )
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use analytics summary
            answer = ai_answer if ai_answer else ops_summary
            
            return {
                "status": "success",
                "intent": "operational_metrics",
                "answer": answer,
                "analysis": convert_numpy_types(analysis),
            }
        except Exception as e:
            logger.error(f"Operational query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"Operational Metrics: {len(work_orders)} projects loaded",
            }

    def _handle_comparison_query(self, query: str, work_orders: pd.DataFrame, deals: pd.DataFrame, entities: Dict) -> Dict[str, Any]:
        """Handle comparison query"""
        try:
            comparison_entities, right_entities = EntityExtractor.extract_comparison_entities(query)
            
            if not (comparison_entities and right_entities):
                return {
                    "status": "error",
                    "answer": "Could not identify entities to compare. Please specify which sectors or metrics to compare.",
                }

            # Build comparison prompt
            prompt = f"""Compare {comparison_entities} and {right_entities}:
            
Work Orders: {len(work_orders)}
Deals: {len(deals)}

Provide analysis based on available metrics."""
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use default
            answer = ai_answer if ai_answer else f"Comparison: {comparison_entities} vs {right_entities}"
            
            return {
                "status": "success",
                "intent": "comparison",
                "answer": answer,
                "compared_entities": {"left": comparison_entities, "right": right_entities},
            }
        except Exception as e:
            logger.error(f"Comparison query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"Unable to perform comparison",
            }

    def _handle_general_query(self, query: str, work_orders: pd.DataFrame, deals: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Handle general query with all available context"""
        try:
            # Compile comprehensive analysis
            ops_analysis = OperationsAnalytics.analyze_project_execution(work_orders)
            sales_analysis = SalesAnalytics.analyze_pipeline_health(deals)
            finance_analysis = FinanceAnalytics.analyze_revenue_metrics(work_orders)

            combined = {
                "operations": ops_analysis,
                "sales": sales_analysis,
                "finance": finance_analysis,
            }

            # Build general analysis response
            general_summary = f"""Business Summary:

Work Orders: {len(work_orders)}
Deals: {len(deals)}
Project Completion Rate: {ops_analysis.get('completion_rate', 0):.1f}%
Deal Win Rate: {sales_analysis.get('win_rate_percentage', 0):.1f}%
Total Revenue: ₹{finance_analysis.get('total_revenue', 0):,.0f}"""

            prompt = PromptBuilder.build_analysis_prompt(
                query, "general", {}, combined
            )
            
            ai_answer = self.openai_client.analyze_query(prompt)
            
            # Use AI answer if available, otherwise use summary
            answer = ai_answer if ai_answer else general_summary
            
            return {
                "status": "success",
                "intent": "general",
                "answer": answer,
                "analysis": convert_numpy_types(combined),
            }
        except Exception as e:
            logger.error(f"General query error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "answer": f"General Analysis: {len(work_orders)} projects, {len(deals)} deals",
            }

    def generate_leadership_update(self) -> Dict[str, Any]:
        """Generate leadership update report"""
        try:
            work_orders = self._get_work_orders_df()
            deals = self._get_deals_df()

            wo_analysis = OperationsAnalytics.analyze_project_execution(work_orders)
            deals_analysis = SalesAnalytics.analyze_pipeline_health(deals)
            sector_perf = OperationsAnalytics.analyze_operational_by_sector(work_orders)

            # Build leadership summary from analytics
            leadership_summary = f"""EXECUTIVE SUMMARY

Operations Status:
- Total Projects: {wo_analysis.get('total_projects', 0)}
- Completion Rate: {wo_analysis.get('completion_rate', 0):.1f}%
- Completed: {wo_analysis.get('completed_projects', 0)}
- Ongoing: {wo_analysis.get('ongoing_projects', 0)}
- Total Value: ₹{wo_analysis.get('total_project_value', 0):,.0f}

Sales Pipeline:
- Total Deals: {deals_analysis.get('total_deals', 0)}
- Win Rate: {deals_analysis.get('win_rate_percentage', 0):.1f}%
- Pipeline Value: ₹{deals_analysis.get('total_pipeline_value', 0):,.0f}
- Average Deal Size: ₹{deals_analysis.get('average_deal_size', 0):,.0f}

Key Sectors: {len(sector_perf) if sector_perf else 0}"""

            # Try to enhance with OpenAI
            prompt = PromptBuilder.build_leadership_update_prompt(
                wo_analysis, deals_analysis, sector_perf
            )
            
            ai_report = self.openai_client.analyze_query(prompt, temperature=0.5)
            
            # Use AI report if available, otherwise use summary
            report = ai_report if ai_report else leadership_summary
            
            return {
                "status": "success",
                "report": report,
                "timestamp": pd.Timestamp.now().isoformat(),
                "metrics": {
                    "operations": convert_numpy_types(wo_analysis),
                    "sales": convert_numpy_types(deals_analysis),
                    "sectors": convert_numpy_types(sector_perf),
                }
            }
        except Exception as e:
            logger.error(f"Leadership update error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "report": f"Leadership update generation failed",
                "timestamp": pd.Timestamp.now().isoformat(),
            }

    def _get_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data quality metrics for a DataFrame"""
        try:
            items = df.to_dict('records') if not df.empty else []
            quality_report = DataValidator.compare_data_quality(items)
            return convert_numpy_types(quality_report)
        except:
            return {}
