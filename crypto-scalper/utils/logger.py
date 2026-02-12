"""
Logging configuration for the crypto scalper bot.
Provides structured logging with file rotation and different log levels.
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Add colors to console log output for better readability."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(config: dict, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for the crypto scalper.
    
    Args:
        config: Configuration dictionary
        log_file: Optional log file path override
        
    Returns:
        Configured logger instance
    """
    
    # Get logging configuration
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_format = log_config.get('format', 
                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    else:
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'crypto_scalper_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = ColoredFormatter(log_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_config.get('file_rotation', True):
        max_bytes = parse_size(log_config.get('max_file_size', '10MB'))
        backup_count = log_config.get('backup_count', 5)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
    else:
        file_handler = logging.FileHandler(log_file)
    
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(log_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Set third-party library log levels to reduce noise
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('websocket').setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    return logger


def parse_size(size_str: str) -> int:
    """Parse size string like '10MB' into bytes."""
    size_str = size_str.strip().upper()
    for suffix, mult in [('GB', 1073741824), ('MB', 1048576), ('KB', 1024), ('B', 1)]:
        if size_str.endswith(suffix):
            return int(float(size_str[:-len(suffix)]) * mult)
    return int(size_str)

class TradeLogger:
    """Specialized logger for trade-related events."""
    
    def __init__(self, name: str = "trades"):
        self.logger = logging.getLogger(name)
        
    def log_signal(self, pair: str, direction: str, indicator: str, 
                  strength: float, price: float):
        """Log a trading signal."""
        self.logger.info(
            f"SIGNAL | {pair} | {direction.upper()} | {indicator} | "
            f"Strength: {strength:.2f} | Price: {price:.4f}"
        )
        
    def log_trade_entry(self, pair: str, direction: str, size: float, 
                       entry_price: float, take_profit: float, stop_loss: float):
        """Log trade entry."""
        self.logger.info(
            f"ENTRY | {pair} | {direction.upper()} | Size: {size:.4f} | "
            f"Entry: {entry_price:.4f} | TP: {take_profit:.4f} | SL: {stop_loss:.4f}"
        )
        
    def log_trade_exit(self, pair: str, direction: str, exit_price: float, 
                      pnl: float, reason: str, duration: float):
        """Log trade exit."""
        pnl_status = "PROFIT" if pnl >= 0 else "LOSS"
        self.logger.info(
            f"EXIT | {pair} | {direction.upper()} | Exit: {exit_price:.4f} | "
            f"{pnl_status}: ${pnl:.2f} | Reason: {reason} | Duration: {duration:.1f}min"
        )
        
    def log_risk_event(self, event_type: str, description: str, severity: str = "INFO"):
        """Log risk management event."""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(f"RISK | {event_type} | {description}")
        
    def log_performance_summary(self, stats: dict):
        """Log performance summary."""
        self.logger.info(
            f"PERFORMANCE | Total Trades: {stats.get('total_trades', 0)} | "
            f"Win Rate: {stats.get('win_rate', 0):.1f}% | "
            f"Total P&L: ${stats.get('total_pnl', 0):.2f} | "
            f"Profit Factor: {stats.get('profit_factor', 0):.2f}"
        )


class AlertLogger:
    """Logger for critical alerts and notifications."""
    
    def __init__(self, name: str = "alerts"):
        self.logger = logging.getLogger(name)
        
        # Create separate handler for alerts with higher visibility
        alert_handler = logging.StreamHandler(sys.stdout)
        alert_formatter = ColoredFormatter(
            '🚨 %(asctime)s - ALERT - %(message)s'
        )
        alert_handler.setFormatter(alert_formatter)
        alert_handler.setLevel(logging.WARNING)
        
        self.logger.addHandler(alert_handler)
        self.logger.setLevel(logging.WARNING)
        
    def daily_loss_limit(self, current_loss: float, limit: float):
        """Alert for daily loss limit."""
        self.logger.warning(
            f"Daily loss limit reached: ${current_loss:.2f} / ${limit:.2f}"
        )
        
    def consecutive_losses(self, count: int):
        """Alert for consecutive losses."""
        self.logger.warning(f"Consecutive losses: {count} trades")
        
    def trading_halted(self, reason: str):
        """Alert for trading halt."""
        self.logger.critical(f"Trading HALTED: {reason}")
        
    def large_drawdown(self, drawdown_pct: float):
        """Alert for large drawdown."""
        self.logger.error(f"Large drawdown detected: {drawdown_pct:.1f}%")
        
    def exchange_error(self, exchange: str, error: str):
        """Alert for exchange connectivity issues."""
        self.logger.error(f"Exchange {exchange} error: {error}")
        
    def signal_overload(self, pair: str, signal_count: int):
        """Alert for too many signals (possible market noise)."""
        self.logger.warning(f"Signal overload on {pair}: {signal_count} signals")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def log_system_info():
    """Log system information at startup."""
    logger = logging.getLogger(__name__)
    
    import platform
    import psutil
    
    logger.info("="*50)
    logger.info("CRYPTO SCALPER BOT STARTUP")
    logger.info("="*50)
    logger.info(f"System: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"CPU: {psutil.cpu_count()} cores")
    logger.info(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f}GB")
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)


def log_config_summary(config: dict):
    """Log configuration summary."""
    logger = logging.getLogger(__name__)
    
    logger.info("Configuration Summary:")
    logger.info(f"  Paper Trading: {config['trading']['paper_trading']}")
    logger.info(f"  Starting Capital: ${config['trading']['starting_capital']}")
    logger.info(f"  Max Position Size: {config['trading']['risk']['max_position_size_percent']}%")
    logger.info(f"  Max Leverage: {config['trading']['risk']['max_leverage']}x")
    logger.info(f"  Daily Loss Limit: {config['trading']['risk']['daily_loss_limit_percent']}%")
    logger.info(f"  Min Signals Required: {config['trading']['signals']['min_confirming_signals']}")
    logger.info(f"  Primary Exchange: {config['exchanges']['primary']}")
    
    # Log enabled pairs
    try:
        import yaml
        with open('config/pairs.yaml', 'r') as f:
            pairs_config = yaml.safe_load(f)
        enabled_pairs = [pair for pair, cfg in pairs_config['pairs'].items() 
                        if cfg.get('enabled', True)]
        logger.info(f"  Trading Pairs: {', '.join(enabled_pairs)}")
    except Exception:
        logger.info("  Trading Pairs: Configuration file not found")


# Context manager for temporary log level changes
class LogLevel:
    """Context manager to temporarily change log level."""
    
    def __init__(self, level: str, logger_name: Optional[str] = None):
        self.new_level = getattr(logging, level.upper())
        self.logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
        self.old_level = self.logger.level
        
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)