# X.AI Grok Configuration for AlphaENRG
# Real-time X/Twitter intelligence integration

GROK_CONFIG = {
    'model': 'grok-3',
    'base_url': 'https://api.x.ai/v1/chat/completions',
    'max_tokens': 1000,
    'temperature': 0.3,  # Lower for factual analysis
    'timeout': 30
}

ENERGY_INTELLIGENCE_PROMPT = """You are Grok with real-time X data access. Analyze current energy market discussions on X/Twitter.

Focus on:
1. Breaking energy news or policy announcements
2. Sentiment around major energy stocks (TSLA, ENPH, NEE, BEP, etc.)
3. Trending clean energy technologies or companies
4. Energy investment discussions from VCs/analysts
5. Regulatory or policy developments affecting energy markets

Provide concise, actionable intelligence suitable for institutional investors.
Include specific ticker symbols when relevant.
Highlight any time-sensitive opportunities or risks.

Current date: {current_date}
Query focus: {query_focus}"""

# Energy-focused hashtags and accounts to monitor
ENERGY_MONITORING_TARGETS = {
    'hashtags': [
        '#CleanEnergy', '#EnergyInvesting', '#EnergyTransition',
        '#SolarEnergy', '#WindEnergy', '#NuclearEnergy', 
        '#EnergyStorage', '#GridModernization', '#QuantumComputing',
        '#Semiconductors', '#GreenTech', '#ClimateInvesting'
    ],
    'key_accounts': [
        '@BloombergNEF', '@IEA', '@WoodMackenzie', '@BusinessGreen',
        '@energyintel', '@pvmagazine', '@cleanenergywire'
    ]
}

# Query templates for different intelligence types
GROK_QUERY_TEMPLATES = {
    'breaking_news': "What breaking energy news or announcements are trending on X right now? Include policy, M&A, or technology breakthroughs.",
    
    'market_sentiment': "What's the current sentiment on X around energy stocks like TSLA, ENPH, NEE, FSLR? Any significant price movements being discussed?",
    
    'emerging_trends': "What new energy technologies or companies are gaining momentum in X discussions today? Focus on early-stage trends before mainstream coverage.",
    
    'regulatory_intel': "Any energy policy or regulatory discussions trending on X? Include government announcements or industry reactions.",
    
    'vc_insights': "What are energy VCs and institutional investors discussing on X today? Any investment themes or opportunities mentioned?"
}