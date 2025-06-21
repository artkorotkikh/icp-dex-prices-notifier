# 🚀 ICP Token Monitor MVP

A comprehensive Telegram bot for monitoring ICP token prices on Raspberry Pi, with real-time alerts and community features.

## 🎯 Features

### 📊 Core Monitoring
- **Real-time Price Tracking**: ICP/nICP, ICP/USD, ICP/USDT, ICP/USDC
- **Multi-DEX Support**: ICPSwap and KongSwap integration
- **Historical Data**: 24h price changes and volume tracking
- **SQLite Database**: Lightweight, perfect for Raspberry Pi

### 🤖 Telegram Bot
- **Interactive Commands**: Easy-to-use bot commands
- **Price Alerts**: Custom threshold notifications
- **Subscription System**: Follow your favorite pairs
- **Community Features**: Referral system and stats

### ⚡ Alert System
- **Price Change Alerts**: Up/down percentage triggers
- **Volume Spike Detection**: Unusual trading activity alerts
- **Cooldown Management**: Anti-spam protection
- **Channel Updates**: Automated market updates

### 🔧 Raspberry Pi Optimized
- **Low Resource Usage**: Designed for Pi hardware
- **Auto-startup**: Systemd service integration
- **Log Management**: Automatic log rotation
- **Health Monitoring**: API status checks

## 🛠️ Quick Setup

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ICP_tokens_bot
chmod +x setup_raspberrypi.sh
./setup_raspberrypi.sh
```

### 2. Configure Your Bot
```bash
# Edit configuration file
nano config.env

# Add your Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username
```

### 3. Run the Bot
```bash
# Test run
python main.py

# Or enable as service
sudo systemctl enable icp-monitor
sudo systemctl start icp-monitor
```

## 📋 Requirements

### Hardware
- **Raspberry Pi 3B+** or newer (recommended)
- **8GB+ SD Card** (16GB+ recommended)
- **Internet Connection** (WiFi or Ethernet)

### Software
- **Raspberry Pi OS** (Bullseye or newer)
- **Python 3.8+**
- **Git**

## 🤖 Bot Commands

### Basic Commands
- `/start` - Initialize your account and get started
- `/help` - Show all available commands
- `/price [pair]` - Get current price (e.g., `/price ICP/nICP`)
- `/status` - Check bot and API status

### Subscription Commands
- `/subscribe [pair]` - Subscribe to price updates
- `/unsubscribe [pair]` - Unsubscribe from updates
- `/portfolio` - View your subscriptions and alerts

### Alert Commands
- `/setalert [pair] [type] [threshold]` - Set price alert
  - Example: `/setalert ICP/nICP price_up 5`
- `/alerts` - View your active alerts

### Community Commands
- `/referral` - Get your referral code and stats
- `/stats` - View your account statistics

## 🔧 Configuration

### Environment Variables
```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username

# Database Configuration
DATABASE_PATH=./data/icp_monitor.db

# API Configuration
ICPSWAP_API_URL=https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers
KONGSWAP_API_URL=https://api.kongswap.io

# Alert Configuration
DEFAULT_PRICE_THRESHOLD=5.0
ALERT_CHECK_INTERVAL=60
DATA_FETCH_INTERVAL=30

# Monitoring Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/icp_monitor.log
```

### Alert Types
- `price_up` - Price increase alerts
- `price_down` - Price decrease alerts  
- `volume_spike` - Volume spike alerts

### Monitored Pairs
- **ICP/nICP** - ICP to Neuron ICP
- **ICP/USD** - ICP to US Dollar
- **ICP/USDT** - ICP to Tether
- **ICP/USDC** - ICP to USD Coin

## 📊 Architecture

```
ICP Token Monitor
├── main.py              # Main application
├── database.py          # SQLite database management
├── api_client.py        # DEX API integration
├── telegram_bot.py      # Telegram bot handlers
├── alert_system.py      # Alert processing
├── config.env           # Configuration
└── requirements.txt     # Python dependencies
```

## 🔍 Monitoring & Maintenance

### Check Status
```bash
# Service status
sudo systemctl status icp-monitor

# View logs
tail -f logs/icp_monitor.log

# Check processes
htop
```

### Database Management
```bash
# View database
sqlite3 data/icp_monitor.db

# Check table structure
.tables
.schema users
```

### Performance Optimization
- **Memory Usage**: ~50-100MB RAM
- **Storage**: ~10MB per month (with cleanup)
- **Network**: ~1MB per day
- **CPU**: Minimal, mainly I/O bound

## 🚀 Advanced Features

### Systemd Service Management
```bash
# Start service
sudo systemctl start icp-monitor

# Stop service
sudo systemctl stop icp-monitor

# Enable auto-start
sudo systemctl enable icp-monitor

# View service logs
journalctl -u icp-monitor -f
```

### Log Rotation
Automatic log rotation is configured to keep logs manageable:
- **Daily rotation**
- **7 days retention**
- **Compression enabled**

### Health Checks
Built-in monitoring includes:
- API connectivity checks
- Database health verification
- Memory usage monitoring
- Automatic restart on failures

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check if service is running
sudo systemctl status icp-monitor

# Check logs for errors
tail -f logs/icp_monitor.log

# Restart service
sudo systemctl restart icp-monitor
```

#### API Connection Issues
```bash
# Test API connectivity
curl -s "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers" | head -5

# Check internet connection
ping -c 4 google.com
```

#### Database Issues
```bash
# Check database file
ls -la data/icp_monitor.db

# Test database connection
sqlite3 data/icp_monitor.db "SELECT COUNT(*) FROM users;"
```

### Performance Issues
- **High Memory Usage**: Check for memory leaks in logs
- **Slow Response**: Verify API response times
- **Disk Space**: Monitor log and database sizes

## 🔐 Security

### Best Practices
- Keep your Telegram bot token secure
- Run with non-root user
- Regular system updates
- Monitor logs for suspicious activity
- Use environment variables for secrets

### Firewall Configuration
```bash
# Only allow SSH and outbound connections
sudo ufw enable
sudo ufw allow ssh
```

## 📈 Scaling & Growth

### Community Growth Features
- **Referral System**: Built-in referral tracking
- **User Statistics**: Engagement metrics
- **Viral Mechanics**: Share incentives
- **Community Challenges**: Future feature

### Adding New Features
The modular architecture makes it easy to add:
- New DEX integrations
- Additional alert types
- Advanced analytics
- Mobile app integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

### Getting Help
- **Documentation**: Check this README
- **Issues**: Open GitHub issues
- **Community**: Join our Telegram channel
- **Email**: support@yourproject.com

### Feature Requests
We welcome feature requests! Please:
1. Check existing issues first
2. Provide detailed use cases
3. Consider implementation complexity
4. Engage with the community

## 🙏 Acknowledgments

- **Internet Computer Protocol** for the amazing blockchain
- **ICPSwap** and **KongSwap** for DEX APIs
- **Telegram** for the bot platform
- **Raspberry Pi Foundation** for affordable computing
- **Open Source Community** for inspiration and tools

---

**Happy Monitoring! 🚀**

*Built with ❤️ for the ICP community* 