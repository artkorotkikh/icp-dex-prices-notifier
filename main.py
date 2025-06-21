#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import schedule
import time
from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

# Import our modules
from src.core import Database, APIClient, AlertSystem
from src.bot import TelegramBot

# Load environment variables
load_dotenv('config/config.env')

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', './logs/icp_monitor.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce telegram logging noise
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)

class ICPMonitorApp:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize components
        self.db = None
        self.api_client = None
        self.telegram_bot = None
        self.alert_system = None
        
        # Background tasks
        self.data_fetch_thread = None
        self.scheduler_thread = None
        self.running = False
    
    def load_config(self) -> dict:
        """Load configuration from environment variables"""
        config = {
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'telegram_channel_id': os.getenv('TELEGRAM_CHANNEL_ID'),
            'database_path': os.getenv('DATABASE_PATH', './data/icp_monitor.db'),
            'icpswap_api_url': os.getenv('ICPSWAP_API_URL', 'https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers'),
            'kongswap_api_url': os.getenv('KONGSWAP_API_URL', 'https://api.kongswap.io'),
            'default_price_threshold': float(os.getenv('DEFAULT_PRICE_THRESHOLD', 5.0)),
            'alert_check_interval': int(os.getenv('ALERT_CHECK_INTERVAL', 60)),
            'data_fetch_interval': int(os.getenv('DATA_FETCH_INTERVAL', 30)),
            'monitored_pairs': os.getenv('MONITORED_PAIRS', 'ICP/nICP,ICP/USD').split(',')
        }
        
        # Validate required configuration
        if not config['telegram_bot_token']:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        return config
    
    def initialize_components(self):
        """Initialize all system components"""
        try:
            self.logger.info("Initializing ICP Monitor components...")
            
            # Initialize database
            self.db = Database(self.config['database_path'])
            self.logger.info("Database initialized")
            
            # Initialize API client
            self.api_client = APIClient()
            self.logger.info("API client initialized")
            
            # Initialize Telegram bot
            self.telegram_bot = TelegramBot(
                token=self.config['telegram_bot_token'],
                db=self.db,
                api_client=self.api_client
            )
            self.telegram_bot.setup_handlers()
            self.logger.info("Telegram bot initialized")
            
            # Initialize alert system
            self.alert_system = AlertSystem(
                db=self.db,
                api_client=self.api_client,
                telegram_bot=self.telegram_bot
            )
            self.logger.info("Alert system initialized")
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def setup_scheduler(self):
        """Setup scheduled tasks"""
        try:
            # Data fetching schedule
            schedule.every(self.config['data_fetch_interval']).seconds.do(self.fetch_and_store_data)
            
            # Alert checking schedule
            schedule.every(self.config['alert_check_interval']).seconds.do(self.run_alert_check)
            
            # Market updates schedule (every 30 minutes)
            schedule.every(30).minutes.do(self.send_market_update)
            
            # Daily cleanup (at 2 AM)
            schedule.every().day.at("02:00").do(self.daily_cleanup)
            
            # Health check (every 5 minutes)
            schedule.every(5).minutes.do(self.health_check)
            
            self.logger.info("Scheduler setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup scheduler: {e}")
            raise
    
    def fetch_and_store_data(self):
        """Fetch current price data and store in database"""
        try:
            self.logger.debug("Fetching and storing price data...")
            
            # Get current prices
            price_data = self.api_client.get_icp_prices()
            
            if not price_data:
                self.logger.warning("No price data received")
                return
            
            # Store each pair's data
            stored_count = 0
            for pair, data in price_data.items():
                success = self.db.add_price_data(
                    pair=pair,
                    price=data['price'],
                    volume_24h=data.get('volume_24h'),
                    source=data.get('source', 'unknown'),
                    raw_data=data.get('raw_data')
                )
                
                if success:
                    stored_count += 1
            
            self.logger.info(f"Stored price data for {stored_count} pairs")
            
        except Exception as e:
            self.logger.error(f"Error fetching and storing data: {e}")
    
    def run_alert_check(self):
        """Run alert checking (wrapper for async function)"""
        try:
            asyncio.run(self.alert_system.check_all_alerts())
        except Exception as e:
            self.logger.error(f"Error running alert check: {e}")
    
    def send_market_update(self):
        """Send market update to channel (wrapper for async function)"""
        try:
            if self.config['telegram_channel_id']:
                asyncio.run(self.alert_system.send_market_updates(self.config['telegram_channel_id']))
        except Exception as e:
            self.logger.error(f"Error sending market update: {e}")
    
    def daily_cleanup(self):
        """Run daily cleanup tasks"""
        try:
            self.logger.info("Running daily cleanup...")
            
            # Clean up old price data (keep 30 days)
            self.db.cleanup_old_data(days=30)
            
            # Clean up alert system
            asyncio.run(self.alert_system.cleanup_old_alerts())
            
            self.logger.info("Daily cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during daily cleanup: {e}")
    
    def health_check(self):
        """Perform system health check"""
        try:
            # Check API health
            health_status = self.api_client.health_check()
            
            # Log health status
            icpswap_status = "✅" if health_status.get('icpswap') else "❌"
            kongswap_status = "✅" if health_status.get('kongswap') else "❌"
            
            self.logger.info(f"Health check - ICPSwap: {icpswap_status}, KongSwap: {kongswap_status}")
            
            # If all APIs are down, this could trigger an admin alert
            if not any(health_status.values()):
                self.logger.warning("All APIs are down!")
            
        except Exception as e:
            self.logger.error(f"Error during health check: {e}")
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        self.logger.info("Starting scheduler thread...")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error in scheduler: {e}")
                time.sleep(5)  # Wait before retrying
    
    def start(self):
        """Start the ICP Monitor application"""
        try:
            self.logger.info("🚀 Starting ICP Token Monitor...")
            
            # Initialize components
            self.initialize_components()
            
            # Setup scheduler
            self.setup_scheduler()
            
            # Set running flag
            self.running = True
            
            # Start scheduler in background thread
            self.scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            # Run initial data fetch
            self.logger.info("Running initial data fetch...")
            self.fetch_and_store_data()
            
            # Start telegram bot (this will block)
            self.logger.info("Starting Telegram bot...")
            self.telegram_bot.run()
            
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
            self.stop()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.stop()
            sys.exit(1)
    
    def stop(self):
        """Stop the application gracefully"""
        self.logger.info("🛑 Stopping ICP Token Monitor...")
        
        self.running = False
        
        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("ICP Token Monitor stopped")

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║               🚀 ICP TOKEN MONITOR MVP 🚀                    ║
    ║                                                              ║
    ║    Real-time ICP price monitoring for Raspberry Pi          ║
    ║    • ICPSwap & KongSwap integration                          ║
    ║    • Telegram bot & alerts                                   ║
    ║    • SQLite database                                         ║
    ║    • Community features                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main entry point"""
    print_banner()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create and start the application
        app = ICPMonitorApp()
        app.start()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 