#!/usr/bin/env python3
"""
Energy Intelligence Agent - Main Runner

Orchestrates data collection, scoring, and reporting.
"""
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.uspto import USPTOCollector
from collectors.arxiv import ArxivCollector
from scoring.engine import ScoringEngine, score_signals
from data.database import SignalDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'logs' / 'agent.log')
    ]
)
logger = logging.getLogger(__name__)


def collect_all(date_from: datetime = None, date_to: datetime = None) -> list:
    """Run all collectors and return combined signals."""
    if date_to is None:
        date_to = datetime.now()
    if date_from is None:
        date_from = date_to - timedelta(days=1)
    
    all_signals = []
    
    # USPTO Patents
    logger.info("Collecting USPTO patents...")
    try:
        uspto = USPTOCollector()
        patents = uspto.collect(date_from, date_to)
        all_signals.extend(patents)
        logger.info(f"Collected {len(patents)} patents")
    except Exception as e:
        logger.error(f"USPTO collection failed: {e}")
    
    # ArXiv Papers
    logger.info("Collecting ArXiv papers...")
    try:
        arxiv = ArxivCollector()
        papers = arxiv.collect(date_from, date_to)
        all_signals.extend(papers)
        logger.info(f"Collected {len(papers)} papers")
    except Exception as e:
        logger.error(f"ArXiv collection failed: {e}")
    
    logger.info(f"Total signals collected: {len(all_signals)}")
    return all_signals


def run_daily_collection():
    """Run daily collection, scoring, and store in database."""
    logger.info("=" * 60)
    logger.info("Starting daily collection run")
    logger.info("=" * 60)
    
    # Initialize database
    db = SignalDatabase()
    
    # Collect signals (yesterday's data)
    date_to = datetime.now()
    date_from = date_to - timedelta(days=1)
    signals = collect_all(date_from, date_to)
    
    # Store in database
    new_count = db.insert_signals(signals)
    logger.info(f"Stored {new_count} new signals ({len(signals) - new_count} duplicates)")
    
    # Score unscored signals
    engine = ScoringEngine()
    unscored = db.get_unscored_signals(limit=500)
    
    for signal in unscored:
        score_result = engine.score(signal, unscored)
        db.save_score(
            signal_id=signal['id'],
            base_score=score_result['base_score'],
            attention_score=score_result['attention_score'],
            final_score=score_result['final_score'],
            breakdown=score_result['breakdown']
        )
    
    logger.info(f"Scored {len(unscored)} signals")
    
    # Get top signals for report
    top_signals = db.get_top_signals(date_from=date_from, limit=15)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TOP SIGNALS")
    print("=" * 60)
    
    for i, sig in enumerate(top_signals[:10], 1):
        print(f"\n{i}. [{sig.get('final_score', 0):.1f}] {sig['title'][:70]}...")
        print(f"   Source: {sig['source']} | Domain: {sig.get('domain', 'unknown')}")
        print(f"   URL: {sig.get('url', 'N/A')}")
    
    # Database stats
    stats = db.get_stats()
    print("\n" + "=" * 60)
    print("DATABASE STATS")
    print("=" * 60)
    print(f"Total signals: {stats['total_signals']}")
    print(f"Scored: {stats['scored_signals']}")
    print(f"By source: {stats['by_source']}")
    print(f"By domain: {stats['by_domain']}")
    
    return top_signals


def test_collection():
    """Test collection without storing to database."""
    logger.info("Running test collection (7 days, no database)")
    
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    signals = collect_all(date_from, date_to)
    scored = score_signals(signals)
    
    print(f"\nCollected and scored {len(scored)} signals")
    print("\nTop 10 by score:")
    
    for i, sig in enumerate(scored[:10], 1):
        score = sig['score']
        print(f"\n{i}. [{score['final_score']:.1f}] {sig['title'][:60]}...")
        print(f"   Category: {score['category']} | Domain: {sig.get('domain')}")
        print(f"   Breakdown: {score['breakdown']}")
        print(f"   URL: {sig.get('url')}")


def main():
    parser = argparse.ArgumentParser(description='Energy Intelligence Agent')
    parser.add_argument('--mode', choices=['daily', 'test', 'stats'], default='test',
                       help='Run mode: daily (full run), test (no DB), stats (show DB stats)')
    parser.add_argument('--days', type=int, default=1,
                       help='Number of days to look back')
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    (Path(__file__).parent / 'logs').mkdir(exist_ok=True)
    
    if args.mode == 'daily':
        run_daily_collection()
    elif args.mode == 'test':
        test_collection()
    elif args.mode == 'stats':
        db = SignalDatabase()
        stats = db.get_stats()
        print(f"Database stats: {stats}")


if __name__ == "__main__":
    main()
