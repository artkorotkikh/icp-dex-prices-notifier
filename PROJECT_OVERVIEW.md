# 🚀 ICP Token Monitor - Project Overview

## 📋 Quick Start

### 🔧 Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure bot
cp config/config.env.example config/config.env
# Edit config/config.env with your Telegram bot token

# 3. Test locally (no Telegram required)
python3 tests/local_test.py

# 4. Run with Telegram
python3 main.py
```

### 🧪 Testing
```bash
python3 tests/test_apis.py           # API connectivity
python3 tests/quick_test.py          # Quick price check
python3 tests/local_test.py          # Full system test
python3 tests/test_main_components.py # Integration test
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
│   └── 📁 bot/               # Telegram bot
├── 📁 tests/                 # Test files
├── 📁 config/                # Configuration
├── 📁 docs/                  # Documentation
├── 📁 scripts/               # Setup scripts
├── 📁 data/                  # Database (runtime)
├── 📁 logs/                  # Log files (runtime)
├── main.py                   # Application entry point
└── requirements.txt          # Dependencies
```

## ⚡ Key Features

### 🤖 Telegram Bot Commands
- `/start` - Welcome & referral code
- `/price <pair>` - Current price
- `/subscribe <pair>` - Follow updates
- `/setalert <pair> <type> <threshold>` - Price alerts
- `/portfolio` - Your subscriptions
- `/stats` - Usage statistics
- `/referral` - Referral program
- `/status` - System health

### 📊 Price Monitoring
- **Real-time data** from ICPSwap DEX
- **10+ ICP pairs** (NICP/ICP, USDT/ICP, etc.)
- **24/7 monitoring** with scheduled updates
- **Alert system** with customizable thresholds
- **Price history** tracking and analytics

### 👥 User Management
- **User profiles** with preferences
- **Referral system** for viral growth
- **Subscription management** for favorite pairs
- **Alert management** with cooldowns
- **Statistics tracking** for engagement

## 🔧 Technical Stack

### 🐍 Backend
- **Python 3.8+** - Main language
- **SQLite** - Database
- **python-telegram-bot** - Telegram API
- **requests** - HTTP API calls
- **schedule** - Task scheduling

### 🌐 APIs
- **ICPSwap** - Primary DEX data source
- **KongSwap** - Secondary DEX (optional)
- **Telegram Bot API** - User interface

### 📦 Dependencies
```
requests==2.31.0
python-telegram-bot==20.7
schedule==1.2.0
python-dotenv==1.0.0
aiohttp==3.9.1
```

## 🚀 Deployment

### 🏠 Local Development
```bash
python3 tests/local_test.py    # Test without Telegram
python3 main.py               # Run with Telegram
```

### 🥧 Raspberry Pi Production
```bash
chmod +x scripts/setup_raspberrypi.sh
./scripts/setup_raspberrypi.sh
```

### 🐳 Docker (Future)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

## 📈 Performance

### 💾 Resource Usage
- **Memory**: 50-100MB
- **CPU**: <5% on Raspberry Pi 4
- **Storage**: ~10MB + database growth
- **Network**: ~1MB/hour API calls

### ⚡ Response Times
- **Bot commands**: <1 second
- **Price updates**: <2 seconds
- **Alert processing**: <5 seconds
- **Database queries**: <100ms

## 🔒 Security

### 🛡️ Best Practices
- Environment variables for secrets
- Input validation on all user data
- Rate limiting on API calls
- Secure database permissions
- Regular security updates

### 📊 Monitoring
- Health checks every 5 minutes
- Error logging and alerting
- Performance metrics tracking
- User activity monitoring

## 🎯 Roadmap

### 🔜 Phase 1 (Current)
- ✅ ICPSwap integration
- ✅ Basic Telegram bot
- ✅ Price alerts
- ✅ User management
- ✅ Raspberry Pi deployment

### 🚀 Phase 2 (Next)
- [ ] KongSwap integration
- [ ] Advanced charting
- [ ] Portfolio tracking
- [ ] DeFi yield monitoring
- [ ] Mobile app

### 🌟 Phase 3 (Future)
- [ ] Multi-chain support
- [ ] AI price predictions
- [ ] Social trading features
- [ ] NFT monitoring
- [ ] DAO governance

## 🤝 Contributing

### 🔧 Development Setup
```bash
git clone <repository>
cd ICP_tokens_bot
pip install -r requirements.txt
cp config/config.env.example config/config.env
```

### 🧪 Testing
```bash
python3 tests/test_apis.py           # API tests
python3 tests/local_test.py          # Full system
python3 tests/test_main_components.py # Integration
```

### 📝 Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write tests

## 📞 Support

### 📚 Documentation
- `docs/README.md` - Complete guide
- `docs/DEPLOYMENT_GUIDE.md` - Deployment instructions
- `docs/PROJECT_STRUCTURE.md` - Technical details

### 🐛 Issues
- Check logs in `logs/` directory
- Run `python3 tests/test_apis.py` for diagnostics
- Verify configuration in `config/config.env`

### 💬 Community
- Telegram: @icp_monitor_bot
- GitHub: Issues and discussions
- Discord: ICP Community

---

🎉 **Ready to monitor ICP tokens like a pro!** 🚀 