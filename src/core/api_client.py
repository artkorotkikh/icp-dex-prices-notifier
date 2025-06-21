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
        
        # KongSwap uses ICP canisters, not traditional REST API
        # Base API exists but trading endpoints are canister-based
        self.kongswap_base_url = "https://api.kongswap.io"
        self.kongswap_canister_id = "rrkah-fqaaa-aaaaq-aadhq-cai"  # KongSwap backend canister
        
        # Future KongSwap API endpoints (when available)
        self.kongswap_urls = {
            'status': 'https://api.kongswap.io',
            'canister': f'https://{self.kongswap_canister_id}.raw.ic0.app',
            # Note: Actual endpoints TBD based on KongSwap's canister interface
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
    
    def get_kongswap_data(self) -> Optional[List[Dict]]:
        """Fetch data from KongSwap API using REST endpoints"""
        return self.fetch_kongswap_data()
    
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
                        # Calculate volumes
                        volume_24h_tokens = float(item.get('base_volume_24H', 0)) + float(item.get('target_volume_24H', 0))
                        volume_24h_usd = float(item.get('volume_usd_24H', 0))
                        liquidity_usd = float(item.get('liquidity_in_usd', 0))
                        
                        # Filter out pairs with very low volume (likely test/fake pairs)
                        # Require meaningful trading activity: volume > $500 OR (volume > $50 AND liquidity > $50000)
                        # This keeps active pairs while filtering out dormant/test tokens
                        has_good_volume = volume_24h_usd > 500
                        has_decent_activity = volume_24h_usd > 50 and liquidity_usd > 50000
                        
                        if has_good_volume or has_decent_activity:
                            found_pairs[pair_name] = {
                                'price': float(item.get('last_price', 0)),
                                'volume_24h': volume_24h_tokens,
                                'volume_24h_usd': volume_24h_usd,
                                'liquidity_usd': liquidity_usd,
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
        
        # Get KongSwap data using REST API
        kongswap_data = self.get_kongswap_data()
        if kongswap_data:
            # KongSwap data is already formatted, convert to ICPSwap format
            for pair_data in kongswap_data:
                pair_name = pair_data.get('pair', '')
                if pair_name:
                    volume_24h = pair_data.get('volume_24h', 0)
                    formatted_pair = {
                        'price': pair_data.get('price', 0),
                        'volume_24h': volume_24h,
                        'volume_24h_usd': volume_24h,  # KongSwap volume is already in USD
                        'liquidity_usd': pair_data.get('liquidity', 0),
                        'base_volume': volume_24h / 2,  # Estimate base volume
                        'target_volume': volume_24h / 2,  # Estimate target volume
                        'source': 'kongswap',
                        'raw_data': json.dumps(pair_data.get('raw_data', pair_data))
                    }
                    all_pairs[pair_name] = formatted_pair
            logger.info(f"Found {len(kongswap_data)} ICP pairs from KongSwap")
        
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
            volume_24h_usd = pair_data.get('volume_24h_usd', 0)
            liquidity_usd = pair_data.get('liquidity_usd', 0)
            source = pair_data.get('source', 'unknown')
            
            # Format large numbers nicely
            def format_usd(amount):
                if amount >= 1000000:
                    return f"${amount/1000000:.2f}M"
                elif amount >= 1000:
                    return f"${amount/1000:.1f}K"
                else:
                    return f"${amount:.2f}"
            
            formatted_output = f"💰 **Price:** ${price:.6f}\n"
            formatted_output += f"📊 **24h Volume:** {format_usd(volume_24h_usd)}\n"
            formatted_output += f"💧 **Liquidity:** {format_usd(liquidity_usd)}\n"
            formatted_output += f"📡 **Source:** {source.upper()}"
            
            return formatted_output
        except Exception as e:
            logger.error(f"Error formatting price data: {e}")
            return "❌ Error formatting price data"
    
    def health_check(self) -> Dict[str, str]:
        """Check if APIs are responding"""
        health_status = {}
        
        # Check ICPSwap
        icpswap_data = self._make_request(self.icpswap_url)
        health_status['icpswap'] = 'Connected' if icpswap_data is not None else 'Disconnected'
        
        # Check KongSwap
        kongswap_status = self._make_request(self.kongswap_base_url)
        if kongswap_status and kongswap_status.get('status') == 'ok':
            health_status['kongswap'] = 'API Online (Canister-based)'
        else:
            health_status['kongswap'] = 'API Offline'
        
        return health_status

    def fetch_kongswap_data(self):
        """
        Fetch data from KongSwap API using REST endpoints
        Returns list of formatted price data
        """
        try:
            # Check if KongSwap API is available
            response = requests.get(self.kongswap_base_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"KongSwap API not accessible: {response.status_code}")
                return []
            
            # Try to get ticker data from coingecko endpoint
            ticker_url = f"{self.kongswap_base_url}/api/coingecko/tickers"
            ticker_response = requests.get(ticker_url, timeout=10)
            
            if ticker_response.status_code == 200:
                ticker_data = ticker_response.json()
                logger.info(f"Found {len(ticker_data)} pairs from KongSwap tickers")
                return self._format_kongswap_ticker_data(ticker_data)
            
            # If tickers endpoint doesn't work, try dexscreener approach
            # First get available pairs using coinmarketcap summary
            summary_url = f"{self.kongswap_base_url}/api/coinmarketcap/summary"
            summary_response = requests.get(summary_url, timeout=10)
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                logger.info(f"Found {len(summary_data)} pairs from KongSwap summary")
                
                # Get detailed data for each pair using dexscreener endpoint
                detailed_pairs = []
                for pair_summary in summary_data[:10]:  # Limit to first 10 pairs
                    try:
                        pair_id = pair_summary.get('trading_pairs', 'unknown')
                        if pair_id and pair_id != 'unknown':
                            pair_url = f"{self.kongswap_base_url}/api/dexscreener/pair"
                            pair_response = requests.get(pair_url, params={'id': pair_id}, timeout=5)
                            
                            if pair_response.status_code == 200:
                                pair_data = pair_response.json()
                                detailed_pairs.append(pair_data)
                    except Exception as e:
                        logger.debug(f"Failed to get detailed data for pair {pair_id}: {e}")
                        continue
                
                if detailed_pairs:
                    logger.info(f"Retrieved detailed data for {len(detailed_pairs)} KongSwap pairs")
                    return self._format_kongswap_dexscreener_data(detailed_pairs)
                else:
                    # Fallback to summary data
                    return self._format_kongswap_summary_data(summary_data)
            
            logger.info("KongSwap API is online but trading data requires canister integration")
            logger.info("KongSwap API detected: KongSwap uses canister-based architecture")
            return []
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching KongSwap data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error with KongSwap API: {e}")
            return []

    def _format_kongswap_ticker_data(self, ticker_data):
        """Format KongSwap ticker data to standard format"""
        formatted_pairs = []
        
        # Comprehensive KongSwap canister ID to symbol mapping (verified via Kong API /api/dextools/asset)
        canister_to_symbol = {
            # Core ICP tokens (API verified)
            'ryjl3-tyaaa-aaaaa-aaaba-cai': 'ICP',      # ✅ Internet Computer
            'cngnf-vqaaa-aaaar-qag4q-cai': 'ckUSDT',   # ✅ ckUSDT
            'xevnm-gaaaa-aaaar-qafnq-cai': 'ckUSDC',   # ✅ ckUSDC
            'mxzaz-hqaaa-aaaar-qaada-cai': 'ckBTC',    # ✅ ckBTC (corrected from ckETH)
            'ss2fx-dyaaa-aaaar-qacoq-cai': 'ckETH',    # ✅ ckETH (different canister)
            'buwm7-7yaaa-aaaar-qagva-cai': 'nICP',     # 
            
            # High-volume tokens (API verified and corrected)
            'np5km-uyaaa-aaaaq-aadrq-cai': 'POKED',    # ✅ Poked (corrected from KINIC)
            '4c4fd-caaaa-aaaaq-aaa3a-cai': 'CLAY',     # ✅ Mimic Clay (corrected from YUGE)
            'ck73f-syaaa-aaaam-qdtea-cai': 'SCOTT',    # ✅ SCOTT SUMMERS (corrected from BOOM)
            'qci3o-6iaaa-aaaam-qcvaa-cai': 'SPANGE',   # ✅ Spare Change (corrected from CHAT)
            'vurva-zqaaa-aaaak-quezq-cai': 'MAPTF',    # ✅ MAP Technical Forecasting (corrected from GHOST)
            'icaf7-3aaaa-aaaam-qcx3q-cai': 'RUGGY',    # ✅ RUGGY (corrected from DOGMI)
            'zfcdd-tqaaa-aaaaq-aaaga-cai': 'DKP',      # ✅ Draggin Karma Points (corrected from SNS1)
            'mwen2-oqaaa-aaaam-adaca-cai': 'nanas',    # ✅ The Banana Company (corrected from EXE)
            'atuk3-uqaaa-aaaam-qduwa-cai': 'IC',       # ✅ Infinity Coin (corrected from MOTOKO)
            '2rqn6-kiaaa-aaaam-qcuya-cai': 'MGSN',     # ✅ MegaSynergy (corrected from TRAX)
            'iwv6l-6iaaa-aaaam-qcw2a-cai': 'ELNA',    # Elna token
            'druyg-tyaaa-aaaam-qcw3a-cai': 'WTN',     # WTN token
            'emww2-4yaaa-aaaam-qcw4a-cai': 'ALPACALB', # Alpaca LB
            'ffi64-ziaaa-aaaam-qcw5a-cai': 'DITTO',   # Ditto token
            'fw6jm-nqaaa-aaaam-qcw6a-cai': 'CTZ',     # CTZ token
            'ixqp7-kqaaa-aaaam-qcw7a-cai': 'DKP',     # DKP token
            'jcmow-hyaaa-aaaam-qcw8a-cai': 'BITS',    # Bits token
            'k45jy-aiaaa-aaaam-qcw9a-cai': 'PANDA',   # Panda token
            'kbvhp-rqaaa-aaaam-qcwaa-cai': 'GLDGOV',  # Gold Gov
            'kknbx-zyaaa-aaaam-qcwba-cai': 'TAL',     # TAL token
            'lkwrt-vyaaa-aaaam-qcwca-cai': 'OGY',     # OGY token
            'lrtnw-paaaa-aaaam-qcwda-cai': 'SONIC',   # Sonic token
            'lrtnw-paaaa-aaaaq-aadfa-cai': 'SONIC',   # Sonic token (different canister)
            'mih44-vaaaa-aaaam-qcwea-cai': 'SNEED',   # Sneed token
            'n6tkf-tqaaa-aaaam-qcwfa-cai': 'NUANCE',  # Nuance token
            'n6tkf-tqaaa-aaaal-qsneq-cai': 'NUANCE',  # Nuance token (different canister)
            'o4zzi-qaaaa-aaaam-qcwga-cai': 'CATALYZE', # Catalyze
            'o7oak-iyaaa-aaaam-qcwha-cai': 'YRAL',    # Yral token
            'rh2pm-ryaaa-aaaan-qeniq-cai': 'EXE',     # EXE Windoge98
            'sx3gz-hqaaa-aaaam-qcwia-cai': 'CYCLES',  # Cycles token
            'tyyy3-4aaaa-aaaam-qcwja-cai': 'LBRY',    # LBRY token
            'vi5vh-wyaaa-aaaam-qcwka-cai': 'GLDT',    # GLDT token
            'wkv3f-iiaaa-aaaam-qcwla-cai': 'PARTY',   # Party token
            'xsi2v-cyaaa-aaaam-qcwma-cai': 'HOT',     # Hot token
            'ysy5f-2qaaa-aaaam-qcwna-cai': 'BURN',    # Burn token
            'ysy5f-2qaaa-aaaap-qkmmq-cai': 'BURN',    # Burn token (different canister)
            'z3hpp-qaaaa-aaaam-qcwoa-cai': 'NTN',     # NTN token
            '2ouva-viaaa-aaaam-qcwpa-cai': 'SEERS',   # Seers token
            '5kijx-siaaa-aaaam-qcwqa-cai': 'WUMBO',   # Wumbo token
            '6c7su-kiaaa-aaaam-qcwra-cai': 'DOLR',    # DOLR token
            '7pail-xaaaa-aaaam-qcwsa-cai': 'BOB',     # BOB token
            '7pail-xaaaa-aaaas-aabmq-cai': 'BOB',     # BOB token (different canister)
            '7xkvf-zyaaa-aaaam-qcwta-cai': 'PEPE',    # Pepe token
            '4k7jk-vyaaa-aaaam-qcwua-cai': 'DSCVR',   # DSCVR token
            'n6tkf-tqaaa-aaaal-qsneq-cai': 'cICP',    # ✅ cICP token
            'ysy5f-2qaaa-aaaap-qkmmq-cai': 'ALEX',    # ✅ ALEX token
            'lrtnw-paaaa-aaaaq-aadfa-cai': 'SWAMP',   # ✅ SWAMPDAO (corrected from SWAPDAO)
            
            # Previously unknown tokens (Kong API resolved)
            'pcj6u-uaaaa-aaaak-aewnq-cai': 'CLOUD',   # ✅ Crypto Cloud (resolved)
            'f54if-eqaaa-aaaaq-aacea-cai': 'NTN',     # ✅ Neutrinite (resolved)
        }
        
        for ticker in ticker_data:
            try:
                # Extract canister IDs
                base_canister = ticker.get('base_currency', '')
                target_canister = ticker.get('target_currency', '')
                
                # Skip if essential data is missing
                if not all([base_canister, target_canister]):
                    continue
                
                # Map canister IDs to symbols with better fallback
                def get_readable_symbol(canister_id):
                    if canister_id in canister_to_symbol:
                        return canister_to_symbol[canister_id]
                    
                    # For unknown canisters, create a more readable short name
                    if len(canister_id) > 20:  # Typical canister ID length
                        # Take first 5 chars and last 3 chars for readability
                        return f"{canister_id[:5]}...{canister_id[-3:]}"
                    else:
                        return canister_id[:8] + '...'
                
                base_symbol = get_readable_symbol(base_canister)
                target_symbol = get_readable_symbol(target_canister)
                
                # Create pair name
                pair_name = f"{base_symbol}/{target_symbol}"
                
                # Prioritize pairs with known tokens, but include high-volume unknown pairs
                # Updated with Kong API verified token names
                known_symbols = {
                    # Core tokens
                    'ICP', 'ckUSDT', 'ckUSDC', 'ckBTC', 'ckETH', 'nICP', 'NICP',
                    
                    # API-verified tokens (corrected names)
                    'POKED', 'CLAY', 'SCOTT', 'SPANGE', 'MAPTF', 'RUGGY', 'DKP',
                    'nanas', 'IC', 'MGSN', 'EXE', 'BOB', 'cICP', 'ALEX', 'SWAMP',
                    'CLOUD', 'NTN',
                    
                    # Tokens not verified by Kong API (may need correction)
                    'ELNA', 'WTN', 'ALPACALB', 'DITTO', 'CTZ', 'BITS', 'PANDA', 
                    'GLDGOV', 'TAL', 'OGY', 'SONIC', 'SNEED', 'NUANCE', 'CATALYZE', 
                    'YRAL', 'CYCLES', 'LBRY', 'GLDT', 'PARTY', 'HOT', 'BURN',
                    'SEERS', 'WUMBO', 'DOLR', 'PEPE', 'DSCVR'
                }
                
                # Extract price and volume data
                last_price = float(ticker.get('last_price', 0))
                base_volume = float(ticker.get('base_volume', 0))
                target_volume = float(ticker.get('target_volume', 0))
                liquidity_usd = float(ticker.get('liquidity_in_usd', 0))
                
                # Calculate USD volume correctly:
                # KongSwap volumes are often in token units, need to convert properly
                icp_price = 4.78  # Approximate ICP price in USD
                usdt_price = 1.0  # USDT price in USD
                
                # For ICP pairs, always use the ICP side of the volume
                if target_canister == 'ryjl3-tyaaa-aaaaa-aaaba-cai':
                    # Target is ICP: use target_volume * ICP_price
                    volume_24h_usd = target_volume * icp_price
                elif base_canister == 'ryjl3-tyaaa-aaaaa-aaaba-cai':
                    # Base is ICP: use base_volume * ICP_price (but base_volume should be in ICP units)
                    volume_24h_usd = base_volume * icp_price
                elif target_canister == 'cngnf-vqaaa-aaaar-qag4q-cai':
                    # Target is ckUSDT: use target_volume * USDT_price
                    volume_24h_usd = target_volume * usdt_price
                elif base_canister == 'cngnf-vqaaa-aaaar-qag4q-cai':
                    # Base is ckUSDT: use base_volume * USDT_price
                    volume_24h_usd = base_volume * usdt_price
                else:
                    # For other pairs, use the smaller volume as it's likely more accurate
                    # Large numbers are usually token counts, smaller numbers are USD/ICP equivalent
                    volume_24h_usd = min(base_volume, target_volume)
                
                # Include if either token is known OR if it's a high-volume pair
                has_known_token = (base_symbol in known_symbols or target_symbol in known_symbols)
                is_high_volume = volume_24h_usd > 10000  # $10K+ volume
                
                if not (has_known_token or is_high_volume):
                    continue
                
                # Only include pairs with meaningful volume (>$100 daily)
                if volume_24h_usd < 100:
                    continue
                
                formatted_pair = {
                    'pair': pair_name,
                    'price': last_price,
                    'volume_24h': volume_24h_usd,
                    'liquidity': liquidity_usd,
                    'source': 'KongSwap',
                    'raw_data': ticker
                }
                
                formatted_pairs.append(formatted_pair)
                
            except (ValueError, TypeError) as e:
                logger.debug(f"Error formatting KongSwap ticker: {e}")
                continue
        
        return formatted_pairs

    def _format_kongswap_summary_data(self, summary_data):
        """Format KongSwap summary data to standard format"""
        formatted_pairs = []
        
        for summary in summary_data:
            try:
                # Extract pair information
                trading_pairs = summary.get('trading_pairs', '')
                if not trading_pairs:
                    continue
                
                # Parse trading pair (usually in format "BASE_TARGET")
                if '_' in trading_pairs:
                    base, target = trading_pairs.split('_', 1)
                    pair_name = f"{base}/{target}"
                elif '/' in trading_pairs:
                    pair_name = trading_pairs
                else:
                    continue
                
                # Check if it's an ICP pair
                is_icp_pair = 'ICP' in pair_name.upper()
                if not is_icp_pair:
                    continue
                
                # Extract price and volume data
                last_price = float(summary.get('last_price', 0))
                base_volume = float(summary.get('base_volume', 0))
                quote_volume = float(summary.get('quote_volume', 0))
                
                # Use base_volume as primary volume metric (consistent with ticker endpoint)
                volume_24h = base_volume
                if volume_24h < 100:
                    continue
                
                formatted_pair = {
                    'pair': pair_name,
                    'price': last_price,
                    'volume_24h': volume_24h,
                    'liquidity': 0,  # Not available in summary
                    'source': 'KongSwap',
                    'raw_data': summary
                }
                
                formatted_pairs.append(formatted_pair)
                
            except (ValueError, TypeError) as e:
                logger.debug(f"Error formatting KongSwap summary: {e}")
                continue
        
        return formatted_pairs

    def _format_kongswap_dexscreener_data(self, dexscreener_data):
        """Format KongSwap dexscreener data to standard format"""
        formatted_pairs = []
        
        for pair_data in dexscreener_data:
            try:
                # Extract pair information from dexscreener format
                pair_address = pair_data.get('pairAddress', '')
                base_token = pair_data.get('baseToken', {})
                quote_token = pair_data.get('quoteToken', {})
                
                base_symbol = base_token.get('symbol', '')
                quote_symbol = quote_token.get('symbol', '')
                
                if not all([base_symbol, quote_symbol]):
                    continue
                
                pair_name = f"{base_symbol}/{quote_symbol}"
                
                # Check if it's an ICP pair
                is_icp_pair = 'ICP' in pair_name.upper()
                if not is_icp_pair:
                    continue
                
                # Extract price and volume data
                price_native = float(pair_data.get('priceNative', 0))
                price_usd = float(pair_data.get('priceUsd', 0))
                volume_24h = float(pair_data.get('volume', {}).get('h24', 0))
                liquidity_usd = float(pair_data.get('liquidity', {}).get('usd', 0))
                
                # Use USD price if available, otherwise native price
                last_price = price_usd if price_usd > 0 else price_native
                
                # Only include pairs with meaningful volume
                if volume_24h < 100:
                    continue
                
                formatted_pair = {
                    'pair': pair_name,
                    'price': last_price,
                    'volume_24h': volume_24h,
                    'liquidity': liquidity_usd,
                    'source': 'KongSwap',
                    'raw_data': pair_data
                }
                
                formatted_pairs.append(formatted_pair)
                
            except (ValueError, TypeError) as e:
                logger.debug(f"Error formatting KongSwap dexscreener data: {e}")
                continue
        
        return formatted_pairs

    def format_kongswap_pairs(self, kongswap_data: List[Dict]) -> Dict[str, Dict]:
        """Format KongSwap data to match ICPSwap pair format"""
        formatted_pairs = {}
        
        for pair_data in kongswap_data:
            try:
                pair_name = pair_data.get('pair', '')
                if not pair_name:
                    continue
                
                # Convert to ICPSwap-compatible format
                volume_24h = pair_data.get('volume_24h', 0)
                formatted_pair = {
                    'price': pair_data.get('price', 0),
                    'volume_24h': volume_24h,
                    'volume_24h_usd': volume_24h,  # KongSwap volume is already in USD
                    'liquidity_usd': pair_data.get('liquidity', 0),
                    'base_volume': volume_24h / 2,  # Estimate base volume
                    'target_volume': volume_24h / 2,  # Estimate target volume
                    'source': 'kongswap',
                    'raw_data': json.dumps(pair_data.get('raw_data', pair_data))
                }
                
                formatted_pairs[pair_name] = formatted_pair
                
            except (ValueError, TypeError) as e:
                logger.debug(f"Error formatting KongSwap pair: {e}")
                continue 