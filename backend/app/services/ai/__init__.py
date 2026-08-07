"""AI services for business intelligence"""

from .intent_parser import IntentParser
from .entity_extractor import EntityExtractor
from .prompt_builder import PromptBuilder
from .insight_engine import InsightEngine

try:
    from .openai_client import OpenAIClient
    from .orchestrator import BIOrchestrator
except ImportError:
    # OpenAI not available - will be loaded at runtime
    pass

__all__ = [
    "IntentParser",
    "EntityExtractor",
    "PromptBuilder",
    "InsightEngine",
]
