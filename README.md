# 1. Telegram Bridge Commands (Handled Locally – Not Sent to Agent Zero)

| Command            | What it does                                         | Example / Notes                                |
|--------------------|------------------------------------------------------|------------------------------------------------|
| `/start`           | Confirms the bridge is alive + shows help            | Always works                                   |
| `/help`            | Shows this command list (you can add it to the bridge if you want) | —                                              |
| `/reset (context_id)` | Clears the current chat context                   | Use before switching projects or starting fresh |
| `/status`          | Shows bridge health and Agent Zero connection status | —                                              |
| `/project <name>`  | (Recommended addition) Resets context + activates the named project | `/project Finance` or `/project MyClient2026` |


# 2. Instructing Agent Zero (Natural Language – Sent to /api_message)

Once inside a chat (or after `/reset + /project`), you can communicate with Agent Zero using natural language. No rigid slash commands are required.

---

## Common effective patterns (copy-paste these):

| Goal                          | What to type in Telegram                                                                 |
|-------------------------------|-------------------------------------------------------------------------------------------|
| **Start fresh with clear goal** | From now on, act as my senior Python engineer. Project: Build a FastAPI backend...        |
| **Switch context / new task**   | New task: Analyze the sales CSV in /data/ and create a dashboard                         |
| **Use project tools**           | List all files in the current project directory                                          |
| **Ask for status / summary**    | Give me a full status report of everything you’re working on right now                   |
| **Memory / knowledge recall**   | Recall everything we discussed about the Q3 financial model                              |
| **Create sub-agents / tasks**   | Create a new subordinate agent called ‘DataCleaner’ that only handles CSV validation     |
| **Git operations (in Git projects)** | Checkout the feature-branch and show me the diff                                    |
| **Proactive notifications**     | When you finish the report, use the send_to.telegram tool to notify me                   |
| **Reset agent behavior**        | Forget all previous instructions and start fresh as a blank slate                        |

---

### 💡 Pro tip
After `/project MyProject`, immediately follow with:

> You are now operating inside the MyProject workspace. Follow the project instructions and use the project directory as your working dir.

The project’s custom instructions + file structure will be automatically injected by Agent Zero.


