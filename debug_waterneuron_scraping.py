#!/usr/bin/env python3
"""
Debug WaterNeuron Scraping
Test script to examine what content we can extract from the WaterNeuron dashboard
"""

import asyncio
import aiohttp
import re
from bs4 import BeautifulSoup
import json

async def debug_waterneuron_scraping():
    """Debug the WaterNeuron scraping process"""
    
    dashboard_url = "https://wtn.ic.app/?tab=nicp"
    
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=15),
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    ) as session:
        
        print("🔍 Fetching WaterNeuron dashboard...")
        async with session.get(dashboard_url) as response:
            print(f"Status: {response.status}")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            html_content = await response.text()
            print(f"Content length: {len(html_content)} characters")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get all text content
            text_content = soup.get_text()
            print(f"\n📄 Text content length: {len(text_content)} characters")
            
            # Show first 1000 characters of text
            print(f"\n📝 First 1000 characters of text content:")
            print("=" * 50)
            print(text_content[:1000])
            print("=" * 50)
            
            # Look for specific patterns we expect
            print(f"\n🔍 Searching for exchange rate patterns...")
            
            # Pattern 1: nICP/ICP = 0.9001
            pattern1 = r'nICP/ICP\s*[=:]\s*([\d.]+)'
            match1 = re.search(pattern1, text_content, re.IGNORECASE)
            if match1:
                print(f"✅ Found nICP/ICP pattern: {match1.group(1)}")
            else:
                print("❌ nICP/ICP pattern not found")
            
            # Pattern 2: ICP/nICP = 1.1110
            pattern2 = r'ICP/nICP\s*[=:]\s*([\d.]+)'
            match2 = re.search(pattern2, text_content, re.IGNORECASE)
            if match2:
                print(f"✅ Found ICP/nICP pattern: {match2.group(1)}")
            else:
                print("❌ ICP/nICP pattern not found")
            
            # Pattern 3: Exchange Rate:
            pattern3 = r'Exchange\s+Rate[:\s]+(.*?)(?:\n|$)'
            match3 = re.search(pattern3, text_content, re.IGNORECASE | re.DOTALL)
            if match3:
                print(f"✅ Found Exchange Rate section: {match3.group(1)[:100]}...")
            else:
                print("❌ Exchange Rate section not found")
            
            # Look for numbers that could be exchange rates
            print(f"\n🔢 Looking for potential exchange rate numbers...")
            number_patterns = [
                r'0\.9\d{3,4}',  # Like 0.9001
                r'1\.1\d{3,4}',  # Like 1.1110
                r'0\.8\d{3,4}',  # Alternative range
                r'1\.0\d{3,4}'   # Alternative range
            ]
            
            for i, pattern in enumerate(number_patterns, 1):
                matches = re.findall(pattern, text_content)
                if matches:
                    print(f"✅ Pattern {i} ({pattern}) found: {matches}")
                else:
                    print(f"❌ Pattern {i} ({pattern}) not found")
            
            # Check if this is a JavaScript-heavy page
            scripts = soup.find_all('script')
            print(f"\n🔧 Found {len(scripts)} script tags")
            
            # Look in script tags for data
            for i, script in enumerate(scripts[:5]):  # Check first 5 scripts
                if script.string and len(script.string) > 100:
                    print(f"\nScript {i+1} content (first 200 chars):")
                    print(script.string[:200] + "...")
                    
                    # Look for exchange rate in script
                    script_matches = re.findall(r'[\d.]+', script.string)
                    potential_rates = [float(m) for m in script_matches if re.match(r'^[01]\.\d{4}$', m)]
                    if potential_rates:
                        print(f"Potential exchange rates in script: {potential_rates}")
            
            # Check if the page loaded properly or if it's a SPA that needs JS
            if len(text_content.strip()) < 500:
                print(f"\n⚠️  WARNING: Very little text content. This might be a JavaScript-heavy SPA.")
                print("The page might require JavaScript execution to load the actual content.")
            
            # Look for common SPA indicators
            spa_indicators = ['React', 'Vue', 'Angular', 'app-root', 'root', 'Loading...']
            for indicator in spa_indicators:
                if indicator.lower() in html_content.lower():
                    print(f"🔍 Found SPA indicator: {indicator}")

if __name__ == "__main__":
    asyncio.run(debug_waterneuron_scraping()) 