import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .database import Database
from .api_client import APIClient

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self, db: Database, api_client: APIClient, telegram_bot=None):
        self.db = db
        self.api_client = api_client
        self.telegram_bot = telegram_bot
        
        # Alert cooldown to prevent spam
        self.alert_cooldown = 300  # 5 minutes in seconds
        self.last_alerts = {}  # Track last alert time per user/pair
        
        # Price change thresholds
        self.default_thresholds = {
            'price_up': 5.0,    # 5% increase
            'price_down': 5.0,  # 5% decrease
            'volume_spike': 50.0  # 50% volume increase
        }
    
    async def check_all_alerts(self):
        """Check all active alerts and trigger notifications"""
        try:
            logger.info("Checking all active alerts...")
            
            # Get current price data
            current_prices = self.api_client.get_icp_prices()
            if not current_prices:
                logger.warning("No price data available for alert checking")
                return
            
            # Get all active alerts
            active_alerts = self.db.get_all_active_alerts()
            logger.info(f"Processing {len(active_alerts)} active alerts")
            
            for alert in active_alerts:
                await self.process_alert(alert, current_prices)
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def process_alert(self, alert: Dict, current_prices: Dict[str, Dict]):
        """Process individual alert"""
        try:
            pair = alert['pair']
            alert_type = alert['alert_type']
            threshold = alert['threshold']
            user_id = alert['user_id']
            telegram_id = alert['telegram_id']
            alert_id = alert['id']
            
            # Check if we have current price data for this pair
            if pair not in current_prices:
                logger.debug(f"No current price data for pair {pair}")
                return
            
            current_price_data = current_prices[pair]
            current_price = current_price_data['price']
            
            # Check cooldown
            cooldown_key = f"{user_id}_{pair}_{alert_type}"
            if self.is_in_cooldown(cooldown_key):
                return
            
            # Get historical data for comparison
            price_change_24h = self.db.get_price_change(pair, 24)
            
            # Check if alert condition is met
            should_trigger = False
            alert_message = ""
            
            if alert_type == 'price_up':
                if price_change_24h and price_change_24h >= threshold:
                    should_trigger = True
                    alert_message = self.create_price_up_message(pair, current_price, price_change_24h, threshold)
            
            elif alert_type == 'price_down':
                if price_change_24h and price_change_24h <= -threshold:
                    should_trigger = True
                    alert_message = self.create_price_down_message(pair, current_price, price_change_24h, threshold)
            
            elif alert_type == 'volume_spike':
                volume_change = await self.calculate_volume_change(pair)
                if volume_change and volume_change >= threshold:
                    should_trigger = True
                    alert_message = self.create_volume_spike_message(pair, current_price, volume_change, threshold)
            
            # Trigger alert if conditions are met
            if should_trigger and alert_message:
                await self.trigger_alert(alert_id, telegram_id, user_id, pair, alert_message, current_price, price_change_24h)
                self.set_cooldown(cooldown_key)
                logger.info(f"Alert triggered for user {telegram_id}, pair {pair}, type {alert_type}")
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    def create_price_up_message(self, pair: str, current_price: float, price_change: float, threshold: float) -> str:
        """Create price increase alert message"""
        return f"""
🚀 **PRICE ALERT: {pair}** 🚀

📈 **Price is UP {price_change:+.2f}%!**
💰 Current Price: ${current_price:.6f}
⚡ Your Alert: +{threshold}% threshold

🎯 Your alert has been triggered!
🕒 {datetime.now().strftime('%H:%M:%S')}

#PriceAlert #{pair.replace('/', '')}
        """.strip()
    
    def create_price_down_message(self, pair: str, current_price: float, price_change: float, threshold: float) -> str:
        """Create price decrease alert message"""
        return f"""
📉 **PRICE ALERT: {pair}** 📉

🔻 **Price is DOWN {price_change:.2f}%!**
💰 Current Price: ${current_price:.6f}
⚡ Your Alert: -{threshold}% threshold

⚠️ Your alert has been triggered!
🕒 {datetime.now().strftime('%H:%M:%S')}

#PriceAlert #{pair.replace('/', '')}
        """.strip()
    
    def create_volume_spike_message(self, pair: str, current_price: float, volume_change: float, threshold: float) -> str:
        """Create volume spike alert message"""
        return f"""
📊 **VOLUME ALERT: {pair}** 📊

🔥 **Volume SPIKE +{volume_change:.2f}%!**
💰 Current Price: ${current_price:.6f}
⚡ Your Alert: +{threshold}% volume threshold

📈 Unusual trading activity detected!
🕒 {datetime.now().strftime('%H:%M:%S')}

#VolumeAlert #{pair.replace('/', '')}
        """.strip()
    
    async def trigger_alert(self, alert_id: int, telegram_id: int, user_id: int, pair: str, 
                          message: str, price: float, price_change: float = None):
        """Send alert to user and log it"""
        try:
            # Send telegram message
            if self.telegram_bot:
                success = await self.telegram_bot.send_alert_to_user(telegram_id, message)
                if success:
                    # Log the alert in database
                    self.db.log_alert_sent(user_id, alert_id, pair, message, price, price_change)
                    logger.info(f"Alert sent successfully to user {telegram_id}")
                else:
                    logger.error(f"Failed to send alert to user {telegram_id}")
            else:
                logger.warning("Telegram bot not available for sending alerts")
                
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def calculate_volume_change(self, pair: str) -> Optional[float]:
        """Calculate volume change over 24 hours"""
        try:
            # Get current volume
            latest_price_data = self.db.get_latest_price(pair)
            if not latest_price_data:
                return None
            
            current_volume = latest_price_data.get('volume_24h', 0)
            
            # Get volume from 24 hours ago (approximate)
            # This is a simplified implementation
            # In production, you'd want more sophisticated volume tracking
            
            # For now, simulate volume change detection
            # This would be replaced with actual historical volume comparison
            return None
            
        except Exception as e:
            logger.error(f"Error calculating volume change: {e}")
            return None
    
    def is_in_cooldown(self, cooldown_key: str) -> bool:
        """Check if alert is in cooldown period"""
        if cooldown_key not in self.last_alerts:
            return False
        
        last_alert_time = self.last_alerts[cooldown_key]
        current_time = datetime.now()
        
        if (current_time - last_alert_time).seconds < self.alert_cooldown:
            return True
        
        return False
    
    def set_cooldown(self, cooldown_key: str):
        """Set cooldown for alert"""
        self.last_alerts[cooldown_key] = datetime.now()
    
    async def send_market_updates(self, channel_id: str):
        """Send periodic market updates to channel"""
        try:
            logger.info("Preparing market update for channel")
            
            # Get current prices
            current_prices = self.api_client.get_icp_prices()
            if not current_prices:
                logger.warning("No price data for market update")
                return
            
            # Create market update message
            message = "📊 **ICP Market Update** 📊\n\n"
            
            for pair, price_data in current_prices.items():
                price = price_data['price']
                volume = price_data.get('volume_24h', 0)
                price_change = self.db.get_price_change(pair, 24)
                
                change_emoji = "📈" if price_change and price_change > 0 else "📉" if price_change and price_change < 0 else "➡️"
                change_text = f"{price_change:+.2f}%" if price_change else "N/A"
                
                message += f"🪙 **{pair}**\n"
                message += f"💰 ${price:.6f} {change_emoji} {change_text}\n"
                message += f"📊 Volume: ${volume:.2f}\n\n"
            
            message += f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"🤖 @your_bot_username | Join our community!"
            
            # Send to channel
            if self.telegram_bot:
                success = await self.telegram_bot.send_channel_update(channel_id, message)
                if success:
                    logger.info("Market update sent to channel successfully")
                else:
                    logger.error("Failed to send market update to channel")
            
        except Exception as e:
            logger.error(f"Error sending market updates: {e}")
    
    async def check_significant_moves(self, threshold: float = 10.0):
        """Check for significant price movements and send notifications"""
        try:
            current_prices = self.api_client.get_icp_prices()
            if not current_prices:
                return
            
            significant_moves = []
            
            for pair, price_data in current_prices.items():
                price_change = self.db.get_price_change(pair, 1)  # 1 hour change
                
                if price_change and abs(price_change) >= threshold:
                    significant_moves.append({
                        'pair': pair,
                        'price': price_data['price'],
                        'change': price_change
                    })
            
            # Send notifications for significant moves
            if significant_moves and self.telegram_bot:
                for move in significant_moves:
                    message = f"""
🚨 **SIGNIFICANT MOVE DETECTED** 🚨

🪙 **{move['pair']}**
💰 Price: ${move['price']:.6f}
📈 Change: {move['change']:+.2f}% (1h)

This is a notable price movement!
🕒 {datetime.now().strftime('%H:%M:%S')}
                    """.strip()
                    
                    # This could be sent to a special alerts channel
                    # await self.telegram_bot.send_channel_update(alerts_channel_id, message)
                    
                logger.info(f"Significant move detected: {move['pair']} {move['change']:+.2f}%")
        
        except Exception as e:
            logger.error(f"Error checking significant moves: {e}")
    
    async def cleanup_old_alerts(self):
        """Clean up old triggered alerts and inactive users"""
        try:
            # This could include:
            # - Removing alerts for inactive users
            # - Cleaning up old alert logs
            # - Optimizing alert checking performance
            logger.info("Alert cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during alert cleanup: {e}")
    
    def get_alert_statistics(self) -> Dict:
        """Get statistics about alerts"""
        try:
            # This could return:
            # - Number of active alerts
            # - Most popular pairs
            # - Alert success rate
            # - etc.
            return {
                'message': 'Alert statistics feature coming soon'
            }
            
        except Exception as e:
            logger.error(f"Error getting alert statistics: {e}")
            return {} 