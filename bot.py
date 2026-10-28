import os
import itertools
import discord
from discord.ext import commands, tasks
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all() # Tüm audit log ve üye verileri için all() önerilir

bot = commands.Bot(command_prefix="w!", intents=intents)

STATUS_LIST = itertools.cycle([
    discord.Streaming(name="Canlı Yayında!", url="https://www.youtube.com/watch?v=Aq5WXmQQooo"),
])

@tasks.loop(seconds=15)
async def change_status():
    current_activity = next(STATUS_LIST)
    await bot.change_presence(status=discord.Status.idle, activity=current_activity)

@bot.event
async def on_ready():
    # Cogs yüklemeleri
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.autorole")
    await bot.load_extension("cogs.logger")
    
    # Ses kanalına bağlanıp pasif durma (kulaklık ve mikrofon kapalı)
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            voice_ch_id = settings.get("voice_channel_id")
            if voice_ch_id:
                for guild in bot.guilds:
                    channel = guild.get_channel(voice_ch_id)
                    if channel and isinstance(channel, discord.VoiceChannel):
                        try:
                            # Kulaklık ve mikrofon kapalı şekilde bağlanma
                            await channel.connect(self_deaf=True, self_mute=True)
                        except Exception as e:
                            print(f"Ses kanalına bağlanılamadı: {e}")

    print(f"{bot.user.name}, Hii, i'm Wentyy! (ID: {bot.user.id})")
    print("--------------------------------------------------------")
    
    if not change_status.is_running():
        change_status.start()

if __name__ == "__main__":
    bot.run(TOKEN)