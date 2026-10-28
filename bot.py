import itertools
import json
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

EXTENSIONS = [
    "cogs.moderation",
    "cogs.autorole",
    "cogs.logger",
    "cogs.welcomer",
    "cogs.register",
]

STATUS_LIST = itertools.cycle([
    discord.Streaming(
        name="Canlı Yayında!",
        url="https://www.youtube.com/watch?v=Aq5WXmQQooo",
    ),
])


class WentyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="w!", intents=discord.Intents.all())
        self.ses_denendi = False

    async def setup_hook(self):
        # Bot bağlanmadan önce bir kez çalışır
        for ext in EXTENSIONS:
            await self.load_extension(ext)
        synced = await self.tree.sync()
        print(f"{len(synced)} slash komutu senkronize edildi.")

    async def on_ready(self):
        print(f"{self.user.name} hazır! (ID: {self.user.id})")
        print("--------------------------------------------------------")

        if not self.ses_denendi:
            self.ses_denendi = True
            await self.ses_kanalina_baglan()

        if not change_status.is_running():
            change_status.start()

    async def ses_kanalina_baglan(self):
        # Ses kanalına kulaklık ve mikrofon kapalı bağlanıp pasif bekler
        if not os.path.exists("settings.json"):
            return
        with open("settings.json", "r", encoding="utf-8") as f:
            ayarlar = json.load(f)

        kanal_id = ayarlar.get("voice_channel_id")
        if not kanal_id:
            return

        for guild in self.guilds:
            kanal = guild.get_channel(kanal_id)
            if isinstance(kanal, discord.VoiceChannel) and guild.voice_client is None:
                try:
                    await kanal.connect(self_deaf=True, self_mute=True)
                except Exception as e:
                    print(f"Ses kanalına bağlanılamadı: {e}")


bot = WentyBot()


@tasks.loop(seconds=15)
async def change_status():
    activity = next(STATUS_LIST)
    await bot.change_presence(status=discord.Status.idle, activity=activity)


if __name__ == "__main__":
    token = os.getenv("TOKEN")
    if not token:
        raise SystemExit("TOKEN bulunamadı. .env dosyasına TOKEN=... satırı ekle.")
    bot.run(token)