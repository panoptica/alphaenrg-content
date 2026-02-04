"""
Configuration settings for the Energy Intelligence Agent.
"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Database
DATABASE_PATH = DATA_DIR / "signals.db"

# API Keys (from environment variables)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Email settings (to be configured)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# Collection settings
USPTO_BASE_URL = "https://api.patentsview.org/patents/query"
SEC_EDGAR_BASE = "https://efts.sec.gov/LATEST/search-index"
ARXIV_API_BASE = "http://export.arxiv.org/api/query"

# Scoring thresholds
SCORE_CRITICAL = 12  # SMS/WhatsApp alert
SCORE_STRONG = 7     # Top 3 candidate
SCORE_INTERESTING = 4  # Watch list

# Technology domains (from spec)
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

# Tier 1 players (auto +2 score)
TIER_1_COMPANIES = [
    # Hyperscalers
    'Google', 'Alphabet', 'Microsoft', 'Amazon', 'AWS', 'Meta', 'Facebook', 'Nvidia',
    # Industrials
    'Rolls-Royce', 'Siemens', 'GE', 'General Electric', 'Schneider Electric', 
    'Vertiv', 'nVent', 'Boyd',
    # Defense
    'BAE Systems', 'Lockheed Martin', 'Northrop Grumman', 'Leonardo', 'Raytheon'
]

TIER_1_VCS = [
    'Founders Fund', 'Social Capital', 'Craft Ventures', 'Launch', 
    'Breakthrough Energy Ventures', 'Sequoia', 'Andreessen Horowitz', 'a16z', 
    'Lux Capital', 'DCVC', 'Khosla Ventures', 'G2 Venture Partners', 'Gigafund', 
    '8VC', 'Atomico', 'Balderton', 'In-Q-Tel'
]

# Tier 2 players (auto +1 score)
TIER_2_COMPANIES = [
    'NuScale', 'X-energy', 'Moltex', 'Oklo', 'Kairos Power', 
    'Commonwealth Fusion', 'TAE Technologies', 'Tokamak Energy', 
    'LiquidStack', 'Submer', 'Iceotope',
    'NREL', 'ORNL', 'Oak Ridge', 'Sandia', 'NPL', 'Fraunhofer'
]
