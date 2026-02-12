"""
Signal Engine for generating trading signals based on technical indicators.
Implements RSI, MACD, Volume spikes, Bollinger Bands, and EMA crossovers.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import ta


class Signal:
    """Represents a trading signal."""
    
    def __init__(self, pair: str, direction: str, strength: float, 
                 indicator: str, timestamp: datetime, price: float):
        self.pair = pair
        self.direction = direction  # 'long' or 'short'
        self.strength = strength    # 0.0 to 1.0
        self.indicator = indicator
        self.timestamp = timestamp
        self.price = price
        
    def __str__(self):
        return f"{self.indicator}: {self.direction} {self.pair} @ {self.price} (strength: {self.strength:.2f})"


class SignalEngine:
    """Generates trading signals from market data using technical indicators."""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.signal_config = config['trading']['signals']
        
    def generate_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate all signals for a trading pair.
        
        Args:
            pair: Trading pair symbol
            data: Dictionary of timeframe -> DataFrame
            
        Returns:
            List of Signal objects
        """
        signals = []
        
        try:
            # Generate signals from each indicator
            signals.extend(self._rsi_signals(pair, data))
            signals.extend(self._macd_signals(pair, data))
            signals.extend(self._volume_signals(pair, data))
            signals.extend(self._bollinger_signals(pair, data))
            signals.extend(self._ema_crossover_signals(pair, data))
            
            # Filter and sort signals by strength
            signals = [s for s in signals if s.strength > 0.5]
            signals.sort(key=lambda x: x.strength, reverse=True)
            
            if signals:
                self.logger.info(f"Generated {len(signals)} signals for {pair}")
                
        except Exception as e:
            self.logger.error(f"Error generating signals for {pair}: {e}")
            
        return signals
        
    def _rsi_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate RSI-based signals."""
        signals = []
        
        try:
            # Use 5m timeframe for RSI
            if '5m' not in data or data['5m'].empty:
                return signals
                
            df = data['5m'].copy()
            rsi_period = self.signal_config['rsi']['period']
            oversold = self.signal_config['rsi']['oversold_threshold']
            overbought = self.signal_config['rsi']['overbought_threshold']
            
            # Calculate RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=rsi_period).rsi()
            
            if len(df) < 2:
                return signals
                
            # Get latest values
            current_rsi = df['rsi'].iloc[-1]
            prev_rsi = df['rsi'].iloc[-2]
            current_price = df['close'].iloc[-1]
            timestamp = df.index[-1]
            
            # Oversold bounce signal (long)
            if prev_rsi <= oversold and current_rsi > oversold:
                strength = min(1.0, (oversold - prev_rsi) / 10)  # Stronger signal if more oversold
                signals.append(Signal(
                    pair=pair,
                    direction='long',
                    strength=strength,
                    indicator='RSI_oversold_bounce',
                    timestamp=timestamp,
                    price=current_price
                ))
                
            # Overbought reversal signal (short)
            elif prev_rsi >= overbought and current_rsi < overbought:
                strength = min(1.0, (prev_rsi - overbought) / 10)  # Stronger signal if more overbought
                signals.append(Signal(
                    pair=pair,
                    direction='short',
                    strength=strength,
                    indicator='RSI_overbought_reversal',
                    timestamp=timestamp,
                    price=current_price
                ))
                
        except Exception as e:
            self.logger.error(f"Error generating RSI signals for {pair}: {e}")
            
        return signals
        
    def _macd_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate MACD crossover signals."""
        signals = []
        
        try:
            # Use 5m timeframe for MACD
            if '5m' not in data or data['5m'].empty:
                return signals
                
            df = data['5m'].copy()
            fast = self.signal_config['macd']['fast_period']
            slow = self.signal_config['macd']['slow_period']
            signal_period = self.signal_config['macd']['signal_period']
            
            # Calculate MACD
            macd_indicator = ta.trend.MACD(df['close'], window_fast=fast, 
                                         window_slow=slow, window_sign=signal_period)
            df['macd'] = macd_indicator.macd()
            df['macd_signal'] = macd_indicator.macd_signal()
            df['macd_diff'] = macd_indicator.macd_diff()
            
            if len(df) < 2:
                return signals
                
            # Get latest values
            current_diff = df['macd_diff'].iloc[-1]
            prev_diff = df['macd_diff'].iloc[-2]
            current_price = df['close'].iloc[-1]
            timestamp = df.index[-1]
            
            # Bullish crossover (MACD crosses above signal)
            if prev_diff <= 0 and current_diff > 0:
                strength = min(1.0, abs(current_diff) / df['macd_diff'].std())
                signals.append(Signal(
                    pair=pair,
                    direction='long',
                    strength=strength,
                    indicator='MACD_bullish_crossover',
                    timestamp=timestamp,
                    price=current_price
                ))
                
            # Bearish crossover (MACD crosses below signal)
            elif prev_diff >= 0 and current_diff < 0:
                strength = min(1.0, abs(current_diff) / df['macd_diff'].std())
                signals.append(Signal(
                    pair=pair,
                    direction='short',
                    strength=strength,
                    indicator='MACD_bearish_crossover',
                    timestamp=timestamp,
                    price=current_price
                ))
                
        except Exception as e:
            self.logger.error(f"Error generating MACD signals for {pair}: {e}")
            
        return signals
        
    def _volume_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate volume spike signals."""
        signals = []
        
        try:
            # Use 1m timeframe for volume spikes
            if '1m' not in data or data['1m'].empty:
                return signals
                
            df = data['1m'].copy()
            spike_multiplier = self.signal_config['volume']['spike_multiplier']
            lookback = self.signal_config['volume']['lookback_periods']
            
            if len(df) < lookback + 1:
                return signals
                
            # Calculate volume moving average
            df['volume_ma'] = df['volume'].rolling(window=lookback).mean()
            
            # Get latest values
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume_ma'].iloc[-1]
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            timestamp = df.index[-1]
            
            # Volume spike with price movement
            if current_volume > (avg_volume * spike_multiplier):
                price_change = (current_price - prev_price) / prev_price
                
                # Bullish volume spike (price up)
                if price_change > 0.002:  # 0.2% price increase
                    strength = min(1.0, (current_volume / avg_volume - 1) / 3)  # Normalize strength
                    signals.append(Signal(
                        pair=pair,
                        direction='long',
                        strength=strength,
                        indicator='Volume_spike_bullish',
                        timestamp=timestamp,
                        price=current_price
                    ))
                    
                # Bearish volume spike (price down)
                elif price_change < -0.002:  # 0.2% price decrease
                    strength = min(1.0, (current_volume / avg_volume - 1) / 3)
                    signals.append(Signal(
                        pair=pair,
                        direction='short',
                        strength=strength,
                        indicator='Volume_spike_bearish',
                        timestamp=timestamp,
                        price=current_price
                    ))
                    
        except Exception as e:
            self.logger.error(f"Error generating volume signals for {pair}: {e}")
            
        return signals
        
    def _bollinger_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate Bollinger Bands breakout signals."""
        signals = []
        
        try:
            # Use 15m timeframe for Bollinger Bands
            if '15m' not in data or data['15m'].empty:
                return signals
                
            df = data['15m'].copy()
            period = self.signal_config['bb']['period']
            std_dev = self.signal_config['bb']['std_dev']
            
            # Calculate Bollinger Bands
            bb_indicator = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std_dev)
            df['bb_upper'] = bb_indicator.bollinger_hband()
            df['bb_lower'] = bb_indicator.bollinger_lband()
            df['bb_middle'] = bb_indicator.bollinger_mavg()
            
            if len(df) < 2:
                return signals
                
            # Get latest values
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            upper_band = df['bb_upper'].iloc[-1]
            lower_band = df['bb_lower'].iloc[-1]
            prev_upper = df['bb_upper'].iloc[-2]
            prev_lower = df['bb_lower'].iloc[-2]
            timestamp = df.index[-1]
            
            # Bullish breakout (price breaks above upper band)
            if prev_price <= prev_upper and current_price > upper_band:
                strength = min(1.0, (current_price - upper_band) / (upper_band * 0.01))
                signals.append(Signal(
                    pair=pair,
                    direction='long',
                    strength=strength,
                    indicator='BB_upper_breakout',
                    timestamp=timestamp,
                    price=current_price
                ))
                
            # Bearish breakdown (price breaks below lower band)
            elif prev_price >= prev_lower and current_price < lower_band:
                strength = min(1.0, (lower_band - current_price) / (lower_band * 0.01))
                signals.append(Signal(
                    pair=pair,
                    direction='short',
                    strength=strength,
                    indicator='BB_lower_breakdown',
                    timestamp=timestamp,
                    price=current_price
                ))
                
        except Exception as e:
            self.logger.error(f"Error generating Bollinger signals for {pair}: {e}")
            
        return signals
        
    def _ema_crossover_signals(self, pair: str, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate EMA crossover signals."""
        signals = []
        
        try:
            # Use 5m timeframe for EMA crossover
            if '5m' not in data or data['5m'].empty:
                return signals
                
            df = data['5m'].copy()
            fast_period = self.signal_config['ema']['fast_period']
            slow_period = self.signal_config['ema']['slow_period']
            
            # Calculate EMAs
            df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=fast_period).ema_indicator()
            df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=slow_period).ema_indicator()
            
            if len(df) < 2:
                return signals
                
            # Get latest values
            current_fast = df['ema_fast'].iloc[-1]
            current_slow = df['ema_slow'].iloc[-1]
            prev_fast = df['ema_fast'].iloc[-2]
            prev_slow = df['ema_slow'].iloc[-2]
            current_price = df['close'].iloc[-1]
            timestamp = df.index[-1]
            
            # Bullish crossover (fast EMA crosses above slow EMA)
            if prev_fast <= prev_slow and current_fast > current_slow:
                strength = min(1.0, (current_fast - current_slow) / current_slow)
                signals.append(Signal(
                    pair=pair,
                    direction='long',
                    strength=strength,
                    indicator='EMA_bullish_crossover',
                    timestamp=timestamp,
                    price=current_price
                ))
                
            # Bearish crossover (fast EMA crosses below slow EMA)
            elif prev_fast >= prev_slow and current_fast < current_slow:
                strength = min(1.0, (current_slow - current_fast) / current_slow)
                signals.append(Signal(
                    pair=pair,
                    direction='short',
                    strength=strength,
                    indicator='EMA_bearish_crossover',
                    timestamp=timestamp,
                    price=current_price
                ))
                
        except Exception as e:
            self.logger.error(f"Error generating EMA signals for {pair}: {e}")
            
        return signals
        
    def analyze_signal_confluence(self, signals: List[Signal]) -> Dict[str, List[Signal]]:
        """Analyze signal confluence and group by direction."""
        confluence = {'long': [], 'short': []}
        
        for signal in signals:
            confluence[signal.direction].append(signal)
            
        return confluence
        
    def has_sufficient_signals(self, signals: List[Signal], direction: str) -> bool:
        """Check if there are enough confirming signals to enter a trade."""
        min_signals = self.signal_config['min_confirming_signals']
        confirming_signals = [s for s in signals if s.direction == direction]
        
        return len(confirming_signals) >= min_signals
        
    def get_signal_strength(self, signals: List[Signal], direction: str) -> float:
        """Calculate overall signal strength for a direction."""
        confirming_signals = [s for s in signals if s.direction == direction]
        
        if not confirming_signals:
            return 0.0
            
        # Average strength weighted by individual strengths
        total_weight = sum(s.strength for s in confirming_signals)
        weighted_strength = sum(s.strength * s.strength for s in confirming_signals)
        
        if total_weight == 0:
            return 0.0
            
        return weighted_strength / total_weight