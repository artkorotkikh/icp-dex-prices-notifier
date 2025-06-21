# 📁 ICP Token Monitor - Project Structure

## 🏗️ Directory Layout

```
ICP_tokens_bot/
├── 📁 src/                     # Source code
│   ├── 📁 core/               # Core business logic
│   │   ├── __init__.py
│   │   ├── database.py        # Database management
│   │   ├── api_client.py      # API integration
│   │   └── alert_system.py    # Alert processing
│   ├── 📁 bot/                # Telegram bot
│   │   ├── __init__.py
│   │   └── telegram_bot.py    # Bot handlers
│   └── 📁 utils/              # Utility functions
│       └── __init__.py
├── 📁 tests/                  # Test files
│   ├── test_apis.py          # API connectivity tests
│   ├── local_test.py         # Full system test
│   ├── quick_test.py         # Quick price check
│   └── test_main_components.py # Integration tests
├── 📁 config/                 # Configuration files
│   └── config.env.example    # Environment variables template
├── 📁 scripts/                # Setup and utility scripts
│   └── setup_raspberrypi.sh  # Raspberry Pi setup
├── 📁 docs/                   # Documentation
│   ├── README.md             # Main documentation
│   ├── DEPLOYMENT_GUIDE.md   # Deployment instructions
│   └── PROJECT_STRUCTURE.md  # This file
├── 📁 data/                   # Database storage (created at runtime)
├── 📁 logs/                   # Log files (created at runtime)
├── main.py                   # Application entry point
└── requirements.txt          # Python dependencies
```

## 📦 Package Structure

### 🔧 Core Modules (`src/core/`)

#### `database.py`
- **Purpose**: SQLite database management
- **Key Classes**: `Database`
- **Features**: User management, price history, alerts, referrals
- **Dependencies**: `sqlite3`, `logging`

#### `api_client.py`
- **Purpose**: DEX API integration
- **Key Classes**: `APIClient`
- **Features**: ICPSwap/KongSwap data fetching, caching, health checks
- **Dependencies**: `requests`, `json`

#### `alert_system.py`
- **Purpose**: Price monitoring and alert processing
- **Key Classes**: `AlertSystem`
- **Features**: Alert checking, cooldowns, market updates
- **Dependencies**: `asyncio`, `database.py`, `api_client.py`

### 🤖 Bot Module (`src/bot/`)

#### `telegram_bot.py`
- **Purpose**: Telegram bot interface
- **Key Classes**: `TelegramBot`
- **Features**: Commands, callbacks, user interaction
- **Dependencies**: `python-telegram-bot`, core modules

### 🧪 Test Modules (`tests/`)

#### `test_apis.py`
- **Purpose**: API connectivity and dependency testing
- **Features**: ICPSwap/KongSwap testing, import validation

#### `local_test.py`
- **Purpose**: Complete system functionality test
- **Features**: Full workflow simulation without Telegram

#### `quick_test.py`
- **Purpose**: Quick price data verification
- **Features**: Simple API test and data display

#### `test_main_components.py`
- **Purpose**: Integration testing
- **Features**: Component interaction testing

## 🔄 Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ICPSwap API   │───▶│   API Client    │───▶│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Telegram Bot   │◀───│  Alert System   │◀───│  Price History  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│     Users       │    │   Channel       │
└─────────────────┘    └─────────────────┘
```

## 🏃‍♂️ Execution Flow

1. **Startup** (`main.py`)
   - Load configuration
   - Initialize database
   - Start API client
   - Setup Telegram bot
   - Configure alert system
   - Start scheduler

2. **Data Collection** (Scheduled)
   - Fetch prices from APIs
   - Store in database
   - Update price history

3. **Alert Processing** (Scheduled)
   - Check user alerts
   - Calculate price changes
   - Send notifications

4. **User Interaction** (Event-driven)
   - Process Telegram commands
   - Update user preferences
   - Manage subscriptions

## 🔧 Configuration

### Environment Variables (`config/config.env.example`)
```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
DATABASE_PATH=./data/icp_monitor.db
ALERT_CHECK_INTERVAL=60
DATA_FETCH_INTERVAL=30
```

### Dependencies (`requirements.txt`)
- `requests`: HTTP API calls
- `python-telegram-bot`: Telegram integration
- `schedule`: Task scheduling
- `python-dotenv`: Environment management
- `aiohttp`: Async HTTP support

## 🚀 Deployment

### Development
```bash
python3 tests/local_test.py    # Test locally
python3 main.py               # Run with Telegram
```

### Production (Raspberry Pi)
```bash
./scripts/setup_raspberrypi.sh  # Automated setup
sudo systemctl start icp-monitor # Run as service
```

## 📈 Scalability

### Adding New Features
1. **New API**: Add to `src/core/api_client.py`
2. **New Commands**: Add to `src/bot/telegram_bot.py`
3. **New Alerts**: Extend `src/core/alert_system.py`
4. **Utilities**: Add to `src/utils/`

### Database Schema
- **Users**: User management and referrals
- **Price History**: Time-series price data
- **Alerts**: User alert configurations
- **Subscriptions**: User pair subscriptions
- **Alert Log**: Alert delivery tracking

## 🔒 Security

### Best Practices
- Environment variables for secrets
- Input validation on all user data
- Rate limiting on API calls
- Secure database permissions
- Regular security updates

### Data Protection
- No sensitive data in logs
- Encrypted bot token storage
- User data privacy compliance
- Secure backup procedures

## 🐛 Debugging

### Log Locations
- **Application**: `logs/icp_monitor.log`
- **System**: `journalctl -u icp-monitor`
- **Database**: SQLite query logs

### Common Issues
- **Import Errors**: Check PYTHONPATH and package structure
- **API Failures**: Verify internet connection and endpoints
- **Database Locks**: Check file permissions and concurrent access
- **Memory Issues**: Monitor with `htop`, adjust swap if needed

## 📊 Monitoring

### Health Checks
- API connectivity status
- Database operation success
- Memory and disk usage
- Alert delivery rates
- User engagement metrics

### Performance Metrics
- Response time < 1 second
- Memory usage < 100MB
- 99%+ uptime target
- Zero data loss guarantee 