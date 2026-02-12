#!/usr/bin/env python3
"""
Test Signals - Extract recent signals from energy agent database for testing
"""

import sqlite3
import json
from datetime import datetime, timedelta

def get_recent_signals(db_path="../energy-agent/data/signals.db", days=1):
    """Get recent signals from database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get signals from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        query = """
        SELECT title, score, domain, summary, created_at 
        FROM signals 
        WHERE created_at >= ? 
        ORDER BY score DESC, created_at DESC
        LIMIT 20
        """
        
        cursor.execute(query, (cutoff_str,))
        rows = cursor.fetchall()
        
        signals = []
        for row in rows:
            signals.append({
                "title": row[0],
                "score": float(row[1]) if row[1] else 0.0,
                "domain": row[2],
                "summary": row[3], 
                "created_at": row[4]
            })
        
        conn.close()
        return signals
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return []

def create_test_signals():
    """Create test signals for development"""
    return [
        {
            "title": "Nanovortex-driven optical diffusion breakthrough", 
            "score": 10.0,
            "domain": "SMR/Nuclear",
            "summary": "Revolutionary optical technique increases small modular reactor efficiency by 40% through quantum field manipulation",
            "created_at": "2026-02-11"
        },
        {
            "title": "Topological quantum error correction via braiding",
            "score": 9.2, 
            "domain": "Quantum Computing",
            "summary": "IBM achieves fault-tolerant quantum computing milestone, making commercial quantum systems viable by 2027",
            "created_at": "2026-02-11"
        },
        {
            "title": "Perovskite-silicon tandem solar breakthrough",
            "score": 8.8,
            "domain": "Solar Energy", 
            "summary": "New tandem design achieves 35% efficiency, could slash solar LCOE by 60% within 3 years",
            "created_at": "2026-02-11"
        }
    ]

def main():
    """Test signal extraction"""
    print("🔋 Energy Intelligence Signal Tester")
    
    # Try to get real signals from database
    real_signals = get_recent_signals()
    
    if real_signals:
        print(f"✅ Found {len(real_signals)} recent signals from database")
        signals = real_signals
    else:
        print("⚠️ No database signals found, using test data")
        signals = create_test_signals()
    
    # Show top signals
    print(f"\n📊 Top {min(len(signals), 5)} Signals:")
    for i, signal in enumerate(signals[:5]):
        print(f"{i+1}. {signal['title']}")
        print(f"   Score: {signal['score']}, Domain: {signal['domain']}")
        print(f"   Summary: {signal['summary'][:80]}...")
        print()
    
    # Save for testing
    output_file = f"test-signals-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(signals, f, indent=2)
    
    print(f"💾 Saved {len(signals)} signals to {output_file}")
    print(f"🧪 Test with: python3 auto-publisher.py")

if __name__ == "__main__":
    main()