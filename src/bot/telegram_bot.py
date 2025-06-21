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
        
        # Available trading pairs
        self.available_pairs = ['ICP/nICP', 'ICP/USD', 'ICP/USDT', 'ICP/USDC']
        
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
• ICP/nICP - ICP to Neuron ICP
• ICP/USD - ICP to US Dollar
• ICP/USDT - ICP to Tether
• ICP/USDC - ICP to USD Coin

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
                # Show specific pair
                if pair in price_data:
                    pair_info = price_data[pair]
                    price_change = self.db.get_price_change(pair, 24)
                    change_text = f"📈 +{price_change:.2f}%" if price_change and price_change > 0 else f"📉 {price_change:.2f}%" if price_change else "➡️ No change data"
                    
                    message = f"""
🪙 **{pair}** 
{self.api_client.format_price_data(pair_info)}
{change_text}
🕒 Last updated: {datetime.now().strftime('%H:%M:%S')}
                    """
                    await update.message.reply_text(message, parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"❌ Pair {pair} not found or not available.")
            else:
                # Show all available pairs
                message = "📊 **Current ICP Prices:**\n\n"
                for pair_name, pair_info in price_data.items():
                    price_change = self.db.get_price_change(pair_name, 24)
                    change_emoji = "📈" if price_change and price_change > 0 else "📉" if price_change and price_change < 0 else "➡️"
                    change_text = f"{price_change:+.2f}%" if price_change else "N/A"
                    
                    message += f"🪙 **{pair_name}**\n"
                    message += f"💰 ${pair_info['price']:.6f} {change_emoji} {change_text}\n\n"
                
                message += f"🕒 Last updated: {datetime.now().strftime('%H:%M:%S')}"
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
        if pair not in self.available_pairs:
            await update.message.reply_text(f"❌ Pair {pair} is not available. Available pairs: {', '.join(self.available_pairs)}")
            return
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        success = self.db.subscribe_user_to_pair(user_data['id'], pair)
        if success:
            await update.message.reply_text(f"✅ Successfully subscribed to {pair} updates!")
        else:
            await update.message.reply_text("❌ Error subscribing to pair. Please try again.")
    
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
        alert_type = context.args[1].lower()
        try:
            threshold = float(context.args[2])
        except ValueError:
            await update.message.reply_text("❌ Invalid threshold value. Please enter a number.")
            return
        
        if pair not in self.available_pairs:
            await update.message.reply_text(f"❌ Pair {pair} is not available. Available pairs: {', '.join(self.available_pairs)}")
            return
        
        if alert_type not in self.alert_types:
            await update.message.reply_text(f"❌ Invalid alert type. Available types: {', '.join(self.alert_types.keys())}")
            return
        
        user_data = self.db.get_user_by_telegram_id(user.id)
        if not user_data:
            await update.message.reply_text("❌ Please start the bot first using /start")
            return
        
        success = self.db.add_user_alert(user_data['id'], pair, alert_type, threshold)
        if success:
            alert_desc = self.alert_types[alert_type]
            await update.message.reply_text(
                f"✅ **Alert set successfully!**\n\n"
                f"🪙 **Pair:** {pair}\n"
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