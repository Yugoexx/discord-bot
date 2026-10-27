import os
import itertools
import discord
from discord import app_commands
from discord.ext import commands, tasks

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
import time
import re
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="w!", intents=intents)

STATUS_LIST = itertools.cycle([
    #discord.Game(name="w!yardım"),
    discord.Streaming(name="Canlı Yayında!", url="https://www.youtube.com/watch?v=Aq5WXmQQooo"),
    #discord.Activity(type=discord.ActivityType.watching, name="Evinizi, hehehehehe ;)!"),
    #discord.Activity(type=discord.ActivityType.listening, name="Seni!"),
])

@tasks.loop(seconds=15)
async def change_status():
    current_activity = next(STATUS_LIST)

    await bot.change_presence(
        status=discord.Status.idle,
        activity=current_activity
    )

@bot.event
async def on_ready():
    print(f"{bot.user.name}, Hii, i'm Wentyy! (ID: {bot.user.id})")
    print("--------------------------------------------------------")
    
    # Arka plan döngüsünü başlatıyoruz!
    if not change_status.is_running():
        change_status.start()

if __name__ == "__main__":
    bot.run(TOKEN)
