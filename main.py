#!/usr/bin/env python3
"""
nICP Discount Tracker
Tracks nICP/ICP discount opportunities across DEXes
"""

import asyncio
import logging
import os
import sys
import signal
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Load environment variables from config file
def load_config():
    """Load environment variables from config/config.env file"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.env')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key.strip()] = value
        print(f"✅ Loaded configuration from {config_path}")
    else:
        print(f"⚠️  Config file not found: {config_path}")

# Load config before importing other modules
load_config()

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.nicp_arbitrage_client import NICPArbitrageClient
from src.core.database import Database
from src.bot.telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nicp_arbitrage_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NICPArbitrageBot:
    def __init__(self):
        # Load environment variables
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # Initialize components
        self.database = Database()
        self.arbitrage_client = NICPArbitrageClient()
        self.telegram_bot = TelegramBot(self.telegram_token, self.database)
        
        # Scheduler for periodic tasks
        self.scheduler = AsyncIOScheduler()
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    async def update_arbitrage_data(self):
        """Periodic task to update nICP arbitrage data"""
        try:
            logger.info("🔍 Updating nICP arbitrage data...")
            
            # Get arbitrage data
            arbitrage_data = await self.arbitrage_client.get_nicp_arbitrage_data()
            
            # Store in database (simplified for now)
            timestamp = datetime.now()
            opportunities = len(arbitrage_data.get('opportunities', []))
            viable_opportunities = arbitrage_data['summary']['viable_opportunities']
            best_profit = arbitrage_data['summary']['best_profit_6m']
            
            logger.info(f"📊 Found {opportunities} opportunities, {viable_opportunities} viable, best: {best_profit:.1f}%")
            
            # TODO: Store detailed data in database for historical tracking
            # self.database.store_arbitrage_data(arbitrage_data)
            
        except Exception as e:
            logger.error(f"Error updating arbitrage data: {e}")

    async def check_api_health(self):
        """Check health of DEX APIs"""
        try:
            health = self.arbitrage_client.check_health()
            status_symbols = {True: "✅", False: "❌"}
            
            health_status = ", ".join([
                f"{dex}: {status_symbols[status]}" 
                for dex, status in health.items()
            ])
            
            logger.info(f"Health check - {health_status}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")

    async def start(self):
        """Start the nICP arbitrage bot"""
        logger.info("🚀 Starting nICP Discount Tracker...")
        
        # Initialize database (already done in constructor)
        # self.database.init_database()  # Already called in __init__
        
        # Start scheduler
        logger.info("Starting scheduler...")
        self.scheduler.add_job(
            self.update_arbitrage_data,
            IntervalTrigger(seconds=30),  # Update every 30 seconds
            id='update_arbitrage_data',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.check_api_health,
            IntervalTrigger(minutes=5),  # Health check every 5 minutes
            id='health_check',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler started")
        
        # Run initial data fetch
        logger.info("Running initial arbitrage data fetch...")
        await self.update_arbitrage_data()
        
        # Start Telegram bot
        logger.info("Starting Telegram bot...")
        self.running = True
        
        # Start bot in background task
        bot_task = asyncio.create_task(self.telegram_bot.start_bot())
        
        try:
            # Keep the main loop running
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("�� Shutting down nICP Discount Tracker...")
        
        # Stop scheduler
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        # Stop Telegram bot
        try:
            await self.telegram_bot.stop_bot()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")
        
        # Close database connection
        self.database.close()
        logger.info("Database connection closed")
        
        logger.info("✅ Shutdown complete")

async def main():
    """Main entry point"""
    try:
        # Create and start the bot
        bot = NICPArbitrageBot()
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('logs', exist_ok=True)
    
    # Check for required environment variables
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is required")
        print("💡 Set it with: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        sys.exit(1)
    
    print("🚀 nICP Discount Tracker")
    print("========================================")
    print("🎯 Tracking nICP/ICP discount opportunities")
    print("📊 Checking KongSwap and other DEXes")
    print("🤖 Telegram bot ready for user commands")
    print("========================================")
    
    # Run the bot
    asyncio.run(main()) 