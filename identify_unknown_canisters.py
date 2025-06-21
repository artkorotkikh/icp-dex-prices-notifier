#!/usr/bin/env python3

import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def identify_unknown_canisters():
    """Identify the unknown canister IDs from KongSwap API"""
    print("🔍 Identifying unknown canister IDs...")
    
    # Get raw API data
    ticker_url = "https://api.kongswap.io/api/coingecko/tickers"
    response = requests.get(ticker_url, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ API request failed: {response.status_code}")
        return
        
    raw_data = response.json()
    print(f"✅ Retrieved {len(raw_data)} raw tickers")
    
    # Known canister mapping from the code
    known_canisters = {
        'ryjl3-tyaaa-aaaaa-aaaba-cai': 'ICP',
        'cngnf-vqaaa-aaaar-qag4q-cai': 'ckUSDT', 
        'xevnm-gaaaa-aaaar-qafnq-cai': 'ckUSDC',
        'bkyz2-fmaaa-aaaah-qcl7q-cai': 'ckBTC',
        'mxzaz-hqaaa-aaaar-qaada-cai': 'ckETH',
        'suaf3-hqaaa-aaaaf-qaaya-cai': 'nICP',
        'f54if-eqbof-4h6no-ico7y-ktyzv-5jvpv-luo5o-mywf4-2lhzv-7eavs-aqe': 'NICP',
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
        '7pail-xaaaa-aaaam-qcwsa-cai': 'NANAS',
        '7xkvf-zyaaa-aaaam-qcwta-cai': 'PEPE',
        '4k7jk-vyaaa-aaaam-qcwua-cai': 'DSCVR',
    }
    
    # Find unknown canisters with high volume
    unknown_canisters = []
    icp_canister = 'ryjl3-tyaaa-aaaaa-aaaba-cai'
    usdt_canister = 'cngnf-vqaaa-aaaar-qag4q-cai'
    
    for ticker in raw_data:
        base_id = ticker.get('base_currency', '') or ticker.get('base_id', '')
        target_id = ticker.get('target_currency', '') or ticker.get('target_id', '')
        base_volume = float(ticker.get('base_volume', 0))
        target_volume = float(ticker.get('target_volume', 0))
        
        # Check for ICP pairs with unknown tokens
        unknown_token = None
        unknown_canister = None
        
        if target_id == icp_canister and base_id not in known_canisters and base_id:
            unknown_token = base_id
            unknown_canister = base_id
            volume = target_volume * 4.78  # ICP price approximation
        elif base_id == icp_canister and target_id not in known_canisters and target_id:
            unknown_token = target_id
            unknown_canister = target_id
            volume = base_volume * 4.78
        elif target_id == usdt_canister and base_id not in known_canisters and base_id:
            unknown_token = base_id
            unknown_canister = base_id
            volume = target_volume
        elif base_id == usdt_canister and target_id not in known_canisters and target_id:
            unknown_token = target_id
            unknown_canister = target_id
            volume = base_volume
        
        if unknown_token and volume > 1000:  # Only high volume pairs
            # Create short name like the bot does
            short_name = f"{unknown_canister[:5]}...{unknown_canister[-3:]}" if len(unknown_canister) > 20 else unknown_canister[:8] + '...'
            unknown_canisters.append((unknown_canister, short_name, volume))
    
    # Remove duplicates and sort by volume
    unique_unknown = {}
    for canister, short_name, volume in unknown_canisters:
        if canister not in unique_unknown or volume > unique_unknown[canister][1]:
            unique_unknown[canister] = (short_name, volume)
    
    # Sort by volume
    sorted_unknown = sorted(unique_unknown.items(), key=lambda x: x[1][1], reverse=True)
    
    print(f"\n🔍 Found {len(sorted_unknown)} unknown high-volume canister IDs:")
    print("-" * 80)
    
    for canister, (short_name, volume) in sorted_unknown:
        print(f"'{canister}': 'UNKNOWN_{short_name}',  # ${volume:,.0f} volume")
    
    print(f"\n📋 These are the canister IDs that need to be identified and mapped to token symbols.")
    print(f"💡 You can research these on the Internet Computer dashboard or token registries.")

if __name__ == "__main__":
    identify_unknown_canisters() 