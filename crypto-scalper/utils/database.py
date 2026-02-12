"""
Database utilities for storing trade logs and performance data.
Uses SQLite for simplicity and portability.
"""

import sqlite3
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class DatabaseManager:
    """Manages SQLite database for trade logging and analytics."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    pair TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    size REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    entry_time TEXT NOT NULL,
                    exit_time TEXT,
                    pnl REAL,
                    fees REAL DEFAULT 0,
                    exit_reason TEXT,
                    duration_minutes REAL,
                    signals_used TEXT,
                    is_paper_trade BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    indicator TEXT NOT NULL,
                    strength REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    was_traded BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    starting_balance REAL NOT NULL,
                    ending_balance REAL NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    total_fees REAL DEFAULT 0,
                    max_drawdown REAL DEFAULT 0,
                    pairs_traded TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Risk events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS risk_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    data TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_entry_time ON trades(entry_time)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_pair ON signals(pair)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
            
    def log_trade(self, trade_data: dict) -> bool:
        """Log a completed trade to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (id, pair, direction, size, entry_price, exit_price, entry_time, 
                 exit_time, pnl, fees, exit_reason, duration_minutes, signals_used, is_paper_trade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade_data.get('id'),
                trade_data.get('pair'),
                trade_data.get('direction'),
                trade_data.get('size'),
                trade_data.get('entry_price'),
                trade_data.get('exit_price'),
                trade_data.get('entry_time'),
                trade_data.get('exit_time'),
                trade_data.get('pnl'),
                trade_data.get('fees', 0),
                trade_data.get('exit_reason'),
                trade_data.get('duration_minutes'),
                json.dumps(trade_data.get('signals_used', [])),
                trade_data.get('is_paper_trade', True)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log trade: {e}")
            return False
            
    def log_signal(self, signal_data: dict) -> bool:
        """Log a trading signal to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO signals 
                (pair, direction, indicator, strength, price, timestamp, was_traded)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                signal_data.get('pair'),
                signal_data.get('direction'),
                signal_data.get('indicator'),
                signal_data.get('strength'),
                signal_data.get('price'),
                signal_data.get('timestamp'),
                signal_data.get('was_traded', False)
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log signal: {e}")
            return False
            
    def log_daily_performance(self, date: str, performance_data: dict) -> bool:
        """Log daily performance metrics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use INSERT OR REPLACE to handle updates
            cursor.execute("""
                INSERT OR REPLACE INTO performance 
                (date, starting_balance, ending_balance, total_trades, winning_trades, 
                 total_pnl, total_fees, max_drawdown, pairs_traded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date,
                performance_data.get('starting_balance'),
                performance_data.get('ending_balance'),
                performance_data.get('total_trades', 0),
                performance_data.get('winning_trades', 0),
                performance_data.get('total_pnl', 0),
                performance_data.get('total_fees', 0),
                performance_data.get('max_drawdown', 0),
                json.dumps(performance_data.get('pairs_traded', []))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log daily performance: {e}")
            return False
            
    def log_risk_event(self, event_type: str, description: str, 
                      severity: str = "INFO", data: dict = None) -> bool:
        """Log a risk management event."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO risk_events (event_type, description, severity, data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event_type,
                description,
                severity,
                json.dumps(data) if data else None,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log risk event: {e}")
            return False
            
    def get_trade_statistics(self, days: int = 30) -> dict:
        """Get trade statistics for the specified number of days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate date threshold
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get trade statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(pnl) as total_pnl,
                    AVG(pnl) as avg_pnl,
                    SUM(fees) as total_fees,
                    AVG(duration_minutes) as avg_duration,
                    MIN(pnl) as worst_trade,
                    MAX(pnl) as best_trade
                FROM trades 
                WHERE exit_time >= ? AND exit_time IS NOT NULL
            """, (threshold_date,))
            
            stats = cursor.fetchone()
            
            if stats[0] == 0:  # No trades
                return {
                    'total_trades': 0,
                    'winning_trades': 0,
                    'win_rate': 0.0,
                    'total_pnl': 0.0,
                    'avg_pnl': 0.0,
                    'total_fees': 0.0,
                    'avg_duration': 0.0,
                    'profit_factor': 0.0,
                    'worst_trade': 0.0,
                    'best_trade': 0.0
                }
            
            # Calculate additional metrics
            total_trades = stats[0]
            winning_trades = stats[1]
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # Get profit factor (gross profit / gross loss)
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN pnl > 0 THEN pnl ELSE 0 END) as gross_profit,
                    SUM(CASE WHEN pnl < 0 THEN ABS(pnl) ELSE 0 END) as gross_loss
                FROM trades 
                WHERE exit_time >= ? AND exit_time IS NOT NULL
            """, (threshold_date,))
            
            profit_loss = cursor.fetchone()
            profit_factor = (profit_loss[0] / profit_loss[1]) if profit_loss[1] > 0 else float('inf')
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': stats[2] or 0,
                'avg_pnl': stats[3] or 0,
                'total_fees': stats[4] or 0,
                'avg_duration': stats[5] or 0,
                'profit_factor': profit_factor,
                'worst_trade': stats[6] or 0,
                'best_trade': stats[7] or 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get trade statistics: {e}")
            return {}
            
    def get_pair_performance(self, days: int = 7) -> List[dict]:
        """Get performance breakdown by trading pair."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT 
                    pair,
                    COUNT(*) as trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(pnl) as total_pnl,
                    AVG(pnl) as avg_pnl,
                    SUM(fees) as fees
                FROM trades 
                WHERE exit_time >= ? AND exit_time IS NOT NULL
                GROUP BY pair
                ORDER BY total_pnl DESC
            """, (threshold_date,))
            
            results = []
            for row in cursor.fetchall():
                win_rate = (row[2] / row[1]) * 100 if row[1] > 0 else 0
                results.append({
                    'pair': row[0],
                    'trades': row[1],
                    'wins': row[2],
                    'win_rate': win_rate,
                    'total_pnl': row[3] or 0,
                    'avg_pnl': row[4] or 0,
                    'fees': row[5] or 0
                })
                
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get pair performance: {e}")
            return []
            
    def get_recent_trades(self, limit: int = 50) -> List[dict]:
        """Get recent trades."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM trades 
                ORDER BY entry_time DESC 
                LIMIT ?
            """, (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            trades = []
            
            for row in cursor.fetchall():
                trade = dict(zip(columns, row))
                if trade['signals_used']:
                    trade['signals_used'] = json.loads(trade['signals_used'])
                trades.append(trade)
                
            conn.close()
            return trades
            
        except Exception as e:
            self.logger.error(f"Failed to get recent trades: {e}")
            return []
            
    def get_signal_effectiveness(self, days: int = 7) -> List[dict]:
        """Analyze effectiveness of different signal types."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT 
                    indicator,
                    direction,
                    COUNT(*) as signal_count,
                    AVG(strength) as avg_strength,
                    SUM(CASE WHEN was_traded = 1 THEN 1 ELSE 0 END) as signals_traded
                FROM signals 
                WHERE timestamp >= ?
                GROUP BY indicator, direction
                ORDER BY signal_count DESC
            """, (threshold_date,))
            
            results = []
            for row in cursor.fetchall():
                trade_rate = (row[4] / row[2]) * 100 if row[2] > 0 else 0
                results.append({
                    'indicator': row[0],
                    'direction': row[1],
                    'signal_count': row[2],
                    'avg_strength': row[3],
                    'signals_traded': row[4],
                    'trade_rate': trade_rate
                })
                
            conn.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get signal effectiveness: {e}")
            return []
            
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to manage database size."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Delete old signals (keep trades longer for analysis)
            cursor.execute("DELETE FROM signals WHERE timestamp < ?", (cutoff_date,))
            
            # Delete old risk events
            cursor.execute("DELETE FROM risk_events WHERE timestamp < ?", (cutoff_date,))
            
            rows_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if rows_deleted > 0:
                self.logger.info(f"Cleaned up {rows_deleted} old records")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database."""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False