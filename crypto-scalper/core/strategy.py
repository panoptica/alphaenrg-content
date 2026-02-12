"""
Strategy Engine that combines signals to make trading decisions.
Implements the multi-signal momentum scalper strategy.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.signals import Signal, SignalEngine
import pandas as pd


@dataclass
class TradeSignal:
    """Represents a complete trading signal with entry/exit criteria."""
    pair: str
    direction: str  # 'long' or 'short'
    entry_price: float
    take_profit: float
    stop_loss: float
    confidence: float
    supporting_signals: List[Signal]
    timestamp: datetime
    timeframe: str = "5m"
    
    def __str__(self):
        return (f"{self.direction.upper()} {self.pair} @ {self.entry_price:.4f} "
                f"(TP: {self.take_profit:.4f}, SL: {self.stop_loss:.4f}, "
                f"Confidence: {self.confidence:.2f})")


class StrategyEngine:
    """Implements the multi-signal momentum scalping strategy."""
    
    def __init__(self, config: dict, signal_engine: SignalEngine):
        self.config = config
        self.signal_engine = signal_engine
        self.logger = logging.getLogger(__name__)
        
        # Strategy configuration
        self.strategy_config = config['trading']
        self.exit_config = config['trading']['exit']
        
        # Track recent trades to avoid over-trading
        self.recent_trades = {}
        self.cooldown_until = {}
        
    def analyze_pair(self, pair: str, market_data: Dict[str, pd.DataFrame]) -> Optional[TradeSignal]:
        """
        Analyze a trading pair and generate trade signal if conditions are met.
        
        Args:
            pair: Trading pair symbol
            market_data: Dictionary of timeframe -> DataFrame
            
        Returns:
            TradeSignal if entry conditions are met, None otherwise
        """
        try:
            # Check if pair is in cooldown
            if self._is_in_cooldown(pair):
                return None
                
            # Generate all signals for the pair
            signals = self.signal_engine.generate_signals(pair, market_data)
            
            if not signals:
                return None
                
            # Analyze signal confluence
            confluence = self.signal_engine.analyze_signal_confluence(signals)
            
            # Check for long opportunities
            if self.signal_engine.has_sufficient_signals(signals, 'long'):
                trade_signal = self._create_trade_signal(
                    pair, 'long', confluence['long'], market_data
                )
                if trade_signal:
                    self.logger.info(f"Long signal generated for {pair}: {trade_signal}")
                    return trade_signal
                    
            # Check for short opportunities
            elif self.signal_engine.has_sufficient_signals(signals, 'short'):
                trade_signal = self._create_trade_signal(
                    pair, 'short', confluence['short'], market_data
                )
                if trade_signal:
                    self.logger.info(f"Short signal generated for {pair}: {trade_signal}")
                    return trade_signal
                    
        except Exception as e:
            self.logger.error(f"Error analyzing {pair}: {e}")
            
        return None
        
    def _create_trade_signal(self, pair: str, direction: str, 
                           supporting_signals: List[Signal], 
                           market_data: Dict[str, pd.DataFrame]) -> Optional[TradeSignal]:
        """Create a complete trade signal with entry/exit levels."""
        try:
            # Get current price (use 1m for most recent)
            if '1m' not in market_data or market_data['1m'].empty:
                return None
                
            current_price = float(market_data['1m']['close'].iloc[-1])
            
            # Calculate confidence based on signal strength and confluence
            confidence = self.signal_engine.get_signal_strength(supporting_signals, direction)
            
            # Minimum confidence threshold
            if confidence < 0.6:
                return None
                
            # Calculate take profit and stop loss levels
            take_profit, stop_loss = self._calculate_exit_levels(
                current_price, direction
            )
            
            # Validate risk/reward ratio (minimum 2:1)
            risk = abs(current_price - stop_loss) / current_price
            reward = abs(take_profit - current_price) / current_price
            
            if reward / risk < 1.8:  # Slightly less than 2:1 to account for slippage
                self.logger.debug(f"Poor risk/reward ratio for {pair}: {reward/risk:.2f}")
                return None
                
            # Additional filters
            if not self._additional_filters(pair, direction, market_data):
                return None
                
            return TradeSignal(
                pair=pair,
                direction=direction,
                entry_price=current_price,
                take_profit=take_profit,
                stop_loss=stop_loss,
                confidence=confidence,
                supporting_signals=supporting_signals,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error creating trade signal for {pair}: {e}")
            return None
            
    def _calculate_exit_levels(self, entry_price: float, direction: str) -> Tuple[float, float]:
        """Calculate take profit and stop loss levels."""
        tp_percent = self.exit_config['take_profit_percent'] / 100
        sl_percent = self.exit_config['stop_loss_percent'] / 100
        
        if direction == 'long':
            take_profit = entry_price * (1 + tp_percent)
            stop_loss = entry_price * (1 - sl_percent)
        else:  # short
            take_profit = entry_price * (1 - tp_percent)
            stop_loss = entry_price * (1 + sl_percent)
            
        return take_profit, stop_loss
        
    def _additional_filters(self, pair: str, direction: str, 
                          market_data: Dict[str, pd.DataFrame]) -> bool:
        """Apply additional filters to improve signal quality."""
        try:
            # Volume filter - ensure sufficient volume
            if '1m' in market_data and not market_data['1m'].empty:
                recent_volume = market_data['1m']['volume'].tail(5).mean()
                if recent_volume < 1000:  # Minimum volume threshold
                    return False
                    
            # Volatility filter - avoid low volatility periods
            if '5m' in market_data and len(market_data['5m']) > 20:
                df = market_data['5m']
                atr = self._calculate_atr(df, period=14)
                current_atr = atr.iloc[-1] if not atr.empty else 0
                
                # Minimum ATR threshold (0.3% of price)
                current_price = df['close'].iloc[-1]
                if current_atr < (current_price * 0.003):
                    return False
                    
            # Time-based filter (avoid trading during low activity periods)
            current_hour = datetime.now().hour
            
            # Avoid 2-6 UTC (lowest activity in crypto)
            if 2 <= current_hour <= 6:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error in additional filters for {pair}: {e}")
            return False
            
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()
        
    def _is_in_cooldown(self, pair: str) -> bool:
        """Check if pair is in trading cooldown."""
        if pair not in self.cooldown_until:
            return False
            
        return datetime.now() < self.cooldown_until[pair]
        
    def set_cooldown(self, pair: str, minutes: int = 30):
        """Set cooldown period for a pair."""
        self.cooldown_until[pair] = datetime.now() + timedelta(minutes=minutes)
        self.logger.info(f"Set {minutes}min cooldown for {pair}")
        
    def should_exit_position(self, pair: str, direction: str, entry_price: float,
                           current_price: float, entry_time: datetime,
                           take_profit: float, stop_loss: float) -> Tuple[bool, str]:
        """
        Check if a position should be exited.
        
        Returns:
            (should_exit, exit_reason)
        """
        try:
            # Take profit check
            if direction == 'long' and current_price >= take_profit:
                return True, "take_profit"
            elif direction == 'short' and current_price <= take_profit:
                return True, "take_profit"
                
            # Stop loss check
            if direction == 'long' and current_price <= stop_loss:
                return True, "stop_loss"
            elif direction == 'short' and current_price >= stop_loss:
                return True, "stop_loss"
                
            # Time-based exit
            time_limit = timedelta(minutes=self.exit_config['time_stop_minutes'])
            if datetime.now() - entry_time >= time_limit:
                # Only exit if not profitable
                if direction == 'long' and current_price <= entry_price:
                    return True, "time_stop"
                elif direction == 'short' and current_price >= entry_price:
                    return True, "time_stop"
                    
            # Trailing stop logic
            trailing_threshold = self.exit_config['trailing_stop_percent'] / 100
            
            if direction == 'long':
                profit_percent = (current_price - entry_price) / entry_price
                if profit_percent >= trailing_threshold:
                    # Move stop to breakeven
                    new_stop_loss = entry_price
                    if current_price <= new_stop_loss:
                        return True, "trailing_stop"
                        
            else:  # short
                profit_percent = (entry_price - current_price) / entry_price
                if profit_percent >= trailing_threshold:
                    # Move stop to breakeven
                    new_stop_loss = entry_price
                    if current_price >= new_stop_loss:
                        return True, "trailing_stop"
                        
            return False, ""
            
        except Exception as e:
            self.logger.error(f"Error checking exit conditions for {pair}: {e}")
            return False, "error"
            
    def get_position_size(self, pair: str, entry_price: float, 
                         stop_loss: float, account_balance: float) -> float:
        """Calculate position size based on risk management rules."""
        try:
            # Maximum risk per trade
            max_risk_percent = self.strategy_config['risk']['max_position_size_percent'] / 100
            max_risk_amount = account_balance * max_risk_percent
            
            # Calculate risk per unit
            risk_per_unit = abs(entry_price - stop_loss)
            
            # Position size based on risk
            if risk_per_unit > 0:
                position_size = max_risk_amount / risk_per_unit
            else:
                position_size = 0
                
            # Apply maximum leverage limit
            max_leverage = self.strategy_config['risk']['max_leverage']
            max_position_value = account_balance * max_leverage
            max_size_by_leverage = max_position_value / entry_price
            
            # Take the smaller of the two
            final_size = min(position_size, max_size_by_leverage)
            
            self.logger.debug(f"Position size for {pair}: {final_size:.6f} "
                            f"(risk: {max_risk_amount:.2f}, leverage constraint: {max_size_by_leverage:.6f})")
            
            return final_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size for {pair}: {e}")
            return 0.0
            
    def record_trade_attempt(self, pair: str, direction: str):
        """Record a trade attempt to track frequency."""
        if pair not in self.recent_trades:
            self.recent_trades[pair] = []
            
        self.recent_trades[pair].append({
            'timestamp': datetime.now(),
            'direction': direction
        })
        
        # Keep only recent trades (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.recent_trades[pair] = [
            trade for trade in self.recent_trades[pair]
            if trade['timestamp'] > cutoff_time
        ]
        
    def get_market_sentiment(self, pair: str, market_data: Dict[str, pd.DataFrame]) -> str:
        """Analyze overall market sentiment for a pair."""
        try:
            if '15m' not in market_data or len(market_data['15m']) < 20:
                return 'neutral'
                
            df = market_data['15m']
            
            # Price trend analysis
            sma_20 = df['close'].rolling(window=20).mean()
            current_price = df['close'].iloc[-1]
            trend_sma = sma_20.iloc[-1]
            
            # Volume trend
            volume_sma = df['volume'].rolling(window=10).mean()
            current_volume = df['volume'].iloc[-1]
            avg_volume = volume_sma.iloc[-1]
            
            # Determine sentiment
            if current_price > trend_sma * 1.01 and current_volume > avg_volume * 1.2:
                return 'bullish'
            elif current_price < trend_sma * 0.99 and current_volume > avg_volume * 1.2:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.error(f"Error analyzing market sentiment for {pair}: {e}")
            return 'neutral'