#!/usr/bin/env python3
"""
Energy Intelligence Agent - Main Runner with Multi-Platform Publishing

Orchestrates data collection, scoring, reporting, and publishing to social platforms.
"""
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.uspto import USPTOCollector
from collectors.arxiv import ArxivCollector
from collectors.sec import SECCollector
from collectors.osint import OSINTCollector
from collectors.lens import LensPatentCollector, LensScholarCollector
from scoring.engine import ScoringEngine, score_signals
from data.database import SignalDatabase
from multi_platform_publisher import MultiPlatformPublisher

# Load environment variables
load_dotenv()

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
    
    # SEC Filings
    logger.info("Collecting SEC filings...")
    try:
        sec = SECCollector()
        filings = sec.collect(date_from, date_to)
        all_signals.extend(filings)
        logger.info(f"Collected {len(filings)} SEC filings")
    except Exception as e:
        logger.error(f"SEC collection failed: {e}")
    
    # Lens.org Patents
    logger.info("Collecting Lens.org patents...")
    try:
        lens_pat = LensPatentCollector()
        lens_patents = lens_pat.collect(date_from, date_to)
        all_signals.extend(lens_patents)
        logger.info(f"Collected {len(lens_patents)} Lens patents")
    except Exception as e:
        logger.error(f"Lens patent collection failed: {e}")
    
    # Lens.org Scholarly Articles
    logger.info("Collecting Lens.org scholarly articles...")
    try:
        lens_sch = LensScholarCollector()
        lens_papers = lens_sch.collect(date_from, date_to)
        all_signals.extend(lens_papers)
        logger.info(f"Collected {len(lens_papers)} Lens scholarly articles")
    except Exception as e:
        logger.error(f"Lens scholar collection failed: {e}")
    
    # OSINT (Reddit + News from Kali)
    logger.info("Collecting OSINT signals from Kali...")
    try:
        osint = OSINTCollector()
        social_signals = osint.collect(days_back=1)
        all_signals.extend(social_signals)
        logger.info(f"Collected {len(social_signals)} OSINT signals")
    except Exception as e:
        logger.error(f"OSINT collection failed: {e}")
    
    logger.info(f"Total signals collected: {len(all_signals)}")
    return all_signals


def create_intelligence_summary(top_signals, total_signals_count):
    """Create intelligence summary for publishing"""
    
    if len(top_signals) < 4:
        return "insufficient signal strength for reliable intelligence synthesis"
    
    # Extract top 4 signals for summary
    top_4 = top_signals[:4]
    
    # Create engaging intelligence text
    intelligence_lines = []
    
    for signal in top_4:
        title = signal.get('title', 'Unknown signal')
        score = signal.get('final_score', 0)
        domain = signal.get('domain', 'general')
        
        # Create condensed insight
        if 'quantum' in title.lower():
            icon = "🔬"
        elif 'battery' in title.lower() or 'storage' in title.lower():
            icon = "🔋"
        elif 'wind' in title.lower() or 'solar' in title.lower():
            icon = "🌊"
        elif 'fusion' in title.lower():
            icon = "⚛️"
        elif 'grid' in title.lower():
            icon = "⚡"
        elif 'hydrogen' in title.lower():
            icon = "💨"
        else:
            icon = "💡"
        
        # Shorten and enhance the title
        clean_title = title.replace('patent', '').replace('filing', '').replace('paper', '')
        clean_title = clean_title.strip()[:80] + ('...' if len(clean_title) > 80 else '')
        
        intelligence_lines.append(f"{icon} {clean_title}")
    
    return '\n'.join(intelligence_lines)


def send_email_digest(top_signals, total_signals_count, new_signals_count):
    """Send email digest to oc@cloudmonkey.io"""
    
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    if not email_user or not email_password:
        logger.warning("Email credentials not configured")
        return False
    
    # Create email content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    subject = f"AlphaENRG Daily Intelligence Brief • {datetime.now().strftime('%B %d, %Y')}"
    
    # Email body
    intelligence_summary = create_intelligence_summary(top_signals, total_signals_count)
    
    body = f"""Energy Intelligence Brief • {timestamp}

{intelligence_summary}

Signals Processed: {total_signals_count} total, {new_signals_count} new
Top Signals: {len(top_signals)} high-impact developments identified

Full analysis available via AlphaENRG intelligence system.

---
This is an automated intelligence digest from AlphaENRG.
"""
    
    # Send email
    try:
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = "oc@cloudmonkey.io"
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        server.send_message(msg)
        server.quit()
        
        logger.info("✅ Email digest sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email sending failed: {e}")
        return False


def publish_to_social_platforms(intelligence_summary, signals_count):
    """Publish intelligence to social media platforms"""
    
    try:
        publisher = MultiPlatformPublisher()
        results = publisher.publish_daily_intelligence(intelligence_summary, signals_count)
        
        # Log results
        successful_platforms = [platform for platform, result in results.items() if result.get('success')]
        failed_platforms = [platform for platform, result in results.items() if not result.get('success')]
        
        if successful_platforms:
            logger.info(f"✅ Published to: {', '.join(successful_platforms).upper()}")
        
        if failed_platforms:
            logger.warning(f"❌ Failed to publish to: {', '.join(failed_platforms).upper()}")
        
        return len(successful_platforms) > 0
        
    except Exception as e:
        logger.error(f"❌ Social media publishing failed: {e}")
        return False


def run_daily_collection_with_publishing():
    """Run daily collection, scoring, store in database, and publish to all platforms."""
    logger.info("=" * 60)
    logger.info("Starting daily collection and publishing run")
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
    
    # Create intelligence summary
    intelligence_summary = create_intelligence_summary(top_signals, len(signals))
    
    # Print summary to console
    print("\n" + "=" * 60)
    print("DAILY INTELLIGENCE SUMMARY")
    print("=" * 60)
    print(intelligence_summary)
    print(f"\nSignals: {len(signals)} collected, {new_count} new")
    
    # Send email digest
    logger.info("📧 Sending email digest...")
    email_success = send_email_digest(top_signals, len(signals), new_count)
    
    # Publish to social platforms
    logger.info("📱 Publishing to social platforms...")
    social_success = publish_to_social_platforms(intelligence_summary, len(signals))
    
    # Final status
    print("\n" + "=" * 60)
    print("PUBLISHING RESULTS")
    print("=" * 60)
    print(f"📧 Email: {'✅ SUCCESS' if email_success else '❌ FAILED'}")
    print(f"📱 Social: {'✅ SUCCESS' if social_success else '❌ FAILED'}")
    
    return top_signals


def run_daily_collection():
    """Run daily collection, scoring, and store in database (original function)."""
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
    parser = argparse.ArgumentParser(description='Energy Intelligence Agent with Publishing')
    parser.add_argument('--mode', choices=['daily', 'publish', 'test', 'stats'], default='test',
                       help='Run mode: daily (DB only), publish (DB + social), test (no DB), stats (show DB stats)')
    parser.add_argument('--days', type=int, default=1,
                       help='Number of days to look back')
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    (Path(__file__).parent / 'logs').mkdir(exist_ok=True)
    
    if args.mode == 'daily':
        run_daily_collection()
    elif args.mode == 'publish':
        run_daily_collection_with_publishing()
    elif args.mode == 'test':
        test_collection()
    elif args.mode == 'stats':
        db = SignalDatabase()
        stats = db.get_stats()
        print(f"Database stats: {stats}")


if __name__ == "__main__":
    main()