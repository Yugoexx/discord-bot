import discord
from discord.ext import commands
import json
import os

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = self.load_settings()
        role_id = settings.get("autorole_id")
        
        if not role_id:
            return

        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role, reason="Automatic Role on Join")
            except discord.HTTPException:
                pass

async def setup(bot):
    await bot.add_cog(AutoRole(bot))