#!/usr/bin/env python3
"""
Crypto Scalper Bot - Main Entry Point
Multi-signal momentum scalping bot with paper trading mode.
"""

import os
import sys
import time
import signal
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
import pandas as pd
from dotenv import load_dotenv

# Import our modules
from core.market_data import MarketDataEngine
from core.signals import SignalEngine
from core.strategy import StrategyEngine
from core.risk_manager import RiskManager
from paper_trader import PaperTradingExecutor
from utils.logger import setup_logging, TradeLogger, AlertLogger, log_system_info, log_config_summary
from utils.database import DatabaseManager


class CryptoScalperBot:
    """Main trading bot orchestrator."""
    
    def __init__(self):
        # Load configuration
        self.config = self._load_config()
        
        # Initialize logging
        self.logger = setup_logging(self.config)
        log_system_info()
        log_config_summary(self.config)
        
        # Specialized loggers
        self.trade_logger = TradeLogger()
        self.alert_logger = AlertLogger()
        
        # Initialize database
        db_path = os.getenv('DATABASE_PATH', './data/trades.db')
        self.database = DatabaseManager(db_path)
        
        # Initialize core components
        self.market_data = MarketDataEngine(self.config)
        self.signal_engine = SignalEngine(self.config)
        self.strategy_engine = StrategyEngine(self.config, self.signal_engine)
        self.risk_manager = RiskManager(self.config)
        
        # Initialize paper trader
        starting_capital = float(os.getenv('STARTING_CAPITAL', 
                                          self.config['trading']['starting_capital']))
        self.paper_trader = PaperTradingExecutor(self.config, starting_capital)
        
        # Bot state
        self.running = False
        self.last_update = None
        self.update_interval = self.config['trading']['data']['update_interval']
        
        # Performance tracking
        self.start_time = datetime.now()
        self.loop_count = 0
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Crypto Scalper Bot initialized successfully")
        
    def _load_config(self) -> dict:
        """Load configuration from files."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Load main config
            with open('config/settings.yaml', 'r') as f:
                config = yaml.safe_load(f)
                
            # Override with environment variables if set
            paper_trading = os.getenv('PAPER_TRADING', '').lower() == 'true'
            if paper_trading is not None:
                config['trading']['paper_trading'] = paper_trading
                
            return config
            
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            sys.exit(1)
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.stop()
        
    def start(self):
        """Start the trading bot."""
        self.logger.info("Starting Crypto Scalper Bot...")
        self.running = True
        
        try:
            # Check exchange connectivity
            if not self._check_system_health():
                self.logger.error("System health check failed. Aborting startup.")
                return
                
            # Start main trading loop
            self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Fatal error in main loop: {e}")
            self.alert_logger.trading_halted(f"Fatal error: {e}")
            
        finally:
            self._cleanup()
            
    def stop(self):
        """Stop the trading bot."""
        self.logger.info("Stopping Crypto Scalper Bot...")
        self.running = False
        
    def _check_system_health(self) -> bool:
        """Verify system components are working."""
        self.logger.info("Performing system health check...")
        
        try:
            # Check exchange connections
            health = self.market_data.health_check()
            for exchange, status in health.items():
                if status:
                    self.logger.info(f"✓ {exchange.title()} exchange: Connected")
                else:
                    self.logger.warning(f"✗ {exchange.title()} exchange: Disconnected")
                    
            if not any(health.values()):
                self.logger.error("No exchange connections available")
                return False
                
            # Test market data fetching
            test_pair = "BTC/USDT"
            test_data = self.market_data.fetch_candles(test_pair, "1m", 10)
            if test_data.empty:
                self.logger.error("Failed to fetch test market data")
                return False
            else:
                self.logger.info(f"✓ Market data: Successfully fetched {len(test_data)} candles")
                
            # Check database
            try:
                stats = self.database.get_trade_statistics(1)  # Test query
                self.logger.info("✓ Database: Connected and operational")
            except Exception as e:
                self.logger.error(f"✗ Database error: {e}")
                return False
                
            self.logger.info("System health check passed ✓")
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
            
    def _run_main_loop(self):
        """Main trading loop."""
        self.logger.info(f"Starting main trading loop (update interval: {self.update_interval}s)")
        
        while self.running:
            try:
                loop_start = time.time()
                
                # Reset daily counters if needed
                self.paper_trader.reset_daily_counters()
                self.risk_manager.reset_daily_counters()
                
                # Update market data for all pairs
                self.logger.debug("Fetching market data...")
                all_market_data = self.market_data.update_all_pairs()
                
                if not all_market_data:
                    self.logger.warning("No market data received, skipping cycle")
                    time.sleep(self.update_interval)
                    continue
                    
                # Update open positions with current prices
                current_prices = {}
                for pair in all_market_data:
                    if '1m' in all_market_data[pair] and not all_market_data[pair]['1m'].empty:
                        current_prices[pair] = all_market_data[pair]['1m']['close'].iloc[-1]
                        
                # Update paper trader positions
                closed_positions = self.paper_trader.update_positions(current_prices)
                
                # Log closed positions
                for position_id in closed_positions:
                    self.logger.info(f"Position closed: {position_id}")
                    
                # Update risk manager
                self.risk_manager.update_position_prices(current_prices)
                
                # Generate and evaluate signals for each pair
                for pair, market_data in all_market_data.items():
                    try:
                        self._process_pair_signals(pair, market_data)
                    except Exception as e:
                        self.logger.error(f"Error processing signals for {pair}: {e}")
                        
                # Log performance summary periodically
                if self.loop_count % 10 == 0:  # Every 10 cycles
                    self._log_performance_summary()
                    
                # Calculate sleep time to maintain consistent interval
                loop_duration = time.time() - loop_start
                sleep_time = max(0, self.update_interval - loop_duration)
                
                if loop_duration > self.update_interval:
                    self.logger.warning(f"Loop took {loop_duration:.1f}s (>{self.update_interval}s interval)")
                    
                self.loop_count += 1
                self.last_update = datetime.now()
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Brief pause before retrying
                
    def _process_pair_signals(self, pair: str, market_data: Dict[str, pd.DataFrame]):
        """Process signals for a specific trading pair."""
        try:
            # Check if we already have a position in this pair
            existing_positions = [pos for pos in self.paper_trader.positions.values() 
                                if pos.pair == pair]
            
            if existing_positions:
                self.logger.debug(f"Skipping {pair} - position already open")
                return
                
            # Generate trade signal
            trade_signal = self.strategy_engine.analyze_pair(pair, market_data)
            
            if not trade_signal:
                return
                
            # Log the signal
            self.trade_logger.log_signal(
                pair, trade_signal.direction, 
                f"{len(trade_signal.supporting_signals)} confirming signals",
                trade_signal.confidence, trade_signal.entry_price
            )
            
            # Log signals to database
            for signal in trade_signal.supporting_signals:
                self.database.log_signal({
                    'pair': signal.pair,
                    'direction': signal.direction,
                    'indicator': signal.indicator,
                    'strength': signal.strength,
                    'price': signal.price,
                    'timestamp': signal.timestamp.isoformat(),
                    'was_traded': False  # Will update if trade is executed
                })
                
            # Check risk management
            account_balance = self.paper_trader.get_total_equity()
            position_size = self.strategy_engine.get_position_size(
                pair, trade_signal.entry_price, trade_signal.stop_loss, account_balance
            )
            
            can_trade, reason, adjusted_size = self.risk_manager.check_trade_eligibility(
                pair, trade_signal.direction, position_size, 
                trade_signal.entry_price, account_balance
            )
            
            if not can_trade:
                self.logger.info(f"Trade rejected for {pair}: {reason}")
                return
                
            # Execute paper trade
            signal_names = [s.indicator for s in trade_signal.supporting_signals]
            position_id = self.paper_trader.open_position(
                pair=pair,
                direction=trade_signal.direction,
                size=adjusted_size,
                entry_price=trade_signal.entry_price,
                take_profit=trade_signal.take_profit,
                stop_loss=trade_signal.stop_loss,
                signals_used=signal_names
            )
            
            if position_id:
                # Register position with risk manager
                self.risk_manager.register_position(
                    position_id, pair, trade_signal.direction,
                    adjusted_size, trade_signal.entry_price, trade_signal.stop_loss
                )
                
                # Log trade entry
                self.trade_logger.log_trade_entry(
                    pair, trade_signal.direction, adjusted_size,
                    trade_signal.entry_price, trade_signal.take_profit, trade_signal.stop_loss
                )
                
                # Update signal database to mark as traded
                for signal in trade_signal.supporting_signals:
                    # This would need a more sophisticated matching in a real system
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error processing signals for {pair}: {e}")
            
    def _log_performance_summary(self):
        """Log current performance summary."""
        try:
            stats = self.paper_trader.get_statistics()
            self.trade_logger.log_performance_summary(stats)
            
            # Log risk metrics
            risk_metrics = self.risk_manager.get_risk_metrics(stats['current_balance'])
            self.risk_manager.log_risk_summary(stats['current_balance'])
            
            # Save daily performance to database
            today = datetime.now().date().isoformat()
            self.database.log_daily_performance(today, {
                'starting_balance': stats['starting_balance'],
                'ending_balance': stats['total_equity'],
                'total_trades': stats['total_trades'],
                'winning_trades': stats['winning_trades'],
                'total_pnl': stats['total_equity'] - stats['starting_balance'],
                'total_fees': stats['total_fees_paid'],
                'max_drawdown': stats['max_drawdown_pct'] / 100,
                'pairs_traded': list(self.market_data.pairs.keys())
            })
            
        except Exception as e:
            self.logger.error(f"Error logging performance summary: {e}")
            
    def _cleanup(self):
        """Cleanup resources on shutdown."""
        self.logger.info("Performing cleanup...")
        
        try:
            # Close all open positions
            if self.paper_trader.positions:
                self.logger.info(f"Closing {len(self.paper_trader.positions)} open positions...")
                current_prices = {}
                
                # Get current prices for position closing
                for pair in self.paper_trader.positions.values():
                    try:
                        price = self.market_data.get_latest_price(pair.pair)
                        if price > 0:
                            current_prices[pair.pair] = price
                    except Exception as e:
                        self.logger.warning(f"Could not get closing price for {pair.pair}: {e}")
                        
                # Close all positions
                for position_id, position in list(self.paper_trader.positions.items()):
                    if position.pair in current_prices:
                        self.paper_trader.close_position(
                            position_id, current_prices[position.pair], "bot_shutdown"
                        )
                        
            # Final performance summary
            final_stats = self.paper_trader.get_statistics()
            self.logger.info(f"Final Performance Summary:")
            self.logger.info(f"  Total Return: {final_stats['total_return_pct']:.2f}%")
            self.logger.info(f"  Total Trades: {final_stats['total_trades']}")
            self.logger.info(f"  Win Rate: {final_stats['win_rate_pct']:.1f}%")
            self.logger.info(f"  Profit Factor: {final_stats['profit_factor']:.2f}")
            self.logger.info(f"  Max Drawdown: {final_stats['max_drawdown_pct']:.2f}%")
            
            # Save final performance
            runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
            self.logger.info(f"Bot ran for {runtime_minutes:.1f} minutes ({self.loop_count} cycles)")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
        self.logger.info("Crypto Scalper Bot shutdown complete")
        

def main():
    """Main entry point."""
    print("Crypto Scalper Bot v1.0")
    print("=" * 50)
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and start the bot
    bot = CryptoScalperBot()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()