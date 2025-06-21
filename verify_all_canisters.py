#!/usr/bin/env python3
"""
Comprehensive Canister Verification Script
Uses Kong API's /api/dextools/asset endpoint to verify ALL canister information
"""

import requests
import json
import time
from typing import Dict, List, Optional

class CanisterVerifier:
    def __init__(self):
        self.kong_base_url = "https://api.kongswap.io"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ICP-Token-Monitor/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # All canister IDs from our mapping (both known and unknown)
        self.all_canisters = {
            # Core ICP tokens
            'ryjl3-tyaaa-aaaaa-aaaba-cai': 'ICP',
            'cngnf-vqaaa-aaaar-qag4q-cai': 'ckUSDT', 
            'xevnm-gaaaa-aaaar-qafnq-cai': 'ckUSDC',
            'bkyz2-fmaaa-aaaah-qcl7q-cai': 'ckBTC',
            'mxzaz-hqaaa-aaaar-qaada-cai': 'ckETH',
            'suaf3-hqaaa-aaaaf-qaaya-cai': 'nICP',
            'f54if-eqbof-4h6no-ico7y-ktyzv-5jvpv-luo5o-mywf4-2lhzv-7eavs-aqe': 'NICP',
            
            # High-volume tokens
            'np5km-uyaaa-aaaaq-aadrq-cai': 'KINIC',
            '4c4fd-caaaa-aaaaq-aaa3a-cai': 'YUGE',
            'ck73f-syaaa-aaaam-qdtea-cai': 'BOOM',
            'qci3o-6iaaa-aaaam-qcvaa-cai': 'CHAT',
            'vurva-zqaaa-aaaak-quezq-cai': 'GHOST',
            'icaf7-3aaaa-aaaam-qcx3q-cai': 'DOGMI',
            'zfcdd-tqaaa-aaaaq-aaaga-cai': 'SNS1',
            'mwen2-oqaaa-aaaam-adaca-cai': 'EXE',
            'atuk3-uqaaa-aaaam-qduwa-cai': 'MOTOKO',
            '2rqn6-kiaaa-aaaam-qcuya-cai': 'TRAX',
            'iwv6l-6iaaa-aaaam-qcw2a-cai': 'ELNA',
            'druyg-tyaaa-aaaam-qcw3a-cai': 'WTN',
            'emww2-4yaaa-aaaam-qcw4a-cai': 'ALPACALB',
            'ffi64-ziaaa-aaaam-qcw5a-cai': 'DITTO',
            'fw6jm-nqaaa-aaaam-qcw6a-cai': 'CTZ',
            'ixqp7-kqaaa-aaaam-qcw7a-cai': 'DKP',
            'jcmow-hyaaa-aaaam-qcw8a-cai': 'BITS',
            'k45jy-aiaaa-aaaam-qcw9a-cai': 'PANDA',
            'kbvhp-rqaaa-aaaam-qcwaa-cai': 'GLDGOV',
            'kknbx-zyaaa-aaaam-qcwba-cai': 'TAL',
            'lkwrt-vyaaa-aaaam-qcwca-cai': 'OGY',
            'lrtnw-paaaa-aaaam-qcwda-cai': 'SONIC',
            'mih44-vaaaa-aaaam-qcwea-cai': 'SNEED',
            'n6tkf-tqaaa-aaaam-qcwfa-cai': 'NUANCE',
            'o4zzi-qaaaa-aaaam-qcwga-cai': 'CATALYZE',
            'o7oak-iyaaa-aaaam-qcwha-cai': 'YRAL',
            'rh2pm-ryaaa-aaaan-qeniq-cai': 'EXE',
            'sx3gz-hqaaa-aaaam-qcwia-cai': 'CYCLES',
            'tyyy3-4aaaa-aaaam-qcwja-cai': 'LBRY',
            'vi5vh-wyaaa-aaaam-qcwka-cai': 'GLDT',
            'wkv3f-iiaaa-aaaam-qcwla-cai': 'PARTY',
            'xsi2v-cyaaa-aaaam-qcwma-cai': 'HOT',
            'ysy5f-2qaaa-aaaam-qcwna-cai': 'BURN',
            'z3hpp-qaaaa-aaaam-qcwoa-cai': 'NTN',
            '2ouva-viaaa-aaaam-qcwpa-cai': 'SEERS',
            '5kijx-siaaa-aaaam-qcwqa-cai': 'WUMBO',
            '6c7su-kiaaa-aaaam-qcwra-cai': 'DOLR',
            '7pail-xaaaa-aaaam-qcwsa-cai': 'BOB',
            '7xkvf-zyaaa-aaaam-qcwta-cai': 'PEPE',
            '4k7jk-vyaaa-aaaam-qcwua-cai': 'DSCVR',
            
            # Updated tokens (user verified)
            '7pail-xaaaa-aaaas-aabmq-cai': 'BOB',
            'n6tkf-tqaaa-aaaal-qsneq-cai': 'cICP',
            'ysy5f-2qaaa-aaaap-qkmmq-cai': 'ALEX',
            'lrtnw-paaaa-aaaaq-aadfa-cai': 'SWAPDAO',
            
            # Still unknown tokens
            'ss2fx-dyaaa-aaaar-qacoq-cai': 'UNKNOWN_SS2FX',
            'pcj6u-uaaaa-aaaak-aewnq-cai': 'UNKNOWN_PCJ6U',
            'f54if-eqaaa-aaaaq-aacea-cai': 'UNKNOWN_F54IF',
        }
    
    def get_asset_info(self, canister_id: str) -> Optional[Dict]:
        """Get asset information from Kong API"""
        try:
            url = f"{self.kong_base_url}/api/dextools/asset"
            params = {'id': canister_id}
            
            print(f"Querying: {canister_id}")
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout for {canister_id}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error for {canister_id}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"  ❌ Invalid JSON response for {canister_id}")
            return None
    
    def verify_all_canisters(self):
        """Verify all canister IDs using Kong API"""
        print("🔍 Comprehensive Canister Verification using Kong API")
        print("=" * 60)
        
        verified_info = {}
        discrepancies = []
        unknown_resolved = []
        api_failures = []
        
        for canister_id, expected_symbol in self.all_canisters.items():
            print(f"\n📊 Verifying: {canister_id} (Expected: {expected_symbol})")
            
            # Get info from Kong API
            asset_info = self.get_asset_info(canister_id)
            
            if asset_info is None:
                api_failures.append((canister_id, expected_symbol))
                print(f"  ❌ API call failed")
                continue
            
            # Extract relevant information from nested asset object
            asset_data = asset_info.get('asset', {})
            api_symbol = asset_data.get('symbol', 'N/A')
            api_name = asset_data.get('name', 'N/A')
            api_decimals = asset_data.get('decimals', 'N/A')
            api_total_supply = asset_data.get('totalSupply', 'N/A')
            api_circulating_supply = asset_data.get('circulatingSupply', 'N/A')
            api_holders_count = asset_data.get('holdersCount', 'N/A')
            
            print(f"  📋 API Response:")
            print(f"     Symbol: {api_symbol}")
            print(f"     Name: {api_name}")
            print(f"     Decimals: {api_decimals}")
            print(f"     Total Supply: {api_total_supply}")
            print(f"     Circulating Supply: {api_circulating_supply}")
            print(f"     Holders Count: {api_holders_count}")
            
            # Store verified info
            verified_info[canister_id] = {
                'expected_symbol': expected_symbol,
                'api_symbol': api_symbol,
                'api_name': api_name,
                'api_decimals': api_decimals,
                'api_total_supply': api_total_supply,
                'api_circulating_supply': api_circulating_supply,
                'api_holders_count': api_holders_count,
                'full_response': asset_info
            }
            
            # Check for discrepancies
            if expected_symbol.startswith('UNKNOWN_'):
                if api_symbol != 'N/A' and api_symbol:
                    unknown_resolved.append((canister_id, expected_symbol, api_symbol, api_name))
                    print(f"  ✅ Unknown token resolved: {api_symbol} ({api_name})")
                else:
                    print(f"  ❓ Still unknown")
            elif api_symbol != expected_symbol and api_symbol != 'N/A':
                discrepancies.append((canister_id, expected_symbol, api_symbol, api_name))
                print(f"  ⚠️  Discrepancy: Expected {expected_symbol}, got {api_symbol}")
            else:
                print(f"  ✅ Confirmed: {api_symbol}")
            
            # Rate limiting
            time.sleep(0.5)
        
        # Print summary
        self.print_summary(verified_info, discrepancies, unknown_resolved, api_failures)
        
        return verified_info
    
    def print_summary(self, verified_info, discrepancies, unknown_resolved, api_failures):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"\n✅ Total canisters verified: {len(verified_info)}")
        print(f"❌ API failures: {len(api_failures)}")
        print(f"⚠️  Discrepancies found: {len(discrepancies)}")
        print(f"🔍 Unknown tokens resolved: {len(unknown_resolved)}")
        
        if discrepancies:
            print(f"\n⚠️  DISCREPANCIES:")
            for canister_id, expected, actual, name in discrepancies:
                print(f"   {canister_id[:20]}... Expected: {expected}, API: {actual} ({name})")
        
        if unknown_resolved:
            print(f"\n🔍 UNKNOWN TOKENS RESOLVED:")
            for canister_id, old_name, new_symbol, new_name in unknown_resolved:
                print(f"   {canister_id[:20]}... {old_name} → {new_symbol} ({new_name})")
        
        if api_failures:
            print(f"\n❌ API FAILURES:")
            for canister_id, expected in api_failures:
                print(f"   {canister_id[:20]}... {expected}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if unknown_resolved:
            print("   • Update canister_to_symbol mapping with resolved tokens")
        if discrepancies:
            print("   • Review and correct symbol discrepancies")
        if api_failures:
            print("   • Retry failed API calls or check canister validity")
    
    def generate_updated_mapping(self, verified_info):
        """Generate updated canister mapping based on API results"""
        print(f"\n🔧 UPDATED CANISTER MAPPING:")
        print("=" * 60)
        
        updated_mapping = {}
        
        for canister_id, info in verified_info.items():
            api_symbol = info['api_symbol']
            expected_symbol = info['expected_symbol']
            
            if api_symbol and api_symbol != 'N/A':
                updated_mapping[canister_id] = api_symbol
                if api_symbol != expected_symbol:
                    print(f"'{canister_id}': '{api_symbol}',  # Updated from {expected_symbol}")
                else:
                    print(f"'{canister_id}': '{api_symbol}',  # Confirmed")
            else:
                updated_mapping[canister_id] = expected_symbol
                print(f"'{canister_id}': '{expected_symbol}',  # No API data")
        
        return updated_mapping

def main():
    """Main verification function"""
    verifier = CanisterVerifier()
    
    print("🚀 Starting comprehensive canister verification...")
    print("This will query Kong API for ALL known canister IDs")
    print("=" * 60)
    
    # Verify all canisters
    verified_info = verifier.verify_all_canisters()
    
    # Generate updated mapping
    updated_mapping = verifier.generate_updated_mapping(verified_info)
    
    # Save results to file
    with open('canister_verification_results.json', 'w') as f:
        json.dump(verified_info, f, indent=2)
    
    print(f"\n💾 Results saved to: canister_verification_results.json")
    print("🎉 Verification complete!")

if __name__ == "__main__":
    main() 