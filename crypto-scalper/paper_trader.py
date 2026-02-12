"""
Paper Trading Executor - simulates trades with realistic fills and slippage.
Provides a safe environment to test strategies without real money.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random
import sqlite3
import json


@dataclass
class PaperPosition:
    """Represents a paper trading position."""
    id: str
    pair: str
    direction: str  # 'long' or 'short'
    size: float
    entry_price: float
    current_price: float
    take_profit: float
    stop_loss: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    fees_paid: float = 0.0
    status: str = 'open'  # 'open', 'closed'
    
    def update_pnl(self, current_price: float):
        """Update unrealized P&L based on current price."""
        self.current_price = current_price
        
        if self.direction == 'long':
            price_change = current_price - self.entry_price
        else:  # short
            price_change = self.entry_price - current_price
            
        self.unrealized_pnl = (price_change / self.entry_price) * self.size * self.entry_price
        

@dataclass
class PaperTrade:
    """Represents a completed paper trade."""
    id: str
    pair: str
    direction: str
    size: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    fees: float
    exit_reason: str
    duration_minutes: float
    signals_used: List[str] = field(default_factory=list)


class PaperTradingExecutor:
    """Simulates trade execution with realistic market conditions."""
    
    def __init__(self, config: dict, starting_balance: float = 1000.0):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Account state
        self.balance = starting_balance
        self.starting_balance = starting_balance
        self.positions: Dict[str, PaperPosition] = {}
        self.completed_trades: List[PaperTrade] = []
        
        # Statistics
        self.total_trades = 0
        self.winning_trades = 0
        self.total_fees_paid = 0.0
        self.max_drawdown = 0.0
        self.daily_pnl = {}
        
        # Risk tracking
        self.daily_loss = 0.0
        self.daily_trade_count = 0
        self.consecutive_losses = 0
        self.last_reset_date = datetime.now().date()
        
        # Trading fees (Bybit-like)
        self.maker_fee = 0.0001  # 0.01%
        self.taker_fee = 0.0006  # 0.06%
        
        # Slippage simulation
        self.base_slippage = 0.0002  # 0.02% base slippage
        self.volume_slippage_factor = 0.00001  # Additional slippage for large orders
        
        self.logger.info(f"Initialized paper trader with ${starting_balance:.2f}")
        
    def can_open_position(self, pair: str, size: float, price: float) -> Tuple[bool, str]:
        """Check if a new position can be opened."""
        try:
            # Daily loss limit check
            daily_limit = self.starting_balance * (self.config['trading']['risk']['daily_loss_limit_percent'] / 100)
            if self.daily_loss >= daily_limit:
                return False, "Daily loss limit reached"
                
            # Maximum concurrent positions check
            max_positions = self.config['trading']['risk']['max_concurrent_positions']
            if len(self.positions) >= max_positions:
                return False, f"Maximum {max_positions} positions already open"
                
            # Sufficient balance check
            position_value = size * price
            required_margin = position_value / self.config['trading']['risk']['max_leverage']
            
            if required_margin > self.balance * 0.8:  # Keep 20% buffer
                return False, "Insufficient margin available"
                
            # Cooldown after consecutive losses
            if self.consecutive_losses >= 3:
                return False, f"Cooling down after {self.consecutive_losses} consecutive losses"
                
            return True, "OK"
            
        except Exception as e:
            self.logger.error(f"Error checking position eligibility: {e}")
            return False, "Error in position check"
            
    def open_position(self, pair: str, direction: str, size: float, 
                     entry_price: float, take_profit: float, 
                     stop_loss: float, signals_used: List[str] = None) -> Optional[str]:
        """Open a new paper trading position."""
        try:
            # Check if position can be opened
            can_open, reason = self.can_open_position(pair, size, entry_price)
            if not can_open:
                self.logger.warning(f"Cannot open position for {pair}: {reason}")
                return None
                
            # Simulate realistic fill price with slippage
            fill_price = self._simulate_fill_price(entry_price, direction, size, 'market')
            
            # Calculate fees
            position_value = size * fill_price
            fees = position_value * self.taker_fee  # Market orders pay taker fee
            
            # Update account balance for fees
            self.balance -= fees
            self.total_fees_paid += fees
            
            # Create position
            position_id = f"{pair}_{direction}_{datetime.now().strftime('%H%M%S')}"
            position = PaperPosition(
                id=position_id,
                pair=pair,
                direction=direction,
                size=size,
                entry_price=fill_price,
                current_price=fill_price,
                take_profit=take_profit,
                stop_loss=stop_loss,
                entry_time=datetime.now(),
                fees_paid=fees
            )
            
            self.positions[position_id] = position
            self.daily_trade_count += 1
            self.total_trades += 1
            
            self.logger.info(f"Opened {direction} position: {pair} x{size:.4f} @ {fill_price:.4f} "
                           f"(TP: {take_profit:.4f}, SL: {stop_loss:.4f}, Fees: ${fees:.2f})")
            
            return position_id
            
        except Exception as e:
            self.logger.error(f"Error opening position for {pair}: {e}")
            return None
            
    def close_position(self, position_id: str, current_price: float, 
                      exit_reason: str = "manual") -> Optional[PaperTrade]:
        """Close an existing position."""
        try:
            if position_id not in self.positions:
                self.logger.warning(f"Position {position_id} not found")
                return None
                
            position = self.positions[position_id]
            
            # Simulate realistic fill price with slippage
            fill_price = self._simulate_fill_price(current_price, 
                                                 self._opposite_direction(position.direction),
                                                 position.size, 'market')
            
            # Calculate P&L
            if position.direction == 'long':
                price_change = fill_price - position.entry_price
            else:  # short
                price_change = position.entry_price - fill_price
                
            pnl = (price_change / position.entry_price) * position.size * position.entry_price
            
            # Calculate exit fees
            position_value = position.size * fill_price
            exit_fees = position_value * self.taker_fee
            
            # Net P&L after fees
            net_pnl = pnl - position.fees_paid - exit_fees
            
            # Update account balance
            self.balance += net_pnl + position.fees_paid  # Fees already deducted at entry
            self.total_fees_paid += exit_fees
            
            # Update daily P&L
            today = datetime.now().date()
            if today not in self.daily_pnl:
                self.daily_pnl[today] = 0.0
            self.daily_pnl[today] += net_pnl
            
            # Update daily loss tracking
            if net_pnl < 0:
                self.daily_loss += abs(net_pnl)
                self.consecutive_losses += 1
            else:
                self.winning_trades += 1
                self.consecutive_losses = 0  # Reset on winning trade
                
            # Calculate trade duration
            duration = (datetime.now() - position.entry_time).total_seconds() / 60
            
            # Create completed trade record
            trade = PaperTrade(
                id=position_id,
                pair=position.pair,
                direction=position.direction,
                size=position.size,
                entry_price=position.entry_price,
                exit_price=fill_price,
                entry_time=position.entry_time,
                exit_time=datetime.now(),
                pnl=net_pnl,
                fees=position.fees_paid + exit_fees,
                exit_reason=exit_reason,
                duration_minutes=duration,
                signals_used=[]  # Could be populated with actual signals used
            )
            
            self.completed_trades.append(trade)
            
            # Remove from active positions
            del self.positions[position_id]
            
            # Update drawdown
            self._update_max_drawdown()
            
            self.logger.info(f"Closed position: {position.pair} {position.direction} "
                           f"@ {fill_price:.4f} | P&L: ${net_pnl:.2f} | Reason: {exit_reason}")
            
            return trade
            
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return None
            
    def update_positions(self, market_prices: Dict[str, float]) -> List[str]:
        """
        Update all positions with current market prices and check exit conditions.
        
        Returns:
            List of position IDs that were closed
        """
        closed_positions = []
        
        try:
            for position_id, position in list(self.positions.items()):
                if position.pair not in market_prices:
                    continue
                    
                current_price = market_prices[position.pair]
                position.update_pnl(current_price)
                
                # Check exit conditions
                should_exit, exit_reason = self._check_exit_conditions(position, current_price)
                
                if should_exit:
                    trade = self.close_position(position_id, current_price, exit_reason)
                    if trade:
                        closed_positions.append(position_id)
                        
        except Exception as e:
            self.logger.error(f"Error updating positions: {e}")
            
        return closed_positions
        
    def _check_exit_conditions(self, position: PaperPosition, current_price: float) -> Tuple[bool, str]:
        """Check if position should be exited."""
        # Take profit
        if position.direction == 'long' and current_price >= position.take_profit:
            return True, "take_profit"
        elif position.direction == 'short' and current_price <= position.take_profit:
            return True, "take_profit"
            
        # Stop loss
        if position.direction == 'long' and current_price <= position.stop_loss:
            return True, "stop_loss"
        elif position.direction == 'short' and current_price >= position.stop_loss:
            return True, "stop_loss"
            
        # Time-based exit (15 minutes)
        time_limit = timedelta(minutes=self.config['trading']['exit']['time_stop_minutes'])
        if datetime.now() - position.entry_time >= time_limit:
            return True, "time_stop"
            
        return False, ""
        
    def _simulate_fill_price(self, market_price: float, direction: str, 
                           size: float, order_type: str) -> float:
        """Simulate realistic fill price with slippage."""
        # Base slippage
        slippage = self.base_slippage
        
        # Add volume-based slippage for larger orders
        position_value = size * market_price
        if position_value > 10000:  # Large order > $10k
            slippage += self.volume_slippage_factor * (position_value / 10000)
            
        # Add random market impact
        market_impact = random.uniform(0, 0.0001)  # 0-0.01% random impact
        
        total_slippage = slippage + market_impact
        
        # Apply slippage based on direction (buying = worse price, selling = worse price)
        if direction == 'long':  # Buying
            fill_price = market_price * (1 + total_slippage)
        else:  # Selling
            fill_price = market_price * (1 - total_slippage)
            
        return fill_price
        
    def _opposite_direction(self, direction: str) -> str:
        """Get opposite direction for closing trades."""
        return 'short' if direction == 'long' else 'long'
        
    def _update_max_drawdown(self):
        """Update maximum drawdown tracking."""
        current_equity = self.get_total_equity()
        peak_equity = max(self.starting_balance, 
                         max([self.starting_balance] + [eq for eq in [current_equity]]))
        
        drawdown = (peak_equity - current_equity) / peak_equity
        self.max_drawdown = max(self.max_drawdown, drawdown)
        
    def get_total_equity(self) -> float:
        """Calculate total account equity including unrealized P&L."""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions.values())
        return self.balance + unrealized_pnl
        
    def get_statistics(self) -> dict:
        """Get comprehensive trading statistics."""
        total_equity = self.get_total_equity()
        total_return = (total_equity - self.starting_balance) / self.starting_balance * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # Calculate average trade metrics
        winning_trades_list = [t for t in self.completed_trades if t.pnl > 0]
        losing_trades_list = [t for t in self.completed_trades if t.pnl < 0]
        
        avg_win = sum(t.pnl for t in winning_trades_list) / len(winning_trades_list) if winning_trades_list else 0
        avg_loss = sum(t.pnl for t in losing_trades_list) / len(losing_trades_list) if losing_trades_list else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.balance,
            'total_equity': total_equity,
            'total_return_pct': total_return,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.total_trades - self.winning_trades,
            'win_rate_pct': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_pct': self.max_drawdown * 100,
            'total_fees_paid': self.total_fees_paid,
            'daily_loss': self.daily_loss,
            'consecutive_losses': self.consecutive_losses,
            'open_positions': len(self.positions),
            'daily_trades': self.daily_trade_count
        }
        
    def reset_daily_counters(self):
        """Reset daily counters for new trading day."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_loss = 0.0
            self.daily_trade_count = 0
            self.last_reset_date = today
            self.logger.info("Daily counters reset for new trading day")
            
    def get_position_summary(self) -> List[dict]:
        """Get summary of all open positions."""
        positions_summary = []
        
        for pos in self.positions.values():
            positions_summary.append({
                'id': pos.id,
                'pair': pos.pair,
                'direction': pos.direction,
                'size': pos.size,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'unrealized_pnl': pos.unrealized_pnl,
                'take_profit': pos.take_profit,
                'stop_loss': pos.stop_loss,
                'entry_time': pos.entry_time.isoformat(),
                'duration_minutes': (datetime.now() - pos.entry_time).total_seconds() / 60
            })
            
        return positions_summary
        
    def save_trade_to_db(self, trade: PaperTrade, db_path: str):
        """Save completed trade to database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO trades 
                (id, pair, direction, size, entry_price, exit_price, entry_time, 
                 exit_time, pnl, fees, exit_reason, duration_minutes, signals_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trade.id, trade.pair, trade.direction, trade.size,
                trade.entry_price, trade.exit_price,
                trade.entry_time.isoformat(), trade.exit_time.isoformat(),
                trade.pnl, trade.fees, trade.exit_reason, trade.duration_minutes,
                json.dumps(trade.signals_used)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error saving trade to database: {e}")