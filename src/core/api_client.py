import requests
import logging
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ICP-Token-Monitor/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # API endpoints
        self.icpswap_url = "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers"
        self.kongswap_urls = {
            'overview': 'https://api.kongswap.io/v1/stats/overview',
            'tokens': 'https://api.kongswap.io/v1/tokens',
            'pairs': 'https://api.kongswap.io/v1/pairs'
        }
        
        # Cache to avoid too frequent requests
        self.cache = {}
        self.cache_duration = 30  # seconds
    
    def _make_request(self, url: str, timeout: int = 10) -> Optional[Dict]:
        """Make HTTP request with error handling and caching"""
        try:
            # Check cache first
            current_time = time.time()
            if url in self.cache:
                cache_time, data = self.cache[url]
                if current_time - cache_time < self.cache_duration:
                    return data
            
            logger.info(f"Fetching data from: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the response
            self.cache[url] = (current_time, data)
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout when fetching from {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error when fetching from {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} when fetching from {url}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error when fetching from {url}: {e}")
            return None
    
    def get_icpswap_data(self) -> Optional[List[Dict]]:
        """Fetch data from ICPSwap API"""
        data = self._make_request(self.icpswap_url)
        if data and isinstance(data, list):
            return data
        return None
    
    def get_kongswap_data(self) -> Optional[Dict]:
        """Fetch data from KongSwap API - trying multiple endpoints"""
        # Try different endpoints until we find one that works
        for endpoint_name, url in self.kongswap_urls.items():
            data = self._make_request(url)
            if data:
                logger.info(f"Successfully fetched data from KongSwap {endpoint_name} endpoint")
                return data
        
        logger.warning("No KongSwap endpoints responded successfully")
        return None
    
    def find_icp_pairs(self, data: List[Dict], target_pairs: List[str] = None) -> Dict[str, Dict]:
        """Find specific ICP pairs from the data"""
        if target_pairs is None:
            target_pairs = ['ICP/nICP', 'ICP/USD', 'ICP/USDT', 'ICP/USDC']
        
        found_pairs = {}
        
        if not data:
            return found_pairs
        
        for item in data:
            try:
                # ICPSwap format
                if 'ticker_name' in item and 'base_currency' in item and 'target_currency' in item:
                    base = item.get('base_currency', '').upper()
                    target = item.get('target_currency', '').upper()
                    
                    # Look for ICP pairs
                    pair_name = None
                    if base == 'ICP':
                        pair_name = f"ICP/{target}"
                    elif target == 'ICP':
                        pair_name = f"{base}/ICP"
                    
                    if pair_name and (pair_name in target_pairs or any(target in pair_name for target in ['NICP', 'USD', 'USDT', 'USDC'])):
                        found_pairs[pair_name] = {
                            'price': float(item.get('last_price', 0)),
                            'volume_24h': float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0)),
                            'base_volume': float(item.get('base_volume', 0)),
                            'target_volume': float(item.get('target_volume', 0)),
                            'source': 'icpswap',
                            'raw_data': json.dumps(item)
                        }
                        
            except (ValueError, TypeError) as e:
                logger.warning(f"Error processing item: {e}")
                continue
        
        return found_pairs
    
    def get_icp_prices(self) -> Dict[str, Dict]:
        """Get current ICP prices from all available sources"""
        all_pairs = {}
        
        # Get ICPSwap data
        icpswap_data = self.get_icpswap_data()
        if icpswap_data:
            icpswap_pairs = self.find_icp_pairs(icpswap_data)
            all_pairs.update(icpswap_pairs)
            logger.info(f"Found {len(icpswap_pairs)} ICP pairs from ICPSwap")
        
        # Try KongSwap data (if available)
        kongswap_data = self.get_kongswap_data()
        if kongswap_data:
            # Note: KongSwap API structure might be different
            # We'll need to adapt this based on actual API response
            logger.info("KongSwap data available but format needs to be analyzed")
        
        return all_pairs
    
    def get_pair_history(self, pair: str, timeframe: str = '24h') -> Optional[List[Dict]]:
        """Get historical data for a pair (placeholder for future implementation)"""
        # This would require more advanced API endpoints
        # For MVP, we'll rely on our stored historical data
        logger.info(f"Historical data request for {pair} ({timeframe}) - using local storage")
        return None
    
    def calculate_price_change(self, current_price: float, old_price: float) -> float:
        """Calculate price change percentage"""
        if old_price == 0:
            return 0
        return ((current_price - old_price) / old_price) * 100
    
    def format_price_data(self, pair_data: Dict) -> str:
        """Format price data for display"""
        try:
            price = pair_data.get('price', 0)
            volume_24h = pair_data.get('volume_24h', 0)
            source = pair_data.get('source', 'unknown')
            
            return f"💰 Price: ${price:.6f}\n📊 24h Volume: ${volume_24h:.2f}\n📡 Source: {source.upper()}"
        except Exception as e:
            logger.error(f"Error formatting price data: {e}")
            return "❌ Error formatting price data"
    
    def health_check(self) -> Dict[str, bool]:
        """Check if APIs are responding"""
        health_status = {}
        
        # Check ICPSwap
        icpswap_data = self._make_request(self.icpswap_url)
        health_status['icpswap'] = icpswap_data is not None
        
        # Check KongSwap
        kongswap_data = self.get_kongswap_data()
        health_status['kongswap'] = kongswap_data is not None
        
        return health_status 