#!/usr/bin/env python3
"""
Test script to verify the crypto scalper installation is working correctly.
Run this before starting the main bot to catch any configuration issues.
"""

import os
import sys
import yaml
import importlib.util
from dotenv import load_dotenv


def test_python_version():
    """Test Python version compatibility."""
    print("Testing Python version...")
    if sys.version_info < (3, 11):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detected. Python 3.11+ required.")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def test_dependencies():
    """Test required Python packages."""
    print("\nTesting dependencies...")
    
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'pyyaml', 
        'python-dotenv', 'ta', 'requests', 'websocket-client'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            # Handle package name differences
            import_name = package
            if package == 'python-dotenv':
                import_name = 'dotenv'
            elif package == 'websocket-client':
                import_name = 'websocket'
            elif package == 'pyyaml':
                import_name = 'yaml'
                
            importlib.import_module(import_name)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def test_configuration():
    """Test configuration files."""
    print("\nTesting configuration...")
    
    # Test main config
    try:
        with open('config/settings.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ config/settings.yaml")
        
        # Validate key sections
        required_sections = ['trading', 'exchanges', 'logging']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing section '{section}' in settings.yaml")
                return False
                
    except FileNotFoundError:
        print("❌ config/settings.yaml not found")
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in settings.yaml: {e}")
        return False
    
    # Test pairs config
    try:
        with open('config/pairs.yaml', 'r') as f:
            pairs_config = yaml.safe_load(f)
        print("✅ config/pairs.yaml")
        
        # Check for enabled pairs
        enabled_pairs = [pair for pair, cfg in pairs_config.get('pairs', {}).items() 
                        if cfg.get('enabled', True)]
        if not enabled_pairs:
            print("⚠️  No trading pairs enabled")
        else:
            print(f"📊 Enabled pairs: {', '.join(enabled_pairs)}")
            
    except FileNotFoundError:
        print("❌ config/pairs.yaml not found")
        return False
    
    return True


def test_environment():
    """Test environment configuration."""
    print("\nTesting environment...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check paper trading setting
        paper_trading = os.getenv('PAPER_TRADING', 'true').lower() == 'true'
        if paper_trading:
            print("✅ Paper trading mode enabled")
        else:
            print("⚠️  Live trading mode - ensure API keys are configured")
            
            # Check API keys if live trading
            api_key = os.getenv('BYBIT_API_KEY')
            api_secret = os.getenv('BYBIT_SECRET')
            
            if not api_key or not api_secret:
                print("❌ Live trading mode requires API keys")
                return False
                
    else:
        print("⚠️  .env file not found (copy from .env.example)")
        print("📝 Using default paper trading mode")
    
    return True


def test_directories():
    """Test required directories."""
    print("\nTesting directories...")
    
    required_dirs = ['data', 'logs', 'config']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - creating...")
            os.makedirs(directory, exist_ok=True)
    
    return True


def test_imports():
    """Test importing bot modules."""
    print("\nTesting bot modules...")
    
    try:
        from core.market_data import MarketDataEngine
        print("✅ core.market_data")
    except ImportError as e:
        print(f"❌ core.market_data: {e}")
        return False
    
    try:
        from core.signals import SignalEngine
        print("✅ core.signals")
    except ImportError as e:
        print(f"❌ core.signals: {e}")
        return False
    
    try:
        from core.strategy import StrategyEngine
        print("✅ core.strategy")
    except ImportError as e:
        print(f"❌ core.strategy: {e}")
        return False
    
    try:
        from core.risk_manager import RiskManager
        print("✅ core.risk_manager")
    except ImportError as e:
        print(f"❌ core.risk_manager: {e}")
        return False
    
    try:
        from paper_trader import PaperTradingExecutor
        print("✅ paper_trader")
    except ImportError as e:
        print(f"❌ paper_trader: {e}")
        return False
    
    try:
        from utils.database import DatabaseManager
        print("✅ utils.database")
    except ImportError as e:
        print(f"❌ utils.database: {e}")
        return False
    
    try:
        from utils.logger import setup_logging
        print("✅ utils.logger")
    except ImportError as e:
        print(f"❌ utils.logger: {e}")
        return False
    
    return True


def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from utils.database import DatabaseManager
        
        # Test database creation
        db_path = 'data/test_trades.db'
        db = DatabaseManager(db_path)
        
        # Test basic operations
        test_signal = {
            'pair': 'BTC/USDT',
            'direction': 'long',
            'indicator': 'TEST',
            'strength': 0.8,
            'price': 50000.0,
            'timestamp': '2023-01-01T12:00:00',
            'was_traded': False
        }
        
        if db.log_signal(test_signal):
            print("✅ Database operations")
        else:
            print("❌ Database operations failed")
            return False
            
        # Clean up test database
        if os.path.exists(db_path):
            os.remove(db_path)
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 Crypto Scalper Bot - Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_dependencies,
        test_directories,
        test_configuration,
        test_environment,
        test_imports,
        test_database
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
            break
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The bot is ready to run.")
        print("Start with: python main.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the bot.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())