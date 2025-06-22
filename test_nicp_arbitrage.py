#!/usr/bin/env python3
"""
Test nICP Discount Tracker
Demonstrates the key functionality of the nICP discount monitoring system
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.nicp_arbitrage_client import NICPArbitrageClient

def print_banner():
    """Print test banner"""
    print("🚀 nICP Discount Tracker - Test Demo")
    print("=" * 50)
    print("🎯 Demonstrating nICP/ICP discount opportunities")
    print("📊 Live data from KongSwap and other DEXes")
    print("💰 Real-time profit calculations")
    print("=" * 50)
    print()

def test_arbitrage_calculations():
    """Test arbitrage calculation logic"""
    print("🧮 **ARBITRAGE CALCULATION TESTS**")
    print("-" * 30)
    
    client = NICPArbitrageClient()
    
    test_scenarios = [
        ("Excellent opportunity", 0.950),
        ("Good opportunity", 0.975),
        ("Current market rate", 0.979),
        ("Break-even", 1.000),
        ("Loss scenario", 1.050)
    ]
    
    for scenario, price in test_scenarios:
        result = client.calculate_arbitrage_opportunity(price)
        status = "✅" if result['viable'] else "❌"
        
        print(f"{status} {scenario}:")
        print(f"   💰 nICP price: {price:.3f} ICP")
        print(f"   📈 Profit: {result['profit_percentage_6m']:.1f}% in 6 months")
        print(f"   🚀 Annualized: {result['annualized_return']:.1f}% APY")
        print(f"   🎯 {result['recommendation']}")
        print()

def test_live_data():
    """Test live data fetching"""
    print("🌐 **LIVE DATA FETCH TEST**")
    print("-" * 30)
    
    client = NICPArbitrageClient()
    
    try:
        print("🔍 Fetching live nICP arbitrage data...")
        arbitrage_data = client.get_nicp_arbitrage_data()
        
        summary = arbitrage_data['summary']
        print(f"📊 **Summary:**")
        print(f"   • DEXes checked: {summary['total_dexes']}")
        print(f"   • Viable opportunities: {summary['viable_opportunities']}")
        print(f"   • Best 6-month profit: {summary['best_profit_6m']:.1f}%")
        print(f"   • Best annualized return: {summary['best_annualized_return']:.1f}%")
        print()
        
        if arbitrage_data['opportunities']:
            print("🏆 **LIVE OPPORTUNITIES:**")
            for opp in arbitrage_data['opportunities']:
                arb = opp['arbitrage']
                status = "✅" if arb['viable'] else "❌"
                
                print(f"{status} **{opp['dex']}** ({opp['pair']}):")
                print(f"   💰 Cost: {arb['cost_per_nicp_icp']:.6f} ICP per nICP")
                print(f"   📈 Future value: {arb['future_icp_per_nicp']:.6f} ICP per nICP")
                print(f"   💸 Profit: {arb['profit_percentage_6m']:.1f}% in 6 months")
                print(f"   📊 Volume: ${opp.get('volume_24h_usd', 0):,.0f}")
                print(f"   🎯 {arb['recommendation']}")
                print()
        else:
            print("❌ No nICP pairs found on any DEX")
            print("💡 This might be temporary - try again later")
            
    except Exception as e:
        print(f"❌ Error fetching live data: {e}")

def demonstrate_user_scenarios():
    """Demonstrate different user investment scenarios"""
    print("👤 **USER INVESTMENT SCENARIOS**")
    print("-" * 30)
    
    # Use current market data
    client = NICPArbitrageClient()
    arbitrage_data = client.get_nicp_arbitrage_data()
    
    if not arbitrage_data.get('opportunities'):
        print("❌ No live data available for scenarios")
        return
    
    best_opp = arbitrage_data.get('best_opportunity')
    if not best_opp:
        print("❌ No viable opportunities for scenarios")
        return
    
    nicp_price = best_opp['arbitrage']['cost_per_nicp_icp']
    profit_per_nicp = best_opp['arbitrage']['profit_per_nicp_icp']
    
    investments = [100, 500, 1000, 5000, 10000]
    
    print(f"💰 **Investment scenarios at {nicp_price:.6f} ICP per nICP:**")
    print()
    
    for investment in investments:
        nicp_tokens = investment / nicp_price
        total_profit = nicp_tokens * profit_per_nicp
        profit_percentage = (total_profit / investment) * 100
        
        print(f"🎯 **{investment:,} ICP investment:**")
        print(f"   • Buy: {nicp_tokens:,.1f} nICP tokens")
        print(f"   • After 6 months: {investment + total_profit:,.1f} ICP")
        print(f"   • Profit: {total_profit:,.1f} ICP ({profit_percentage:.1f}%)")
        print(f"   • Monthly return: {profit_percentage/6:.1f}%")
        print()

def show_risks_and_considerations():
    """Show important risks and considerations"""
    print("⚠️  **RISKS & CONSIDERATIONS**")
    print("-" * 30)
    
    risks = [
        "🔒 **6-month lock-up period** - Your ICP will be locked during dissolution",
        "📈 **ICP price volatility** - ICP value may change during the 6-month period",
        "💧 **Liquidity risk** - nICP pairs may have low trading volume",
        "⏰ **Opportunity cost** - ICP might gain more than arbitrage profit",
        "🔧 **Technical risk** - Smart contract or dissolution process issues",
        "📊 **Market efficiency** - Arbitrage gaps may close quickly"
    ]
    
    for risk in risks:
        print(f"   {risk}")
    
    print()
    print("💡 **Best Practices:**")
    practices = [
        "📊 Monitor opportunities regularly with this bot",
        "💰 Don't invest more than you can lock up for 6 months",
        "🎯 Consider dollar-cost averaging into positions",
        "📈 Keep some ICP liquid for other opportunities",
        "🔍 Understand the dissolution process before starting"
    ]
    
    for practice in practices:
        print(f"   {practice}")

async def test_nicp_discount_tracker():
    """Test the nICP discount tracker with WaterNeuron integration"""
    
    print("🚀 nICP Discount Tracker - Test Demo")
    print("=" * 50)
    print("🎯 Demonstrating nICP/ICP discount opportunities")
    print()
    
    # Initialize the arbitrage client
    client = NICPArbitrageClient()
    
    print("1. Testing WaterNeuron integration...")
    waterneuron_data = await client.get_waterneuron_exchange_rate()
    
    if waterneuron_data and waterneuron_data.get('success'):
        print(f"✅ WaterNeuron data retrieved successfully!")
        print(f"   Source: {waterneuron_data.get('source', 'unknown')}")
        print(f"   nICP/ICP rate: {waterneuron_data.get('nicp_to_icp_rate', 'N/A')}")
        print(f"   ICP/nICP rate: {waterneuron_data.get('icp_to_nicp_rate', 'N/A')}")
        if 'total_supply' in waterneuron_data:
            print(f"   Total nICP supply: {waterneuron_data['total_supply']:,.2f}")
    else:
        print("⚠️ WaterNeuron data not available, using fallback")
    
    print()
    print("2. Fetching discount opportunities from DEXes...")
    
    # Get arbitrage data
    arbitrage_data = await client.get_nicp_arbitrage_data()
    
    print(f"📊 Found {arbitrage_data['summary']['total_dexes']} DEXes")
    print(f"💰 Viable opportunities: {arbitrage_data['summary']['viable_opportunities']}")
    
    if arbitrage_data['opportunities']:
        print("\n🔍 Detailed opportunities:")
        for i, opp in enumerate(arbitrage_data['opportunities'], 1):
            dex_name = opp.get('dex', 'Unknown')
            ticker = opp.get('ticker_name', 'N/A')
            price = opp.get('nicp_price_in_icp', 0)
            arbitrage = opp.get('arbitrage', {})
            
            print(f"\n{i}. {dex_name}")
            print(f"   Pair: {ticker}")
            print(f"   nICP Price: {price:.6f} ICP")
            
            if arbitrage.get('viable', False):
                print(f"   ✅ VIABLE - {arbitrage.get('recommendation', 'N/A')}")
                print(f"   💰 6-month profit: {arbitrage.get('profit_percentage_6m', 0):.2f}%")
                print(f"   📈 Annualized APY: {arbitrage.get('annualized_return', 0):.2f}%")
                print(f"   💵 Future value: 1 nICP → {arbitrage.get('future_icp_per_nicp', 0):.4f} ICP")
                
                # WaterNeuron source info
                if arbitrage.get('waterneuron_source'):
                    print(f"   🌊 Using live WaterNeuron data ({arbitrage.get('waterneuron_data_source', 'unknown')})")
                else:
                    print(f"   ⚠️ Using fallback rate")
            else:
                print(f"   ❌ NOT VIABLE - {arbitrage.get('recommendation', 'Low profit')}")
    
    # Show best opportunity
    best_opp = arbitrage_data.get('best_opportunity')
    if best_opp:
        print(f"\n🏆 BEST OPPORTUNITY:")
        print(f"   DEX: {best_opp.get('dex', 'Unknown')}")
        print(f"   6-month profit: {best_opp['arbitrage']['profit_percentage_6m']:.2f}%")
        print(f"   Annualized APY: {best_opp['arbitrage']['annualized_return']:.2f}%")
        print(f"   {best_opp['arbitrage']['recommendation']}")
    
    print()
    print("3. Testing bot summary formatting...")
    summary = client.format_arbitrage_summary(arbitrage_data)
    print("📱 Telegram Bot Summary:")
    print(summary)
    
    print()
    print("🤖 The nICP Discount Tracker bot is ready!")
    print("📱 Telegram Commands:")
    print("   • /discount - Check live opportunities")
    print("   • /help - Show all commands")
    print("   • /status - Bot health check")
    print()
    print("🚀 Ready to help users find nICP discount opportunities!")

if __name__ == "__main__":
    asyncio.run(test_nicp_discount_tracker()) 