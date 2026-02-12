"""
Market Data Engine for fetching and managing cryptocurrency market data.
Handles real-time and historical data from exchanges via ccxt.
"""

import ccxt
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import asyncio
from threading import Thread, Lock
import yaml
import os


class MarketDataEngine:
    """Handles fetching and caching market data from exchanges."""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.exchanges = {}
        self.data_cache = {}
        self.cache_lock = Lock()
        self.last_update = {}
        
        # Initialize exchanges
        self._init_exchanges()
        
        # Load trading pairs
        self.pairs = self._load_pairs()
        
    def _init_exchanges(self):
        """Initialize exchange connections."""
        try:
            # Primary exchange (Bybit)
            bybit_config = {
                'apiKey': os.getenv('BYBIT_API_KEY'),
                'secret': os.getenv('BYBIT_SECRET'),
                'sandbox': self.config['exchanges']['bybit']['sandbox'],
                'enableRateLimit': True,
                'rateLimit': self.config['exchanges']['bybit']['rate_limit']
            }
            
            self.exchanges['bybit'] = ccxt.bybit(bybit_config)
            self.logger.info("Initialized Bybit exchange connection")
            
            # Backup exchange (Binance)
            if os.getenv('BINANCE_API_KEY'):
                binance_config = {
                    'apiKey': os.getenv('BINANCE_API_KEY'),
                    'secret': os.getenv('BINANCE_SECRET'),
                    'sandbox': self.config['exchanges']['binance']['sandbox'],
                    'enableRateLimit': True,
                    'rateLimit': self.config['exchanges']['binance']['rate_limit']
                }
                
                self.exchanges['binance'] = ccxt.binance(binance_config)
                self.logger.info("Initialized Binance exchange connection")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize exchanges: {e}")
            
    def _load_pairs(self) -> dict:
        """Load trading pairs configuration."""
        try:
            pairs_file = os.path.join('config', 'pairs.yaml')
            with open(pairs_file, 'r') as f:
                pairs_config = yaml.safe_load(f)
                
            # Filter enabled pairs only
            enabled_pairs = {
                pair: config for pair, config in pairs_config['pairs'].items()
                if config.get('enabled', True)
            }
            
            self.logger.info(f"Loaded {len(enabled_pairs)} enabled trading pairs")
            return enabled_pairs
            
        except Exception as e:
            self.logger.error(f"Failed to load pairs config: {e}")
            return {}
            
    def fetch_candles(self, pair: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV candles for a trading pair.
        
        Args:
            pair: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (1m, 5m, 15m, etc.)
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Try primary exchange first
            exchange_name = self.config['exchanges']['primary']
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                # Fallback to backup exchange
                exchange_name = self.config['exchanges']['backup']
                exchange = self.exchanges.get(exchange_name)
                
            if not exchange:
                raise Exception("No exchange connection available")
                
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
            
            if not ohlcv:
                raise Exception(f"No data returned for {pair}")
                
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Cache the data
            cache_key = f"{pair}_{timeframe}"
            with self.cache_lock:
                self.data_cache[cache_key] = df.copy()
                self.last_update[cache_key] = datetime.now()
                
            self.logger.debug(f"Fetched {len(df)} candles for {pair} {timeframe}")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to fetch candles for {pair} {timeframe}: {e}")
            return pd.DataFrame()
            
    def get_latest_price(self, pair: str) -> float:
        """Get the latest price for a trading pair."""
        try:
            exchange_name = self.config['exchanges']['primary']
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                exchange_name = self.config['exchanges']['backup']
                exchange = self.exchanges.get(exchange_name)
                
            if not exchange:
                raise Exception("No exchange connection available")
                
            ticker = exchange.fetch_ticker(pair)
            return float(ticker['last'])
            
        except Exception as e:
            self.logger.error(f"Failed to get latest price for {pair}: {e}")
            return 0.0
            
    def get_cached_data(self, pair: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get cached market data if available and fresh."""
        cache_key = f"{pair}_{timeframe}"
        
        with self.cache_lock:
            if cache_key not in self.data_cache:
                return None
                
            # Check if data is fresh (less than 2 minutes old)
            last_update = self.last_update.get(cache_key)
            if not last_update or datetime.now() - last_update > timedelta(minutes=2):
                return None
                
            return self.data_cache[cache_key].copy()
            
    def update_all_pairs(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Update market data for all trading pairs and timeframes."""
        all_data = {}
        timeframes = self.config['trading']['data']['timeframes']
        
        for pair in self.pairs.keys():
            all_data[pair] = {}
            
            for timeframe in timeframes:
                try:
                    df = self.fetch_candles(pair, timeframe, self.config['trading']['data']['candle_limit'])
                    if not df.empty:
                        all_data[pair][timeframe] = df
                        
                except Exception as e:
                    self.logger.error(f"Failed to update {pair} {timeframe}: {e}")
                    
                # Rate limiting
                time.sleep(0.1)
                
        self.logger.info(f"Updated market data for {len(all_data)} pairs")
        return all_data
        
    def get_pair_info(self, pair: str) -> dict:
        """Get trading pair information and constraints."""
        try:
            exchange_name = self.config['exchanges']['primary']
            exchange = self.exchanges.get(exchange_name)
            
            if not exchange:
                return {}
                
            markets = exchange.load_markets()
            market = markets.get(pair, {})
            
            return {
                'symbol': pair,
                'base': market.get('base', ''),
                'quote': market.get('quote', ''),
                'active': market.get('active', False),
                'min_amount': market.get('limits', {}).get('amount', {}).get('min', 0),
                'max_amount': market.get('limits', {}).get('amount', {}).get('max', 0),
                'min_cost': market.get('limits', {}).get('cost', {}).get('min', 0),
                'tick_size': market.get('precision', {}).get('price', 0),
                'lot_size': market.get('precision', {}).get('amount', 0),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get pair info for {pair}: {e}")
            return {}
            
    def is_market_open(self) -> bool:
        """Check if markets are open (crypto trades 24/7)."""
        return True
        
    def health_check(self) -> Dict[str, bool]:
        """Check health of exchange connections."""
        health = {}
        
        for name, exchange in self.exchanges.items():
            try:
                # Test with a simple API call (fetch_time as fallback)
                try:
                    exchange.fetch_status()
                except Exception:
                    exchange.fetch_time()
                health[name] = True
                
            except Exception as e:
                self.logger.warning(f"Exchange {name} health check failed: {e}")
                health[name] = False
                
        return health