"""Analytics services for business insights"""

from .sales import SalesAnalytics
from .operations import OperationsAnalytics
from .finance import FinanceAnalytics
from .risk import RiskAnalytics
from .cross_board import CrossBoardAnalytics

__all__ = [
    "SalesAnalytics",
    "OperationsAnalytics",
    "FinanceAnalytics",
    "RiskAnalytics",
    "CrossBoardAnalytics",
]
