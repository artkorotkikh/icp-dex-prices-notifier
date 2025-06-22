#!/usr/bin/env python3
"""
Test WaterNeuron API Client
Test the updated WaterNeuron client that uses the API endpoint
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.waterneuron_client import WaterNeuronClient

async def test_waterneuron_client():
    """Test the WaterNeuron client"""
    
    print("🧪 Testing WaterNeuron Client")
    print("=" * 50)
    
    client = WaterNeuronClient()
    
    # Test the exchange rate fetch
    print("1. Testing exchange rate fetch...")
    result = await client.get_exchange_rate()
    
    print(f"Success: {result['success']}")
    print(f"Source: {result.get('source', 'unknown')}")
    
    if result['success']:
        print(f"nICP/ICP rate: {result['nicp_to_icp_rate']:.4f}")
        print(f"ICP/nICP rate: {result['icp_to_nicp_rate']:.4f}")
        
        if 'total_supply' in result:
            print(f"Total nICP supply: {result['total_supply']:,.2f}")
        
        if 'icpswap_pool' in result:
            pool = result['icpswap_pool']
            print(f"ICPSwap pool - ICP: {pool['icp_balance']:,.2f}, nICP: {pool['nicp_balance']:,.2f}")
            print(f"Pool ratio: {pool['pool_ratio']:.4f}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    
    print()
    print("2. Testing cache (second call should be faster)...")
    result2 = await client.get_exchange_rate()
    print(f"Second call success: {result2['success']}")
    print(f"Source: {result2.get('source', 'unknown')}")
    
    print()
    print("3. Testing sync wrapper...")
    result3 = client.get_exchange_rate_sync()
    print(f"Sync call success: {result3['success']}")
    print(f"Source: {result3.get('source', 'unknown')}")
    
    print()
    print("✅ WaterNeuron client test completed!")

if __name__ == "__main__":
    asyncio.run(test_waterneuron_client()) 