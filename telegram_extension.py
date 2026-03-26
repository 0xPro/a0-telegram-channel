from python.helpers.extension import Extension
from python.helpers.tool import Tool
import os
from dotenv import load_dotenv
from telegram import Bot

load_dotenv("/a0/usr/secrets.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("TELEGRAM_OWNER_CHAT_ID", 0))

class SendToTelegram(Tool):
    async def run(self, message: str, chat_id: int = None):
        bot = Bot(token=TELEGRAM_TOKEN)
        target = chat_id or OWNER_CHAT_ID
        await bot.send_message(chat_id=target, text=message)
        return f"✅ Message sent to Telegram chat {target}"

class TelegramExtension(Extension):
    def __init__(self):
        super().__init__("telegram")

    async def on_agent_init(self):
        # Ensure bridge is running (Supervisor already handles it)
        print("🔌 Telegram extension initialized – bridge should be running via Supervisor")

    def get_tools(self):
        return [SendToTelegram]