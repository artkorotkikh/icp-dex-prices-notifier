import sqlite3
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "./data/icp_monitor.db"):
        self.db_path = db_path
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        with self.get_connection() as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referred_by) REFERENCES users (id)
                )
            ''')
            
            # Price history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume_24h REAL,
                    market_cap REAL,
                    price_change_24h REAL,
                    source TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data TEXT
                )
            ''')
            
            # User alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pair TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_triggered TIMESTAMP,
                    trigger_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # User subscriptions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pair TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, pair)
                )
            ''')
            
            # Alert log table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alert_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    alert_id INTEGER NOT NULL,
                    pair TEXT NOT NULL,
                    message TEXT NOT NULL,
                    price REAL NOT NULL,
                    price_change REAL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (alert_id) REFERENCES user_alerts (id)
                )
            ''')
            
            # Create indexes for better performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_price_history_pair_timestamp ON price_history (pair, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_alerts_user_active ON user_alerts (user_id, is_active)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_active ON user_subscriptions (user_id, is_active)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def add_user(self, telegram_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, referred_by: int = None) -> Optional[int]:
        """Add new user to database"""
        try:
            with self.get_connection() as conn:
                # Generate unique referral code
                referral_code = f"ICP{telegram_id % 10000:04d}"
                
                cursor = conn.execute('''
                    INSERT INTO users (telegram_id, username, first_name, last_name, referral_code, referred_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (telegram_id, username, first_name, last_name, referral_code, referred_by))
                
                conn.commit()
                logger.info(f"Added new user: {telegram_id}")
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # User already exists, update last activity
            self.update_user_activity(telegram_id)
            return self.get_user_by_telegram_id(telegram_id)['id']
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return None
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_activity(self, telegram_id: int):
        """Update user's last activity timestamp"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE users SET last_activity = CURRENT_TIMESTAMP 
                    WHERE telegram_id = ?
                ''', (telegram_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating user activity: {e}")
    
    def add_price_data(self, pair: str, price: float, volume_24h: float = None, 
                      source: str = "icpswap", raw_data: str = None) -> bool:
        """Add price data to history"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO price_history (pair, price, volume_24h, source, raw_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (pair, price, volume_24h, source, raw_data))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding price data: {e}")
            return False
    
    def get_latest_price(self, pair: str) -> Optional[Dict]:
        """Get latest price for a pair"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT * FROM price_history 
                    WHERE pair = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (pair,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting latest price: {e}")
            return None
    
    def get_price_change(self, pair: str, hours: int = 24) -> Optional[float]:
        """Get price change percentage over specified hours"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT price FROM price_history 
                    WHERE pair = ? AND timestamp >= datetime('now', '-{} hours')
                    ORDER BY timestamp ASC 
                    LIMIT 1
                '''.format(hours), (pair,))
                old_price_row = cursor.fetchone()
                
                if not old_price_row:
                    return None
                
                current_price_data = self.get_latest_price(pair)
                if not current_price_data:
                    return None
                
                old_price = old_price_row['price']
                current_price = current_price_data['price']
                
                if old_price == 0:
                    return None
                
                return ((current_price - old_price) / old_price) * 100
        except Exception as e:
            logger.error(f"Error calculating price change: {e}")
            return None
    
    def add_user_alert(self, user_id: int, pair: str, alert_type: str, threshold: float) -> bool:
        """Add user alert"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO user_alerts (user_id, pair, alert_type, threshold)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, pair, alert_type, threshold))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user alert: {e}")
            return False
    
    def get_user_alerts(self, user_id: int) -> List[Dict]:
        """Get all active alerts for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT * FROM user_alerts 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC
                ''', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
    
    def get_all_active_alerts(self) -> List[Dict]:
        """Get all active alerts for processing"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT ua.*, u.telegram_id 
                    FROM user_alerts ua
                    JOIN users u ON ua.user_id = u.id
                    WHERE ua.is_active = 1 AND u.is_active = 1
                ''')
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all active alerts: {e}")
            return []
    
    def subscribe_user_to_pair(self, user_id: int, pair: str) -> bool:
        """Subscribe user to a trading pair"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO user_subscriptions (user_id, pair, is_active)
                    VALUES (?, ?, 1)
                ''', (user_id, pair))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error subscribing user to pair: {e}")
            return False
    
    def unsubscribe_user_from_pair(self, user_id: int, pair: str) -> bool:
        """Unsubscribe user from a trading pair"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE user_subscriptions 
                    SET is_active = 0 
                    WHERE user_id = ? AND pair = ?
                ''', (user_id, pair))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error unsubscribing user from pair: {e}")
            return False
    
    def get_user_subscriptions(self, user_id: int) -> List[str]:
        """Get all active subscriptions for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    SELECT pair FROM user_subscriptions 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                return [row['pair'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting user subscriptions: {e}")
            return []
    
    def log_alert_sent(self, user_id: int, alert_id: int, pair: str, message: str, 
                      price: float, price_change: float = None):
        """Log that an alert was sent"""
        try:
            with self.get_connection() as conn:
                # Log the alert
                conn.execute('''
                    INSERT INTO alert_log (user_id, alert_id, pair, message, price, price_change)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, alert_id, pair, message, price, price_change))
                
                # Update alert trigger count and last triggered time
                conn.execute('''
                    UPDATE user_alerts 
                    SET last_triggered = CURRENT_TIMESTAMP, trigger_count = trigger_count + 1
                    WHERE id = ?
                ''', (alert_id,))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            with self.get_connection() as conn:
                # Get basic user info
                user_cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = user_cursor.fetchone()
                
                if not user:
                    return {}
                
                # Get subscription count
                sub_cursor = conn.execute('''
                    SELECT COUNT(*) as count FROM user_subscriptions 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                sub_count = sub_cursor.fetchone()['count']
                
                # Get alert count
                alert_cursor = conn.execute('''
                    SELECT COUNT(*) as count FROM user_alerts 
                    WHERE user_id = ? AND is_active = 1
                ''', (user_id,))
                alert_count = alert_cursor.fetchone()['count']
                
                # Get referral count
                ref_cursor = conn.execute('''
                    SELECT COUNT(*) as count FROM users 
                    WHERE referred_by = ?
                ''', (user_id,))
                ref_count = ref_cursor.fetchone()['count']
                
                return {
                    'user': dict(user),
                    'subscriptions': sub_count,
                    'alerts': alert_count,
                    'referrals': ref_count
                }
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old price data to save space"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    DELETE FROM price_history 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted} old price records")
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}") 