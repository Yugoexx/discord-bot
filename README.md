# Wenty Discord Bot 🤖

A modular, advanced, and clean Discord bot built with Python using `discord.py`. Designed for seamless server management, automated tasks, and future expandability.

---

## ✨ Features

- **Dynamic Status Loop:** Automatically rotates through custom streaming, gaming, and activity statuses using `discord.ext.tasks`.
- **Secure Configuration:** Uses python-dotenv to keep sensitive credentials safe.
- **Modular Architecture:** Built with clean code practices, making it easy to add new features via Cogs under the `cogs/` directory.
- **Robust Intents:** Configured with specific intents (`message_content`, `members`, `voice_states`, `guild_messages`) for advanced server interaction.

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