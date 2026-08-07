"""Enum and categorical data cleaning utilities"""

import logging
from typing import Any, Optional, List

logger = logging.getLogger(__name__)


class EnumCleaner:
    """Handles enum and categorical data normalization"""

    # Common mappings
    STATUS_MAPPINGS = {
        "completed": ["completed", "done", "closed", "finished"],
        "in_progress": ["in progress", "ongoing", "active", "executing", "executed until current month"],
        "not_started": ["not started", "pending", "todo", "open"],
        "on_hold": ["on hold", "paused", "pause / struck", "struck"],
        "failed": ["failed", "cancelled", "cancelled", "not billable"],
    }

    SECTOR_MAPPINGS = {
        "mining": ["mining"],
        "renewables": ["renewables", "renewable energy", "solar"],
        "powerline": ["powerline", "power"],
        "railways": ["railways", "rail", "road/rail survey"],
        "construction": ["construction"],
        "others": ["others", "security and surveillance", "dsp", "tender", "aviation", "manufacturing", "powerline inspection"],
    }

    DEAL_STAGE_MAPPINGS = {
        "lead": ["a. lead generated", "lead generated"],
        "qualified": ["b. sales qualified leads", "sales qualified leads"],
        "demo": ["c. demo done", "demo done"],
        "feasibility": ["d. feasibility", "feasibility"],
        "proposal": ["e. proposal/commercials sent", "proposal/commercials sent"],
        "negotiation": ["f. negotiations", "negotiations"],
        "won": ["g. project won", "project won", "h. work order received", "work order received"],
        "poc": ["i. poc", "poc"],
        "accrued": ["k. amount accrued", "amount accrued"],
        "invoice_sent": ["j. invoice sent", "invoice sent"],
        "completed": ["project completed"],
        "on_hold": ["m. projects on hold", "projects on hold"],
        "lost": ["l. project lost", "project lost"],
        "not_relevant": ["n. not relevant at the moment", "not relevant at the moment", "o. not relevant at all", "not relevant at all"],
    }

    WORK_TYPE_MAPPINGS = {
        "survey": ["survey", "volumetric survey", "topography survey", "lidar survey", "mine survey"],
        "inspection": ["inspection", "powerline inspection", "solar inspection", "thermography"],
        "imagery": ["imagery", "raw images", "videography", "raw images/videography", "video"],
        "hydrology": ["hydrology"],
        "others": ["others", "flood risk", "surveillance"],
    }

    @staticmethod
    def clean_status(value: Any) -> Optional[str]:
        """
        Normalize status value
        
        Args:
            value: Status value
            
        Returns:
            Normalized status code or None
        """
        if not value:
            return None

        value_lower = str(value).strip().lower()
        
        for normalized, variations in EnumCleaner.STATUS_MAPPINGS.items():
            if value_lower in variations:
                return normalized

        logger.debug(f"Unknown status: {value}")
        return value_lower

    @staticmethod
    def clean_sector(value: Any) -> Optional[str]:
        """Normalize sector/vertical"""
        if not value:
            return None

        value_lower = str(value).strip().lower()
        
        for normalized, variations in EnumCleaner.SECTOR_MAPPINGS.items():
            if value_lower in variations:
                return normalized

        logger.debug(f"Unknown sector: {value}")
        return value_lower

    @staticmethod
    def clean_deal_stage(value: Any) -> Optional[str]:
        """Normalize deal stage"""
        if not value:
            return None

        value_lower = str(value).strip().lower()
        
        for normalized, variations in EnumCleaner.DEAL_STAGE_MAPPINGS.items():
            if value_lower in variations:
                return normalized

        logger.debug(f"Unknown deal stage: {value}")
        return value_lower

    @staticmethod
    def clean_work_type(value: Any) -> Optional[str]:
        """Normalize work type"""
        if not value:
            return None

        value_lower = str(value).strip().lower()
        
        for normalized, variations in EnumCleaner.WORK_TYPE_MAPPINGS.items():
            if value_lower in variations:
                return normalized

        logger.debug(f"Unknown work type: {value}")
        return value_lower

    @staticmethod
    def parse_multiple_values(value: Any, delimiter: str = ",") -> List[str]:
        """Parse comma-separated or delimited values"""
        if not value:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, str):
            return [v.strip() for v in value.split(delimiter) if v.strip()]

        return []

    @staticmethod
    def is_valid_boolean(value: Any) -> Optional[bool]:
        """Parse boolean-like values"""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value_lower = value.strip().lower()
            if value_lower in ["true", "yes", "1", "y", "on"]:
                return True
            elif value_lower in ["false", "no", "0", "n", "off"]:
                return False

        return None
