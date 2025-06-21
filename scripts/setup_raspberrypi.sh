#!/bin/bash

# ICP Token Monitor - Raspberry Pi Setup Script
# This script sets up the ICP monitoring bot on a Raspberry Pi

set -e

echo "🚀 Setting up ICP Token Monitor on Raspberry Pi..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [[ ! -f /proc/device-tree/model ]] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
        print_warning "This doesn't appear to be a Raspberry Pi, but continuing anyway..."
    else
        print_success "Raspberry Pi detected!"
    fi
}

# Update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System updated!"
}

# Install Python and dependencies
install_python() {
    print_status "Installing Python and pip..."
    sudo apt install -y python3 python3-pip python3-venv python3-dev
    
    # Install system dependencies
    sudo apt install -y build-essential libssl-dev libffi-dev
    
    print_success "Python installed!"
}

# Install Git if not present
install_git() {
    if ! command -v git &> /dev/null; then
        print_status "Installing Git..."
        sudo apt install -y git
        print_success "Git installed!"
    else
        print_success "Git already installed!"
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created!"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Make sure we're in virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    print_success "Dependencies installed!"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data
    mkdir -p logs
    
    print_success "Directories created!"
}

# Setup configuration
setup_config() {
    print_status "Setting up configuration..."
    
    if [[ ! -f config/config.env ]]; then
        cp config/config.env.example config/config.env
        print_warning "Configuration file created from template."
        print_warning "Please edit config/config.env with your Telegram bot token and other settings."
    else
        print_success "Configuration file already exists!"
    fi
}

# Create systemd service for auto-start
create_service() {
    print_status "Creating systemd service..."
    
    # Get current directory
    CURRENT_DIR=$(pwd)
    USER=$(whoami)
    
    # Create service file
    sudo tee /etc/systemd/system/icp-monitor.service > /dev/null <<EOF
[Unit]
Description=ICP Token Monitor Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload
    
    print_success "Systemd service created!"
    print_status "To enable auto-start: sudo systemctl enable icp-monitor"
    print_status "To start service: sudo systemctl start icp-monitor"
    print_status "To check status: sudo systemctl status icp-monitor"
}

# Install optional monitoring tools
install_monitoring() {
    print_status "Installing monitoring tools..."
    
    # Install htop for system monitoring
    sudo apt install -y htop
    
    # Install tree for directory structure viewing
    sudo apt install -y tree
    
    print_success "Monitoring tools installed!"
}

# Setup log rotation
setup_logrotate() {
    print_status "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/icp-monitor > /dev/null <<EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

    print_success "Log rotation configured!"
}

# Main setup function
main() {
    echo "========================================"
    echo "🚀 ICP Token Monitor Setup"
    echo "========================================"
    
    check_raspberry_pi
    update_system
    install_python
    install_git
    setup_venv
    install_dependencies
    create_directories
    setup_config
    create_service
    install_monitoring
    setup_logrotate
    
    echo "========================================"
    echo "✅ Setup Complete!"
    echo "========================================"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit config/config.env with your Telegram bot token"
    echo "2. Get your bot token from @BotFather on Telegram"
    echo "3. Run: python main.py (for testing)"
    echo "4. Or enable service: sudo systemctl enable icp-monitor"
    echo ""
    echo "📖 Useful Commands:"
    echo "• Test bot: python main.py"
    echo "• Check logs: tail -f logs/icp_monitor.log"
    echo "• Service status: sudo systemctl status icp-monitor"
    echo "• View processes: htop"
    echo ""
    echo "🎯 Configuration file: config/config.env"
    echo "📊 Database location: data/icp_monitor.db"
    echo "📝 Logs location: logs/icp_monitor.log"
    echo ""
    print_success "Happy monitoring! 🚀"
}

# Run main function
main 