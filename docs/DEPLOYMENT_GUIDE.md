# 🚀 ICP Token Monitor - Raspberry Pi Deployment Guide

## 📋 Pre-Deployment Checklist

### Hardware Requirements
- ✅ Raspberry Pi 3B+ or newer
- ✅ 16GB+ MicroSD card (Class 10 recommended)
- ✅ Stable internet connection
- ✅ Power supply (5V 3A recommended)

### Software Requirements
- ✅ Raspberry Pi OS (Bullseye or newer)
- ✅ SSH access enabled (optional but recommended)

## 🛠️ Step-by-Step Deployment

### 1. Prepare Your Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl vim htop
```

### 2. Create Telegram Bot

1. **Message @BotFather** on Telegram
2. **Create new bot**: `/newbot`
3. **Choose bot name**: `YourICP Monitor Bot`
4. **Choose username**: `your_icp_monitor_bot`
5. **Save the token**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 3. Deploy the Bot

```bash
# Clone the repository
git clone <your-repo-url>
cd ICP_tokens_bot

# Run automated setup
chmod +x setup_raspberrypi.sh
./setup_raspberrypi.sh
```

### 4. Configure the Bot

```bash
# Edit configuration
nano config.env

# Add your bot token
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@your_channel_username  # Optional
```

### 5. Test the Installation

```bash
# Run tests
python3 test_apis.py

# Expected output: 5/5 tests passed
```

### 6. Start the Bot

```bash
# Test run (Ctrl+C to stop)
python3 main.py

# Enable as service
sudo systemctl enable icp-monitor
sudo systemctl start icp-monitor
```

## 🔍 Monitoring & Maintenance

### Check Bot Status
```bash
# Service status
sudo systemctl status icp-monitor

# Live logs
tail -f logs/icp_monitor.log

# System resources
htop
```

### Common Commands
```bash
# Restart bot
sudo systemctl restart icp-monitor

# Stop bot
sudo systemctl stop icp-monitor

# View recent logs
journalctl -u icp-monitor -n 50

# Check disk space
df -h
```

## 📊 Performance Optimization

### Memory Usage
- **Expected RAM**: 50-100MB
- **Monitor with**: `free -h`
- **Optimize**: Increase swap if needed

### Storage Management
```bash
# Check database size
ls -lh data/icp_monitor.db

# Check log size
ls -lh logs/

# Manual cleanup (if needed)
sudo journalctl --vacuum-time=7d
```

### Network Optimization
```bash
# Check network status
ping -c 4 8.8.8.8

# Test API connectivity
curl -s "https://uvevg-iyaaa-aaaak-ac27q-cai.raw.ic0.app/tickers" | head -5
```

## 🔧 Troubleshooting

### Bot Not Starting
```bash
# Check configuration
cat config.env

# Check Python environment
python3 --version
pip3 list | grep telegram

# Check permissions
ls -la main.py
```

### API Connection Issues
```bash
# Test internet
ping -c 4 google.com

# Test ICPSwap API
python3 test_apis.py

# Check firewall
sudo ufw status
```

### Database Issues
```bash
# Check database
sqlite3 data/icp_monitor.db ".tables"

# Check database permissions
ls -la data/

# Backup database
cp data/icp_monitor.db data/backup_$(date +%Y%m%d).db
```

### Memory Issues
```bash
# Check memory usage
free -h

# Check swap
swapon --show

# Add swap if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 🔐 Security Best Practices

### System Security
```bash
# Update regularly
sudo apt update && sudo apt upgrade

# Enable firewall
sudo ufw enable
sudo ufw allow ssh

# Create non-root user (if not already)
sudo adduser icpbot
sudo usermod -aG sudo icpbot
```

### Bot Security
- ✅ Keep bot token secret
- ✅ Use environment variables
- ✅ Monitor logs for suspicious activity
- ✅ Regular backups

### Network Security
```bash
# Change default SSH port (optional)
sudo nano /etc/ssh/sshd_config
# Port 2222

# Disable password auth (use keys)
# PasswordAuthentication no
```

## 📈 Scaling & Growth

### Adding Features
1. **Fork the repository**
2. **Create feature branch**
3. **Test on development Pi**
4. **Deploy to production**

### Multiple Bots
```bash
# Clone for second bot
cp -r ICP_tokens_bot ICP_tokens_bot_2
cd ICP_tokens_bot_2

# Edit config with different token
nano config.env

# Create separate service
sudo cp /etc/systemd/system/icp-monitor.service /etc/systemd/system/icp-monitor-2.service
sudo nano /etc/systemd/system/icp-monitor-2.service
```

### Database Scaling
```bash
# Monitor database growth
watch -n 60 'ls -lh data/icp_monitor.db'

# Set up automated backups
crontab -e
# 0 2 * * * cp /home/pi/ICP_tokens_bot/data/icp_monitor.db /home/pi/backups/icp_$(date +\%Y\%m\%d).db
```

## 📱 Mobile Access

### SSH Access
```bash
# Install SSH client on phone
# Termux (Android) or iSH (iOS)

# Connect to Pi
ssh pi@your-pi-ip-address

# Check bot status
sudo systemctl status icp-monitor
```

### Web Dashboard (Future Feature)
- Monitor via web interface
- Mobile-responsive design
- Real-time statistics

## 🆘 Emergency Procedures

### Bot Crashed
```bash
# Quick restart
sudo systemctl restart icp-monitor

# Check what happened
journalctl -u icp-monitor -n 100

# Emergency stop
sudo systemctl stop icp-monitor
```

### SD Card Corruption
```bash
# Check filesystem
sudo fsck /dev/mmcblk0p2

# Create backup image (from another computer)
dd if=/dev/sdX of=pi-backup.img bs=4M

# Regular backups prevent this
```

### Network Issues
```bash
# Restart networking
sudo systemctl restart networking

# Check WiFi
iwconfig

# Reconnect WiFi
sudo wpa_cli reconfigure
```

## 📞 Support & Community

### Getting Help
- 📖 **Documentation**: Check README.md
- 🐛 **Issues**: GitHub Issues
- 💬 **Community**: Telegram group
- 📧 **Direct**: support@yourproject.com

### Contributing
1. **Report bugs** with logs
2. **Suggest features** with use cases
3. **Submit PRs** with tests
4. **Help others** in community

## 🎯 Success Metrics

### Bot Health
- ✅ 99%+ uptime
- ✅ <100MB RAM usage
- ✅ <1 second response time
- ✅ Zero data loss

### Community Growth
- 📈 User acquisition rate
- 📊 Alert engagement
- 🔄 Referral conversion
- ⭐ User satisfaction

---

## 🎉 Congratulations!

Your ICP Token Monitor is now running on Raspberry Pi! 

**What's Next?**
1. **Share your bot** with the ICP community
2. **Monitor performance** and optimize
3. **Add features** based on user feedback
4. **Scale up** as your community grows

**Happy Monitoring! 🚀**

*Built with ❤️ for the ICP community* 