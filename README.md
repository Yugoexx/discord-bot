# Wenty Discord Bot 🤖

![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)

A modular Discord moderation and utility bot built with Python and discord.py. It covers server moderation, event logging, an interactive staff-managed registration flow, welcome messages and automatic roles.

---

## ✨ Features

- **Modular architecture:** features are split into cogs under `cogs/`, so new ones are easy to add.
- **Registration system (`/setup-register`):**
  - Staff-managed flow built with a slash command, buttons and a modal form.
  - Name and age input (age is validated, 13–99) with automatic nickname formatting (`Tag Name | Age`).
  - A per-staff registration counter stored in `stats.json`.
  - A welcome announcement in the general chat after a successful registration.
- **Event logging:** bans, kicks, timeouts, message edits and deletions, channel changes and voice activity are posted to separate log channels configured in `settings.json`. Long contents are truncated to fit Discord's embed limits.
- **Moderation commands:** `ban`, `unban`, `kick`, `timeout`, `untimeout` and `clear`, with role hierarchy checks. The executing moderator's name is recorded in the audit log reason.
- **Auto-role:** assigns a configured role to new members when they join.
- **Welcome and goodbye messages:** embed messages when members join or leave.
- **Passive voice presence:** joins a configured voice channel on startup, self-muted and self-deafened.
- **Custom status:** a streaming status set by a background task (`discord.ext.tasks`).
- **Cached settings:** `ayarlar.py` loads `settings.json` once and reloads it only when the file changes.

---

## 📋 Commands

### Prefix commands (`w!`)

| Command | Aliases | Usage | Description | Required permission |
| :--- | :--- | :--- | :--- | :--- |
| `ban` | - | `w!ban @user [reason]` | Bans a user | Ban Members |
| `unban` | - | `w!unban <user_id> [reason]` | Unbans a user by ID | Ban Members |
| `kick` | - | `w!kick @user [reason]` | Kicks a user | Kick Members |
| `timeout` | `mute` | `w!timeout @user [time] [reason]` | Times out a user. Default `15m`, maximum 28 days (units: `s`, `m`, `h`, `d`) | Moderate Members |
| `untimeout` | `unmute` | `w!untimeout @user` | Removes a timeout | Moderate Members |
| `clear` | `sil` | `w!clear <1-100>` | Deletes the given number of messages | Manage Messages |

### Slash commands (`/`)

| Command | Description | Required permission |
| :--- | :--- | :--- |
| `/setup-register` | Configures the registration channel, staff role, member roles, welcome channel and name tag | Administrator |

---

## 🚀 Setup

**1. Create the bot** in the [Discord Developer Portal](https://discord.com/developers/applications). Under **Bot**, enable the **Presence**, **Server Members** and **Message Content** privileged intents (the bot currently uses `Intents.all()`).

**2. Invite it** to your server with these permissions: Ban Members, Kick Members, Moderate Members, Manage Messages, Manage Roles, Manage Nicknames, View Audit Log, Send Messages, Embed Links and Connect. Place the bot's role above the roles it should manage.

**3. Install:**

```bash
git clone https://github.com/Yugoexx/discord-bot.git
cd discord-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Configure:**

```bash
cp .env.example .env                    # put your bot token in .env
cp settings.example.json settings.json  # fill in your channel and role IDs
```

**5. Run:**

```bash
python3 bot.py
```

Never commit `.env`. If a token ever leaks, reset it in the Developer Portal.

---

## 🔒 Privacy note

The bot logs the contents of deleted and edited messages and voice channel activity to the channels you configure, and the registration flow puts a name and an age in the member's nickname. If you run it on a server, tell your members what is logged, and avoid showing ages publicly if minors may be present.

---

## 📂 Project structure

```text
discord-bot/
├── cogs/
│   ├── moderation.py   # Moderation commands
│   ├── autorole.py     # Role assignment on join
│   ├── logger.py       # Event logging
│   ├── welcomer.py     # Welcome and goodbye messages
│   └── register.py     # Registration system (slash command, buttons, modal)
├── ayarlar.py              # Cached loader for settings.json
├── bot.py                  # Entry point
├── settings.example.json   # Template for settings.json (channel and role IDs)
├── .env.example            # Template for .env (bot token)
├── requirements.txt
└── README.md
```

`settings.json`, `stats.json` and `.env` are created locally and are git-ignored.

---

## ⚠️ Known limitations

- Registration buttons stop working after a restart for panels posted before it, because the views are not registered as persistent.
- Settings are global, not per server, so the bot is meant for a single server for now.
- There are no automated tests yet.

## 🗺️ Roadmap

- [ ] Persistent registration buttons that survive restarts
- [ ] Per-server settings
- [ ] Automated tests