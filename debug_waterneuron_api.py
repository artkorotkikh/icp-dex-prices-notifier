#!/usr/bin/env python3
"""
Debug WaterNeuron API endpoints
Try to find API calls that the dashboard makes to get exchange rate data
"""

import asyncio
import aiohttp
import json
import re

async def test_waterneuron_apis():
    """Test various potential API endpoints for WaterNeuron data"""
    
    # Potential API endpoints based on common patterns
    base_urls = [
        "https://wtn.ic.app",
        "https://api.wtn.ic.app", 
        "https://backend.wtn.ic.app"
    ]
    
    endpoints = [
        "/api/nicp",
        "/api/exchange-rate",
        "/api/stats",
        "/api/data",
        "/nicp/stats",
        "/nicp/rate",
        "/stats",
        "/data"
    ]
    
    # Also try the canister endpoints that might be accessible
    canister_endpoints = [
        "https://tsbvt-pyaaa-aaaar-qafva-cai.raw.ic0.app/stats",
        "https://tsbvt-pyaaa-aaaar-qafva-cai.raw.ic0.app/exchange_rate", 
        "https://tsbvt-pyaaa-aaaar-qafva-cai.raw.ic0.app/get_exchange_rate",
        "https://tsbvt-pyaaa-aaaar-qafva-cai.raw.ic0.app/nicp_stats"
    ]
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    ) as session:
        
        print("🔍 Testing potential API endpoints...")
        
        # Test regular API endpoints
        for base_url in base_urls:
            for endpoint in endpoints:
                url = base_url + endpoint
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            content = await response.text()
                            
                            print(f"✅ {url} - Status: {response.status}")
                            print(f"   Content-Type: {content_type}")
                            print(f"   Content length: {len(content)}")
                            
                            # If it's JSON, try to parse it
                            if 'json' in content_type:
                                try:
                                    data = json.loads(content)
                                    print(f"   JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                                    
                                    # Look for exchange rate related fields
                                    if isinstance(data, dict):
                                        rate_fields = [k for k in data.keys() if 'rate' in k.lower() or 'exchange' in k.lower()]
                                        if rate_fields:
                                            print(f"   🎯 Rate fields found: {rate_fields}")
                                            for field in rate_fields:
                                                print(f"      {field}: {data[field]}")
                                except json.JSONDecodeError:
                                    pass
                            else:
                                # Show first 200 chars of text content
                                print(f"   Content preview: {content[:200]}...")
                            
                            print()
                        else:
                            print(f"❌ {url} - Status: {response.status}")
                            
                except Exception as e:
                    print(f"❌ {url} - Error: {str(e)[:50]}...")
        
        print("\n🔍 Testing canister endpoints...")
        
        # Test canister endpoints
        for url in canister_endpoints:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        content = await response.text()
                        
                        print(f"✅ {url} - Status: {response.status}")
                        print(f"   Content-Type: {content_type}")
                        print(f"   Content: {content[:300]}...")
                        print()
                    else:
                        print(f"❌ {url} - Status: {response.status}")
                        
            except Exception as e:
                print(f"❌ {url} - Error: {str(e)[:50]}...")
        
        print("\n🔍 Testing with different HTTP methods...")
        
        # Try POST requests to common endpoints
        post_endpoints = [
            "https://wtn.ic.app/api/query",
            "https://tsbvt-pyaaa-aaaar-qafva-cai.raw.ic0.app/query"
        ]
        
        for url in post_endpoints:
            try:
                # Try empty POST
                async with session.post(url, json={}) as response:
                    if response.status < 500:  # Any response that's not server error
                        content = await response.text()
                        print(f"✅ POST {url} - Status: {response.status}")
                        print(f"   Content: {content[:200]}...")
                        print()
                        
            except Exception as e:
                print(f"❌ POST {url} - Error: {str(e)[:50]}...")

async def analyze_page_network_calls():
    """Analyze the page source to find what network calls it might make"""
    
    print("\n🔍 Analyzing page source for network calls...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get("https://wtn.ic.app/?tab=nicp") as response:
            html_content = await response.text()
            
            # Look for URLs in the JavaScript
            url_patterns = [
                r'https?://[^\s\'"]+',
                r'[\'"`]/api/[^\s\'"]+',
                r'[\'"`]/[a-zA-Z]+/[^\s\'"]+',
                r'fetch\([\'"`]([^\'"`]+)[\'"`]\)',
                r'axios\.[get|post]+\([\'"`]([^\'"`]+)[\'"`]\)'
            ]
            
            found_urls = set()
            
            for pattern in url_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    if len(match) > 5 and not match.endswith('.js') and not match.endswith('.css'):
                        found_urls.add(match)
            
            print(f"Found potential API URLs:")
            for url in sorted(found_urls):
                print(f"  {url}")

if __name__ == "__main__":
    asyncio.run(test_waterneuron_apis())
    asyncio.run(analyze_page_network_calls()) 