"""
WaterNeuron Dashboard Scraper

This module provides functionality to scrape nICP exchange rate data
from the WaterNeuron dashboard web page since direct canister access
is complex and requires specialized IC libraries.
"""

import asyncio
import logging
import aiohttp
import re
from typing import Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WaterNeuronScraper:
    """Scraper for WaterNeuron dashboard data"""
    
    def __init__(self):
        self.dashboard_url = "https://wtn.ic.app/?tab=nicp"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_exchange_rate(self) -> Optional[Dict[str, Any]]:
        """
        Scrape exchange rate from WaterNeuron dashboard
        Returns dict with exchange rate info or None if failed
        """
        try:
            logger.info("Scraping WaterNeuron dashboard for exchange rate...")
            
            # Fetch the dashboard page
            async with self.session.get(self.dashboard_url) as response:
                if response.status != 200:
                    logger.warning(f"Dashboard returned status {response.status}")
                    return None
                
                html_content = await response.text()
                
            # Parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for exchange rate information in various ways
            exchange_rate = None
            method_used = None
            
            # Method 1: Look for text patterns containing exchange rates
            text_content = soup.get_text()
            
            # Pattern 1: "1 ICP = X nICP" or similar
            icp_to_nicp_pattern = r'1\s*ICP\s*[=:]\s*([\d.]+)\s*nICP'
            match = re.search(icp_to_nicp_pattern, text_content, re.IGNORECASE)
            if match:
                exchange_rate = float(match.group(1))
                method_used = "ICP to nICP pattern"
            
            # Pattern 2: "X nICP per ICP" or similar
            if not exchange_rate:
                nicp_per_icp_pattern = r'([\d.]+)\s*nICP\s*per\s*ICP'
                match = re.search(nicp_per_icp_pattern, text_content, re.IGNORECASE)
                if match:
                    exchange_rate = float(match.group(1))
                    method_used = "nICP per ICP pattern"
            
            # Pattern 3: Look for exchange rate in data attributes or JSON
            if not exchange_rate:
                # Look for JSON data in script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for exchange rate in JSON data
                        json_pattern = r'"exchange_rate":\s*([\d.]+)'
                        match = re.search(json_pattern, script.string)
                        if match:
                            exchange_rate = float(match.group(1))
                            method_used = "JSON script data"
                            break
                        
                        # Alternative JSON patterns
                        alt_patterns = [
                            r'"rate":\s*([\d.]+)',
                            r'"icp_to_nicp":\s*([\d.]+)',
                            r'"conversion_rate":\s*([\d.]+)'
                        ]
                        
                        for pattern in alt_patterns:
                            match = re.search(pattern, script.string)
                            if match:
                                exchange_rate = float(match.group(1))
                                method_used = f"JSON alternative pattern: {pattern}"
                                break
                        
                        if exchange_rate:
                            break
            
            # Method 2: Look for specific HTML elements that might contain the rate
            if not exchange_rate:
                # Common selectors for exchange rate displays
                selectors = [
                    '[data-testid*="exchange"]',
                    '[data-testid*="rate"]',
                    '.exchange-rate',
                    '.conversion-rate',
                    '.rate-display',
                    '[class*="rate"]',
                    '[id*="rate"]'
                ]
                
                for selector in selectors:
                    elements = soup.select(selector)
                    for element in elements:
                        text = element.get_text().strip()
                        # Look for numbers in the text
                        number_match = re.search(r'([\d.]+)', text)
                        if number_match:
                            potential_rate = float(number_match.group(1))
                            # Sanity check: exchange rate should be between 0.8 and 1.0
                            if 0.8 <= potential_rate <= 1.0:
                                exchange_rate = potential_rate
                                method_used = f"HTML selector: {selector}"
                                break
                    if exchange_rate:
                        break
            
            if exchange_rate:
                logger.info(f"Successfully scraped exchange rate: {exchange_rate} (method: {method_used})")
                return {
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'exchange_rate': exchange_rate,
                    'method': method_used,
                    'source': 'WaterNeuron Dashboard Scraping'
                }
            else:
                logger.warning("Could not find exchange rate in dashboard content")
                return {
                    'success': False,
                    'timestamp': datetime.now().isoformat(),
                    'error': 'Exchange rate not found in dashboard content',
                    'source': 'WaterNeuron Dashboard Scraping'
                }
                
        except Exception as e:
            logger.error(f"Error scraping WaterNeuron dashboard: {e}")
            return {
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'source': 'WaterNeuron Dashboard Scraping'
            }

    async def get_page_info(self) -> Dict[str, Any]:
        """Get general information about the dashboard page for debugging"""
        try:
            async with self.session.get(self.dashboard_url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                return {
                    'title': soup.title.string if soup.title else 'No title',
                    'status_code': response.status,
                    'content_length': len(html_content),
                    'has_scripts': len(soup.find_all('script')) > 0,
                    'text_sample': soup.get_text()[:500] + '...' if len(soup.get_text()) > 500 else soup.get_text()
                }
        except Exception as e:
            return {'error': str(e)}

async def get_waterneuron_exchange_rate_scraper() -> Optional[Dict[str, Any]]:
    """
    Convenience function to scrape WaterNeuron exchange rate
    Returns the exchange rate data or None if unavailable
    """
    try:
        async with WaterNeuronScraper() as scraper:
            return await scraper.scrape_exchange_rate()
    except Exception as e:
        logger.error(f"Error in get_waterneuron_exchange_rate_scraper: {e}")
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'source': 'WaterNeuron Dashboard Scraping'
        }

# Combined function that tries both canister and scraping methods
async def get_waterneuron_exchange_rate_combined() -> Optional[Dict[str, Any]]:
    """
    Try to get exchange rate using multiple methods:
    1. Direct canister query (from waterneuron_client.py)
    2. Dashboard scraping (this module)
    3. Fallback to known rate
    """
    try:
        # First try the canister method
        from .waterneuron_client import get_waterneuron_exchange_rate
        canister_result = await get_waterneuron_exchange_rate()
        
        if (canister_result and 
            canister_result.get('success') and 
            canister_result.get('exchange_rate')):
            logger.info("Using exchange rate from canister query")
            return canister_result
        
        # If canister method fails, try scraping
        logger.info("Canister method failed, trying dashboard scraping...")
        scraper_result = await get_waterneuron_exchange_rate_scraper()
        
        if (scraper_result and 
            scraper_result.get('success') and 
            scraper_result.get('exchange_rate')):
            logger.info("Using exchange rate from dashboard scraping")
            return scraper_result
        
        # If both fail, return failure with both error messages
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': 'Both canister query and dashboard scraping failed',
            'canister_error': canister_result.get('error') if canister_result else 'No result',
            'scraper_error': scraper_result.get('error') if scraper_result else 'No result',
            'source': 'Combined Method (Canister + Scraping)'
        }
        
    except Exception as e:
        logger.error(f"Error in combined exchange rate fetch: {e}")
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'source': 'Combined Method (Canister + Scraping)'
        } 