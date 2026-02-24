#!/bin/bash

# UAE Expat Finance Bot - Deployment Script
# This script helps set up and deploy the bot

echo "🇦🇪 UAE Expat Finance Bot - Deployment Setup"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements_finance.txt

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p user_profiles
mkdir -p logs

# Check for .env file
echo ""
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from template..."
    cp .env.example.finance .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your tokens!"
    echo "   1. Get Telegram bot token from @BotFather"
    echo "   2. Get Anthropic API key from console.anthropic.com"
    echo ""
    read -p "Press Enter when you've updated .env file..."
fi

# Verify credentials
echo ""
echo "🔍 Verifying configuration..."
source .env

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set properly"
    echo "   Edit .env file and set your Telegram bot token"
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ ANTHROPIC_API_KEY not set properly"
    echo "   Edit .env file and set your Anthropic API key"
    exit 1
fi

echo "✅ Configuration verified"

# Create systemd service file (optional)
echo ""
read -p "📋 Create systemd service for auto-start? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/uae-finance-bot.service"
    
    echo "Creating service file..."
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=UAE Expat Finance Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN"
Environment="ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
ExecStart=$(pwd)/venv/bin/python $(pwd)/uae_expat_finance_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Service file created"
    echo "Run these commands to enable:"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable uae-finance-bot"
    echo "  sudo systemctl start uae-finance-bot"
fi

# Final instructions
echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "To start the bot manually:"
echo "  source venv/bin/activate"
echo "  python uae_expat_finance_bot.py"
echo ""
echo "To run in background:"
echo "  nohup python uae_expat_finance_bot.py &"
echo ""
echo "To check if bot is running:"
echo "  ps aux | grep uae_expat_finance_bot"
echo ""
echo "Log files will be in: logs/"
echo "User data stored in: user_profiles/"
echo ""
echo "🎉 Happy budgeting!"
