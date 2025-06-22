import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import json
from datetime import datetime
import os
import sys
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.nicp_arbitrage_client import NICPArbitrageClient
from src.core.database import Database

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, database: Database):
        self.token = token
        self.database = database
        self.arbitrage_client = NICPArbitrageClient()
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with nICP discount focus"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Store user in database
        self.database.add_user(user_id, username)
        
        welcome_text = f"""
🚀 **Welcome to nICP Discount Tracker!**

💰 **What is nICP?**
nICP is staked ICP that unlocks after 6 months. When nICP trades below ICP price, it creates a discount opportunity!

🎯 **Key Commands:**
• `/start` - Show this welcome message
• `/help` - Show all commands and features
• `/discount` - Check current discount opportunities
• `/status` - Bot health and API status

🔥 **Coming Soon:**
• Price alerts when discounts exceed thresholds
• Historical discount tracking
• More discount opportunities across ICP ecosystem!

Ready to find nICP discounts? Try `/discount` to see live data! 🚀
"""
        
        keyboard = [
            [InlineKeyboardButton("🎯 Check Discounts", callback_data="discount")],
            [InlineKeyboardButton("📚 Learn More", callback_data="explain")],
            [InlineKeyboardButton("🧮 Calculator", callback_data="calculator")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def show_discount_opportunities(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current nICP discount opportunities with clear comparison"""
        try:
            logger.info("💰 User requested discount opportunities")
            
            # Send initial "fetching" message
            loading_msg = await update.message.reply_text(
                "🔍 **Analyzing nICP discount opportunities...**\n"
                "📊 Checking live prices across DEXes\n"
                "🌊 Fetching WaterNeuron exchange rates\n"
                "⏳ Please wait a moment...",
                parse_mode='Markdown'
            )
            
            # Get arbitrage data
            arbitrage_data = await self.arbitrage_client.get_nicp_arbitrage_data()
            
            if not arbitrage_data or not arbitrage_data.get('opportunities'):
                await loading_msg.edit_text(
                    "❌ **No Data Available**\n\n"
                    "Could not fetch nICP price data from DEXes.\n"
                    "Please try again in a few minutes.\n\n"
                    "💡 Use /status to check API health.",
                    parse_mode='Markdown'
                )
                return
            
            # Build comprehensive message
            message_parts = []
            
            # Header with WaterNeuron status
            waterneuron_data = arbitrage_data.get('waterneuron_data')
            if waterneuron_data and waterneuron_data.get('success'):
                wn_status = "✅ Live WaterNeuron data"
                exchange_rate = waterneuron_data.get('nicp_to_icp_rate', 0.9001)
            else:
                wn_status = "⚠️ Using fallback rates"
                exchange_rate = 0.9001
            
            message_parts.append(f"🎯 **nICP Discount Opportunities**")
            message_parts.append(f"🌊 {wn_status}")
            message_parts.append(f"📅 Current exchange rate: 1 ICP = {exchange_rate:.4f} nICP")
            message_parts.append("")
            
            # Show direct staking option first for comparison
            message_parts.append("🏛️ **Direct WaterNeuron Staking**")
            message_parts.append(f"• Exchange: 1,000 ICP → {1000 * exchange_rate:.1f} nICP")
            message_parts.append(f"• After 6 months: {1000 * exchange_rate:.1f} nICP → {1000:.1f} ICP")
            # Direct staking gives you the same ICP back after 6 months, so 0% profit
            # But we should show the comparison properly
            message_parts.append(f"• **Result: Break-even (0% profit, 0% APY)**")
            message_parts.append("• ⏱️ 6-month lockup period")
            message_parts.append("• 💡 This is the baseline to compare against")
            message_parts.append("")
            
            # Show DEX opportunities
            opportunities = arbitrage_data.get('opportunities', [])
            viable_opportunities = [opp for opp in opportunities if opp.get('arbitrage', {}).get('viable', False)]
            
            if viable_opportunities:
                message_parts.append("🚀 **DEX Discount Opportunities**")
                message_parts.append("*(Better than direct staking!)*")
                message_parts.append("")
                
                # Sort by profit percentage
                viable_opportunities.sort(key=lambda x: x['arbitrage']['profit_percentage_6m'], reverse=True)
                
                for i, opp in enumerate(viable_opportunities, 1):
                    dex_name = opp.get('dex', 'Unknown')
                    price = opp.get('nicp_price_in_icp', 0)
                    arbitrage = opp.get('arbitrage', {})
                    
                    # Safety check for valid price
                    if price <= 0:
                        logger.warning(f"Invalid price for {dex_name}: {price}")
                        continue
                    
                    profit_6m = arbitrage.get('profit_percentage_6m', 0)
                    apy = arbitrage.get('annualized_return', 0)
                    
                    # Calculate example with 1000 ICP - with safety checks
                    try:
                        nicp_bought = 1000 / price
                        future_icp = nicp_bought / exchange_rate if exchange_rate > 0 else nicp_bought
                        profit_icp = future_icp - 1000
                    except (ZeroDivisionError, TypeError) as e:
                        logger.error(f"Error calculating profits for {dex_name}: {e}")
                        continue
                    
                    # Determine emoji based on profit level
                    if profit_6m >= 20:
                        emoji = "🚀"
                    elif profit_6m >= 15:
                        emoji = "🔥"
                    elif profit_6m >= 10:
                        emoji = "✅"
                    else:
                        emoji = "💡"
                    
                    message_parts.append(f"{emoji} **#{i}. {dex_name}**")
                    message_parts.append(f"• Price: {price:.6f} ICP per nICP")
                    message_parts.append(f"• Exchange: 1,000 ICP → {nicp_bought:.1f} nICP")
                    message_parts.append(f"• After 6 months: {nicp_bought:.1f} nICP → {future_icp:.1f} ICP")
                    message_parts.append(f"• **Profit: {profit_icp:.1f} ICP ({profit_6m:.1f}% / {apy:.1f}% APY)**")
                    
                    # Compare to direct staking
                    extra_profit = profit_icp - 0
                    if extra_profit > 0:
                        message_parts.append(f"• 💰 **+{extra_profit:.1f} ICP more than direct staking!**")
                    
                    message_parts.append("")
                
                # Summary
                best_opp = viable_opportunities[0]
                best_profit = best_opp['arbitrage']['profit_percentage_6m']
                best_dex = best_opp.get('dex', 'Unknown')
                
                message_parts.append("📊 **Summary**")
                message_parts.append(f"• {len(viable_opportunities)} discount opportunities found")
                message_parts.append(f"• Best: {best_dex} with {best_profit:.1f}% profit")
                message_parts.append(f"• All opportunities beat direct staking!")
                
            else:
                message_parts.append("❌ **No DEX Discounts Available**")
                message_parts.append("Currently, nICP is trading at or above fair value on DEXes.")
                message_parts.append("")
                message_parts.append("💡 **Recommendation:** Consider direct WaterNeuron staking")
                message_parts.append("or wait for better DEX prices.")
            
            message_parts.append("")
            message_parts.append("⚠️ **Important Notes:**")
            message_parts.append("• 6-month lockup period for all options")
            message_parts.append("• Prices change constantly - act quickly!")
            message_parts.append("• Consider gas fees and slippage")
            message_parts.append("• This is not financial advice")
            
            message_parts.append("")
            message_parts.append("🔄 Use /discount for updated prices")
            message_parts.append("📈 Use /status for system health")
            
            # Send the complete message
            full_message = "\n".join(message_parts)
            
            # Split if too long (Telegram limit ~4096 chars)
            if len(full_message) > 4000:
                # Send in parts
                parts = self._split_long_message(message_parts)
                await loading_msg.edit_text(parts[0], parse_mode='Markdown')
                for part in parts[1:]:
                    await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await loading_msg.edit_text(full_message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error showing discount opportunities: {e}")
            error_msg = (
                "❌ **Error fetching discount data**\n\n"
                f"Technical details: {str(e)}\n\n"
                "Please try again in a few minutes or use /status to check system health."
            )
            
            try:
                await loading_msg.edit_text(error_msg, parse_mode='Markdown')
            except:
                await update.message.reply_text(error_msg, parse_mode='Markdown')

    def _split_long_message(self, message_parts: List[str]) -> List[str]:
        """Split a long message into multiple parts for Telegram"""
        parts = []
        current_part = []
        current_length = 0
        
        for line in message_parts:
            line_length = len(line) + 1  # +1 for newline
            
            if current_length + line_length > 4000:
                # Start a new part
                if current_part:
                    parts.append("\n".join(current_part))
                current_part = [line]
                current_length = line_length
            else:
                current_part.append(line)
                current_length += line_length
        
        # Add the last part
        if current_part:
            parts.append("\n".join(current_part))
        
        return parts

    async def explain_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Explain nICP discount in detail"""
        explanation = """
📚 **nICP Discount Explained**

🔵 **What is nICP?**
• nICP = "neuron ICP" - staked ICP tokens
• When you stake ICP, you get nICP tokens
• nICP can be dissolved back to ICP after 6 months
• Direct staking rate: 1 ICP = 0.9001103 nICP

💰 **The Discount Opportunity:**

**DEX Discount:**
• Buy 1 nICP on DEX for ~0.979 ICP
• Immediately unstake → Start 6-month dissolution
• After 6 months: Get 1.111 ICP
• Net result: 13.5% gain in 6 months!

🎯 **Why Does This Work?**
• DEX prices aren't always efficient
• Many don't understand nICP mechanics
• Low liquidity creates pricing gaps
• You're providing liquidity to earn returns

⚠️ **Important Considerations:**
• **6-month lock-up:** Your ICP is locked during dissolution
• **ICP price risk:** ICP value may fluctuate during 6 months
• **Liquidity risk:** nICP pairs may have low volume
• **Opportunity cost:** Could ICP gain more than discount profit?

🚀 **Getting Started:**
1. Have ICP in a wallet (Plug, Stoic, etc.)
2. Go to KongSwap or ICPSwap
3. Buy nICP with ICP at current market rate
4. Use NNS app to start dissolution process
5. Wait 6 months and collect profits!

💡 **Pro Tips:**
• Monitor this bot for best opportunities
• Consider dollar-cost averaging into positions
• Don't invest more than you can lock up for 6 months
• Keep some ICP liquid for other opportunities

Ready to check current opportunities? Use `/discount`! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Check Current Opportunity", callback_data="discount")],
            [InlineKeyboardButton("🧮 Profit Calculator", callback_data="calculator")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            explanation,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def calculator_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Interactive profit calculator"""
        calculator_msg = """
🧮 **nICP Discount Calculator**

💰 **Example Calculations:**

**Investment: 100 ICP**
• Buy nICP at 0.979 ICP each
• Get: 102.14 nICP tokens
• After 6 months: 113.47 ICP
• **Profit: 13.47 ICP (13.5%)**

**Investment: 1,000 ICP**
• Buy nICP at 0.979 ICP each
• Get: 1,021.4 nICP tokens
• After 6 months: 1,134.7 ICP
• **Profit: 134.7 ICP (13.5%)**

**Investment: 10,000 ICP**
• Buy nICP at 0.979 ICP each
• Get: 10,214 nICP tokens
• After 6 months: 11,347 ICP
• **Profit: 1,347 ICP (13.5%)**

📊 **Key Metrics:**
• Current nICP price: ~0.979 ICP
• Dissolution value: 1.111 ICP per nICP
• Profit per nICP: 0.132 ICP (13.5%)
• Annualized return: ~27% APY
• Lock-up period: 6 months

💡 **Custom Calculation:**
Profit = (Investment ÷ nICP_Price) × (1.111 - nICP_Price)

Want to see live opportunities? Use `/discount`! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Live Opportunities", callback_data="discount")],
            [InlineKeyboardButton("📚 Learn More", callback_data="explain")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            calculator_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = f"""
🤖 **nICP Discount Tracker - Commands**

📊 **Main Commands:**
• `/start` - Welcome message and overview
• `/discount` - Check current discount opportunities  
• `/status` - Bot and API health status
• `/help` - Show this help message

🔍 **What This Bot Does:**
• Monitors nICP prices across DEXes
• Calculates real-time discount opportunities
• Shows potential profits and APY
• Tracks WaterNeuron exchange rates

💰 **Features:**
• Live price data from ICPSwap & KongSwap
• More discount opportunities across ICP ecosystem
• Real-time discount calculations
• 6-month APY projections

💡 **Pro Tips:**
• Check `/discount` regularly for best opportunities
• Consider the 6-month lock-up period
• Factor in market volatility risks

Ready to explore nICP discounts? Use `/discount` to see current opportunities! 🚀
"""
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "discount":
            # Create a fake update object for the discount command
            fake_update = type('obj', (object,), {'message': query.message})()
            await self.show_discount_opportunities(fake_update, context)
        elif query.data == "explain":
            await self.explain_command_callback(query)
        elif query.data == "calculator":
            await self.calculator_command_callback(query)

    async def discount_command_callback(self, query):
        """Handle discount button callback"""
        await query.edit_message_text("🔍 Checking nICP discount opportunities...")
        
        try:
            # Use async method with WaterNeuron integration
            arbitrage_data = await self.arbitrage_client.get_nicp_data()
            
            if not arbitrage_data.get('opportunities'):
                await query.edit_message_text("❌ No nICP discount opportunities found at the moment. Try again later!")
                return
            
            # Build response
            timestamp = datetime.now().strftime("%H:%M:%S")
            waterneuron_status = arbitrage_data.get('waterneuron_status', '❌ Offline')
            best = arbitrage_data.get('best_opportunity')
            
            header = [
                "🎯 **nICP Discount Tracker**",
                f"🕐 Last updated: {timestamp}",
                f"🌊 WaterNeuron: {waterneuron_status}",
                "",
                f"💰 **Best Discount: {best['arbitrage']['profit_percentage_6m']:.1f}%** ({best['exchange']})" if best else "💰 **No viable discounts found**",
                "",
                "📊 **Available Discounts:**"
            ]
            
            response_parts = header
            
            # Add all opportunities
            response_parts.append("📋 **All Opportunities:**")
            for opp in arbitrage_data['opportunities']:
                arb = opp['arbitrage']
                status = "✅" if arb['viable'] else "❌"
                response_parts.append(
                    f"{status} **{opp['dex']}:** {arb['profit_percentage_6m']:.1f}% profit "
                    f"(${opp.get('volume_24h_usd', 0):,.0f} vol)"
                )
            
            response_parts.extend([
                "",
                "💡 **How it works:**",
                "1. Buy nICP at discount price on DEX",
                "2. Dissolve nICP → Get full ICP value",
                "3. Wait 6 months for unlock",
                "4. Profit from the discount!",
                "",
                "⚠️ **Risks:** 6-month lock-up, market volatility, protocol risk"
            ])
            
            # Calculate potential profit for different amounts
            profit_examples = []
            for amount in [100, 500, 1000, 5000]:
                profit_icp = (amount * best['arbitrage']['profit_percentage_6m']) / 100
                profit_examples.append(f"• {amount:,} ICP → **+{profit_icp:.0f} ICP** profit")
            
            examples_text = "\n".join(profit_examples)
            
            explanation = f"""
💰 **The Discount Opportunity:**

{examples_text}

⏰ **Timeline:** 6-month lock-up period
📈 **APY:** {best['arbitrage']['annualized_return']:.1f}% annualized return

💡 **How it works:**
1. Buy nICP at discount price on DEX
2. Dissolve nICP → Get full ICP value  
3. Wait 6 months for unlock
4. Profit from the discount!

⚠️ **Risks:** 6-month lock-up, market volatility, protocol risk
"""
            
            response_parts.append(explanation)
            
            # Create action buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="discount")],
                [InlineKeyboardButton("🧮 Calculator", callback_data="calculator")],
                [InlineKeyboardButton("📚 Learn More", callback_data="explain")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "\n".join(response_parts),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in discount callback: {e}")
            await query.edit_message_text("❌ Error fetching data. Please try again.")

    async def explain_command_callback(self, query):
        """Handle explain button callback"""
        explanation = """
📚 **nICP Discount Quick Guide**

💰 **The Opportunity:**
• Buy nICP at discount price on DEX
• Unstake immediately (6-month dissolution)
• Receive 1.111 ICP after 6 months
• **Profit: ~13.5% in 6 months**

🎯 **Why It Works:**
• Direct staking: 1 ICP = 0.9001 nICP
• DEX trading: Often closer to 1:1 ratio
• Discount gap = Your profit opportunity

⚠️ **Key Risks:**
• 6-month lock-up period
• ICP price volatility
• Low liquidity on some DEXes

Ready to check live opportunities?
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Check Opportunities", callback_data="discount")],
            [InlineKeyboardButton("🧮 Calculator", callback_data="calculator")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            explanation,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def calculator_command_callback(self, query):
        """Handle calculator button callback"""
        calculator_msg = """
🧮 **Quick Profit Calculator**

**Your Investment → Profit:**
• 100 ICP → 13.5 ICP profit
• 500 ICP → 67.5 ICP profit  
• 1,000 ICP → 135 ICP profit
• 5,000 ICP → 675 ICP profit

📊 **Current Rate:**
• nICP price: ~0.979 ICP
• Profit per nICP: 0.132 ICP
• Return: 13.5% in 6 months
• Annualized: ~27% APY

💡 **Formula:**
Profit = Investment ÷ 0.979 × 0.132
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Live Data", callback_data="discount")],
            [InlineKeyboardButton("📚 Learn More", callback_data="explain")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            calculator_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def start_bot(self):
        """Start the Telegram bot"""
        logger.info("Starting nICP Discount Telegram bot...")
        
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("discount", self.show_discount_opportunities))
        self.application.add_handler(CommandHandler("explain", self.explain_command))
        self.application.add_handler(CommandHandler("calculator", self.calculator_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        await self.application.updater.idle()

    async def stop_bot(self):
        """Stop the Telegram bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown() 