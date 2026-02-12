# Crypto Scalper Bot

A multi-signal momentum scalping bot for cryptocurrency trading with comprehensive paper trading mode. The bot uses technical indicators to identify short-term trading opportunities on crypto futures markets.

## Features

- **Paper Trading Mode**: Safe testing environment with realistic simulation
- **Multi-Signal Strategy**: Requires 3+ confirming signals before entering trades
- **Technical Indicators**: RSI, MACD, Volume spikes, Bollinger Bands, EMA crossovers
- **Risk Management**: Position sizing, daily loss limits, leverage controls
- **Real-time Market Data**: Via CCXT library for Bybit and Binance
- **Comprehensive Logging**: Trade logs, performance metrics, risk events
- **SQLite Database**: Persistent storage for trades and analytics

## Strategy Overview

The bot implements a momentum scalping strategy targeting 15-minute trades:

**Entry Signals (requires 3+ confirming):**
- RSI(14) oversold bounce or overbought reversal
- MACD crossover on 5m timeframe  
- Volume spike (>2x average)
- Bollinger Band breakout on 15m timeframe
- EMA(9) crossing EMA(21) on 5m timeframe

**Risk Management:**
- Maximum 10% position size per trade
- Maximum 5x leverage
- 5% daily loss limit
- Maximum 2 concurrent positions
- 30-minute cooldown after 3 consecutive losses

**Exit Rules:**
- Take profit: 1.5% target
- Stop loss: 0.75% maximum loss
- Time stop: 15 minutes
- Trailing stop: Move to breakeven after 0.5% profit

## Installation

### Prerequisites

- Python 3.11 or higher
- Git

### Setup

1. **Clone and navigate to the project:**
```bash
cd /path/to/crypto-scalper
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` file with your API credentials:
```env
# For live trading (optional - paper trading works without these)
BYBIT_API_KEY=your_bybit_api_key_here
BYBIT_SECRET=your_bybit_secret_here
BYBIT_TESTNET=true

# Bot settings
PAPER_TRADING=true
STARTING_CAPITAL=1000.0
```

### API Key Setup (Optional for Paper Trading)

**For Bybit:**
1. Visit [Bybit API Management](https://www.bybit.com/app/user/api-management)
2. Create new API key with futures trading permissions
3. Add your IP address to the whitelist
4. Copy API key and secret to `.env` file

**Note:** Paper trading mode works without API keys and is enabled by default.

## Configuration

### Main Settings (`config/settings.yaml`)

Key configuration options:

```yaml
trading:
  paper_trading: true        # Enable paper trading mode
  starting_capital: 1000.0   # Starting balance in USDT
  
  risk:
    max_position_size_percent: 10  # Max 10% per trade
    max_leverage: 5               # Max 5x leverage
    daily_loss_limit_percent: 5   # Stop trading at 5% daily loss
    max_concurrent_positions: 2   # Maximum 2 positions open
    
  signals:
    min_confirming_signals: 3     # Require 3+ signals to trade
    
  exit:
    take_profit_percent: 1.5      # 1.5% profit target
    stop_loss_percent: 0.75       # 0.75% stop loss
    time_stop_minutes: 15         # Exit after 15 minutes
```

### Trading Pairs (`config/pairs.yaml`)

Configure which pairs to trade:

```yaml
pairs:
  BTC/USDT:
    enabled: true
    priority: 1
    
  ETH/USDT:
    enabled: true  
    priority: 2
    
  SOL/USDT:
    enabled: true
    priority: 3
```

## Usage

### Start the Bot

```bash
python main.py
```

The bot will:
1. Perform system health checks
2. Connect to exchanges (if configured)
3. Start the main trading loop
4. Update market data every 60 seconds
5. Generate signals and execute paper trades
6. Log all activity to console and files

### Monitor Performance

**Real-time logs:**
- Console output shows live trading activity
- Log files in `logs/` directory with detailed information

**Database analytics:**
- SQLite database at `data/trades.db`
- Contains trades, signals, and performance metrics
- Can be analyzed with any SQLite browser

**Performance metrics:**
- Win rate percentage
- Profit factor (gross profit / gross loss)
- Average trade duration
- Maximum drawdown
- Daily P&L tracking

### Stop the Bot

Use `Ctrl+C` to stop gracefully. The bot will:
- Close all open positions at market price
- Save final performance statistics
- Complete database writes
- Display final summary

## Safety Features

### Paper Trading Mode (Default)
- Simulates realistic trade execution with slippage
- Uses actual market data and signals
- Safe environment for strategy testing
- No real money at risk

### Risk Controls
- Automatic position sizing based on stop loss distance
- Daily loss limits with automatic trading halt
- Maximum leverage enforcement
- Cooldown periods after consecutive losses
- Emergency halt capabilities

### Data Backup
- All trades logged to SQLite database
- Automatic log file rotation
- Performance metrics saved daily
- Trade signals recorded for analysis

## File Structure

```
crypto-scalper/
├── config/
│   ├── settings.yaml      # Main configuration
│   └── pairs.yaml         # Trading pairs setup
├── core/
│   ├── market_data.py     # Market data engine
│   ├── signals.py         # Technical indicators
│   ├── strategy.py        # Trading strategy logic
│   └── risk_manager.py    # Risk management
├── utils/
│   ├── database.py        # SQLite database manager
│   └── logger.py          # Logging utilities
├── data/
│   └── trades.db          # SQLite database
├── logs/                  # Log files
├── main.py                # Main application
├── paper_trader.py        # Paper trading simulator
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
└── README.md              # This file
```

## Development

### Adding New Indicators

To add a new technical indicator:

1. Create indicator function in `core/signals.py`
2. Add configuration to `config/settings.yaml`
3. Update signal generation logic
4. Test in paper trading mode

### Modifying Strategy

The main strategy logic is in `core/strategy.py`:
- `analyze_pair()`: Main signal evaluation
- `_create_trade_signal()`: Trade signal creation
- `should_exit_position()`: Exit condition checks

### Database Schema

The SQLite database contains these tables:
- `trades`: Completed trades with P&L
- `signals`: All generated signals
- `performance`: Daily performance metrics
- `risk_events`: Risk management events

## Troubleshooting

### Common Issues

**"No market data received"**
- Check internet connection
- Verify exchange status
- Review API key configuration (if using live data)

**"Daily loss limit reached"**
- This is normal risk management
- Review strategy parameters
- Wait for next trading day or restart manually

**High CPU usage**
- Reduce update frequency in settings
- Limit number of trading pairs
- Check for infinite loops in logs

### Support

For issues or questions:
1. Check log files in `logs/` directory
2. Review configuration files
3. Verify all dependencies are installed
4. Test with minimal configuration (1 pair, default settings)

## Disclaimer

This software is for educational and testing purposes only. Cryptocurrency trading involves substantial risk of loss. Never trade more than you can afford to lose. Past performance does not guarantee future results.

**Paper trading mode is enabled by default.** Real trading requires explicit configuration and should only be used after thorough testing.

## License

MIT License - see LICENSE file for details.