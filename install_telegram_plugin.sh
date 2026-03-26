#!/bin/bash
set -e

INSTALL_DIR="/a0/usr/telegram"
mkdir -p "$INSTALL_DIR"

echo "🚀 Installing Advanced Telegram Plugin v2.1 (with pinned dependencies)..."

# Copy all files
cp telegram_bridge.py "$INSTALL_DIR/"
cp api_client.py "$INSTALL_DIR/"
cp telegram_extension.py "$INSTALL_DIR/"
cp supervisord.conf "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/telegram_bridge.py"

# === DEPENDENCY INSTALLATION (this is the version control part) ===
echo "📦 Installing pinned Python libraries..."
python3 -m pip install -r "$INSTALL_DIR/requirements.txt" --quiet --upgrade --no-cache-dir --no-deps

# Update secrets.env if missing
if ! grep -q "TELEGRAM_BOT_TOKEN" /a0/usr/secrets.env 2>/dev/null; then
    cat >> /a0/usr/secrets.env << EOF
TELEGRAM_BOT_TOKEN=your_bot_token_here
AGENT_ZERO_API_KEY=your_api_key_from_Settings_External_Services
AGENT_ZERO_URL=http://localhost:8000
TELEGRAM_OWNER_CHAT_ID=123456789
TELEGRAM_ALLOWED_CHAT_IDS=[123456789]
POLL_INTERVAL=1.5
EOF
    echo "⚠️  Edit /a0/usr/secrets.env with your real values then re-run this script."
    exit 1
fi

# Supervisor setup
if [ -d "/etc/supervisor/conf.d" ]; then
    cp "$INSTALL_DIR/supervisord.conf" /etc/supervisor/conf.d/telegram_bridge.conf
    supervisorctl reread && supervisorctl update
    supervisorctl restart telegram_bridge || true
else
    nohup python3 -u "$INSTALL_DIR/telegram_bridge.py" > "$INSTALL_DIR/bridge.log" 2>&1 &
fi

echo "✅ Advanced Telegram Plugin v2.1 installed successfully!"
echo "   • Dependencies pinned and installed from requirements.txt"
echo "   • Live progressive updates enabled"
echo "   • Logs: $INSTALL_DIR/bridge.log"
echo "   Test with /start in Telegram"