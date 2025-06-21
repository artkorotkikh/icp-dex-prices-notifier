import logging
import os
from datetime import datetime
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from ..core import Database, APIClient

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, db: Database, api_client: APIClient):
        self.token = token
        self.db = db
        self.api_client = api_client
        self.application = None
        
        # Available trading pairs (dynamically updated from API)
        self.available_pairs = ['NICP/ICP', 'CKUSDT/ICP', 'CKUSDC/ICP']
        
        # Pair aliases for user-friendly input
        self.pair_aliases = {
            'ICP/NICP': 'NICP/ICP',
            'ICP/nICP': 'NICP/ICP', 
            'ICP/USDT': 'CKUSDT/ICP',
            'ICP/USDC': 'CKUSDC/ICP',
            'ICP/ckUSDT': 'ICP/ckUSDT',
            'ICP/ckUSDC': 'ckUSDC/ckUSDT',
            'NICP/ICP': 'NICP/ICP',
            'CKUSDT/ICP': 'CKUSDT/ICP',
            'CKUSDC/ICP': 'CKUSDC/ICP'
        }
        
        # Alert types
        self.alert_types = {
            'price_up': 'Price increase',
            'price_down': 'Price decrease',
            'volume_spike': 'Volume spike'
        }
    
    def setup_handlers(self):
        """Setup all command and callback handlers"""
        if not self.application:
            self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("price", self.price_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
        self.application.add_handler(CommandHandler("alerts", self.alerts_command))
        self.application.add_handler(CommandHandler("setalert", self.set_alert_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("referral", self.referral_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Telegram bot handlers setup complete")
    
    def update_available_pairs(self):
        """Update available pairs from API client"""
        try:
            price_data = self.api_client.get_icp_prices()
            if price_data:
                self.available_pairs = list(price_data.keys())
                logger.info(f"Updated available pairs: {len(self.available_pairs)} pairs")
        except Exception as e:
            logger.error(f"Error updating available pairs: {e}")

    def resolve_pair_name(self, user_input: str) -> str:
        """Resolve user input to actual pair name, preferring higher volume pairs"""
        user_input = user_input.upper().strip()
        
        # Update available pairs from API
        self.update_available_pairs()
        
        # Get current price data for volume comparison
        try:
            price_data = self.api_client.get_icp_prices()
        except:
            price_data = {}
        
        # Check if it's already a valid pair
        if user_input in self.available_pairs:
            return user_input
            
        # Check aliases
        if user_input in self.pair_aliases:
            return self.pair_aliases[user_input]
        
        # Smart resolution: find all matching pairs and prefer higher volume
        matching_pairs = []
        
        # Parse user input
        if '/' in user_input:
            user_parts = user_input.split('/')
            if len(user_parts) == 2:
                token1, token2 = user_parts
                
                # Look for exact matches and reverse matches
                for pair_name in self.available_pairs:
                    if '/' in pair_name:
                        pair_parts = pair_name.split('/')
                        if len(pair_parts) == 2:
                            p1, p2 = pair_parts
                            
                            # Normalize tokens for comparison
                            def normalize_token(token):
                                return token.replace('NICP', 'nICP').replace('CKUSDT', 'USDT').replace('CKUSDC', 'USDC')
                            
                            norm_user1, norm_user2 = normalize_token(token1), normalize_token(token2)
                            norm_p1, norm_p2 = normalize_token(p1), normalize_token(p2)
                            
                            # Check for matches (both directions)
                            if (norm_user1 == norm_p1 and norm_user2 == norm_p2) or \
                               (norm_user1 == norm_p2 and norm_user2 == norm_p1):
                                volume = price_data.get(pair_name, {}).get('volume_24h_usd', 0)
                                matching_pairs.append((pair_name, volume))
        
        # If we found matching pairs, return the one with highest volume
        if matching_pairs:
            matching_pairs.sort(key=lambda x: x[1], reverse=True)  # Sort by volume desc
            return matching_pairs[0][0]  # Return highest volume pair
        
        # Try some common variations
        variations = [
            user_input,
            user_input.replace('NICP', 'nICP'),
            user_input.replace('nICP', 'NICP'),
            user_input.replace('/', '_'),
            user_input.replace('_', '/'),
            user_input.replace('CK', 'ck'),
            user_input.replace('ck', 'CK'),
            user_input.replace('USDT', 'ckUSDT'),
            user_input.replace('USDC', 'ckUSDC')
        ]
        
        for variation in variations:
            if variation in self.pair_aliases:
                return self.pair_aliases[variation]
            if variation in self.available_pairs:
                return variation
                
        return user_input  # Return original if no match found
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        user_id = self.db.add_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        if user_id:
            # Get user stats for referral code
            user_data = self.db.get_user_by_telegram_id(user.id)
            referral_code = user_data.get('referral_code', '') if user_data else ''
            
            welcome_message = f"""
🚀 **Welcome to ICP Token Monitor!** 🚀

Hi {user.first_name}! I'm your personal ICP price monitoring assistant.

**🎯 What I can do:**
• 📊 Real-time price updates for ICP pairs
• ⚡ Custom price alerts
• 📈 24h price changes and volume data
• 🔔 Subscribe to your favorite pairs
• 📱 Community features and referrals

**🎮 Your Referral Code:** `{referral_code}`
Share this code with friends to earn rewards!

**🚀 Quick Start:**
1. Use /price to check current prices
2. Use /subscribe ICP/nICP to get updates
3. Use /setalert to set price alerts

Type /help for all commands or choose an option below:
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 Check Prices", callback_data="quick_prices")],
                [InlineKeyboardButton("🔔 Subscribe to Pairs", callback_data="quick_subscribe")],
                [InlineKeyboardButton("⚡ Set Alert", callback_data="quick_alert")],
                [InlineKeyboardButton("📱 Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Error setting up your account. Please try again.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **ICP Token Monitor - Commands** 🤖

**📊 Price Commands:**
• `/price [pair]` - Get current price (e.g., /price ICP/nICP)
• `/subscribe [pair]` - Subscribe to pair updates
• `/unsubscribe [pair]` - Unsubscribe from pair

**⚡ Alert Commands:**
• `/setalert [pair] [type] [threshold]` - Set price alert
• `/alerts` - View your active alerts
• `/portfolio` - View your subscriptions

**👥 Community Commands:**
• `/referral` - Get your referral link
• `/stats` - View your account stats

**🔧 System Commands:**
• `/status` - Check bot status
• `/help` - Show this help message

**📈 Available Pairs:**
• NICP/ICP - Neuron ICP to ICP (liquid staking)
• CKUSDT/ICP - Chain Key USDT to ICP 
• CKUSDC/ICP - Chain Key USDC to ICP

**🔄 You can also use these formats:**
• ICP/nICP → NICP/ICP
• ICP/USDT → CKUSDT/ICP  
• ICP/USDC → CKUSDC/ICP

**⚡ Alert Types:**
• `price_up` - Price increase alert
• `price_down` - Price decrease alert
• `volume_spike` - Volume spike alert

**💡 Examples:**
• `/price ICP/nICP` - Get ICP/nICP price
• `/subscribe ICP/USD` - Subscribe to ICP/USD updates
• `/setalert ICP/nICP price_up 5` - Alert when ICP/nICP rises 5%

Need help? Contact @your_support_username
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        # Get specific pair if provided
        pair = None
        if context.args:
            pair = context.args[0].upper()
            if '/' not in pair:
                await update.message.reply_text("❌ Invalid pair format. Use format like: ICP/nICP")
                return
        
        try:
            await update.message.reply_text("📊 Fetching current prices...")
            
            # Get price data
            price_data = self.api_client.get_icp_prices()
            
            if not price_data:
                await update.message.reply_text("❌ Unable to fetch price data. Please try again later.")
                return
            
            if pair:
                # Find all matching pairs (not just the highest volume one)
                matching_pairs = []
                
                if '/' in pair:
                    user_parts = pair.split('/')
                    if len(user_parts) == 2:
                        token1, token2 = user_parts
                        
                        # Look for exact matches and reverse matches
                        for pair_name in price_data.keys():
                            if '/' in pair_name:
                                pair_parts = pair_name.split('/')
                                if len(pair_parts) == 2:
                                    p1, p2 = pair_parts
                                    
                                    # Normalize tokens for comparison
                                    def normalize_token(token):
                                        return token.replace('NICP', 'nICP').replace('CKUSDT', 'USDT').replace('CKUSDC', 'USDC')
                                    
                                    norm_user1, norm_user2 = normalize_token(token1), normalize_token(token2)
                                    norm_p1, norm_p2 = normalize_token(p1), normalize_token(p2)
                                    
                                    # Check for matches (both directions)
                                    if (norm_user1 == norm_p1 and norm_user2 == norm_p2) or \
                                       (norm_user1 == norm_p2 and norm_user2 == norm_p1):
                                        volume = price_data.get(pair_name, {}).get('volume_24h_usd', 0)
                                        matching_pairs.append((pair_name, volume))
                
                # If no matches found, try direct lookup
                if not matching_pairs:
                    resolved_pair = self.resolve_pair_name(pair)
                    if resolved_pair in price_data:
                        volume = price_data.get(resolved_pair, {}).get('volume_24h_usd', 0)
                        matching_pairs.append((resolved_pair, volume))
                
                if matching_pairs:
                    # Sort by volume (highest first)
                    matching_pairs.sort(key=lambda x: x[1], reverse=True)
                    
                    if len(matching_pairs) == 1:
                        # Single match - show detailed info
                        pair_name = matching_pairs[0][0]
                        pair_info = price_data[pair_name]
                        price_change = self.db.get_price_change(pair_name, 24)
                        change_text = f"📈 +{price_change:.2f}%" if price_change and price_change > 0 else f"📉 {price_change:.2f}%" if price_change else "➡️ No change data"
                        
                        # Get source info
                        source = pair_info.get('source', 'unknown').title()
                        source_emoji = "🏪" if source.lower() == 'icpswap' else "🦍" if source.lower() == 'kongswap' else "📡"
                        
                        message = f"""
🪙 **{pair_name}** 

{self.api_client.format_price_data(pair_info)}
📈 **24h Change:** {change_text}
{source_emoji} **Source:** {source}
🕒 **Last updated:** {datetime.now().strftime('%H:%M:%S')}
                        """
                        await update.message.reply_text(message, parse_mode='Markdown')
                    else:
                        # Multiple matches - show comparison
                        message = f"🪙 **{pair}** - Found {len(matching_pairs)} matches:\n\n"
                        
                        for i, (pair_name, volume) in enumerate(matching_pairs[:3], 1):  # Show top 3
                            pair_info = price_data[pair_name]
                            source = pair_info.get('source', 'unknown').lower()
                            source_emoji = "🏪" if source == "icpswap" else "🦍" if source == "kongswap" else "📡"
                            source_name = source.title()
                            
                            price = pair_info.get('price', 0)
                            volume_24h = pair_info.get('volume_24h_usd', 0)
                            
                            # Format volume nicely
                            if volume_24h >= 1000000:
                                volume_str = f"${volume_24h/1000000:.1f}M"
                            elif volume_24h >= 1000:
                                volume_str = f"${volume_24h/1000:.1f}K"
                            else:
                                volume_str = f"${volume_24h:.0f}"
                            
                            message += f"**{i}. {pair_name}** {source_emoji}\n"
                            message += f"   💰 ${price:.6f}\n"
                            message += f"   📊 {volume_str} volume\n"
                            message += f"   🔗 {source_name}\n\n"
                        
                        message += f"🕒 **Last updated:** {datetime.now().strftime('%H:%M:%S')}"
                        await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    # Show available pairs in error message
                    available_list = "\n".join([f"• {p}" for p in self.available_pairs])
                    user_friendly_list = "\n".join([f"• {alias} (→ {actual})" for alias, actual in self.pair_aliases.items() if alias != actual])
                    
                    await update.message.reply_text(
                        f"❌ Pair '{pair}' not found.\n\n"
                        f"**Available pairs:**\n{available_list}\n\n"
                        f"**You can also use:**\n{user_friendly_list}",
                        parse_mode='Markdown'
                    )
            else:
                # Show all available pairs (limit to top 10 by volume for readability)
                sorted_pairs = sorted(price_data.items(), key=lambda x: x[1].get('volume_24h_usd', 0), reverse=True)
                top_pairs = sorted_pairs[:10]
                
                message = "📊 **Top 10 ICP Pairs by Volume:**\n\n"
                
                for i, (pair_name, pair_info) in enumerate(top_pairs, 1):
                    price_change = self.db.get_price_change(pair_name, 24)
                    change_emoji = "📈" if price_change and price_change > 0 else "📉" if price_change and price_change < 0 else "➡️"
                    change_text = f"{price_change:+.2f}%" if price_change else "N/A"
                    
                    # Format volume nicely
                    volume_usd = pair_info.get('volume_24h_usd', 0)
                    if volume_usd >= 1000000:
                        volume_str = f"${volume_usd/1000000:.1f}M"
                    elif volume_usd >= 1000:
                        volume_str = f"${volume_usd/1000:.1f}K"
                    else:
                        volume_str = f"${volume_usd:.0f}"
                    
                    # Get source emoji
                    source = pair_info.get('source', 'unknown').lower()
                    source_emoji = "🏪" if source == 'icpswap' else "🦍" if source == 'kongswap' else "📡"
                    
                    message += f"{i:2d}. **{pair_name}** {source_emoji}\n"
                    message += f"    💰 ${pair_info['price']:.6f} {change_emoji} {change_text}\n"
                    message += f"    📊 Vol: {volume_str} | 💧 Liq: ${pair_info.get('liquidity_usd', 0)/1000:.0f}K\n\n"
                
                # Count sources
                icpswap_count = sum(1 for _, p in price_data.items() if p.get('source', '').lower() == 'icpswap')
                kongswap_count = sum(1 for _, p in price_data.items() if p.get('source', '').lower() == 'kongswap')
                
                message += f"🕒 **Last updated:** {datetime.now().strftime('%H:%M:%S')}\n"
                message += f"📊 **Total pairs:** {len(price_data)} (🏪 {icpswap_count} ICPSwap, 🦍 {kongswap_count} KongSwap)\n"
                message += f"💡 *Use `/price [pair]` for detailed info*"
                await update.message.reply_text(message, parse_mode='Markdown')
        
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text("❌ Error fetching price data. Please try again.")
    
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        if not context.args:
            # Show available pairs
            keyboard = []
            for pair in self.available_pairs:
                keyboard.append([InlineKeyboardButton(f"Subscribe to {pair}", callback_data=f"sub_{pair}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🔔 **Choose a pair to subscribe to:**\n\nYou'll receive updates when significant price movements occur.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        pair = context.args[0].upper()
        resolved_pair = self.resolve_pair_name(pair)
        
        if resolved_pair not in self.available_pairs:
            await update.message.reply_text(f"❌ Pair '{pair}' is not available. Available pairs: {', '.join(self.available_pairs)}")
            return
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        success = self.db.subscribe_user_to_pair(user_data['id'], resolved_pair)
        if success:
            display_name = pair if pair != resolved_pair else resolved_pair
            await update.message.reply_text(f"✅ Successfully subscribed to {display_name} updates!")
        else:
            await update.message.reply_text("❌ Error subscribing to pair. Please try again.")
    
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        if not context.args:
            await update.message.reply_text(
                "❌ **Please specify a pair to unsubscribe from!**\n\n"
                "**Usage:** `/unsubscribe [pair]`\n\n"
                "**Example:** `/unsubscribe ICP/nICP`\n\n"
                "**Available pairs:** " + ", ".join(self.available_pairs),
                parse_mode='Markdown'
            )
            return
        
        pair = context.args[0].upper()
        
        if pair not in self.available_pairs:
            await update.message.reply_text(f"❌ Pair {pair} is not available. Available pairs: {', '.join(self.available_pairs)}")
            return
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        success = self.db.remove_user_subscription(user_data['id'], pair)
        if success:
            await update.message.reply_text(
                f"✅ **Successfully unsubscribed!**\n\n"
                f"🪙 You will no longer receive updates for **{pair}**\n\n"
                f"💡 Use `/subscribe {pair}` to re-subscribe anytime!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Error unsubscribing. You might not be subscribed to this pair.")
    
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        alerts = self.db.get_user_alerts(user_data['id'])
        
        if not alerts:
            message = """
⚡ **No Active Alerts**

You don't have any price alerts set up yet.

**💡 Set your first alert:**
`/setalert ICP/nICP price_up 5`

This will notify you when ICP/nICP price increases by 5%!
            """
        else:
            message = "⚡ **Your Active Alerts**\n\n"
            for i, alert in enumerate(alerts, 1):
                alert_desc = self.alert_types.get(alert['alert_type'], alert['alert_type'])
                status = "🟢 Active" if alert.get('is_active', True) else "🔴 Inactive"
                message += f"**{i}.** {alert['pair']}\n"
                message += f"   📊 {alert_desc} ({alert['threshold']}%)\n"
                message += f"   {status}\n\n"
            
            message += "💡 Use `/setalert` to add more alerts!"
        
        await update.message.reply_text(message, parse_mode='Markdown')

    async def set_alert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setalert command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "❌ **Invalid format!**\n\n"
                "**Usage:** `/setalert [pair] [type] [threshold]`\n\n"
                "**Example:** `/setalert ICP/nICP price_up 5`\n"
                "This sets an alert when ICP/nICP price increases by 5%\n\n"
                "**Alert types:** price_up, price_down, volume_spike",
                parse_mode='Markdown'
            )
            return
        
        pair = context.args[0].upper()
        resolved_pair = self.resolve_pair_name(pair)
        alert_type = context.args[1].lower()
        try:
            threshold = float(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Invalid threshold value. Please enter a number.")
            return
        
        if resolved_pair not in self.available_pairs:
            await update.message.reply_text(f"❌ Pair '{pair}' is not available. Available pairs: {', '.join(self.available_pairs)}")
            return
        
        if alert_type not in self.alert_types:
            await update.message.reply_text(f"❌ Invalid alert type. Available types: {', '.join(self.alert_types.keys())}")
            return
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        success = self.db.add_user_alert(user_data['id'], resolved_pair, alert_type, threshold)
        if success:
            alert_desc = self.alert_types[alert_type]
            display_name = pair if pair != resolved_pair else resolved_pair
            await update.message.reply_text(
                f"✅ **Alert set successfully!**\n\n"
                f"🪙 **Pair:** {display_name}\n"
                f"⚡ **Type:** {alert_desc}\n"
                f"📊 **Threshold:** {threshold}%\n\n"
                f"You'll be notified when this condition is met!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("❌ Error setting alert. Please try again.")
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        subscriptions = self.db.get_user_subscriptions(user_data['id'])
        alerts = self.db.get_user_alerts(user_data['id'])
        
        message = "📱 **Your Portfolio**\n\n"
        
        if subscriptions:
            message += "🔔 **Active Subscriptions:**\n"
            for pair in subscriptions:
                message += f"• {pair}\n"
            message += "\n"
        else:
            message += "🔔 **No active subscriptions**\n\n"
        
        if alerts:
            message += "⚡ **Active Alerts:**\n"
            for alert in alerts:
                alert_desc = self.alert_types.get(alert['alert_type'], alert['alert_type'])
                message += f"• {alert['pair']} - {alert_desc} ({alert['threshold']}%)\n"
            message += "\n"
        else:
            message += "⚡ **No active alerts**\n\n"
        
        message += "💡 Use /subscribe or /setalert to add more!"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /referral command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        stats = self.db.get_user_stats(user_data['id'])
        referral_count = stats.get('referrals', 0)
        referral_code = user_data.get('referral_code', '')
        
        message = f"""
👥 **Your Referral Program**

🎯 **Your Code:** `{referral_code}`
👥 **Referrals:** {referral_count}

**🎁 Referral Benefits:**
• 5+ referrals: Priority alerts ⚡
• 15+ referrals: Custom features 🎛️
• 50+ referrals: Premium access 👑

**📤 Share your link:**
`https://t.me/your_bot_username?start={referral_code}`

Earn rewards by inviting friends to monitor ICP prices!
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        stats = self.db.get_user_stats(user_data['id'])
        
        message = f"""
📊 **Your Statistics**

👤 **Account:** {user_data.get('username', 'N/A')}
📅 **Member since:** {user_data.get('created_at', 'Unknown')[:10]}
🔔 **Subscriptions:** {stats.get('subscriptions', 0)}
⚡ **Active alerts:** {stats.get('alerts', 0)}
👥 **Referrals:** {stats.get('referrals', 0)}

Keep monitoring and growing! 🚀
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        health_status = self.api_client.health_check()
        
        message = "🔧 **Bot Status**\n\n"
        message += f"🤖 **Bot:** ✅ Online\n"
        message += f"🔄 **ICPSwap API:** {'✅ Connected' if health_status.get('icpswap') else '❌ Disconnected'}\n"
        message += f"🔄 **KongSwap API:** {'✅ Connected' if health_status.get('kongswap') else '❌ Disconnected'}\n"
        message += f"💾 **Database:** ✅ Connected\n"
        message += f"🕒 **Last check:** {datetime.now().strftime('%H:%M:%S')}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "quick_prices":
            await self.price_command(update, context)
        elif data == "quick_subscribe":
            await self.subscribe_command(update, context)
        elif data == "quick_alert":
            await query.edit_message_text(
                "⚡ **Set an Alert**\n\n"
                "Use this format:\n"
                "`/setalert [pair] [type] [threshold]`\n\n"
                "**Example:**\n"
                "`/setalert ICP/nICP price_up 5`\n\n"
                "**Available pairs:** ICP/nICP, ICP/USD\n"
                "**Alert types:** price_up, price_down, volume_spike",
                parse_mode='Markdown'
            )
        elif data == "help":
            await self.help_command(update, context)
        elif data.startswith("sub_"):
            pair = data[4:]  # Remove "sub_" prefix
            context.args = [pair]
            await self.subscribe_command(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        user = update.effective_user
        self.db.update_user_activity(user.id)
        
        text = update.message.text.lower()
        
        # Simple keyword responses
        if 'price' in text and 'icp' in text:
            await self.price_command(update, context)
        elif 'help' in text:
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 I didn't understand that. Try /help for available commands or use the buttons below!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Prices", callback_data="quick_prices")],
                    [InlineKeyboardButton("📱 Help", callback_data="help")]
                ])
            )
    
    async def send_alert_to_user(self, telegram_id: int, message: str):
        """Send alert message to a specific user"""
        try:
            await self.application.bot.send_message(chat_id=telegram_id, text=message, parse_mode='Markdown')
            return True
        except Exception as e:
            logger.error(f"Failed to send alert to user {telegram_id}: {e}")
            return False
    
    async def send_channel_update(self, channel_id: str, message: str):
        """Send update to channel"""
        try:
            await self.application.bot.send_message(chat_id=channel_id, text=message, parse_mode='Markdown')
            return True
        except Exception as e:
            logger.error(f"Failed to send channel update: {e}")
            return False
    
    def run(self):
        """Start the bot"""
        if not self.application:
            self.setup_handlers()
        
        logger.info("Starting Telegram bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES) 