#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.api_client import APIClient

def test_canister_mapping():
    """Test the updated canister mapping"""
    print("🧪 Testing updated canister mapping...")
    
    client = APIClient()
    
    # Get KongSwap data
    kongswap_data = client.fetch_kongswap_data()
    
    if not kongswap_data:
        print("❌ No KongSwap data retrieved")
        return
    
    print(f"✅ Retrieved {len(kongswap_data)} KongSwap pairs")
    
    # Sort by volume to see top pairs
    sorted_pairs = sorted(kongswap_data, key=lambda x: x.get('volume_24h', 0), reverse=True)
    
    print("\n📊 Top 10 KongSwap pairs (after canister mapping update):")
    print("-" * 70)
    
    for i, pair in enumerate(sorted_pairs[:10], 1):
        volume = pair.get('volume_24h', 0)
        liquidity = pair.get('liquidity', 0)
        pair_name = pair.get('pair', 'Unknown')
        price = pair.get('price', 0)
        
        # Check if this was previously unknown
        status = ""
        if "UNKNOWN_" in pair_name:
            status = " 🔍 STILL UNKNOWN"
        elif any(x in pair_name for x in ["n6tkf", "7pail", "ysy5f", "lrtnw"]):
            status = " ✅ FIXED"
        
        print(f"{i:2}. {pair_name:<25} ${price:.8f}")
        print(f"    📊 Vol: ${volume:,.0f} | 💧 Liq: ${liquidity:,.0f}{status}")
    
    # Count unknown vs known pairs
    unknown_pairs = [p for p in kongswap_data if "UNKNOWN_" in p.get('pair', '')]
    known_pairs = [p for p in kongswap_data if "UNKNOWN_" not in p.get('pair', '')]
    
    print(f"\n📈 Summary:")
    print(f"   ✅ Known pairs: {len(known_pairs)}")
    print(f"   🔍 Unknown pairs: {len(unknown_pairs)}")
    print(f"   📊 Total pairs: {len(kongswap_data)}")
    
    if unknown_pairs:
        print(f"\n🔍 Remaining unknown pairs:")
        for pair in unknown_pairs:
            print(f"   • {pair.get('pair')}: ${pair.get('volume_24h', 0):,.0f} volume")

if __name__ == "__main__":
    test_canister_mapping() 