#!/usr/bin/env python3
"""
Quick test - Just show live ICP price data
"""

import requests
import json
import sys
import os
from datetime import datetime

# Add project root to Python path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_icp_prices():
    """Get current ICP prices from ICPSwap"""
    print("🌐 Fetching live ICP prices from ICPSwap...")
    
    try:
        url = "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched {len(data)} trading pairs")
        
        # Look for ICP pairs
        target_currencies = ['NICP', 'USD', 'USDT', 'USDC', 'CKUSDT', 'CKUSDC']
        icp_pairs = []
        
        for item in data:
            base = item.get('base_currency', '').upper()
            target = item.get('target_currency', '').upper()
            
            # Check for relevant ICP pairs
            if base == 'ICP' and target in target_currencies:
                pair_name = f"{base}/{target}"
                price = float(item.get('last_price', 0))
                volume = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                icp_pairs.append((pair_name, price, volume))
            elif target == 'ICP' and base in target_currencies:
                pair_name = f"{base}/ICP"
                price = float(item.get('last_price', 0))
                volume = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                icp_pairs.append((pair_name, price, volume))
        
        return icp_pairs
        
    except Exception as e:
        print(f"❌ Error fetching prices: {e}")
        return []

def main():
    print("🚀 ICP Token Monitor - Quick Price Check")
    print("=" * 50)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get prices
    pairs = get_icp_prices()
    
    if pairs:
        print(f"💰 Found {len(pairs)} relevant ICP pairs:")
        print()
        
        # Sort by volume (highest first)
        pairs.sort(key=lambda x: x[2], reverse=True)
        
        for pair, price, volume in pairs:
            volume_str = f"${volume:,.2f}" if volume > 0 else "No volume"
            print(f"   📊 {pair:<12} ${price:>12.6f}   📈 24h Vol: {volume_str}")
        
        print()
        print("🎯 Key Pairs for Monitoring:")
        
        # Highlight important pairs
        important_pairs = ['NICP/ICP', 'ICP/NICP', 'USDT/ICP', 'ICP/USDT', 'USDC/ICP', 'ICP/USDC']
        
        for pair, price, volume in pairs:
            if pair in important_pairs:
                status = "🔥 High Volume" if volume > 1000 else "✅ Available"
                print(f"   • {pair}: ${price:.6f} - {status}")
        
        print()
        print("📱 This data would be sent to Telegram users!")
        print("⚡ Alerts would trigger based on price changes")
        print("🤖 Bot would respond to user commands")
        
    else:
        print("❌ No ICP pairs found")
    
    print()
    print("💡 Ready to deploy to Raspberry Pi!")

if __name__ == "__main__":
    main() 