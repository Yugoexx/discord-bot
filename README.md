# Wenty Discord Bot 🤖

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)

A modular, advanced, and clean Discord moderation and utility bot built with Python. Designed for seamless server management, comprehensive audit logging, automated tasks, and high expandability.

</div>

---

## ✨ Features

- **Modular Architecture:** Cleanly organized using `cogs/` for easy feature expansion and maintenance.
- **Comprehensive Audit Logging:** Tracks and logs everything from moderation actions (bans, kicks, timeouts) and message edits/deletions to server channel modifications and voice state activities into specific channels configured via `settings.json`.
- **Auto-Role System:** Instantly and automatically assigns designated roles to new members upon joining the server.
- **Passive Voice Presence:** Automatically connects to a configured voice channel on startup with automated self-deafen and self-mute states.
- **Dynamic Status Loop:** Automatically rotates through custom bot statuses using `discord.ext.tasks`.
- **Welcome & Goodbye System:** Sends custom interactive embed messages when members join or leave the server, configured via `settings.json`.
---

## 📋 Command Reference

Prefix: `w!`

| Command | Aliases | Usage | Description | Required Permission |
| :--- | :--- | :--- | :--- | :--- |
| `ban` | - | `w!ban @user [reason]` | Bans a specified user from the server | Ban Members |
| `unban` | - | `w!unban <user_id> [reason]` | Unbans a user using their Discord ID | Ban Members |
| `kick` | - | `w!kick @user [reason]` | Kicks a specified user from the server | Kick Members |
| `timeout` | `mute` | `w!timeout @user [time] [reason]` | Times out a user (blocks text/voice). Default: `15m` | Moderate Members |
| `untimeout` | `unmute` | `w!untimeout @user` | Removes active timeout from a user | Moderate Members |
| `clear` | `sil` | `w!clear <amount>` | Deletes a specified amount of messages | Manage Messages |

---

## 📂 Project Structure

```text
discord-bot/
│
├── cogs/
│   ├── moderation.py  # Core moderation commands (ban, kick, timeout, clear)
│   ├── autorole.py    # Automated member role assignment cog
│   └── logger.py      # Comprehensive audit & event logging cog
│   └── welcomer.py    # Welcome and goodbye greeting messages cog
│
├── bot.py             # Main entry point and event loop runner
├── settings.json      # Dynamic configuration & channel/role IDs
├── requirements.txt   # Project dependencies (discord.py, PyNaCl, davey, etc.)
├── .env               # Private environment variables (ignored by git)
├── .gitignore         # Git ignore configuration rules
└── README.md          # Project documentation
