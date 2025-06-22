#!/bin/bash

# nICP Discount Tracker Startup Script
echo "🚀 nICP Discount Tracker"
echo "=" * 40

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Create data directory if it doesn't exist
mkdir -p data

echo "🔧 Starting bot with automatic configuration loading..."
echo "📝 Logs will be written to: logs/nicp_arbitrage_bot.log"
echo "💾 Database will be stored in: data/icp_monitor.db"
echo ""

# Run the bot
$PYTHON_CMD main.py 