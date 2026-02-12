"""
Risk Manager - handles position sizing, daily loss limits, and risk controls.
Ensures trading stays within defined risk parameters.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json


@dataclass
class RiskMetrics:
    """Risk metrics for monitoring."""
    current_exposure: float
    daily_pnl: float
    daily_loss: float
    max_drawdown: float
    open_positions: int
    leverage_used: float
    risk_per_trade: float
    total_risk: float


class RiskManager:
    """Manages trading risk and enforces risk limits."""
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.risk_config = config['trading']['risk']
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.daily_loss = 0.0
        self.max_drawdown = 0.0
        self.trade_count_today = 0
        self.consecutive_losses = 0
        self.last_reset_date = datetime.now().date()
        
        # Position tracking
        self.open_positions = {}
        self.total_exposure = 0.0
        
        # Emergency controls
        self.trading_halted = False
        self.halt_reason = ""
        self.cooldown_until = None
        
        self.logger.info("Risk Manager initialized")
        
    def check_trade_eligibility(self, pair: str, direction: str, 
                              proposed_size: float, entry_price: float,
                              account_balance: float) -> Tuple[bool, str, float]:
        """
        Check if a trade can be executed and return adjusted size if needed.
        
        Returns:
            (can_trade, reason, adjusted_size)
        """
        try:
            # Check if trading is halted
            if self.trading_halted:
                return False, f"Trading halted: {self.halt_reason}", 0.0
                
            # Check cooldown period
            if self.cooldown_until and datetime.now() < self.cooldown_until:
                remaining = (self.cooldown_until - datetime.now()).total_seconds() / 60
                return False, f"In cooldown for {remaining:.1f} more minutes", 0.0
                
            # Daily loss limit check
            daily_limit = account_balance * (self.risk_config['daily_loss_limit_percent'] / 100)
            if self.daily_loss >= daily_limit:
                self._activate_cooldown("Daily loss limit reached")
                return False, "Daily loss limit exceeded", 0.0
                
            # Maximum concurrent positions check
            max_positions = self.risk_config['max_concurrent_positions']
            if len(self.open_positions) >= max_positions:
                return False, f"Maximum {max_positions} positions already open", 0.0
                
            # Position size validation and adjustment
            max_size = self._calculate_max_position_size(entry_price, account_balance)
            adjusted_size = min(proposed_size, max_size)
            
            if adjusted_size <= 0:
                return False, "Position size too small or insufficient capital", 0.0
                
            # Leverage check
            position_value = adjusted_size * entry_price
            required_margin = position_value / self.risk_config['max_leverage']
            
            if required_margin > account_balance * 0.8:  # Keep 20% buffer
                return False, "Insufficient margin for position", 0.0
                
            # Exposure check
            max_exposure = account_balance * (self.risk_config['max_leverage'] - 1)  # Leave some buffer
            if self.total_exposure + position_value > max_exposure:
                return False, "Maximum exposure limit reached", 0.0
                
            # Check if pair already has position (avoid doubling up)
            if pair in self.open_positions:
                existing_pos = self.open_positions[pair]
                if existing_pos['direction'] == direction:
                    return False, f"Already have {direction} position in {pair}", 0.0
                    
            return True, "Trade approved", adjusted_size
            
        except Exception as e:
            self.logger.error(f"Error checking trade eligibility: {e}")
            return False, "Risk check error", 0.0
            
    def _calculate_max_position_size(self, entry_price: float, account_balance: float) -> float:
        """Calculate maximum allowed position size."""
        # Maximum risk per trade
        max_risk_percent = self.risk_config['max_position_size_percent'] / 100
        max_risk_amount = account_balance * max_risk_percent
        
        # For simplicity, assume 1% stop loss to calculate max size
        # In practice, this would use the actual stop loss distance
        assumed_stop_distance = 0.01  # 1%
        risk_per_unit = entry_price * assumed_stop_distance
        
        max_size_by_risk = max_risk_amount / risk_per_unit
        
        # Maximum size by leverage
        max_leverage = self.risk_config['max_leverage']
        max_position_value = account_balance * max_leverage
        max_size_by_leverage = max_position_value / entry_price
        
        # Return the more conservative limit
        return min(max_size_by_risk, max_size_by_leverage)
        
    def register_position(self, position_id: str, pair: str, direction: str,
                         size: float, entry_price: float, stop_loss: float) -> bool:
        """Register a new position with risk manager."""
        try:
            position_value = size * entry_price
            risk_amount = abs(entry_price - stop_loss) * size
            
            position_info = {
                'pair': pair,
                'direction': direction,
                'size': size,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'position_value': position_value,
                'risk_amount': risk_amount,
                'entry_time': datetime.now()
            }
            
            self.open_positions[position_id] = position_info
            self.total_exposure += position_value
            self.trade_count_today += 1
            
            self.logger.info(f"Registered position: {pair} {direction} "
                           f"Size: {size:.4f} Risk: ${risk_amount:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering position {position_id}: {e}")
            return False
            
    def close_position(self, position_id: str, exit_price: float, 
                      exit_reason: str, realized_pnl: float) -> bool:
        """Close a position and update risk metrics."""
        try:
            if position_id not in self.open_positions:
                self.logger.warning(f"Position {position_id} not found in risk manager")
                return False
                
            position = self.open_positions[position_id]
            self.total_exposure -= position['position_value']
            
            # Update P&L tracking
            self.daily_pnl += realized_pnl
            
            if realized_pnl < 0:
                self.daily_loss += abs(realized_pnl)
                self.consecutive_losses += 1
                
                # Check if we need emergency cooldown
                if self.consecutive_losses >= 3:
                    self._activate_cooldown(f"{self.consecutive_losses} consecutive losses")
                    
            else:
                self.consecutive_losses = 0  # Reset on winning trade
                
            # Remove from tracking
            del self.open_positions[position_id]
            
            self.logger.info(f"Closed position: {position['pair']} "
                           f"P&L: ${realized_pnl:.2f} Reason: {exit_reason}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return False
            
    def update_position_prices(self, market_prices: Dict[str, float]):
        """Update positions with current market prices for risk monitoring."""
        try:
            total_unrealized_pnl = 0.0
            
            for position_id, position in self.open_positions.items():
                pair = position['pair']
                if pair in market_prices:
                    current_price = market_prices[pair]
                    
                    # Calculate unrealized P&L
                    if position['direction'] == 'long':
                        price_change = current_price - position['entry_price']
                    else:
                        price_change = position['entry_price'] - current_price
                        
                    unrealized_pnl = (price_change / position['entry_price']) * position['position_value']
                    total_unrealized_pnl += unrealized_pnl
                    
            # Check for emergency exit conditions
            self._check_emergency_conditions(total_unrealized_pnl)
            
        except Exception as e:
            self.logger.error(f"Error updating position prices: {e}")
            
    def _check_emergency_conditions(self, total_unrealized_pnl: float):
        """Check for conditions that require emergency action."""
        # Emergency stop if unrealized losses are too large
        emergency_loss_threshold = 0.15  # 15% of account
        
        if total_unrealized_pnl < -emergency_loss_threshold:
            self.halt_trading("Emergency: Large unrealized losses detected")
            
    def _activate_cooldown(self, reason: str):
        """Activate trading cooldown period."""
        cooldown_minutes = self.risk_config.get('cooldown_after_losses', 30)
        self.cooldown_until = datetime.now() + timedelta(minutes=cooldown_minutes)
        
        self.logger.warning(f"Activated {cooldown_minutes}min cooldown: {reason}")
        
    def halt_trading(self, reason: str):
        """Emergency halt all trading."""
        self.trading_halted = True
        self.halt_reason = reason
        
        self.logger.critical(f"TRADING HALTED: {reason}")
        
    def resume_trading(self):
        """Resume trading after halt."""
        self.trading_halted = False
        self.halt_reason = ""
        self.cooldown_until = None
        
        self.logger.info("Trading resumed")
        
    def reset_daily_counters(self):
        """Reset daily risk counters."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_loss = 0.0
            self.trade_count_today = 0
            self.last_reset_date = today
            
            self.logger.info("Daily risk counters reset")
            
    def get_risk_metrics(self, account_balance: float) -> RiskMetrics:
        """Get current risk metrics."""
        total_risk = sum(pos['risk_amount'] for pos in self.open_positions.values())
        leverage_used = self.total_exposure / account_balance if account_balance > 0 else 0
        
        return RiskMetrics(
            current_exposure=self.total_exposure,
            daily_pnl=self.daily_pnl,
            daily_loss=self.daily_loss,
            max_drawdown=self.max_drawdown,
            open_positions=len(self.open_positions),
            leverage_used=leverage_used,
            risk_per_trade=total_risk / len(self.open_positions) if self.open_positions else 0,
            total_risk=total_risk
        )
        
    def get_position_limits(self, account_balance: float) -> Dict[str, float]:
        """Get current position limits."""
        max_daily_loss = account_balance * (self.risk_config['daily_loss_limit_percent'] / 100)
        max_position_size = account_balance * (self.risk_config['max_position_size_percent'] / 100)
        max_exposure = account_balance * self.risk_config['max_leverage']
        
        return {
            'max_daily_loss': max_daily_loss,
            'remaining_daily_loss': max_daily_loss - self.daily_loss,
            'max_position_size': max_position_size,
            'max_exposure': max_exposure,
            'current_exposure': self.total_exposure,
            'remaining_exposure': max_exposure - self.total_exposure,
            'max_positions': self.risk_config['max_concurrent_positions'],
            'current_positions': len(self.open_positions)
        }
        
    def validate_stop_loss(self, entry_price: float, stop_loss: float, 
                          direction: str, max_risk_percent: float = 2.0) -> Tuple[bool, str]:
        """Validate stop loss is within acceptable risk range."""
        try:
            if direction == 'long':
                risk_percent = (entry_price - stop_loss) / entry_price * 100
            else:  # short
                risk_percent = (stop_loss - entry_price) / entry_price * 100
                
            if risk_percent > max_risk_percent:
                return False, f"Stop loss risk ({risk_percent:.1f}%) exceeds maximum ({max_risk_percent}%)"
                
            if risk_percent <= 0:
                return False, "Invalid stop loss level"
                
            return True, "Stop loss validated"
            
        except Exception as e:
            return False, f"Error validating stop loss: {e}"
            
    def get_recommended_position_size(self, entry_price: float, stop_loss: float,
                                    account_balance: float, risk_percent: float = 1.0) -> float:
        """Calculate recommended position size based on risk."""
        try:
            # Calculate risk per unit
            risk_per_unit = abs(entry_price - stop_loss)
            
            # Calculate risk amount
            risk_amount = account_balance * (risk_percent / 100)
            
            # Calculate position size
            if risk_per_unit > 0:
                position_size = risk_amount / risk_per_unit
            else:
                position_size = 0
                
            # Apply leverage constraints
            max_leverage = self.risk_config['max_leverage']
            max_position_value = account_balance * max_leverage
            max_size_by_leverage = max_position_value / entry_price
            
            return min(position_size, max_size_by_leverage)
            
        except Exception as e:
            self.logger.error(f"Error calculating recommended position size: {e}")
            return 0.0
            
    def log_risk_summary(self, account_balance: float):
        """Log current risk summary."""
        try:
            metrics = self.get_risk_metrics(account_balance)
            limits = self.get_position_limits(account_balance)
            
            self.logger.info(
                f"Risk Summary - "
                f"Positions: {metrics.open_positions}/{limits['max_positions']}, "
                f"Exposure: ${metrics.current_exposure:.2f}/${limits['max_exposure']:.2f}, "
                f"Leverage: {metrics.leverage_used:.1f}x/{self.risk_config['max_leverage']}x, "
                f"Daily P&L: ${metrics.daily_pnl:.2f}, "
                f"Daily Loss: ${metrics.daily_loss:.2f}/${limits['max_daily_loss']:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging risk summary: {e}")
            
    def export_risk_report(self) -> Dict:
        """Export comprehensive risk report."""
        return {
            'timestamp': datetime.now().isoformat(),
            'trading_status': 'halted' if self.trading_halted else 'active',
            'halt_reason': self.halt_reason,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'daily_stats': {
                'pnl': self.daily_pnl,
                'loss': self.daily_loss,
                'trade_count': self.trade_count_today,
                'consecutive_losses': self.consecutive_losses
            },
            'positions': {
                'count': len(self.open_positions),
                'total_exposure': self.total_exposure,
                'individual_positions': [
                    {
                        'id': pos_id,
                        'pair': pos['pair'],
                        'direction': pos['direction'],
                        'size': pos['size'],
                        'value': pos['position_value'],
                        'risk': pos['risk_amount']
                    }
                    for pos_id, pos in self.open_positions.items()
                ]
            },
            'limits': self.risk_config
        }