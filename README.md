# 🚀 ICP Token Monitor Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://telegram.org/)
[![ICP](https://img.shields.io/badge/ICP-Internet%20Computer-brightgreen.svg)](https://internetcomputer.org/)

> **A comprehensive Telegram bot for real-time ICP token price monitoring with smart alerts and community features**

## 🌟 Features

### 📊 **Real-Time Price Monitoring**
- **Live price data** from ICPSwap DEX
- **10+ ICP trading pairs** (NICP/ICP, USDT/ICP, USDC/ICP, etc.)
- **24/7 automated monitoring** with scheduled updates
- **Price history tracking** and analytics

### 🤖 **Telegram Bot Interface**
- **Interactive commands** for price checking and alerts
- **Subscription system** for favorite trading pairs
- **Customizable alerts** with percentage thresholds
- **User-friendly interface** with inline keyboards

### ⚡ **Smart Alert System**
- **Price movement alerts** (up/down thresholds)
- **Volume spike notifications**
- **Cooldown management** to prevent spam
- **Personalized alert preferences**

### 👥 **Community Features**
- **Referral system** for viral growth
- **User statistics** and engagement tracking
- **Channel updates** for market movements
- **Portfolio management** for subscriptions

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Internet connection for API access

### ⚡ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ICP_tokens_bot.git
   cd ICP_tokens_bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp config/config.env.example config/config.env
   # Edit config/config.env with your settings
   ```

4. **Test locally (no Telegram required)**
   ```bash
   python3 tests/local_test.py
   ```

5. **Run the bot**
   ```bash
   python3 main.py
   ```

### 🔧 Configuration

Edit `config/config.env` with your settings:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel

# Database Configuration
DATABASE_PATH=./data/icp_monitor.db

# API Configuration
ICPSWAP_API_URL=https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers
KONGSWAP_API_URL=https://api.kongswap.io

# Alert Configuration
ALERT_CHECK_INTERVAL=60
DATA_FETCH_INTERVAL=30
MARKET_UPDATE_INTERVAL=1800
```

## 🎮 Bot Commands

### 📱 **User Commands**
- `/start` - Welcome message and referral code
- `/price <pair>` - Get current price for a trading pair
- `/subscribe <pair>` - Subscribe to price updates
- `/setalert <pair> <type> <threshold>` - Set price alerts
- `/portfolio` - View your subscriptions and alerts
- `/stats` - Your usage statistics
- `/referral` - Referral program details
- `/status` - Bot and API health status

### 💡 **Example Usage**
```
/price NICP/ICP
/subscribe USDT/ICP
/setalert NICP/ICP price_up 5
/portfolio
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ICP Token Monitor                        │
├─────────────────────────────────────────────────────────────┤
│  📱 Telegram Bot  │  ⚡ Alert System  │  🌐 API Client     │
│  User Commands    │  Price Monitoring │  ICPSwap/KongSwap  │
├─────────────────────────────────────────────────────────────┤
│                    💾 SQLite Database                       │
│         Users • Price History • Alerts • Referrals         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ICP_tokens_bot/
├── 📁 src/                    # Source code
│   ├── 📁 core/              # Core business logic
│   │   ├── database.py       # Database management
│   │   ├── api_client.py     # API integration
│   │   └── alert_system.py   # Alert processing
│   └── 📁 bot/               # Telegram bot
│       └── telegram_bot.py   # Bot handlers
├── 📁 tests/                 # Test files
├── 📁 config/                # Configuration
├── 📁 docs/                  # Documentation
├── 📁 scripts/               # Setup scripts
├── main.py                   # Application entry point
└── requirements.txt          # Dependencies
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# API connectivity test
python3 tests/test_apis.py

# Quick price check
python3 tests/quick_test.py

# Full system test (no Telegram required)
python3 tests/local_test.py

# Integration test
python3 tests/test_main_components.py
```

## 🥧 Raspberry Pi Deployment

### 🔧 Automated Setup
```bash
chmod +x scripts/setup_raspberrypi.sh
./scripts/setup_raspberrypi.sh
```

### 📊 Performance on Raspberry Pi 4
- **Memory Usage**: 50-100MB
- **CPU Usage**: <5%
- **Storage**: ~10MB + database growth
- **Network**: ~1MB/hour

### 🔄 Service Management
```bash
# Start the service
sudo systemctl start icp-monitor

# Enable auto-start
sudo systemctl enable icp-monitor

# Check status
sudo systemctl status icp-monitor

# View logs
journalctl -u icp-monitor -f
```

## 📊 Supported Trading Pairs

The bot currently monitors these ICP pairs from ICPSwap:

- **NICP/ICP** - Neuron ICP
- **USDT/ICP** - Tether USD
- **USDC/ICP** - USD Coin
- **CKUSDT/ICP** - Chain Key USDT
- **CKUSDC/ICP** - Chain Key USDC
- **And more...**

## 🔧 Technical Stack

### 🐍 **Backend**
- **Python 3.8+** - Main programming language
- **SQLite** - Lightweight database
- **asyncio** - Asynchronous programming

### 📡 **APIs & Integrations**
- **ICPSwap API** - Primary DEX data source
- **KongSwap API** - Secondary DEX (optional)
- **Telegram Bot API** - User interface

### 📦 **Key Dependencies**
- `python-telegram-bot` - Telegram integration
- `requests` - HTTP API calls
- `schedule` - Task scheduling
- `python-dotenv` - Environment management
- `aiohttp` - Async HTTP support

## 🔒 Security Features

- **Environment variables** for sensitive data
- **Input validation** on all user inputs
- **Rate limiting** on API calls
- **Secure database** permissions
- **Error handling** and logging

## 📈 Performance Metrics

- **Response time**: <1 second for bot commands
- **Price updates**: <2 seconds
- **Alert processing**: <5 seconds
- **Database queries**: <100ms
- **Uptime target**: 99%+

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### 🔧 Development Setup
```bash
git clone https://github.com/yourusername/ICP_tokens_bot.git
cd ICP_tokens_bot
pip install -r requirements.txt
cp config/config.env.example config/config.env
```

### 🧪 Running Tests
```bash
python3 tests/test_apis.py
python3 tests/local_test.py
```

### 📝 Code Style
- Follow PEP 8
- Use type hints
- Add comprehensive docstrings
- Write tests for new features

## 📚 Documentation

- [📖 **Complete Guide**](docs/README.md) - Detailed documentation
- [🚀 **Deployment Guide**](docs/DEPLOYMENT_GUIDE.md) - Production deployment
- [🏗️ **Project Structure**](docs/PROJECT_STRUCTURE.md) - Technical architecture
- [📋 **Project Overview**](PROJECT_OVERVIEW.md) - High-level overview
- [🔧 **Git Setup Guide**](docs/GIT_SETUP.md) - Git workflow and GitHub setup

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**API Connection Issues**
```bash
# Test API connectivity
python3 tests/test_apis.py
```

**Database Issues**
```bash
# Check database permissions
ls -la data/
```

### 📝 Logs
- **Application logs**: `logs/icp_monitor.log`
- **System logs**: `journalctl -u icp-monitor`

## 🎯 Roadmap

### ✅ **Phase 1 - MVP (Current)**
- ICPSwap integration
- Basic Telegram bot
- Price alerts
- User management
- Raspberry Pi deployment

### 🚀 **Phase 2 - Enhanced Features**
- [ ] KongSwap integration
- [ ] Advanced charting
- [ ] Portfolio tracking
- [ ] DeFi yield monitoring
- [ ] Mobile notifications

### 🌟 **Phase 3 - Advanced Features**
- [ ] Multi-chain support
- [ ] AI price predictions
- [ ] Social trading features
- [ ] NFT monitoring
- [ ] DAO governance integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Internet Computer Protocol** - For the amazing blockchain platform
- **ICPSwap** - For providing reliable DEX data
- **Telegram** - For the excellent bot platform
- **Python Community** - For the fantastic libraries

## 📞 Support

### 💬 **Community**
- **Telegram**: [@icp_monitor_bot](https://t.me/icp_monitor_bot)
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/ICP_tokens_bot/issues)
- **Discussions**: [Community discussions](https://github.com/yourusername/ICP_tokens_bot/discussions)

### 📧 **Contact**
- **Email**: support@icpmonitor.com
- **Twitter**: [@ICPMonitorBot](https://twitter.com/ICPMonitorBot)

---

<div align="center">

**🎉 Ready to monitor ICP tokens like a pro! 🚀**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/ICP_tokens_bot.svg?style=social&label=Star)](https://github.com/yourusername/ICP_tokens_bot)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/ICP_tokens_bot.svg?style=social&label=Fork)](https://github.com/yourusername/ICP_tokens_bot/fork)

</div> 