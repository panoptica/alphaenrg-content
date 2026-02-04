# Energy & Cooling Intelligence Agent - Technical Specification

**Version**: 1.0  
**Date**: 2026-02-04  
**Status**: Build-Ready for OpenClaw Implementation

---

## Executive Summary

Automated intelligence system monitoring energy generation, cooling technologies, and quantum computing infrastructure to identify investment opportunities 12-18 months before market consensus.

**Core Hypothesis**: Convergence of AI scaling and quantum computing creates shared infrastructure bottleneck (energy + cooling). Information arbitrage opportunity exists in correlating patents, funding, regulatory actions, and academic research before signals reach mainstream analyst coverage.

**Success Target**: Identify 2-3 actionable trades/month with 12-18 month time horizon.

---

## 1. Signal Detection Framework

### 1.1 Technology Domains (What We Monitor)

#### Energy Generation
- **Nuclear**: SMRs (all designs: PWR, MSR, HTGR, microreactors), fusion (tokamak, stellarator, inertial confinement), advanced fuels (HALEU, thorium, ATF)
- **Solar**: Novel materials (perovskite, tandem, organic PV, quantum dots), novel deployment (bifacial, agrivoltaics, BIPV)
- **Wind**: Novel only (floating offshore, airborne, advanced materials) - exclude incremental turbine improvements
- **Geothermal**: Enhanced/deep drilling, closed-loop, supercritical CO2
- **Hydrogen**: Production (electrolysis, pyrolysis, photocatalytic), storage (solid-state, LOHC)
- **Storage**: Novel batteries (solid-state, Li-S, Na-ion, flow), mechanical (gravity, CAES, LAES), thermal (molten salt, PCM)

#### Cooling Technologies (Use Case: Nvidia Data Centre + Google Willow Quantum)
- **Liquid**: Direct-to-chip, immersion, two-phase
- **Cryogenic**: Dilution refrigerators, pulse tubes, closed-cycle
- **Phase-Change**: Novel PCMs, thermal buffers
- **Heat Rejection**: Dry cooling, geothermal sinks, radiative cooling
- **Components**: Heat pipes, vapor chambers, microchannels, thermal interface materials, novel coolants

#### Quantum Computing
- Energy efficiency improvements (room-temp qubits, error correction reducing cooling)
- Cooling infrastructure (cryogenic systems, control electronics thermal management)
- Quantum sensing for energy (grid monitoring, geophysical)

#### Excluded (For Now)
- Space-based solar (too early)
- Tidal/wave (capital drying up)
- Ocean thermal (academic only)
- Exotic physics (unless Tier 1 player involved)

### 1.2 Geographic & Regulatory Scope

#### Primary (Daily Monitoring)
**United States**:
- Patents: USPTO
- Corporate: SEC EDGAR (10-K, 10-Q, 8-K)
- Government: DOE, ARPA-E, NRC, NSF
- Regulators: NRC (nuclear), FERC (energy)

**United Kingdom**:
- Patents: UKIPO
- Corporate: Companies House, LSE RNS
- Government: UKRI, Innovate UK, Net Zero programmes
- Regulators: ONR (nuclear), Ofgem (energy)

**European Union**:
- Patents: EUIPO
- Government: EIC, Horizon Europe, REPowerEU
- Regulators: ASN (France nuclear), BNetzA (Germany energy) - Tier 1 only

**Australia**:
- Corporate: ASX (mining/rare earths/uranium signals)
- Government: ARENA
- Research: CSIRO (solar/hydrogen)

**New Zealand**: Major geothermal projects only (skip daily monitoring)

#### Tertiary (Macro Signals Only, ≥$100M)
**China**: State energy announcements, Belt & Road projects, top-tier institutions (Tsinghua, CAS) breakthroughs - skip daily patent monitoring

**Middle East**: Saudi Vision 2030, UAE sovereign wealth investments, NEOM/Masdar developments

### 1.3 Key Players & Credibility Tiers

#### Tier 1 (Auto +2 Score)
**Hyperscalers**: Google, Microsoft, Amazon, Meta, Nvidia

**Industrials**: Rolls-Royce, Siemens Energy, GE Vernova, Schneider Electric, Vertiv, nVent, Boyd

**Defense**: BAE Systems, Lockheed Martin, Northrop Grumman, Leonardo

**VCs**: 
- US: Founders Fund (Thiel), Social Capital (Chamath), Craft Ventures (Sacks), Launch (JCal), Breakthrough Energy Ventures (Gates), Sequoia, a16z, Lux Capital, DCVC, Khosla, G2 Venture Partners, Gigafund, 8VC
- UK/EU: Atomico, Balderton, Hoxton Ventures, Lakestar, EQT Ventures
- Corporate: Intel Capital, Google Ventures, Microsoft M12, Amazon Climate Pledge Fund
- Defense/Gov: In-Q-Tel, Shield Capital, Ridgeline

**Public Market**: ARK Invest (Cathie Wood) - retail attention signal, not quality signal

#### Tier 2 (Auto +1 Score)
**Credible Startups**: Prior exit OR PhD from MIT/Stanford/Cambridge/Oxford OR top-tier VC backing

**Specialists**: NuScale, X-energy, Moltex, Oklo, Kairos (SMR), Commonwealth Fusion, TAE, Tokamak Energy (fusion), LiquidStack, Submer, Iceotope (cooling)

**National Labs**: NREL, ORNL, Sandia (US), NPL (UK), Fraunhofer (Germany)

#### Tier 3 (Filtered Unless Corroborated)
Unknown startups, generic university research (no commercial path)

**Exception**: If Tier 3 work gets cited/validated by Tier 1/2, elevate signal

---

## 2. Signal Scoring Model

### 2.1 Base Score Components (0-15 points)

**Convergence** (+3): ≥2 independent sources on same tech/company within 90 days (patent + paper, SEC filing + grant, patent + media)

**Government Alignment** (+2): Matches announced policy (US: IRA/CHIPS/ARPA-E, UK: Net Zero/SMR, EU: Green Deal/REPowerEU)

**Capital Commitment** (+2-3):
- US: ≥$100M VC/PE OR ≥$50M gov grant (+2)
- UK/EU: ≥£20M VC/PE OR ≥£10M gov grant (+3, rarer)
- Mega-rounds: ≥$500M (+3 regardless)

**Time-to-Market TRL 5-7** (+2):
- TRL 7: "field trial", "pilot", "customer validation"
- TRL 6: "demonstration", "prototype testing"
- TRL 5: "component validation", "subsystem"

**Player Credibility** (+2): Tier 1 player (see section 1.3)

**M&A Likelihood** (+1): Strategic acquirer active in space + startup fills gap

**Novelty & Impact** (+1): 5-10x improvement (step-change) + commercially viable

**Macro Tailwind** (+1): Energy security, US-China decoupling, climate commitments

### 2.2 Attention Multiplier (0-3)

**High Attention** (+3):
- Citations: Top 5% (papers 15+ cites in 30d, patents 3+ forward cites)
- Stock: ≥3% move on announcement
- GitHub: 500+ stars in 14 days
- Media: FT, MIT Tech Review, Nature News coverage

**Medium Attention** (+2):
- Citations: 5-15 in 30d
- Analyst: Rating upgrade, price target increase
- GitHub: 100-500 stars in 30d
- Media: IEEE Spectrum, TechCrunch, Data Center Dynamics

**Low Attention** (+1):
- Just filed (0-30 days), no validation yet
- Conference: NeurIPS/ICML spotlight/oral

**No Attention** (0): 90+ days old, no citations, no coverage

### 2.3 Final Score Calculation

**Formula**: `Final Score = Base Score × (1 + Attention × 0.2)`

**Thresholds**:
- **≥12**: Critical alert (SMS/WhatsApp)
- **≥7**: Strong signal (Top 3 candidate)
- **4-6**: Interesting (watch list)
- **<4**: Filtered (noise)

### 2.4 Complexity/Impact Modifiers (Tiebreaker)

**Complexity** (Lower = Better):
- Low (+2): Existing supply chains, proven manufacturing, clear regulatory path
- Medium (0): New manufacturing, known materials
- High (-2): Exotic materials, unproven, regulatory uncertainty

**Impact** (Higher = Better):
- Transformative (+3): 5-10x improvement, enables new applications
- Substantial (+2): 2-5x improvement, significant cost reduction
- Incremental (+1): 20-50% improvement
- Marginal (0): <20% improvement

**Prioritization**: High Impact + Low Complexity > High Impact + High Complexity

---

## 3. Data Sources & Collection

### 3.1 Phase 1 - Free Sources (Weeks 1-4)

**Patents**:
- USPTO: Free full-text, bulk downloads via PatentsView
- UKIPO: Free search
- EUIPO: Free via EPO Espacenet
- Lens.org: Free patent analytics (citations, families)

**Corporate Filings**:
- SEC EDGAR: Free (10-K, 10-Q, 8-K, Form 4)
- Companies House (UK): Free
- Yahoo/Google Finance: Free stock prices

**Academic Papers**:
- ArXiv: Free (cs.AI, physics.app-ph, cond-mat, quant-ph)
- Google Scholar: Free search + citations
- PubMed: Free
- IEEE Xplore: Via Oxford access (user's son)
- Nature/Science: Via Oxford (user's wife/son)

**Government**:
- US: DOE grants, ARPA-E projects, NRC filings (all free)
- UK: UKRI Gateway to Research, Innovate UK (free)
- EU: EIC projects (free)

**News**:
- Financial Times: User has subscription
- TechCrunch, MIT Tech Review, Ars Technica: Free tier
- Company press releases: Free

**VC/Funding**:
- Crunchbase Free: Limited (5-10 searches/month)
- PitchBook: Possible via Oxford

**Social** (Use Sparingly):
- Hacker News: Free API
- Twitter/X: Free tier (rate-limited)
- Reddit: Free (r/MachineLearning, r/energy)

### 3.2 Phase 2 - Paid Sources (Month 2+, If Validated)

**Priority 1 - If Patent Signals Valuable**:
- Lens.org Plus (£500/year): Enhanced analytics
- PatentSight (£5k/year): Professional analytics
- **Start with free Lens.org, upgrade if needed**

**Priority 2 - If Funding Signals Valuable**:
- Crunchbase Pro (£1.5k/year): Real-time funding, M&A
- **Alternative**: Manual TechCrunch + FT monitoring

**Priority 3 - Market Signals**:
- Bloomberg Terminal (£20k/year): NOT recommended for Phase 1
- **Alternative**: FT + Yahoo Finance + SEC EDGAR

### 3.3 Collection Schedule

**Daily (Monday-Friday, Overnight Processing)**:
- 10:00 PM: Begin collection
- 11:00 PM: Patents (new filings from previous day)
- 12:00 AM: SEC/Companies House
- 1:00 AM: Academic papers (ArXiv posts midnight ET)
- 2:00 AM: Government sources
- 3:00 AM: News aggregation
- 4:00 AM: Social signals
- 5:00 AM: Scoring, correlation, synthesis
- 6:00 AM: Report generation
- 7:00 AM: Email sent (revised to 4:00 PM if 9-hour processing needed)

**Weekend**: No collection (Saturday/Sunday accumulate)

**Monday**: Includes Friday PM + weekend signals (2x volume)

**Weekly (Sunday Evening)**: Calibration report based on user ratings

**Monthly (First Sunday)**: Performance review, suggested adjustments

---

## 4. Signal Correlation & Synthesis

### 4.1 Correlation Patterns

**Timeline Clustering**: Multiple sources on same tech/company within 90 days
- Example: MIT paper → Google patent → DOE grant → Vertiv SEC filing

**Supply Chain Mapping**: Upstream/downstream relationships
- Example: Startup (material) → Vertiv (integrator) → Google (customer) → GV invests in startup

**Validation Cascade**: Early signal progressively validated
- Example: University paper (TRL 3) → Startup founded + VC funding → OEM partnership → Manufacturing patent (TRL 6)

### 4.2 Synthesis Format (Top 3 Signals)

Each Top 3 signal includes:

**Header**: [Tech/Company] - [One-line hook]

**Score**: Final score (Base: X, Attention: +Y, Complexity: Z, Impact: W)

**Convergence Summary**:
- Timeline of signals (dates, sources, what happened)
- Pattern type (clustering/supply chain/validation)

**Government Alignment**: Programme name, how signal aligns, funding/approval/commitment

**Time to Market**: TRL level, evidence, commercial timeline (6-12/12-18/18-24 months), deployment signals

**Key Players**: Primary company/group, tier, financial backing, strategic relationships

**Meta-Signals**: Citations (N papers/patents in Y days), market reaction (stock %), GitHub stars, media coverage

**Commercial Play**: Direct equity (ticker or "Private - watch for IPO/M&A"), adjacent plays, time horizon, catalysts to watch

**Contrarian Check**: What could kill this, what's priced in, alternative outcomes

**Suggested Action**: Immediate (research/watch/pass), if actionable (position sizing, entry/exit criteria)

**Sources**: Clickable links (patent PDFs, SEC filings, papers, press releases)

### 4.3 Interesting Signals Format (10 Signals)

**Format**: `[Score] | [Tech] | [Player] | [One-line summary] | [Why interesting] | [👍] [👎]`

**Example**: `8.2 | Liquid Cooling | Submer + Microsoft | Submer announces Azure immersion pilot in Iceland. M&A likelihood: High. Hiring spike: 30+ engineers. 👍 👎`

---

## 5. User Training & Feedback Loop

### 5.1 Phase 1 - Training Mode (Weeks 1-2)

**Objective**: Agent learns user mental model

**Process**:
- Agent delivers 15-20 candidates/day (lower threshold: score ≥5)
- User rates each: 👍 (more like this), ➡️ (neutral), 👎 (noise)
- Agent tracks patterns: tech preferences, player preferences, attention metric preferences, TRL preferences, novelty threshold

**Daily Learning Summary**: "Based on today's ratings: You prefer [cooling > hydrogen > SMRs], [VC-backed > university], [citation velocity > social hype]. Adjusting tomorrow."

**Weekly Calibration (Sunday, Weeks 1-2)**:
- Technology preferences (avg ratings by category)
- Player preferences (Tier 1 vs startups vs academic)
- Attention preferences (citations vs stock vs GitHub vs social)
- TRL sweet spot (which stages get highest ratings)
- Suggested adjustments for next week
- User approves/rejects adjustments

### 5.2 Phase 2 - Auto-Pilot (Week 3+)

**Objective**: Agent operates autonomously, minimal user input

**Process**:
- Agent delivers 10-12 candidates/day (tighter threshold: score ≥7 + user preference weighting)
- Top 3 pre-ranked by agent
- User only rates if agent got it wrong (👍 = "too low, should've been Top 3", 👎 = "too high")
- No rating = agent got it right

**Continuous Learning**:
- Track disagreement rate (user overrides)
- If >30% disagreement for 3 days → flag "Need recalibration"
- If <10% disagreement for 7 days → increase confidence, tighten threshold further

**Monthly Deep Calibration (First Sunday)**:
- Performance metrics (approval rates, false positives, technology breakdown)
- Time-to-market accuracy (validate predictions against actual outcomes)
- Recommended adjustments (technology mix, scoring weights)
- New features to consider (regulatory tracker, patent landscape density, earnings call mentions)

### 5.3 Adaptive Features

**Rating System**: Star-based (⭐⭐⭐⭐⭐ exactly what I want, ⭐⭐⭐ interesting occasionally, ⭐ noise)

**Weekly Audit**: Top 10 signals user rated 5-star, technology breakdown with avg ratings, suggested taxonomy adjustments

**Outcome Tracking (Optional)**: User marks "Traded", "Watching", "Passed" → later reports "Profitable", "Breakeven", "Loss" → agent learns which patterns led to profitable trades

**Confidence Intervals**: After 3 months, agent calculates prediction accuracy, adds confidence bands to scores ("Score 12.5 - High confidence 85% historical approval")

---

## 6. Technical Implementation

### 6.1 Architecture

```
ORCHESTRATION LAYER (Daily scheduler)
    │
    ├── DATA COLLECTORS
    │   ├── Patents (USPTO, UKIPO, EUIPO, Lens.org)
    │   ├── SEC/Companies House
    │   ├── Academic Papers (ArXiv, Google Scholar)
    │   ├── Government (DOE, UKRI, EIC)
    │   ├── News (FT, TechCrunch, press releases)
    │   └── Social (HN, Twitter, Reddit - light)
    │
    ├── SCORING ENGINE
    │   ├── Base scoring (convergence, gov alignment, capital, TRL, player, M&A, impact, macro)
    │   ├── Attention multiplier (citations, stock, GitHub, media)
    │   ├── User preference weighting (after training)
    │   └── Correlation (entity extraction, temporal clustering, convergence scoring)
    │
    ├── SYNTHESIS MODULE
    │   ├── Template selection (validation cascade, supply chain, patent cluster)
    │   ├── Narrative generation (Claude API)
    │   └── Contrarian analysis (risk identification)
    │
    ├── EMAIL GENERATOR
    │   ├── HTML template (Top 3 full analysis + 10 one-liners)
    │   ├── Thumbs buttons (clickable API endpoints)
    │   └── SMTP delivery
    │
    └── USER FEEDBACK LOOP
        ├── Rating capture (API or email replies)
        ├── Weekly calibration
        └── Monthly optimization
```

### 6.2 Data Store (SQLite or PostgreSQL)

**Tables**:
- `signals`: Raw data from collectors
- `scored_signals`: Base + attention + final scores
- `user_ratings`: Thumbs up/down/neutral
- `convergence_clusters`: Related signals grouped
- `user_preferences`: Learned weights (technology, player, attention)
- `performance_metrics`: Approval rates, disagreement, outcomes

### 6.3 Technology Stack

**Language**: Python 3.10+

**Libraries**:
- Data collection: `requests`, `beautifulsoup4`, `pandas`
- Database: `sqlite3` or `psycopg2` (PostgreSQL)
- NLP: `spacy` (entity extraction) or Hugging Face Transformers
- API: `anthropic` (Claude synthesis), `flask` or `fastapi` (thumbs buttons)
- Email: `smtplib` (built-in Python)
- Scheduling: `cron` (Linux), systemd timer, or Task Scheduler (Windows)

**Hosting**:
- Phase 1: Local machine or DigitalOcean Droplet ($12/month)
- Phase 2: AWS Lambda/Google Cloud Functions (serverless, pay per use)

### 6.4 Patent Collection Example

**Search Query (Liquid Cooling)**:
```
((cooling OR thermal OR immersion) 
AND (data center OR datacentre OR server OR rack) 
AND (filing_date:[NOW-1DAY TO NOW]))
```

**Fields Captured**: Patent number, title, abstract, first 3 independent claims, assignee, inventors, dates, citations (backward/forward), patent family, CPC codes

**TRL Detection**:
```python
trl_keywords = {
    7: ["field trial", "pilot", "commercial", "customer", "production"],
    6: ["demonstration", "prototype", "system test", "validation"],
    5: ["component test", "subsystem", "proof of concept", "lab"],
}
# Scan claims for keywords, assign estimated TRL
```

**Frequency**: Daily (new filings from previous day)

### 6.5 SEC Collection Example

**8-K Item 1.01 (Material Agreements)**:
```
company: (Vertiv OR Nvidia OR Microsoft) 
AND form: 8-K 
AND item: 1.01 
AND filing_date:[2025-01-01 TO 2026-02-04]
```

**Attention Metric**: Stock price on filing date vs 5 days prior (% change), volume spike (vs 30-day avg)

### 6.6 Correlation Module

**Entity Extraction**:
```python
def extract_entities(signal):
    text = signal['title'] + ' ' + signal['abstract']
    entities = {'companies': [], 'technologies': []}
    
    # Company extraction (from known list)
    for company in TIER_1_COMPANIES + TIER_2_COMPANIES:
        if company.lower() in text.lower():
            entities['companies'].append(company)
    
    # Technology extraction
    for tech in TECHNOLOGY_KEYWORDS['cooling'] + TECHNOLOGY_KEYWORDS['smr']:
        if tech.lower() in text.lower():
            entities['technologies'].append(tech)
    
    return entities
```

**Temporal Clustering**:
```python
def find_convergence(signals, window_days=90):
    clusters = []
    for i, sig_a in enumerate(signals):
        cluster = [sig_a]
        for sig_b in signals[i+1:]:
            days_apart = abs((sig_a['date'] - sig_b['date']).days)
            if days_apart <= window_days:
                # Check entity overlap
                common = (set(sig_a['entities']['companies']) & set(sig_b['entities']['companies'])) or \
                         (set(sig_a['entities']['technologies']) & set(sig_b['entities']['technologies']))
                if common:
                    cluster.append(sig_b)
        if len(cluster) >= 2:
            clusters.append(cluster)
    return clusters
```

### 6.7 Synthesis Module (Claude API)

**Generate Human-Readable Analysis**:
```python
def generate_synthesis(cluster):
    signals_text = ""
    for s in cluster:
        signals_text += f"- {s['date']}: {s['type']} - {s['title']}\n"
        signals_text += f"  Summary: {s['abstract'][:200]}...\n"
    
    prompt = f"""
    You are an intelligence analyst generating a concise signal summary.
    
    Signals:
    {signals_text}
    
    Generate a 150-word analysis covering:
    1. What is converging (technology/company)
    2. Why it matters (commercial implications)
    3. Timeline to market
    4. Key players
    5. One contrarian risk
    
    Be direct, avoid hype, focus on actionable insights.
    """
    
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

**Contrarian Check**:
```python
def generate_contrarian(cluster):
    risks = []
    if any('nuclear' in s['tech'] for s in cluster):
        risks.append("NRC approval: 5-7 years. Deployment may be optimistic.")
    if any(s['stock_change'] > 15 for s in cluster):
        risks.append("Stock already moved significantly. May be priced in.")
    if any(s['trl'] < 6 for s in cluster):
        risks.append("TRL <6. Commercial timeline uncertain.")
    patent_count = count_related_patents(cluster)
    if patent_count > 20:
        risks.append(f"{patent_count} related patents. Crowded space, limited M&A premium.")
    return risks
```

### 6.8 Email Generation (HTML + Thumbs Buttons)

**Template**: Clean HTML with inline CSS, mobile-friendly

**Thumbs Buttons**: Links to agent API
- `https://agent-api.com/rate/{signal_id}/{token}/up`
- `https://agent-api.com/rate/{signal_id}/{token}/neutral`
- `https://agent-api.com/rate/{signal_id}/{token}/down`

**Token**: Unique per signal+user, expires after 30 days

**Alternative**: "Reply with: +123 (thumbs up signal 123), -456 (thumbs down 456)" - agent parses email replies

### 6.9 Critical Alert System (SMS/WhatsApp)

**Trigger**: Final score ≥12

**Implementation**: Start with **email-to-SMS gateway** (free, e.g., `5551234567@tmomail.net`). Upgrade to Twilio if unreliable.

**SMS Message (160 char)**:
```
🚨 CRITICAL (12.3): Google/Vertiv graphene cooling + $40M DOE grant. Check email. Reply STOP to disable.
```

**WhatsApp Message** (no limit):
```
🚨 CRITICAL SIGNAL

Score: 12.3
Tech: Graphene cooling
Players: Google, Vertiv, MIT
Pattern: Academic → Industry → Gov funding

Developments:
- MIT paper (18 cites/21d)
- Google patent
- DOE $40M
- Vertiv SEC (capex +30%)

Timeline: 12-18mo
Play: Vertiv (NYSE:VRT)
Risk: Graphene scale-up unproven

Full analysis in email.
```

**Timing**: Immediate (not batched)

---

## 7. Deployment & Operations

### 7.1 Hosting

**Phase 1**: DigitalOcean Droplet ($12/month, 2GB RAM, SQLite + Python)

**Phase 2**: AWS Lambda or Google Cloud Functions (serverless, pay per use)

### 7.2 Scheduling

**Cron Job** (runs overnight, Monday-Friday):
```bash
0 22 * * 1-5 /usr/bin/python3 /opt/agent/main.py --mode daily_collection
```

**Critical Alert Check** (every 2 hours during business hours):
```bash
0 */2 * * 1-5 /usr/bin/python3 /opt/agent/main.py --mode critical_alert
```

### 7.3 Error Handling

- If data source down (USPTO, SEC, ArXiv): Retry 3 times with exponential backoff, then skip, log warning
- If down >2 consecutive days: Alert user via email
- All runs logged to `/var/log/agent/collection.log`

### 7.4 Security

- Email: SMTP with TLS
- Thumbs API: Unique token per signal, expires 30 days
- Data: Stored locally (user's VPS), no third-party tracking
- API keys: Environment variables (not in code)

### 7.5 Backup

- Daily database backup to S3/Dropbox/external drive
- Keep 30 days rolling
- Disaster recovery: Reinstall + restore database (user ratings preserved)

---

## 8. Cost Estimate

### Phase 1 (Weeks 1-4, Free Sources)

**Development**: $0 if user builds, $2k-5k if outsourced

**Infrastructure**: DigitalOcean $12/month, domain $12/year = ~$15 Month 1

**Data**: $0 (all free: USPTO, SEC, ArXiv, Lens.org, FT subscription user has)

**Claude API**: ~$6/month (20 signals/day × 500 tokens × 30 days = 300K tokens, Sonnet 4: $3/M input + $15/M output)

**Total Month 1**: $21 ongoing + $2k-5k one-time dev

### Phase 2 (Month 2+, Paid Sources If Validated)

**Data**:
- Crunchbase Pro: £125/month (£1.5k/year)
- Lens.org Plus: £40/month (£500/year)
- **Total**: $165/month (~£1,750/year)

**Infrastructure**: $12/month

**Claude API**: $6/month

**Total Month 2+**: $183/month (~£150/month, £1,800/year)

### ROI

**Break-even**: 1 trade/year making >£2k profit

**Target**: 1.5 winning trades/month × £5k profit = £7.5k/month profit vs £150 agent cost = **50x ROI**

**Failure**: Zero actionable trades in 6 months → shut down, loss £900

---

## 9. Success Metrics

### Phase 1 (Weeks 1-2, Training)

1. User rates 80%+ of signals (≥12/day out of 15)
2. Clear preference patterns emerge (≥3 tech categories have distinct approval rates)
3. User flags ≥2 signals as "worth researching"

### Phase 2 (Week 3+, Auto-Pilot)

1. Top 3 approval rate ≥70% (user 👍 ≥2 out of 3 daily)
2. Disagreement rate <20% (user rarely overrides agent ranking)
3. User reduces rating frequency (only 3-5 ratings/day, not all 10-12)

### Phase 3 (Month 2+, Outcomes)

1. Actionable trades: ≥2-3 signals/month marked "Traded" or "Researching"
2. Signal lead time: 12-18 months before mainstream coverage
3. False positive rate: <25% of Top 3 rated 👎

### Long-Term (Month 6+)

- Historical backtest accuracy (would agent have flagged past market moves?)
- User testimonial: "Did this help you make money?" (yes/no)
- Decision: Keep for personal use, or productize?

---

## 10. Risk Assessment & Mitigation

**Risk 1 - Signal Overload**: User overwhelmed → Tighten threshold (score ≥6), add "snooze" option, monthly volume check

**Risk 2 - Signal Drought**: Too few signals → Expand sources, lower threshold temporarily, user provides missing signal examples

**Risk 3 - Data Source Failures**: USPTO down >2 days → Implement retry logic, alert user, maintain 7-day buffer

**Risk 4 - User Disengagement**: User stops rating → Gamification ("95/100 rated!"), weekly impact summary, simplify to 👍👎 only

**Risk 5 - Claude API Costs Spike**: Bill jumps to $50/month → Monitor daily, optimize prompts, set $20/month hard limit

**Risk 6 - No Actionable Trades**: 6 months, zero trades → Month 3 retrospective (review past signals, adjust to "tradeable" focus), add paper trading mode

---

## 11. Implementation Roadmap

### Week 1: Core Infrastructure
- **Days 1-2**: Build USPTO + SEC collectors, test (10-20 patents/day, 5-10 SEC filings/day)
- **Days 3-4**: Build ArXiv + DOE/UKRI + FT RSS collectors, test (20-30 papers/day, 5-10 grants/week, 10-20 news/day)
- **Days 5-7**: Build scoring engine (base + attention), test (can score 50 signals and rank)

### Week 2: Synthesis & Delivery
- **Days 8-9**: Build correlation (entity extraction, convergence detection), test (identify 2-3 clusters from 100 signals)
- **Days 10-11**: Build email generator (HTML template, thumbs API), test (send formatted digest)
- **Days 12-14**: End-to-end testing (collection → scoring → correlation → synthesis → email), user receives first digest

### Week 3-4: Training & Tuning
- **Week 3**: User rates signals daily, agent logs, mid-week check-in for obvious issues
- **Week 4**: Continue training, Sunday Week 2 first calibration report, user approves adjustments, agent transitions to auto-pilot

### Month 2: Validation
- **Weeks 5-8**: Auto-pilot mode, minimal user feedback, weekly/monthly calibration, user identifies 1-2 signals worth trading
- **End Month 2**: Decision on paid sources (Crunchbase, PatentSight?), decision on long-term viability

---

## 12. Technology Keyword Dictionary (Reference)

```python
TECHNOLOGY_KEYWORDS = {
    'cooling': [
        'liquid cooling', 'immersion cooling', 'direct-to-chip', 'two-phase',
        'phase change material', 'PCM', 'thermal management', 'heat exchanger',
        'cold plate', 'microchannel', 'vapor chamber', 'heat pipe',
        'thermal interface material', 'TIM', 'coolant', 'refrigerant',
        'dilution refrigerator', 'pulse tube', 'cryogenic', 'cryocooler'
    ],
    'smr': [
        'small modular reactor', 'SMR', 'microreactor', 'advanced nuclear',
        'light water reactor', 'PWR', 'molten salt reactor', 'MSR',
        'high temperature gas reactor', 'HTGR', 'HALEU', 'accident tolerant fuel'
    ],
    'fusion': [
        'fusion', 'tokamak', 'stellarator', 'inertial confinement',
        'magnetic confinement', 'plasma', 'ITER', 'Commonwealth Fusion',
        'TAE', 'Tokamak Energy', 'tritium', 'deuterium'
    ],
    'solar': [
        'perovskite', 'tandem solar', 'multi-junction', 'organic photovoltaic',
        'quantum dot', 'CIGS', 'CdTe', 'bifacial', 'agrivoltaics', 'BIPV'
    ],
    'hydrogen': [
        'hydrogen', 'electrolysis', 'electrolyzer', 'PEM', 'alkaline',
        'solid oxide', 'SOEC', 'pyrolysis', 'SMR', 'steam methane reforming',
        'LOHC', 'liquid organic hydrogen carrier', 'ammonia', 'fuel cell'
    ],
    'battery': [
        'solid-state battery', 'lithium-sulfur', 'Li-S', 'sodium-ion',
        'flow battery', 'vanadium redox', 'zinc-bromine',
        'lithium-metal', 'silicon anode', 'electrolyte'
    ],
    'quantum': [
        'quantum computing', 'qubit', 'superconducting', 'transmon',
        'ion trap', 'topological', 'error correction', 'quantum advantage'
    ]
}
```

---

## 13. Example Patent Search Queries (Reference)

**Liquid Cooling**:
```
(cooling OR thermal OR immersion) 
AND (data center OR datacentre OR server OR rack) 
AND (filing_date:[2024-01-01 TO 2026-02-04])
```

**SMR**:
```
("small modular reactor" OR SMR OR microreactor OR "advanced nuclear") 
AND (filing_date:[2024-01-01 TO 2026-02-04])
```

**Quantum Cooling**:
```
(dilution OR cryogenic OR "pulse tube" OR refrigeration) 
AND (quantum OR qubit OR superconducting) 
AND (filing_date:[2024-01-01 TO 2026-02-04])
```

---

## 14. Example SEC Search Queries (Reference)

**8-K Material Agreements**:
```
company: (Vertiv OR Nvidia OR Microsoft) 
AND form: 8-K 
AND item: 1.01 
AND filing_date:[2025-01-01 TO 2026-02-04]
```

**10-Q MD&A Cooling Mentions**:
```
company: (Vertiv OR nVent OR "Schneider Electric") 
AND form: 10-Q 
AND text: (cooling OR thermal OR "data centre") 
AND filing_date:[2025-01-01 TO 2026-02-04]
```

---

## 15. Player Tier Lists (Reference)

### Tier 1 Players (Auto +2 Score)

**Hyperscalers**: Google, Alphabet, Microsoft, Amazon, AWS, Meta, Facebook, Nvidia

**Industrials**: Rolls-Royce, Siemens, GE, General Electric, Schneider Electric, Vertiv, nVent, Boyd

**Defense**: BAE Systems, Lockheed Martin, Northrop Grumman, Leonardo, Raytheon

**VCs**: Founders Fund, Social Capital, Craft Ventures, Launch, Breakthrough Energy Ventures, Sequoia, Andreessen Horowitz, a16z, Lux Capital, DCVC, Khosla Ventures, G2 Venture Partners, Gigafund, 8VC, Atomico, Balderton, In-Q-Tel

### Tier 2 Players (Auto +1 Score)

**Startups**: NuScale, X-energy, Moltex, Oklo, Kairos Power, Commonwealth Fusion, TAE Technologies, Tokamak Energy, LiquidStack, Submer, Iceotope

**National Labs**: NREL, ORNL, Oak Ridge, Sandia, NPL, Fraunhofer

---

## 16. Data Source URLs (Reference)

**USPTO**: https://bulkdata.uspto.gov/, https://developer.uspto.gov/

**SEC EDGAR**: https://www.sec.gov/edgar, https://efts.sec.gov/LATEST/search-index

**ArXiv**: https://arxiv.org/help/api, https://info.arxiv.org/help/bulk_data.html

**Google Scholar**: No official API (use Semantic Scholar API free: 100 req/min)

**Lens.org**: https://www.lens.org/lens/api

**DOE**: https://www.energy.gov/funding-financing, https://arpa-e.energy.gov/?q=site-page/project-listing

**UKRI**: https://gtr.ukri.org/, API: https://gtr.ukri.org/resources/api.html

**Claude API**: https://docs.anthropic.com/, Python SDK: `pip install anthropic`

---

## END OF SPECIFICATION

**Status**: Build-Ready for OpenClaw  
**Next Action**: User shares with OpenClaw → Begin Week 1 implementation  
**Estimated Development**: 40-60 hours (1-2 weeks full-time)

---

This specification is complete and ready for implementation by Claude in Chrome (OpenClaw) or a human developer.
