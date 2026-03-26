# Advanced Telegram Plugin for Agent Zero (v2.1)

A Telegram bot bridge that connects [Agent Zero](https://github.com/frdel/agent-zero) to Telegram, providing live progressive updates and full project management through chat.

## Architecture

```
Telegram <-> telegram_bridge.py <-> Agent Zero API (localhost:8000)
                   |
            api_client.py        (HTTP client for Agent Zero endpoints)
            telegram_extension.py (Agent Zero extension - send_to_telegram tool)
```

| File                           | Purpose                                                         |
|--------------------------------|-----------------------------------------------------------------|
| `telegram_bridge.py`          | Main bot - handles commands, messages, media, and live updates  |
| `api_client.py`               | Async HTTP wrapper for the Agent Zero REST API                  |
| `telegram_extension.py`       | Agent Zero extension that exposes a `SendToTelegram` tool       |
| `install_telegram_plugin.sh`  | One-command installer (copies files, installs deps, starts bot) |
| `supervisord.conf`            | Keeps the bridge running and auto-restarts on crash             |
| `requirements.txt`            | Pinned Python dependencies                                     |

## Prerequisites

- A running [Agent Zero](https://github.com/frdel/agent-zero) instance (default `http://localhost:8000`)
- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- Your Telegram chat ID (use [@userinfobot](https://t.me/userinfobot) to find it)

## Installation

1. **Clone this repo** inside your Agent Zero environment:

   ```bash
   git clone https://github.com/0xPro/a0-telegram-channel.git
   cd a0-telegram-channel
   ```

2. **Run the installer:**

   ```bash
   bash install_telegram_plugin.sh
   ```

   On first run the script creates a template `/a0/usr/secrets.env` and exits.

3. **Edit `/a0/usr/secrets.env`** with your real values:

   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   AGENT_ZERO_API_KEY=your_api_key_from_Settings_External_Services
   AGENT_ZERO_URL=http://localhost:8000
   TELEGRAM_OWNER_CHAT_ID=123456789
   TELEGRAM_ALLOWED_CHAT_IDS=[123456789]
   POLL_INTERVAL=1.5
   ```

   All of the variables above are actively referenced by the Python code. Their purpose and usage points are:

   | Variable                     | What it is                                                                  | Referenced in code?                                                                 |
   |------------------------------|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
   | `TELEGRAM_BOT_TOKEN`         | Token from @BotFather                                                       | Yes — loaded in `telegram_bridge.py` and `telegram_extension.py` to authenticate the Telegram bot |
   | `AGENT_ZERO_API_KEY`         | API key from Agent Zero > Settings > External Services                      | Yes — loaded in `api_client.py` and sent as the `X-API-KEY` header on Agent Zero API requests |
   | `AGENT_ZERO_URL`             | Agent Zero base URL (default `http://localhost:8000`)                       | Yes — loaded in `api_client.py` and used to construct Agent Zero API endpoint URLs |
   | `TELEGRAM_OWNER_CHAT_ID`     | Your Telegram chat ID (used by the `SendToTelegram` tool)                   | Yes — loaded in `telegram_bridge.py` and `telegram_extension.py`; used as the fallback chat for outbound messages |
   | `TELEGRAM_ALLOWED_CHAT_IDS`  | JSON array of chat IDs allowed to use the bot (empty `[]` = allow everyone) | Yes — loaded in `telegram_bridge.py` and checked before handling incoming Telegram messages |
   | `POLL_INTERVAL`              | Seconds between progressive-update polls (default `1.5`)                    | Yes — loaded in `api_client.py`, imported into `telegram_bridge.py`, and used between progressive-update polls |

4. **Re-run the installer** to finish setup:

   ```bash
   bash install_telegram_plugin.sh
   ```

5. **Test** by sending `/start` to your bot in Telegram.

## Bot Commands

| Command              | What it does                                              |
|----------------------|-----------------------------------------------------------|
| `/start`             | Confirms the bridge is alive and shows help               |
| `/help`              | Lists all available commands                              |
| `/project <name>`    | Resets context and activates the named project            |
| `/list_projects`     | Asks Agent Zero to list projects in `/a0/usr/projects/`   |
| `/reset`             | Clears the current chat context                           |
| `/terminate`         | Ends the current chat and removes the context             |
| `/status`            | Shows bridge health and connection status                 |

## Talking to Agent Zero

After choosing a project (or just starting a chat), send natural-language messages. No rigid slash syntax is needed.

### Common patterns

| Goal                                | What to type in Telegram                                                              |
|-------------------------------------|---------------------------------------------------------------------------------------|
| **Start fresh with a clear goal**   | From now on, act as my senior Python engineer. Project: Build a FastAPI backend...    |
| **Switch context / new task**       | New task: Analyze the sales CSV in /data/ and create a dashboard                      |
| **Use project tools**               | List all files in the current project directory                                       |
| **Ask for status / summary**        | Give me a full status report of everything you're working on right now                |
| **Memory / knowledge recall**       | Recall everything we discussed about the Q3 financial model                           |
| **Create sub-agents / tasks**       | Create a new subordinate agent called 'DataCleaner' that only handles CSV validation  |
| **Git operations**                  | Checkout the feature-branch and show me the diff                                      |
| **Proactive notifications**         | When you finish the report, use the send_to_telegram tool to notify me                |
| **Reset agent behavior**            | Forget all previous instructions and start fresh as a blank slate                     |

### Pro tip

After `/project MyProject`, immediately follow with:

> You are now operating inside the MyProject workspace. Follow the project instructions and use the project directory as your working dir.

The project's custom instructions and file structure will be automatically injected by Agent Zero.

## Logs

Logs are written to `/a0/usr/telegram/bridge.log`. If Supervisor is available it manages log rotation automatically (see `supervisord.conf`).
