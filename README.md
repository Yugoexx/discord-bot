# Wenty Discord Bot 🤖

A modular, advanced, and clean Discord bot built with Python using `discord.py`. Designed for seamless server management, automated tasks, and future expandability.

---

## ✨ Features

- **Dynamic Status Loop:** Automatically rotates through custom statuses using `discord.ext.tasks`.
- **Auto-Role System:** Automatically assigns specified roles to new members upon joining.
- **Passive Voice Presence:** Automatically connects to a designated voice channel on startup with muted microphone and deafened headphones.
- **Comprehensive Logging System:** Tracks and logs moderation actions (ban, unban), messages (delete, edit), server changes (channels), and voice state activities into specific channels via `settings.json`.
- **Modular Architecture:** Built with clean code practices using Cogs under the `cogs/` directory.

---

## 📋 Moderation Commands

Prefix: `w!`

| Command | Usage | Description | Required Permission |
| :--- | :--- | :--- | :--- |
| `ban` | `w!ban @user [reason]` | Bans a user from the server | Ban Members |
| `unban` | `w!unban <user_id> [reason]` | Unbans a user using their ID | Ban Members |
| `kick` | `w!kick @user [reason]` | Kicks a user from the server | Kick Members |
| `timeout` (`mute`) | `w!timeout @user <time> [reason]` | Times out a user (blocks text/voice). Default: `15m` | Moderate Members |
| `untimeout` (`unmute`) | `w!untimeout @user` | Removes timeout from a user | Moderate Members |
| `clear` (`sil`) | `w!clear <amount>` | Deletes a specified amount of messages | Manage Messages |

---
## 📂 Project Structure

```text
discord-bot/
│
├── cogs/
│   ├── moderation.py  # Moderation commands cog
│   ├── autorole.py    # Auto-role cog
│   └── logger.py      # Comprehensive log system cog
├── bot.py             # Main entry point of the bot
├── settings.json      # Configuration & Channel IDs
├── .env               # Environment variables (ignored by git)
├── .gitignore         # Git ignore rules
└── README.md          # Project documentation
## 🚀 Getting Started

Follow these steps to set up and run the bot locally on your machine.

### Prerequisites

- Python 3.8 or higher installed on your system.
- Git installed.

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Yugoexx/discord-bot.git](https://github.com/Yugoexx/discord-bot.git)
   cd discord-bot