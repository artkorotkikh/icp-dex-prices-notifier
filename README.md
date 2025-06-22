# 🚀 nICP Discount Tracker

**Discover and monitor nICP discount opportunities on the Internet Computer ecosystem**

## 💰 What is nICP?

nICP (neuron ICP) is staked ICP that can be dissolved back to regular ICP after 6 months. This creates a unique discount opportunity:

- **Direct staking**: 1 ICP = 0.9001 nICP (exchange rate from WaterNeuron)
- **DEX trading**: nICP often trades closer to 1:1 with ICP
- **Discount opportunity**: Buy nICP on DEX → Unstake immediately → Wait 6 months → Profit!

## 🎯 Key Features

- **Real-time monitoring** of nICP/ICP pairs across DEXes
- **Live price data** from ICPSwap and KongSwap
- **WaterNeuron integration** for accurate exchange rates
- **Profit calculations** with 6-month APY projections
- **Telegram bot interface** for easy access
- **Discount alerts** (coming soon)
- Calculates live discount opportunities
- Shows potential profits and risks
- Educational content about nICP

## 🤖 Telegram Commands

- `/start` - Welcome message and bot overview
- `/discount` - Check current discount opportunities
- `/help` - Show all available commands
- `/status` - Bot and API health status

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ICP_tokens_bot.git
cd ICP_tokens_bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

4. **Run the bot**
```bash
python3 main.py
```

### 🧪 Test the System
```bash
python3 test_nicp_arbitrage.py
```

## 📊 How nICP Arbitrage Works

### The Process
1. **Buy nICP** on a DEX (like KongSwap) using ICP
2. **Immediately unstake** the nICP to start 6-month dissolution
3. **Wait 6 months** for the dissolution period to complete
4. **Receive more ICP** than you originally spent

### Example Calculation
```
Investment: 1,000 ICP
nICP price on DEX: 1.02 ICP per nICP
nICP tokens purchased: 980.4 nICP
After 6 months: 1,088 ICP
Profit: 88 ICP (8.8% return)
```

### ⚠️ Important Risks
- **6-month lock-up period**: Your ICP is locked during dissolution
- **ICP price volatility**: ICP value may fluctuate during the 6-month period
- **Liquidity risk**: nICP pairs may have low trading volume
- **Opportunity cost**: ICP might gain more than arbitrage profit

## 🏗️ Architecture

```
nICP Discount Tracker
├── src/
│   ├── core/
│   │   ├── nicp_arbitrage_client.py  # Core arbitrage logic
│   │   └── database.py               # Data storage
│   └── bot/
│       └── telegram_bot.py           # Telegram interface
├── main.py                           # Main application
└── test_nicp_arbitrage.py           # Test suite
```

### Key Components

- **NICPArbitrageClient**: Fetches live data and calculates opportunities
- **TelegramBot**: User interface for monitoring and alerts
- **Database**: Stores historical data and user preferences

## 📈 Live Data Sources

- **KongSwap**: Primary DEX for nICP/ICP pairs
- **ICPSwap**: Secondary DEX monitoring
- **Direct staking rate**: 1 ICP = 0.9001103 nICP

## 🔮 Coming Soon

- **Price alerts** when discount opportunities exceed thresholds
- **Historical tracking** and analytics
- **More discount opportunities** across ICP ecosystem
- **Portfolio tracking** for active arbitrageurs
- **Multi-DEX comparison** and routing

## 🤝 Contributing

We welcome contributions! Areas of focus:

1. **Additional DEX integrations** (ICDex, Sonic, etc.)
2. **Enhanced risk analysis** and modeling
3. **UI/UX improvements** for Telegram bot
4. **Historical data analysis** and trends
5. **Automated opportunity alerts**

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This bot provides information for educational purposes only. nICP arbitrage involves financial risks including:

- 6-month lock-up periods
- ICP price volatility
- Smart contract risks
- Liquidity risks

Always do your own research and never invest more than you can afford to lose or lock up for 6 months.

---

**Ready to explore nICP discount opportunities? Start the bot and use `/discount` to see live data!** 🚀 