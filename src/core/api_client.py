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
            'User-Agent': 'nICP-Discount-Tracker/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # API endpoints
        self.icpswap_url = "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers"
        self.kongswap_base_url = "https://api.kongswap.io"
        
        # nICP arbitrage constants
        self.DIRECT_STAKING_RATE = 0.9001103  # 1 ICP = 0.9001103 nICP (13.4% APY)
        self.DISSOLUTION_MONTHS = 6
        self.ANNUAL_STAKING_APY = 0.134  # 13.4%
        
        # Key canister IDs for nICP arbitrage
        self.ICP_CANISTER = 'ryjl3-tyaaa-aaaaa-aaaba-cai'
        self.NICP_CANISTER = 'buwm7-7yaaa-aaaar-qagva-cai'
        self.CKUSDT_CANISTER = 'cngnf-vqaaa-aaaar-qag4q-cai'
        self.CKUSDC_CANISTER = 'xevnm-gaaaa-aaaar-qafnq-cai'
        
        # Cache to avoid too frequent requests
        self.cache = {}
        self.cache_duration = 30  # seconds

    def calculate_arbitrage_opportunity(self, nicp_price_in_icp: float) -> Dict:
        """Calculate the arbitrage opportunity for nICP"""
        if nicp_price_in_icp <= 0:
            return {
                'viable': False,
                'error': 'Invalid nICP price'
            }
        
        # Calculate potential returns
        cost_per_nicp = nicp_price_in_icp  # Cost in ICP to buy 1 nICP
        future_icp_per_nicp = 1.0 / self.DIRECT_STAKING_RATE  # ICP received after unstaking 1 nICP
        
        # Profit calculation
        profit_per_nicp = future_icp_per_nicp - cost_per_nicp
        profit_percentage = (profit_per_nicp / cost_per_nicp) * 100
        annualized_return = profit_percentage * (12 / self.DISSOLUTION_MONTHS)
        
        # Determine if viable (profitable)
        is_viable = profit_percentage > 5.0  # Minimum 5% return to be worth it
        
        return {
            'viable': is_viable,
            'cost_per_nicp_icp': cost_per_nicp,
            'future_icp_per_nicp': future_icp_per_nicp,
            'profit_per_nicp_icp': profit_per_nicp,
            'profit_percentage_6m': profit_percentage,
            'annualized_return': annualized_return,
            'dissolution_months': self.DISSOLUTION_MONTHS,
            'direct_staking_rate': self.DIRECT_STAKING_RATE,
            'recommendation': self._get_arbitrage_recommendation(profit_percentage)
        }
    
    def _get_arbitrage_recommendation(self, profit_percentage: float) -> str:
        """Get recommendation based on profit percentage"""
        if profit_percentage >= 20:
            return "🚀 EXCELLENT - Very high arbitrage opportunity!"
        elif profit_percentage >= 15:
            return "🔥 GREAT - Strong arbitrage opportunity!"
        elif profit_percentage >= 10:
            return "✅ GOOD - Solid arbitrage opportunity"
        elif profit_percentage >= 5:
            return "💡 MODERATE - Decent arbitrage opportunity"
        else:
            return "❌ POOR - Not recommended"

    def get_nicp_arbitrage_data(self) -> Dict:
        """Get nICP arbitrage data from all available DEXes"""
        cache_key = "nicp_arbitrage"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_duration:
                return cached_data
        
        logger.info("🔍 Fetching nICP arbitrage data from DEXes...")
        
        arbitrage_data = {
            'timestamp': datetime.now().isoformat(),
            'opportunities': [],
            'best_opportunity': None,
            'summary': {
                'total_dexes': 0,
                'viable_opportunities': 0,
                'best_profit_6m': 0,
                'best_annualized_return': 0
            }
        }
        
        # Check ICPSwap
        icpswap_data = self._get_nicp_from_icpswap()
        if icpswap_data:
            arbitrage_data['opportunities'].append(icpswap_data)
            arbitrage_data['summary']['total_dexes'] += 1
        
        # Check KongSwap
        kongswap_data = self._get_nicp_from_kongswap()
        if kongswap_data:
            arbitrage_data['opportunities'].append(kongswap_data)
            arbitrage_data['summary']['total_dexes'] += 1
        
        # Find best opportunity
        viable_opportunities = [opp for opp in arbitrage_data['opportunities'] if opp.get('arbitrage', {}).get('viable', False)]
        arbitrage_data['summary']['viable_opportunities'] = len(viable_opportunities)
        
        if viable_opportunities:
            best_opp = max(viable_opportunities, key=lambda x: x['arbitrage']['profit_percentage_6m'])
            arbitrage_data['best_opportunity'] = best_opp
            arbitrage_data['summary']['best_profit_6m'] = best_opp['arbitrage']['profit_percentage_6m']
            arbitrage_data['summary']['best_annualized_return'] = best_opp['arbitrage']['annualized_return']
        
        # Cache the result
        self.cache[cache_key] = (arbitrage_data, current_time)
        
        return arbitrage_data

    def _get_nicp_from_icpswap(self) -> Optional[Dict]:
        """Get nICP data from ICPSwap"""
        try:
            response = self.session.get(self.icpswap_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Look for nICP/ICP pairs
            for item in data:
                base_currency = item.get('base_currency', '')
                target_currency = item.get('target_currency', '')
                
                # Check for nICP/ICP pair in either direction
                if ((base_currency == self.NICP_CANISTER and target_currency == self.ICP_CANISTER) or
                    (base_currency == self.ICP_CANISTER and target_currency == self.NICP_CANISTER)):
                    
                    last_price = float(item.get('last_price', 0))
                    if last_price <= 0:
                        continue
                    
                    # Determine nICP price in ICP terms
                    if base_currency == self.NICP_CANISTER:
                        # nICP/ICP pair - price is ICP per nICP
                        nicp_price_in_icp = last_price
                        pair_name = "nICP/ICP"
                    else:
                        # ICP/nICP pair - price is nICP per ICP, so invert
                        nicp_price_in_icp = 1.0 / last_price
                        pair_name = "ICP/nICP"
                    
                    # Calculate arbitrage
                    arbitrage = self.calculate_arbitrage_opportunity(nicp_price_in_icp)
                    
                    # Get volume data
                    volume_24h_tokens = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                    volume_24h_usd = float(item.get('volume_usd_24H', 0))
                    liquidity_usd = float(item.get('liquidity_in_usd', 0))
                    
                    return {
                        'dex': 'ICPSwap',
                        'pair': pair_name,
                        'nicp_price_in_icp': nicp_price_in_icp,
                        'last_price': last_price,
                        'volume_24h_tokens': volume_24h_tokens,
                        'volume_24h_usd': volume_24h_usd,
                        'liquidity_usd': liquidity_usd,
                        'arbitrage': arbitrage,
                        'raw_data': item
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching nICP data from ICPSwap: {e}")
        
        return None

    def _get_nicp_from_kongswap(self) -> Optional[Dict]:
        """Get nICP data from KongSwap"""
        try:
            ticker_url = f"{self.kongswap_base_url}/api/coingecko/tickers"
            response = self.session.get(ticker_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Look for nICP/ICP pairs
            for ticker in data:
                base_id = ticker.get('base_currency', '') or ticker.get('base_id', '')
                target_id = ticker.get('target_currency', '') or ticker.get('target_id', '')
                
                # Check for nICP/ICP pair in either direction
                if ((base_id == self.NICP_CANISTER and target_id == self.ICP_CANISTER) or
                    (base_id == self.ICP_CANISTER and target_id == self.NICP_CANISTER)):
                    
                    last_price = float(ticker.get('last_price', 0))
                    if last_price <= 0:
                        continue
                    
                    # Determine nICP price in ICP terms
                    if base_id == self.NICP_CANISTER:
                        # nICP/ICP pair - price is ICP per nICP
                        nicp_price_in_icp = last_price
                        pair_name = "nICP/ICP"
                    else:
                        # ICP/nICP pair - price is nICP per ICP, so invert
                        nicp_price_in_icp = 1.0 / last_price
                        pair_name = "ICP/nICP"
                    
                    # Calculate arbitrage
                    arbitrage = self.calculate_arbitrage_opportunity(nicp_price_in_icp)
                    
                    # Get volume data
                    base_volume = float(ticker.get('base_volume', 0))
                    target_volume = float(ticker.get('target_volume', 0))
                    
                    # Estimate USD volume (using approximate ICP price of $4.80)
                    icp_price_usd = 4.80
                    if target_id == self.ICP_CANISTER:
                        volume_24h_usd = target_volume * icp_price_usd
                    else:
                        volume_24h_usd = base_volume * icp_price_usd
                    
                    return {
                        'dex': 'KongSwap',
                        'pair': pair_name,
                        'nicp_price_in_icp': nicp_price_in_icp,
                        'last_price': last_price,
                        'base_volume': base_volume,
                        'target_volume': target_volume,
                        'volume_24h_usd': volume_24h_usd,
                        'arbitrage': arbitrage,
                        'raw_data': ticker
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching nICP data from KongSwap: {e}")
        
        return None

    def get_icp_price_usd(self) -> float:
        """Get current ICP price in USD for reference"""
        try:
            # Use CoinGecko API for reliable ICP price
            url = "https://api.coingecko.com/api/v3/simple/price?ids=internet-computer&vs_currencies=usd"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return float(data.get('internet-computer', {}).get('usd', 4.80))
        except Exception as e:
            logger.warning(f"Could not fetch ICP price from CoinGecko: {e}")
            return 4.80  # Fallback price

    # Legacy method for backward compatibility
    def get_price_data(self) -> Dict[str, Dict]:
        """Get price data - now focused on nICP arbitrage"""
        arbitrage_data = self.get_nicp_arbitrage_data()
        
        # Convert to legacy format for compatibility
        price_data = {}
        
        for opportunity in arbitrage_data.get('opportunities', []):
            dex = opportunity['dex']
            pair = opportunity['pair']
            key = f"{pair}_{dex}"
            
            price_data[key] = {
                'price': opportunity['nicp_price_in_icp'],
                'volume_24h_usd': opportunity.get('volume_24h_usd', 0),
                'source': dex.lower(),
                'arbitrage_profit_6m': opportunity['arbitrage']['profit_percentage_6m'],
                'arbitrage_viable': opportunity['arbitrage']['viable'],
                'raw_data': json.dumps(opportunity)
            }
        
        return price_data

    def check_health(self) -> Dict[str, bool]:
        """Check health of DEX APIs"""
        health = {}
        
        # Check ICPSwap
        try:
            response = self.session.get(self.icpswap_url, timeout=5)
            health['ICPSwap'] = response.status_code == 200
        except:
            health['ICPSwap'] = False
        
        # Check KongSwap
        try:
            response = self.session.get(self.kongswap_base_url, timeout=5)
            health['KongSwap'] = response.status_code == 200
        except:
            health['KongSwap'] = False
        
        return health