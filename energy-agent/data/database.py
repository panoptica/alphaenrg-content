"""
Database module for storing and retrieving signals.
Uses SQLite for Phase 1 simplicity.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SignalDatabase:
    """SQLite database for signal storage and retrieval."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).resolve().parent / "signals.db")
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Signals table - raw collected data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    title TEXT,
                    abstract TEXT,
                    signal_date DATE,
                    url TEXT,
                    domain TEXT,
                    raw_data JSON,
                    entities JSON,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, source_id)
                )
            """)
            
            # Scored signals table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scored_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER REFERENCES signals(id),
                    base_score REAL,
                    attention_score REAL,
                    final_score REAL,
                    score_breakdown JSON,
                    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(signal_id)
                )
            """)
            
            # User ratings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER REFERENCES signals(id),
                    rating INTEGER,  -- 1=down, 2=neutral, 3=up, 4=interesting, 5=excellent
                    comment TEXT,
                    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Convergence clusters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS convergence_clusters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_ids JSON,  -- List of signal IDs in cluster
                    cluster_type TEXT,  -- 'temporal', 'entity', 'supply_chain'
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences (learned from ratings)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_type TEXT,  -- 'domain', 'player_tier', 'trl', 'attention'
                    preference_key TEXT,
                    weight REAL DEFAULT 1.0,
                    sample_count INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(preference_type, preference_key)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(signal_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_domain ON signals(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scored_final ON scored_signals(final_score)")
            
            conn.commit()
    
    def insert_signal(self, signal: Dict[str, Any]) -> Optional[int]:
        """Insert a signal, returning its ID. Returns None if duplicate."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO signals (source, source_id, title, abstract, signal_date, url, domain, raw_data, entities)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    signal['source'],
                    signal['source_id'],
                    signal.get('title', ''),
                    signal.get('abstract', ''),
                    signal.get('date', datetime.now()).strftime('%Y-%m-%d') if signal.get('date') else None,
                    signal.get('url', ''),
                    signal.get('domain', ''),
                    json.dumps(signal.get('raw_data', {})),
                    json.dumps(signal.get('entities', {}))
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Duplicate signal
                return None
    
    def insert_signals(self, signals: List[Dict[str, Any]]) -> int:
        """Insert multiple signals using a single connection. Returns count of new signals inserted."""
        count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for signal in signals:
                try:
                    cursor.execute("""
                        INSERT INTO signals (source, source_id, title, abstract, signal_date, url, domain, raw_data, entities)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        signal["source"],
                        signal["source_id"],
                        signal.get("title", ""),
                        signal.get("abstract", ""),
                        signal.get("date", datetime.now()).strftime("%Y-%m-%d") if signal.get("date") else None,
                        signal.get("url", ""),
                        signal.get("domain", ""),
                        json.dumps(signal.get("raw_data", {})),
                        json.dumps(signal.get("entities", {}))
                    ))
                    count += 1
                except sqlite3.IntegrityError:
                    pass
            conn.commit()
        return count
    
    def get_unscored_signals(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get signals that haven't been scored yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.* FROM signals s
                LEFT JOIN scored_signals ss ON s.id = ss.signal_id
                WHERE ss.id IS NULL
                ORDER BY s.signal_date DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def get_top_signals(self, date_from: datetime = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scored signals."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT s.*, ss.final_score, ss.score_breakdown
                FROM signals s
                JOIN scored_signals ss ON s.id = ss.signal_id
            """
            params = []
            
            if date_from:
                query += " WHERE s.signal_date >= ?"
                params.append(date_from.strftime('%Y-%m-%d'))
            
            query += " ORDER BY ss.final_score DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def save_score(self, signal_id: int, base_score: float, attention_score: float, 
                   final_score: float, breakdown: Dict) -> None:
        """Save score for a signal."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO scored_signals 
                (signal_id, base_score, attention_score, final_score, score_breakdown)
                VALUES (?, ?, ?, ?, ?)
            """, (signal_id, base_score, attention_score, final_score, json.dumps(breakdown)))
            conn.commit()
    
    def save_rating(self, signal_id: int, rating: int, comment: str = None) -> None:
        """Save user rating for a signal."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_ratings (signal_id, rating, comment)
                VALUES (?, ?, ?)
            """, (signal_id, rating, comment))
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM signals")
            total_signals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scored_signals")
            scored_signals = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM user_ratings")
            total_ratings = cursor.fetchone()[0]
            
            cursor.execute("SELECT source, COUNT(*) FROM signals GROUP BY source")
            by_source = dict(cursor.fetchall())
            
            cursor.execute("SELECT domain, COUNT(*) FROM signals WHERE domain IS NOT NULL GROUP BY domain")
            by_domain = dict(cursor.fetchall())
            
            return {
                'total_signals': total_signals,
                'scored_signals': scored_signals,
                'total_ratings': total_ratings,
                'by_source': by_source,
                'by_domain': by_domain
            }
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to dictionary."""
        d = dict(row)
        # Parse JSON fields
        for field in ['raw_data', 'entities', 'score_breakdown']:
            if field in d and d[field]:
                try:
                    d[field] = json.loads(d[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        return d


if __name__ == "__main__":
    # Test database
    db = SignalDatabase()
    print("Database initialized")
    print(f"Stats: {db.get_stats()}")
