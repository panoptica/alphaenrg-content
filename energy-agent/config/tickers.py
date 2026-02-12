"""
Company to stock ticker mapping for Energy Intelligence Agent.
"""

COMPANY_TICKERS = {
    # Hyperscalers
    'Google': 'GOOGL', 'Alphabet': 'GOOGL', 'Microsoft': 'MSFT', 'Amazon': 'AMZN',
    'AWS': 'AMZN', 'Meta': 'META', 'Facebook': 'META', 'Nvidia': 'NVDA', 'NVIDIA': 'NVDA',
    'Apple': 'AAPL', 'Intel': 'INTC', 'AMD': 'AMD', 'IBM': 'IBM', 'Oracle': 'ORCL',
    'Tesla': 'TSLA', 'Palantir': 'PLTR', 'Broadcom': 'AVGO',
    
    # Industrials - Energy/Cooling
    'Rolls-Royce': 'RR.L', 'Siemens': 'SIE.DE', 'Siemens Energy': 'ENR.DE',
    'GE': 'GE', 'General Electric': 'GE', 'GE Vernova': 'GEV',
    'Schneider Electric': 'SU.PA', 'Vertiv': 'VRT', 'nVent': 'NVT',
    'Boyd': 'BYD', 'Eaton': 'ETN', 'Honeywell': 'HON',
    'ABB': 'ABBN.SW', 'Emerson': 'EMR',
    
    # Defense
    'BAE Systems': 'BA.L', 'Lockheed Martin': 'LMT', 'Northrop Grumman': 'NOC',
    'Leonardo': 'LDO.MI', 'Raytheon': 'RTX', 'RTX': 'RTX',
    'L3Harris': 'LHX', 'General Dynamics': 'GD',
    
    # Nuclear/SMR
    'NuScale': 'SMR', 'Oklo': 'OKLO', 'Cameco': 'CCJ', 'Uranium Energy': 'UEC',
    'Centrus Energy': 'LEU', 'BWX Technologies': 'BWXT', 'Lightbridge': 'LTBR',
    'Nano Nuclear': 'NNE', 'NANO Nuclear': 'NNE',
    
    # Fusion
    'TAE Technologies': 'Private', 'Commonwealth Fusion': 'Private',
    'Tokamak Energy': 'Private', 'General Fusion': 'Private',
    'Helion': 'Private', 'Zap Energy': 'Private',
    
    # Solar
    'First Solar': 'FSLR', 'Enphase': 'ENPH', 'SolarEdge': 'SEDG',
    'SunPower': 'SPWR', 'Canadian Solar': 'CSIQ', 'JinkoSolar': 'JKS',
    'Array Technologies': 'ARRY', 'Maxeon': 'MAXN',
    
    # Hydrogen/Fuel Cell
    'Plug Power': 'PLUG', 'Bloom Energy': 'BE', 'FuelCell Energy': 'FCEL',
    'Ballard Power': 'BLDP', 'ITM Power': 'ITM.L', 'Nel': 'NEL.OL',
    'Ceres Power': 'CWR.L', 'AFC Energy': 'AFC.L',
    
    # Battery/Storage
    'QuantumScape': 'QS', 'Solid Power': 'SLDP', 'EnerSys': 'ENS',
    'Fluence': 'FLNC', 'Eos Energy': 'EOSE', 'ESS Tech': 'GWH',
    'CATL': '300750.SZ', 'BYD': '1211.HK', 'Panasonic': '6752.T',
    'Samsung SDI': '006400.KS', 'LG Energy': '373220.KS',
    
    # Quantum
    'IonQ': 'IONQ', 'Rigetti': 'RGTI', 'D-Wave': 'QBTS',
    'Quantum Computing Inc': 'QUBT', 'Arqit': 'ARQQ',
    
    # Utilities/Grid
    'NextEra': 'NEE', 'Duke Energy': 'DUK', 'Southern Company': 'SO',
    'Constellation Energy': 'CEG', 'Vistra': 'VST', 'Dominion': 'D',
    'AES': 'AES', 'Brookfield Renewable': 'BEPC',
    
    # Oil/Gas transitioning
    'ExxonMobil': 'XOM', 'Chevron': 'CVX', 'BP': 'BP.L', 'Shell': 'SHEL',
    'TotalEnergies': 'TTE', 'Equinor': 'EQNR',
    
    # Data Center / Cooling
    'Equinix': 'EQIX', 'Digital Realty': 'DLR', 'CyrusOne': 'Private',
    'LiquidStack': 'Private', 'Submer': 'Private', 'Iceotope': 'Private',
}

# Lowercase lookup for fuzzy matching
_TICKER_LOOKUP = {k.lower(): v for k, v in COMPANY_TICKERS.items()}


def get_ticker(company_name: str) -> str | None:
    """Get ticker for a company name (case-insensitive, fuzzy)."""
    if not company_name:
        return None
    
    name_lower = company_name.lower().strip()
    
    # Exact match
    if name_lower in _TICKER_LOOKUP:
        t = _TICKER_LOOKUP[name_lower]
        return t if t != 'Private' else None
    
    # Substring match
    for key, val in _TICKER_LOOKUP.items():
        if val == 'Private':
            continue
        if key in name_lower or name_lower in key:
            return val
    
    return None


def find_tickers_in_text(text: str) -> list[tuple[str, str]]:
    """Find all company tickers mentioned in text. Returns [(company, ticker), ...]."""
    if not text:
        return []
    
    text_lower = text.lower()
    found = []
    seen_tickers = set()
    
    # Sort by length descending to match longer names first
    for company, ticker in sorted(COMPANY_TICKERS.items(), key=lambda x: len(x[0]), reverse=True):
        if ticker == 'Private':
            continue
        if company.lower() in text_lower and ticker not in seen_tickers:
            found.append((company, ticker))
            seen_tickers.add(ticker)
    
    return found
