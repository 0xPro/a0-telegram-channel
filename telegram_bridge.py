#!/usr/bin/env python3
import asyncio
import json
import os
import base64
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from api_client import ApiClient, POLL_INTERVAL

load_dotenv("/a0/usr/secrets.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("TELEGRAM_OWNER_CHAT_ID", 0))
ALLOWED_CHAT_IDS = json.loads(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "[]"))

CONTEXTS_FILE = "/a0/usr/telegram/contexts.json"
LOG_FILE = "/a0/usr/telegram/bridge.log"

api = ApiClient()
contexts = {}

def load_contexts():
    if os.path.exists(CONTEXTS_FILE):
        with open(CONTEXTS_FILE) as f:
            return json.load(f)
    return {}

def save_contexts():
    with open(CONTEXTS_FILE + ".tmp", "w") as f:
        json.dump(contexts, f)
    os.replace(CONTEXTS_FILE + ".tmp", CONTEXTS_FILE)

contexts = load_contexts()

async def progressive_update(chat_id: int, context_id: str, message_obj):
    """Live-edits the Telegram message as Agent Zero generates."""
    last_content = ""
    while True:
        data = await api.api_log_get(context_id, length=100)
        if not data or not data.get("log"):
            await asyncio.sleep(1.5)
            continue

        log_items = data["log"].get("items", [])
        assistant_parts = [item["content"] for item in log_items if item.get("role") == "assistant"]
        current_content = "\n".join(assistant_parts).strip()

        if current_content and current_content != last_content:
            try:
                await message_obj.edit_text(current_content + " ⬇️ (still thinking...)")
                last_content = current_content
            except:
                pass  # message may be too new

        if data["log"].get("progress") == "complete":
            if last_content:
                try:
                    await message_obj.edit_text(last_content)
                except:
                    pass
            break
        await asyncio.sleep(POLL_INTERVAL)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
        return

    user_msg = update.message.text or "📎 Media received"
    attachment = None

    # Media handling
    if update.message.photo or update.message.document or update.message.voice:
        file_obj = await (update.message.photo[-1].get_file() if update.message.photo else
                          update.message.document.get_file() if update.message.document else
                          update.message.voice.get_file())
        file_bytes = await file_obj.download_as_bytearray()
        filename = file_obj.file_path.split("/")[-1] if hasattr(file_obj, "file_path") else "attachment"
        b64 = base64.b64encode(file_bytes).decode()
        attachment = [{"filename": filename, "base64": b64}]
        if update.message.voice:
            user_msg = "[Voice note] " + (update.message.caption or user_msg)

    # Send "Thinking..." placeholder
    thinking_msg = await update.message.reply_text("🤖 Thinking... (live updates coming)")

    try:
        # Get or create context
        ctx_id = contexts.get(str(chat_id))

        # Launch api_message as a task so progressive updates can run concurrently
        api_task = asyncio.create_task(api.api_message(user_msg, ctx_id, attachment))

        # Start live progressive updates if we already have a context
        prog_task = None
        if ctx_id:
            prog_task = asyncio.create_task(progressive_update(chat_id, ctx_id, thinking_msg))

        response, new_ctx = await api_task
        contexts[str(chat_id)] = new_ctx
        save_contexts()

        # Cancel progressive update if still running
        if prog_task and not prog_task.done():
            prog_task.cancel()
            try:
                await prog_task
            except asyncio.CancelledError:
                pass

        # Show final response
        final_text = response or "✅ Done (no text response)"
        try:
            await thinking_msg.edit_text(final_text)
        except Exception:
            pass  # May already show the same text from progressive update

    except Exception as e:
        await thinking_msg.edit_text(f"❌ Error: {str(e)}")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Advanced Telegram Bridge v2.1 is online!\nLive progressive updates enabled.\nCommands: /help")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """**Advanced Commands**
/start – Bridge status
/project <name> – Switch project
/list_projects – List all projects
/reset – Reset current context
/terminate – End current chat
/status – Health check

Just chat normally after switching project!"""
    await update.message.reply_text(help_text)

async def cmd_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_name = " ".join(context.args).strip()
    if not project_name:
        await update.message.reply_text("Usage: /project MyProjectName")
        return
    chat_id = str(update.effective_chat.id)
    contexts.pop(chat_id, None)
    save_contexts()
    await update.message.reply_text(f"🔄 Resetting context and activating project: **{project_name}**")
    # Trigger activation message
    _, new_ctx = await api.api_message(f"Activate project {project_name}", None, None, project_name)
    contexts[chat_id] = new_ctx
    save_contexts()
    await update.message.reply_text(f"✅ Now working inside project **{project_name}**")

async def cmd_list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thinking = await update.message.reply_text("📋 Asking Agent Zero for project list...")
    response, _ = await api.api_message("List all available projects in /a0/usr/projects/ with a short description of each.", None)
    await thinking.edit_text(f"**Available Projects:**\n\n{response}")

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    ctx = contexts.get(chat_id)
    if ctx:
        await api.api_reset_chat(ctx)
        contexts.pop(chat_id, None)
        save_contexts()
        await update.message.reply_text("🔄 Context reset successfully.")
    else:
        await update.message.reply_text("No active context to reset.")

async def cmd_terminate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    ctx = contexts.get(chat_id)
    if ctx:
        await api.api_terminate_chat(ctx)
        contexts.pop(chat_id, None)
        save_contexts()
        await update.message.reply_text("🗑️ Chat terminated and removed.")
    else:
        await update.message.reply_text("No active context.")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Bridge healthy | Live updates enabled | Connected to Agent Zero")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("project", cmd_project))
    app.add_handler(CommandHandler("list_projects", cmd_list_projects))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("terminate", cmd_terminate))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    print("Advanced Telegram Bridge v2.1 started with live updates...")
    app.run_polling()

if __name__ == "__main__":
    main()