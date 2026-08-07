from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging
from ..models.schemas import ChatRequest, ChatResponse
from ..services.monday.monday_client import MondayClient
from ..services.monday.monday_service import MondayService
from ..services.ai.openai_client import OpenAIClient
from ..services.ai.orchestrator import BIOrchestrator
from ..services.analytics.sales import SalesAnalytics
from ..services.analytics.operations import OperationsAnalytics
from ..core.config import settings
from ..utils.serializer import convert_numpy_types
import pandas as pd
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])

# Global instances (in production, use dependency injection)
_monday_client = None
_monday_service = None
_openai_client = None
_orchestrator = None


def get_orchestrator() -> BIOrchestrator:
    """Get or create orchestrator instance"""
    global _monday_client, _monday_service, _openai_client, _orchestrator
    
    try:
        if _orchestrator is None:
            if _monday_client is None:
                _monday_client = MondayClient(settings.MONDAY_API_TOKEN)
            if _monday_service is None:
                _monday_service = MondayService(_monday_client)
            if _openai_client is None:
                _openai_client = OpenAIClient(settings.OPENAI_API_KEY)
            _orchestrator = BIOrchestrator(_monday_service, _openai_client)
        return _orchestrator
    except Exception as e:
        logger.error(f"Error initializing orchestrator: {str(e)}")
        raise HTTPException(status_code=500, detail="Service initialization failed")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for BI queries
    
    Args:
        request: ChatRequest with user question
        
    Returns:
        ChatResponse with answer
    """
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.process_query(request.question)
        
        # Extract answer, ensuring it's never None
        answer = result.get("answer")
        
        if not answer:
            if result.get("status") == "clarification_needed":
                answer = result.get("message", "Could you provide more details?")
            elif result.get("status") == "error":
                answer = result.get("message", "An error occurred while processing your query")
            else:
                answer = "Unable to generate a response. Please try a different query."
        
        logger.info(f"Chat response: {answer[:100]}...")
        return ChatResponse(answer=answer)
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        error_message = f"An unexpected error occurred. Please try again. Error: {str(e)[:100]}"
        return ChatResponse(answer=error_message)


@router.get("/kpi-dashboard")
async def get_kpi_dashboard():
    """Get KPI metrics for dashboard"""
    try:
        orchestrator = get_orchestrator()
        
        # Fetch data
        deals = orchestrator._get_deals_df()
        work_orders = orchestrator._get_work_orders_df()
        
        logger.info(f"KPI Request: Deals={len(deals)}, Work Orders={len(work_orders)}")
        
        # Calculate metrics
        kpis = {
            "revenue": "No data available",
            "deals": str(len(deals)) if not deals.empty else "0",
            "workOrders": str(len(work_orders)) if not work_orders.empty else "0",
            "delayedProjects": "0"
        }
        
        # Calculate revenue
        if not work_orders.empty:
            try:
                # Try common revenue column names
                revenue_cols = ["value", "amount", "revenue", "deal value", "Amount in Rupees (Excl of GST) (Masked)"]
                revenue_value = 0
                
                for col in revenue_cols:
                    if col in work_orders.columns:
                        revenue_value = pd.to_numeric(work_orders[col], errors='coerce').sum()
                        if revenue_value > 0:
                            kpis["revenue"] = f"₹{int(revenue_value):,}"
                            break
                
                if revenue_value == 0:
                    kpis["revenue"] = "No data available"
            except Exception as e:
                logger.error(f"Error calculating revenue: {e}")
                kpis["revenue"] = "Error calculating"
        
        # Calculate delayed projects
        if not work_orders.empty:
            try:
                # Look for status columns that indicate delays
                status_cols = ["status", "Execution Status", "Status"]
                delayed_count = 0
                
                for col in status_cols:
                    if col in work_orders.columns:
                        delayed_count = sum(1 for status in work_orders[col] 
                                          if status and any(keyword in str(status).lower() 
                                          for keyword in ["delayed", "overdue", "late", "pending", "behind"]))
                        if delayed_count > 0:
                            kpis["delayedProjects"] = str(delayed_count)
                            break
            except Exception as e:
                logger.error(f"Error calculating delayed projects: {e}")
        
        logger.info(f"KPI Response: {kpis}")
        return kpis
    
    except Exception as e:
        logger.error(f"KPI dashboard error: {str(e)}", exc_info=True)
        return {
            "revenue": "—",
            "deals": "—",
            "workOrders": "—",
            "delayedProjects": "—"
        }


@router.get("/leadership-update")
async def get_leadership_update():
    """Generate leadership update report"""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.generate_leadership_update()
        
        report = result.get("report")
        if not report:
            report = "Leadership report generation failed. Please try again."
        
        logger.info(f"Leadership report generated: {report[:100]}...")
        return {
            "status": result.get("status", "error"),
            "report": report,
            "timestamp": result.get("timestamp"),
        }
    except Exception as e:
        logger.error(f"Leadership update error: {str(e)}", exc_info=True)
        error_message = f"Unable to generate leadership update. Error: {str(e)[:100]}"
        return {
            "status": "error",
            "report": error_message,
            "timestamp": pd.Timestamp.now().isoformat(),
        }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        orchestrator = get_orchestrator()
        
        # Test Monday connection
        monday_ok = True
        try:
            boards = orchestrator.monday_service.client.get_boards()
            monday_ok = len(boards) > 0
        except:
            monday_ok = False
        
        # Test OpenAI connection
        openai_ok = orchestrator.openai_client.health_check()
        
        return {
            "status": "healthy" if (monday_ok and openai_ok) else "degraded",
            "monday_com": "connected" if monday_ok else "disconnected",
            "openai": "connected" if openai_ok else "disconnected",
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }