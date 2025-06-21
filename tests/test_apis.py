#!/usr/bin/env python3
"""
Test script to verify API connectivity and basic functionality
Run this before starting the main bot to ensure everything works
"""

import requests
import json
import sys
import os
from typing import Dict, List

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_icpswap_api():
    """Test ICPSwap API connectivity"""
    print("🔍 Testing ICPSwap API...")
    
    try:
        url = "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ ICPSwap API working - Found {len(data)} trading pairs")
            
            # Look for specific ICP pairs we want to monitor
            target_currencies = ['NICP', 'USD', 'USDT', 'USDC']
            relevant_pairs = []
            
            for item in data:
                if 'base_currency' in item and 'target_currency' in item:
                    base = item.get('base_currency', '').upper()
                    target = item.get('target_currency', '').upper()
                    
                    # Check for our target pairs
                    if base == 'ICP' and target in target_currencies:
                        pair_name = f"{base}/{target}"
                        price = float(item.get('last_price', 0))
                        volume = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                        relevant_pairs.append((pair_name, price, volume))
                    elif target == 'ICP' and base in target_currencies:
                        pair_name = f"{base}/ICP"
                        price = float(item.get('last_price', 0))
                        volume = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                        relevant_pairs.append((pair_name, price, volume))
            
            if relevant_pairs:
                print(f"📊 Found {len(relevant_pairs)} relevant ICP pairs:")
                for pair, price, volume in relevant_pairs:
                    print(f"   • {pair}: ${price:.6f} (24h vol: ${volume:.2f})")
            else:
                print("⚠️ No relevant ICP pairs found (nICP, USD, USDT, USDC)")
            
            return True
        else:
            print("❌ ICPSwap API returned empty or invalid data")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ICPSwap API connection failed: {e}")
        return False
    except json.JSONDecodeError:
        print("❌ ICPSwap API returned invalid JSON")
        return False
    except Exception as e:
        print(f"❌ ICPSwap API test failed: {e}")
        return False

def test_kongswap_api():
    """Test KongSwap API connectivity (optional for MVP)"""
    print("\n🔍 Testing KongSwap API (Optional)...")
    
    endpoints = [
        "https://api.kongswap.io/v1/stats/overview",
        "https://api.kongswap.io/v1/tokens",
        "https://api.kongswap.io/v1/pairs"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"   Testing: {endpoint}")
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} - Status: 200, Data type: {type(data)}")
                return True
            else:
                print(f"   ⚠️ {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {endpoint} - Connection failed: {e}")
        except json.JSONDecodeError:
            print(f"   ❌ {endpoint} - Invalid JSON response")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    print("ℹ️ KongSwap API not available - MVP will use ICPSwap only")
    return True  # Return True for MVP since KongSwap is optional

def test_database():
    """Test database creation and basic operations"""
    print("\n🔍 Testing Database...")
    
    try:
        # Import our database module
        from src.core import Database
        
        # Create test database
        db = Database("./test_db.db")
        
        # Test adding a user
        user_id = db.add_user(
            telegram_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        if user_id:
            print("✅ Database test passed - User creation successful")
            
            # Test adding price data
            success = db.add_price_data(
                pair="ICP/TEST",
                price=1.234,
                volume_24h=1000.0,
                source="test"
            )
            
            if success:
                print("✅ Database test passed - Price data storage successful")
                
                # Clean up test database
                import os
                os.remove("./test_db.db")
                
                return True
            else:
                print("❌ Database test failed - Price data storage failed")
                return False
        else:
            print("❌ Database test failed - User creation failed")
            return False
            
    except ImportError as e:
        print(f"❌ Database module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_telegram_imports():
    """Test if Telegram bot dependencies are available"""
    print("\n🔍 Testing Telegram Bot Dependencies...")
    
    try:
        import telegram
        from telegram.ext import Application
        print("✅ Telegram bot libraries imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Telegram bot import failed: {e}")
        print("💡 Try: pip install python-telegram-bot")
        return False

def test_all_imports():
    """Test all required imports"""
    print("\n🔍 Testing Python Dependencies...")
    
    required_modules = [
        'requests',
        'schedule',
        'dotenv',
        'aiohttp',
        'sqlite3',
        'asyncio',
        'logging',
        'json',
        'threading'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            if module == 'dotenv':
                import dotenv
            else:
                __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Try: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies available")
        return True

def main():
    """Run all tests"""
    print("🧪 ICP Token Monitor - API and System Tests")
    print("=" * 50)
    
    tests = [
        ("Python Dependencies", test_all_imports),
        ("ICPSwap API", test_icpswap_api),
        ("KongSwap API", test_kongswap_api),
        ("Database Operations", test_database),
        ("Telegram Dependencies", test_telegram_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to run the bot.")
        print("💡 Next steps:")
        print("   1. Configure config.env with your Telegram bot token")
        print("   2. Run: python main.py")
        return True
    else:
        print("⚠️ Some tests failed. Please fix the issues before running the bot.")
        print("💡 Common fixes:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Check internet connection")
        print("   • Verify Python version (3.8+ required)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 