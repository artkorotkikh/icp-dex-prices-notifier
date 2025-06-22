import requests
import logging
import json
import time
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .waterneuron_client import WaterNeuronClient

logger = logging.getLogger(__name__)

class NICPArbitrageClient:
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
        
        # Initialize WaterNeuron client
        self.waterneuron_client = WaterNeuronClient()
        
        # nICP arbitrage constants (will be updated from WaterNeuron)
        self.DIRECT_STAKING_RATE = 0.9001  # Default: 1 ICP = 0.9001 nICP (from WaterNeuron)
        self.DISSOLUTION_MONTHS = 6
        self.ANNUAL_STAKING_APY = 0.134  # 13.4%
        
        # Key canister IDs for nICP arbitrage
        self.ICP_CANISTER = 'ryjl3-tyaaa-aaaaa-aaaba-cai'
        self.NICP_CANISTER = 'buwm7-7yaaa-aaaar-qagva-cai'
        
        # Cache to avoid too frequent requests
        self.cache = {}
        self.cache_duration = 30  # seconds
        
        # WaterNeuron data cache
        self.waterneuron_cache = {}
        self.waterneuron_cache_duration = 120  # 2 minutes for WaterNeuron data

    async def get_waterneuron_exchange_rate(self) -> Optional[Dict]:
        """Get current exchange rate from WaterNeuron protocol using the new API client"""
        try:
            logger.info("🌊 Fetching live exchange rate from WaterNeuron...")
            waterneuron_data = await self.waterneuron_client.get_exchange_rate()
            
            if waterneuron_data and waterneuron_data.get('success'):
                # Update our direct staking rate if we got valid data
                if waterneuron_data.get('nicp_to_icp_rate'):
                    self.DIRECT_STAKING_RATE = float(waterneuron_data['nicp_to_icp_rate'])
                    logger.info(f"✅ Updated direct staking rate from WaterNeuron: {self.DIRECT_STAKING_RATE}")
                
                return waterneuron_data
            else:
                logger.warning("❌ Failed to get valid data from WaterNeuron")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching WaterNeuron exchange rate: {e}")
            return None

    def calculate_arbitrage_opportunity(self, nicp_price_in_icp: float, waterneuron_data: Optional[Dict] = None) -> Dict:
        """Calculate the arbitrage opportunity for nICP"""
        if nicp_price_in_icp <= 0:
            return {
                'viable': False,
                'error': 'Invalid nICP price'
            }
        
        # Use current exchange rate from WaterNeuron if available
        current_staking_rate = self.DIRECT_STAKING_RATE
        if waterneuron_data and waterneuron_data.get('success') and waterneuron_data.get('nicp_to_icp_rate'):
            current_staking_rate = float(waterneuron_data['nicp_to_icp_rate'])
        
        # Calculate potential returns
        cost_per_nicp = nicp_price_in_icp  # Cost in ICP to buy 1 nICP
        future_icp_per_nicp = 1.0 / current_staking_rate  # ICP received after unstaking 1 nICP
        
        # Profit calculation
        profit_per_nicp = future_icp_per_nicp - cost_per_nicp
        profit_percentage = (profit_per_nicp / cost_per_nicp) * 100
        
        # Calculate proper APY using compound interest formula
        # APY = (1 + r)^(12/months) - 1, where r is the period return rate
        period_return_rate = profit_percentage / 100  # Convert percentage to decimal
        periods_per_year = 12 / self.DISSOLUTION_MONTHS  # How many 6-month periods in a year
        annualized_return = ((1 + period_return_rate) ** periods_per_year - 1) * 100
        
        # Determine if viable (profitable)
        is_viable = profit_percentage > 5.0  # Minimum 5% return to be worth it
        
        result = {
            'viable': is_viable,
            'cost_per_nicp_icp': cost_per_nicp,
            'future_icp_per_nicp': future_icp_per_nicp,
            'profit_per_nicp_icp': profit_per_nicp,
            'profit_percentage_6m': profit_percentage,
            'annualized_return': annualized_return,
            'dissolution_months': self.DISSOLUTION_MONTHS,
            'direct_staking_rate': current_staking_rate,
            'recommendation': self._get_arbitrage_recommendation(profit_percentage)
        }
        
        # Add WaterNeuron data source info
        if waterneuron_data and waterneuron_data.get('success'):
            result['waterneuron_source'] = True
            result['waterneuron_timestamp'] = waterneuron_data.get('timestamp')
            result['waterneuron_data_source'] = waterneuron_data.get('source', 'unknown')
        else:
            result['waterneuron_source'] = False
            result['note'] = 'Using fallback exchange rate - WaterNeuron data unavailable'
        
        return result
    
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

    async def get_nicp_arbitrage_data(self) -> Dict:
        """Get nICP arbitrage data from all available DEXes with WaterNeuron integration"""
        cache_key = "nicp_arbitrage"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_duration:
                return cached_data
        
        logger.info("🔍 Fetching nICP arbitrage data from DEXes...")
        
        # First, get current exchange rate from WaterNeuron
        waterneuron_data = await self.get_waterneuron_exchange_rate()
        
        arbitrage_data = {
            'timestamp': datetime.now().isoformat(),
            'waterneuron_data': waterneuron_data,
            'current_direct_staking_rate': self.DIRECT_STAKING_RATE,
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
        icpswap_data = await self._get_nicp_from_icpswap(waterneuron_data)
        if icpswap_data:
            arbitrage_data['opportunities'].append(icpswap_data)
            arbitrage_data['summary']['total_dexes'] += 1
        
        # Check KongSwap
        kongswap_data = await self._get_nicp_from_kongswap(waterneuron_data)
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

    def get_nicp_arbitrage_data_sync(self) -> Dict:
        """Synchronous wrapper for get_nicp_arbitrage_data"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.get_nicp_arbitrage_data())
                    return future.result()
            else:
                return loop.run_until_complete(self.get_nicp_arbitrage_data())
        except Exception as e:
            logger.error(f"Error in sync wrapper: {e}")
            # Fallback to old synchronous method
            return self._get_nicp_arbitrage_data_fallback()

    def _get_nicp_arbitrage_data_fallback(self) -> Dict:
        """Fallback method without WaterNeuron integration"""
        logger.warning("Using fallback arbitrage data method")
        cache_key = "nicp_arbitrage"
        current_time = time.time()
        
        arbitrage_data = {
            'timestamp': datetime.now().isoformat(),
            'waterneuron_data': None,
            'current_direct_staking_rate': self.DIRECT_STAKING_RATE,
            'opportunities': [],
            'best_opportunity': None,
            'summary': {
                'total_dexes': 0,
                'viable_opportunities': 0,
                'best_profit_6m': 0,
                'best_annualized_return': 0
            },
            'note': 'Fallback mode - WaterNeuron integration unavailable'
        }
        
        # Check ICPSwap without WaterNeuron data
        icpswap_data = self._get_nicp_from_icpswap_sync(None)
        if icpswap_data:
            arbitrage_data['opportunities'].append(icpswap_data)
            arbitrage_data['summary']['total_dexes'] += 1
        
        # Check KongSwap without WaterNeuron data
        kongswap_data = self._get_nicp_from_kongswap_sync(None)
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
        
        return arbitrage_data

    async def _get_nicp_from_icpswap(self, waterneuron_data: Optional[Dict] = None) -> Optional[Dict]:
        """Get nICP data from ICPSwap (async version)"""
        return self._get_nicp_from_icpswap_sync(waterneuron_data)

    async def _get_nicp_from_kongswap(self, waterneuron_data: Optional[Dict] = None) -> Optional[Dict]:
        """Get nICP data from KongSwap (async version)"""
        return self._get_nicp_from_kongswap_sync(waterneuron_data)

    def _get_nicp_from_kongswap_sync(self, waterneuron_data: Optional[Dict] = None) -> Optional[Dict]:
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
                    
                    # Calculate arbitrage with WaterNeuron data
                    arbitrage = self.calculate_arbitrage_opportunity(nicp_price_in_icp, waterneuron_data)
                    
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

    def _get_nicp_from_icpswap_sync(self, waterneuron_data: Optional[Dict] = None) -> Optional[Dict]:
        """Get nICP data from ICPSwap"""
        try:
            response = self.session.get(self.icpswap_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Look for nICP/ICP pairs
            for item in data:
                base_id = item.get('base_id', '')
                target_id = item.get('target_id', '')
                
                # Check for nICP/ICP pair in either direction
                if ((base_id == self.NICP_CANISTER and target_id == self.ICP_CANISTER) or
                    (base_id == self.ICP_CANISTER and target_id == self.NICP_CANISTER)):
                    
                    last_price = float(item.get('last_price', 0))
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
                    
                    # Calculate arbitrage with WaterNeuron data
                    arbitrage = self.calculate_arbitrage_opportunity(nicp_price_in_icp, waterneuron_data)
                    
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

    def check_health(self) -> Dict[str, bool]:
        """Check if DEX APIs are accessible"""
        health = {}
        
        # Check ICPSwap
        try:
            response = self.session.get(self.icpswap_url, timeout=5)
            health['ICPSwap'] = response.status_code == 200
        except:
            health['ICPSwap'] = False
        
        # Check KongSwap
        try:
            response = self.session.get(f"{self.kongswap_base_url}/api/coingecko/tickers", timeout=5)
            health['KongSwap'] = response.status_code == 200
        except:
            health['KongSwap'] = False
        
        return health

    def format_arbitrage_summary(self, arbitrage_data: Dict) -> str:
        """Format arbitrage data into a readable summary"""
        if not arbitrage_data.get('opportunities'):
            return "❌ No nICP arbitrage opportunities found"
        
        summary = []
        summary.append("🔍 **nICP Arbitrage Analysis**")
        summary.append(f"📅 Updated: {arbitrage_data.get('timestamp', 'Unknown')}")
        
        # WaterNeuron status
        if arbitrage_data.get('waterneuron_data'):
            if arbitrage_data['waterneuron_data'].get('success'):
                summary.append("🌊 WaterNeuron: ✅ Live data")
            else:
                summary.append("🌊 WaterNeuron: ⚠️ Partial data")
        else:
            summary.append("🌊 WaterNeuron: ❌ Using fallback rate")
        
        summary.append(f"📊 Direct staking rate: 1 ICP = {arbitrage_data.get('current_direct_staking_rate', 'Unknown')} nICP")
        summary.append("")
        
        # Best opportunity
        best_opp = arbitrage_data.get('best_opportunity')
        if best_opp:
            arb = best_opp['arbitrage']
            summary.append(f"🏆 **Best Opportunity: {best_opp['dex']}**")
            summary.append(f"💰 Profit: {arb['profit_percentage_6m']:.1f}% in 6 months")
            summary.append(f"📈 Annualized: {arb['annualized_return']:.1f}%")
            summary.append(f"💵 Cost: {arb['cost_per_nicp_icp']:.6f} ICP per nICP")
            summary.append(f"🎯 {arb['recommendation']}")
            summary.append("")
        
        # All opportunities
        summary.append("📋 **All Opportunities:**")
        for opp in arbitrage_data['opportunities']:
            arb = opp['arbitrage']
            status = "✅" if arb['viable'] else "❌"
            summary.append(f"{status} {opp['dex']}: {arb['profit_percentage_6m']:.1f}% profit")
        
        return "\n".join(summary) 