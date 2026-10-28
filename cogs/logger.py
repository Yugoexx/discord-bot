import discord
from discord.ext import commands
import json
import os

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self, guild, category):
        if not os.path.exists("settings.json"):
            return None
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            
        channel_id = settings.get("log_channels", {}).get(category)
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    # --- BAN & KICK LOGS ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = self.get_log_channel(guild, "moderation")
        if channel:
            embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.red())
            embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        channel = self.get_log_channel(guild, "moderation")
        if channel:
            embed = discord.Embed(title="🔓 Member Unbanned", color=discord.Color.green())
            embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Kick kontrolü audit log üzerinden yapılabilir, burada genel ayrılış/kick takibi için temel atıyoruz
        pass

    # --- MESSAGE LOGS (Delete / Edit) ---
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return
        channel = self.get_log_channel(message.guild, "message")
        if channel:
            embed = discord.Embed(title="🗑️ Message Deleted", color=discord.Color.orange())
            embed.add_field(name="Author", value=f"{message.author} (`{message.author.id}`)", inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)
            embed.add_field(name="Content", value=message.content or "No content (Embed or Image)", inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        channel = self.get_log_channel(before.guild, "message")
        if channel:
            embed = discord.Embed(title="✏️ Message Edited", color=discord.Color.blue())
            embed.add_field(name="Author", value=f"{before.author} (`{before.author.id}`)", inline=False)
            embed.add_field(name="Before", value=before.content or "Empty", inline=False)
            embed.add_field(name="After", value=after.content or "Empty", inline=False)
            await channel.send(embed=embed)

    # --- SERVER / CHANNEL LOGS ---
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_ch = self.get_log_channel(channel.guild, "server")
        if log_ch:
            embed = discord.Embed(title="📁 Channel Created", description=f"Channel: {channel.mention} (`{channel.name}`)", color=discord.Color.green())
            await log_ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_ch = self.get_log_channel(channel.guild, "server")
        if log_ch:
            embed = discord.Embed(title="🗑️ Channel Deleted", description=f"Channel Name: `{channel.name}`", color=discord.Color.red())
            await log_ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        log_ch = self.get_log_channel(before.guild, "server")
        if log_ch and before.name != after.name:
            embed = discord.Embed(title="✏️ Channel Updated", description=f"Before: `{before.name}` -> After: `{after.name}`", color=discord.Color.gold())
            await log_ch.send(embed=log_ch)

    # --- VOICE LOGS (Mute, Deaf, Move, Connect, Disconnect) ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        channel = self.get_log_channel(member.guild, "voice")
        if not channel:
            return

        embed = None
        # Kanal Değiştirme / Giriş / Çıkış
        if before.channel != after.channel:
            if before.channel is None:
                embed = discord.Embed(title="🎤 Voice Channel Joined", description=f"**{member}** joined `{after.channel.name}`", color=discord.Color.green())
            elif after.channel is None:
                embed = discord.Embed(title="disconnected", description=f"**{member}** left `{before.channel.name}`", color=discord.Color.red())
            else:
                embed = discord.Embed(title="🔀 Voice Channel Moved", description=f"**{member}** moved from `{before.channel.name}` to `{after.channel.name}`", color=discord.Color.blue())

        # Susturma / Sağırlaştırma (Mute / Deaf)
        elif before.self_mute != after.self_mute or before.mute != after.mute:
            status = "Muted" if (after.self_mute or after.mute) else "Unmuted"
            embed = discord.Embed(title=f"🔇 Voice Status: {status}", description=f"**{member}** is now {status.lower()}", color=discord.Color.orange())
        elif before.self_deaf != after.self_deaf or before.deaf != after.deaf:
            status = "Deafened" if (after.self_deaf or after.deaf) else "Undeafened"
            embed = discord.Embed(title=f"🎧 Voice Status: {status}", description=f"**{member}** is now {status.lower()}", color=discord.Color.orange())

        if embed:
            await channel.send(embed=embed)

async def setup(bot):
    await Logger(bot) # İsteğe bağlı yükleme yöntemi
    # Normalde: await bot.add_cog(Logger(bot))