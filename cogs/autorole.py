import discord
from discord.ext import commands

from ayarlar import get_settings


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_id = get_settings().get("autorole_id")

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