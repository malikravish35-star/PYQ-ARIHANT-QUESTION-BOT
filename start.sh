#!/bin/bash
# NEET Quiz Bot - Deploy Script
# MADE BY SPARTA 🫠

echo "🤖 NEET Quiz Bot Setup"
echo "━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Install Python 3.8+"
    exit 1
fi

echo "✅ Python3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "━━━━━━━━━━━━━━━━━━━━"
echo "🔑 Enter your Bot Token from @BotFather:"
read -r BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Token is empty!"
    exit 1
fi

export BOT_TOKEN="$BOT_TOKEN"

echo ""
echo "🚀 Starting bot..."
python3 bot.py
