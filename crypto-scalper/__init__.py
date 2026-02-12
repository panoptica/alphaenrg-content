"""
Crypto Scalper Bot - Multi-signal momentum scalping bot for cryptocurrency trading.

Version: 1.0.0
Author: Crypto Scalper Development Team
License: MIT

This package provides a comprehensive crypto trading bot with:
- Multi-signal technical analysis
- Paper trading mode for safe testing
- Risk management and position sizing
- Real-time market data integration
- Comprehensive logging and analytics
"""

__version__ = "1.0.0"
__author__ = "Crypto Scalper Development Team"
__license__ = "MIT"

# Main components
from .main import CryptoScalperBot
from .paper_trader import PaperTradingExecutor

__all__ = [
    'CryptoScalperBot',
    'PaperTradingExecutor'
]