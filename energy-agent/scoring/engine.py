"""
Signal Scoring Engine

Implements the scoring model from the spec:
- Base score (0-15 points): convergence, gov alignment, capital, TRL, player, M&A, impact, macro
- Attention multiplier (0-3): citations, stock movement, GitHub stars, media coverage
- Final score = Base × (1 + Attention × 0.2)

Thresholds:
- ≥12: Critical alert
- ≥7: Strong signal (Top 3)
- 4-6: Interesting (watch list)
- <4: Filtered
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import (
    TIER_1_COMPANIES, TIER_1_VCS, TIER_2_COMPANIES,
    TECHNOLOGY_KEYWORDS, SCORE_CRITICAL, SCORE_STRONG, SCORE_INTERESTING
)

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Score signals based on the defined model."""
    
    def __init__(self, user_preferences: Dict[str, float] = None):
        """
        Initialize scoring engine.
        
        Args:
            user_preferences: Learned weights from user feedback (domain -> weight)
        """
        self.user_preferences = user_preferences or {}
    
    def score(self, signal: Dict[str, Any], related_signals: List[Dict] = None) -> Dict[str, Any]:
        """
        Score a signal.
        
        Args:
            signal: The signal to score
            related_signals: Other signals in same time window (for convergence detection)
            
        Returns:
            Dict with base_score, attention_score, final_score, and breakdown
        """
        breakdown = {}
        
        # Base score components
        base_score = 0
        
        # 1. Convergence (+3): Multiple independent sources
        convergence_score = self._score_convergence(signal, related_signals or [])
        base_score += convergence_score
        breakdown['convergence'] = convergence_score
        
        # 2. Government alignment (+2)
        gov_score = self._score_government_alignment(signal)
        base_score += gov_score
        breakdown['government'] = gov_score
        
        # 3. Capital commitment (+2-3)
        capital_score = self._score_capital(signal)
        base_score += capital_score
        breakdown['capital'] = capital_score
        
        # 4. TRL 5-7 (+2)
        trl_score = self._score_trl(signal)
        base_score += trl_score
        breakdown['trl'] = trl_score
        
        # 5. Player credibility (+1-2)
        player_score = self._score_player(signal)
        base_score += player_score
        breakdown['player'] = player_score
        
        # 6. M&A likelihood (+1)
        ma_score = self._score_ma_likelihood(signal)
        base_score += ma_score
        breakdown['ma_likelihood'] = ma_score
        
        # 7. Novelty & impact (+1)
        impact_score = self._score_impact(signal)
        base_score += impact_score
        breakdown['impact'] = impact_score
        
        # 8. Macro tailwind (+1)
        macro_score = self._score_macro(signal)
        base_score += macro_score
        breakdown['macro'] = macro_score
        
        # Attention multiplier (0-3)
        attention_score = self._score_attention(signal)
        breakdown['attention'] = attention_score
        
        # Final score calculation
        final_score = base_score * (1 + attention_score * 0.2)
        
        # Apply user preference weighting if available
        domain = signal.get('domain')
        if domain and domain in self.user_preferences:
            preference_weight = self.user_preferences[domain]
            final_score *= preference_weight
            breakdown['preference_adjustment'] = preference_weight
        
        # Determine threshold category
        if final_score >= SCORE_CRITICAL:
            category = 'critical'
        elif final_score >= SCORE_STRONG:
            category = 'strong'
        elif final_score >= SCORE_INTERESTING:
            category = 'interesting'
        else:
            category = 'filtered'
        
        return {
            'base_score': round(base_score, 2),
            'attention_score': round(attention_score, 2),
            'final_score': round(final_score, 2),
            'category': category,
            'breakdown': breakdown
        }
    
    def _score_convergence(self, signal: Dict, related: List[Dict]) -> float:
        """
        +3 if ≥2 independent sources on same tech/company within 90 days.
        """
        if not related:
            return 0
        
        signal_entities = signal.get('entities', {})
        signal_companies = set(signal_entities.get('companies', []))
        signal_techs = set(signal_entities.get('technologies', []))
        
        matches = 0
        for other in related:
            if other.get('source_id') == signal.get('source_id'):
                continue
            if other.get('source') == signal.get('source'):
                continue  # Must be different source type
                
            other_entities = other.get('entities', {})
            other_companies = set(other_entities.get('companies', []))
            other_techs = set(other_entities.get('technologies', []))
            
            # Check for overlap
            if signal_companies & other_companies or signal_techs & other_techs:
                matches += 1
        
        if matches >= 2:
            return 3
        elif matches == 1:
            return 1.5
        return 0
    
    def _score_government_alignment(self, signal: Dict) -> float:
        """
        +2 if matches announced policy (IRA, CHIPS, Net Zero, etc.)
        """
        gov_keywords = [
            'inflation reduction act', 'ira', 'chips act', 'arpa-e',
            'net zero', 'green deal', 'repowereu', 'doe grant',
            'department of energy', 'nrc', 'nuclear regulatory',
            'innovate uk', 'ukri', 'horizon europe'
        ]
        
        text = f"{signal.get('title', '')} {signal.get('abstract', '')}".lower()
        
        for kw in gov_keywords:
            if kw in text:
                return 2
        
        # Check source - if from government, automatic alignment
        if signal.get('source') in ['doe', 'ukri', 'arpa-e', 'nrc']:
            return 2
        
        return 0
    
    def _score_capital(self, signal: Dict) -> float:
        """
        +2-3 based on funding level.
        US: ≥$100M VC/PE OR ≥$50M gov grant (+2)
        UK/EU: ≥£20M VC/PE OR ≥£10M gov grant (+3)
        Mega-rounds ≥$500M: +3
        """
        # This requires funding data - for patents, default to 0
        # Will be populated when we add SEC/Crunchbase collectors
        return 0
    
    def _score_trl(self, signal: Dict) -> float:
        """
        +2 for TRL 5-7 (component validation through field trial)
        """
        trl_keywords = {
            7: ["field trial", "pilot", "commercial deployment", "customer validation", "production"],
            6: ["demonstration", "prototype", "system test", "validated"],
            5: ["component", "subsystem", "proof of concept"],
        }
        
        text = f"{signal.get('title', '')} {signal.get('abstract', '')}".lower()
        
        for trl, keywords in sorted(trl_keywords.items(), reverse=True):
            for kw in keywords:
                if kw in text:
                    if trl >= 5:
                        return 2
        return 0
    
    def _score_player(self, signal: Dict) -> float:
        """
        +2 for Tier 1 player, +1 for Tier 2
        """
        entities = signal.get('entities', {})
        companies = entities.get('companies', [])
        
        # Check explicit tier if set
        if entities.get('tier') == 1:
            return 2
        if entities.get('tier') == 2:
            return 1
        
        # Check company names
        text = f"{signal.get('title', '')} {signal.get('abstract', '')} {' '.join(companies)}".lower()
        
        for company in TIER_1_COMPANIES + TIER_1_VCS:
            if company.lower() in text:
                return 2
        
        for company in TIER_2_COMPANIES:
            if company.lower() in text:
                return 1
        
        return 0
    
    def _score_ma_likelihood(self, signal: Dict) -> float:
        """
        +1 if strategic acquirer active in space + startup fills gap
        """
        # M&A signals - harder to detect from patents alone
        # Look for partnership/licensing language
        ma_keywords = ['license', 'partnership', 'collaboration', 'joint venture', 'acquisition']
        text = f"{signal.get('title', '')} {signal.get('abstract', '')}".lower()
        
        for kw in ma_keywords:
            if kw in text:
                return 1
        return 0
    
    def _score_impact(self, signal: Dict) -> float:
        """
        +1 for 5-10x improvement claims + commercially viable
        """
        impact_keywords = [
            '10x', 'ten times', 'order of magnitude', 'breakthrough',
            'revolutionary', 'novel', 'first', 'unprecedented',
            'significantly improved', 'substantially reduced'
        ]
        
        text = f"{signal.get('title', '')} {signal.get('abstract', '')}".lower()
        
        for kw in impact_keywords:
            if kw in text:
                return 1
        return 0
    
    def _score_macro(self, signal: Dict) -> float:
        """
        +1 for energy security, US-China decoupling, climate themes
        """
        macro_keywords = [
            'energy security', 'grid resilience', 'domestic supply',
            'decarbonization', 'net zero', 'climate', 'carbon',
            'supply chain', 'reshoring', 'critical minerals'
        ]
        
        text = f"{signal.get('title', '')} {signal.get('abstract', '')}".lower()
        
        for kw in macro_keywords:
            if kw in text:
                return 1
        return 0
    
    def _score_attention(self, signal: Dict) -> float:
        """
        Attention multiplier (0-3):
        +3: Top citations, stock moves, viral
        +2: Medium attention
        +1: Just filed, early
        +0: Old, ignored
        """
        attention = 0
        
        # Check for OSINT attention multiplier (from Reddit/news)
        entities = signal.get('entities', {})
        osint_multiplier = entities.get('attention_multiplier', 1.0)
        if osint_multiplier > 1.5:
            attention += 1.5
        elif osint_multiplier > 1.0:
            attention += 0.5
        
        # Check for Reddit-specific metrics
        reddit_score = entities.get('reddit_score', 0)
        num_comments = entities.get('num_comments', 0)
        if reddit_score > 100 or num_comments > 50:
            attention += 1.0
        elif reddit_score > 50 or num_comments > 20:
            attention += 0.5
        
        # Recency bonus
        signal_date = signal.get('date')
        if signal_date:
            if isinstance(signal_date, str):
                try:
                    signal_date = datetime.strptime(signal_date, '%Y-%m-%d')
                except ValueError:
                    signal_date = datetime.now()
            
            days_old = (datetime.now() - signal_date).days
            
            if days_old <= 7:
                attention += 0.5  # Fresh
            elif days_old <= 30:
                attention += 0.25
        else:
            attention += 0.5  # Default for new signals
        
        return min(attention, 3.0)  # Cap at 3


def score_signals(signals: List[Dict], engine: ScoringEngine = None) -> List[Dict]:
    """Score a list of signals and return sorted by final score."""
    if engine is None:
        engine = ScoringEngine()
    
    scored = []
    for signal in signals:
        score_result = engine.score(signal, signals)  # Pass all for convergence
        scored.append({
            **signal,
            'score': score_result
        })
    
    # Sort by final score descending
    scored.sort(key=lambda x: x['score']['final_score'], reverse=True)
    return scored


if __name__ == "__main__":
    # Test scoring
    test_signal = {
        'source': 'uspto',
        'source_id': 'TEST123',
        'title': 'Advanced Liquid Cooling System for Data Center Servers',
        'abstract': 'A novel immersion cooling system providing 10x improved thermal management for high-density computing. This breakthrough technology enables commercial deployment in hyperscale data centers.',
        'date': datetime.now(),
        'domain': 'cooling',
        'entities': {
            'companies': ['Google', 'Vertiv'],
            'technologies': ['cooling', 'liquid cooling']
        }
    }
    
    engine = ScoringEngine()
    result = engine.score(test_signal)
    
    print(f"Base Score: {result['base_score']}")
    print(f"Attention: {result['attention_score']}")
    print(f"Final Score: {result['final_score']}")
    print(f"Category: {result['category']}")
    print(f"Breakdown: {result['breakdown']}")
