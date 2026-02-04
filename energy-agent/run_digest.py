#!/usr/bin/env python3
"""
Run a full digest: collect, score, email.
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from collectors.arxiv import ArxivCollector
from collectors.sec import SECCollector
from scoring.engine import ScoringEngine
from data.database import SignalDatabase
from delivery.email import EmailDelivery

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_full_digest():
    """Run complete collection, scoring, and email delivery."""
    
    logger.info("=" * 60)
    logger.info("🔋 ENERGY INTELLIGENCE AGENT - FULL RUN")
    logger.info("=" * 60)
    
    # Date range: last 7 days
    date_to = datetime.now()
    date_from = date_to - timedelta(days=7)
    
    all_signals = []
    
    # Collect from ArXiv
    logger.info("\n📚 Collecting ArXiv papers...")
    try:
        arxiv = ArxivCollector()
        papers = arxiv.collect(date_from, date_to)
        all_signals.extend(papers)
        logger.info(f"   → {len(papers)} papers")
    except Exception as e:
        logger.error(f"   ✗ ArXiv failed: {e}")
    
    # Collect from SEC
    logger.info("\n📊 Collecting SEC filings...")
    try:
        sec = SECCollector()
        filings = sec.collect(date_from, date_to)
        all_signals.extend(filings)
        logger.info(f"   → {len(filings)} filings")
    except Exception as e:
        logger.error(f"   ✗ SEC failed: {e}")
    
    logger.info(f"\n📦 Total signals collected: {len(all_signals)}")
    
    # Score all signals
    logger.info("\n🎯 Scoring signals...")
    engine = ScoringEngine()
    scored_signals = []
    
    for signal in all_signals:
        score_result = engine.score(signal, all_signals)
        signal['score'] = score_result
        scored_signals.append(signal)
    
    # Sort by final score
    scored_signals.sort(key=lambda x: x['score']['final_score'], reverse=True)
    
    # Categorize
    critical = [s for s in scored_signals if s['score']['category'] == 'critical']
    strong = [s for s in scored_signals if s['score']['category'] == 'strong']
    interesting = [s for s in scored_signals if s['score']['category'] == 'interesting']
    
    logger.info(f"   🚨 Critical (≥12): {len(critical)}")
    logger.info(f"   ⭐ Strong (≥7): {len(strong)}")
    logger.info(f"   📋 Interesting (≥4): {len(interesting)}")
    
    # Print top 10
    logger.info("\n" + "=" * 60)
    logger.info("TOP 10 SIGNALS")
    logger.info("=" * 60)
    
    for i, sig in enumerate(scored_signals[:10], 1):
        score = sig['score']
        logger.info(f"\n{i}. [{score['final_score']:.1f}] {sig['title'][:60]}...")
        logger.info(f"   Domain: {sig.get('domain', 'N/A')} | Source: {sig['source']}")
        logger.info(f"   Category: {score['category']}")
    
    # Store in database
    logger.info("\n💾 Storing in database...")
    db = SignalDatabase()
    new_count = db.insert_signals(scored_signals)
    logger.info(f"   → {new_count} new signals stored")
    
    # Save scores
    for sig in scored_signals:
        if sig.get('id'):  # Only if we have a DB id
            db.save_score(
                signal_id=sig['id'],
                base_score=sig['score']['base_score'],
                attention_score=sig['score']['attention_score'],
                final_score=sig['score']['final_score'],
                breakdown=sig['score']['breakdown']
            )
    
    # Send email digest
    logger.info("\n📧 Sending digest email...")
    delivery = EmailDelivery()
    
    top_3 = scored_signals[:3]
    next_10 = scored_signals[3:13]
    
    stats = {
        'total_signals': len(all_signals),
        'by_source': {},
        'by_domain': {}
    }
    for sig in all_signals:
        src = sig.get('source', 'unknown')
        stats['by_source'][src] = stats['by_source'].get(src, 0) + 1
        dom = sig.get('domain', 'unknown')
        stats['by_domain'][dom] = stats['by_domain'].get(dom, 0) + 1
    
    if delivery.send_digest(top_3, next_10, stats):
        logger.info("   ✅ Digest sent!")
    else:
        logger.error("   ✗ Failed to send digest")
    
    # Send critical alerts
    for sig in critical:
        logger.info(f"\n🚨 Sending critical alert for: {sig['title'][:40]}...")
        delivery.send_critical_alert(sig)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ DIGEST RUN COMPLETE")
    logger.info("=" * 60)
    
    return scored_signals


if __name__ == "__main__":
    run_full_digest()
