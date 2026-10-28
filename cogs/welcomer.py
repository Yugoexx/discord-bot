import discord
from discord.ext import commands
import json
import os

class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_welcome_channel(self, guild):
        if not os.path.exists("settings.json"):
            return None
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            
        channel_id = settings.get("welcome_channel_id")
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.get_welcome_channel(member.guild)
        if not channel:
            return

        embed = discord.Embed(
            title="👋 Welcome to the Server!",
            description=f"Hey {member.mention}, welcome to **{member.guild.name}**! We are glad to have you here. 🎉",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Member Count", value=f"We are now `{member.guild.member_count}` members!", inline=False)
        embed.set_footer(text=f"ID: {member.id}")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self.get_welcome_channel(member.guild)
        if not channel:
            return

        embed = discord.Embed(
            title="😢 Goodbye!",
            description=f"**{member}** has left the server. See you next time!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcomer(bot))