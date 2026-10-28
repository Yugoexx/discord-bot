import discord
from discord.ext import commands
import json
import os
import asyncio

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

    # --- BAN & UNBAN LOGS ---
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = self.get_log_channel(guild, "moderation")
        if not channel:
            return
        
        await asyncio.sleep(1)
        executor = "Unknown"
        reason = "No reason provided"
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    executor = entry.user
                    if entry.reason:
                        reason = entry.reason
                    break
        except Exception:
            pass

        embed = discord.Embed(title="🔨 Member Banned", color=discord.Color.red())
        embed.add_field(name="Banned User", value=f"{user} (`{user.id}`)", inline=False)
        embed.add_field(name="Moderator", value=f"{executor}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        channel = self.get_log_channel(guild, "moderation")
        if not channel:
            return

        await asyncio.sleep(1)
        executor = "Unknown"
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    executor = entry.user
                    break
        except Exception:
            pass

        embed = discord.Embed(title="🔓 Member Unbanned", color=discord.Color.green())
        embed.add_field(name="Unbanned User", value=f"{user} (`{user.id}`)", inline=False)
        embed.add_field(name="Moderator", value=f"{executor}", inline=False)
        await channel.send(embed=embed)

    # --- KICK & TIMEOUT (MUTE/UNMUTE) LOGS ---
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild
        channel = self.get_log_channel(guild, "moderation")
        if not channel:
            return

        await asyncio.sleep(1)
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    embed = discord.Embed(title="👢 Member Kicked", color=discord.Color.orange())
                    embed.add_field(name="Kicked User", value=f"{member} (`{member.id}`)", inline=False)
                    embed.add_field(name="Moderator", value=f"{entry.user}", inline=False)
                    embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)
                    await channel.send(embed=embed)
                    break
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild = after.guild
        channel = self.get_log_channel(guild, "moderation")
        if not channel:
            return

        # Check for Timeout (Mute / Unmute) using is_timed_out()
        if before.is_timed_out() != after.is_timed_out():
            await asyncio.sleep(1)
            executor = "Unknown"
            reason = "No reason provided"
            try:
                async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id:
                        executor = entry.user
                        if entry.reason:
                            reason = entry.reason
                        break
            except Exception:
                pass

            if after.is_timed_out():
                embed = discord.Embed(title="🔇 Member Timed Out (Muted)", color=discord.Color.orange())
                embed.add_field(name="User", value=f"{after} (`{after.id}`)", inline=False)
                embed.add_field(name="Moderator", value=f"{executor}", inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(title="🔊 Timeout Removed (Unmuted)", color=discord.Color.green())
                embed.add_field(name="User", value=f"{after} (`{after.id}`)", inline=False)
                embed.add_field(name="Moderator", value=f"{executor}", inline=False)
                await channel.send(embed=embed)

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
        guild = channel.guild
        log_ch = self.get_log_channel(guild, "server")
        if not log_ch:
            return

        await asyncio.sleep(1)
        executor = "Unknown"
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    executor = entry.user
                    break
        except Exception:
            pass

        embed = discord.Embed(title="📁 Channel Created", color=discord.Color.green())
        embed.add_field(name="Channel", value=f"{channel.mention} (`{channel.name}`)", inline=False)
        embed.add_field(name="Created By", value=f"{executor}", inline=False)
        await log_ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild
        log_ch = self.get_log_channel(guild, "server")
        if not log_ch:
            return

        await asyncio.sleep(1)
        executor = "Unknown"
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.target.name == channel.name:
                    executor = entry.user
                    break
        except Exception:
            pass

        embed = discord.Embed(title="🗑️ Channel Deleted", color=discord.Color.red())
        embed.add_field(name="Channel Name", value=f"`{channel.name}`", inline=False)
        embed.add_field(name="Deleted By", value=f"{executor}", inline=False)
        await log_ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        guild = before.guild
        log_ch = self.get_log_channel(guild, "server")
        if not log_ch or before.name == after.name:
            return

        await asyncio.sleep(1)
        executor = "Unknown"
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                if entry.target.id == after.id:
                    executor = entry.user
                    break
        except Exception:
            pass

        embed = discord.Embed(title="✏️ Channel Updated", color=discord.Color.gold())
        embed.add_field(name="Channel", value=f"{after.mention}", inline=False)
        embed.add_field(name="Change", value=f"`{before.name}` ➡️ `{after.name}`", inline=False)
        embed.add_field(name="Updated By", value=f"{executor}", inline=False)
        await log_ch.send(embed=embed)

    # --- VOICE LOGS ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        channel = self.get_log_channel(member.guild, "voice")
        if not channel:
            return

        embed = None
        guild = member.guild

        if before.channel != after.channel:
            if before.channel is None:
                embed = discord.Embed(title="🎤 Voice Channel Joined", description=f"**{member}** joined `{after.channel.name}`", color=discord.Color.green())
            elif after.channel is None:
                embed = discord.Embed(title="🔌 Voice Channel Left", description=f"**{member}** left `{before.channel.name}`", color=discord.Color.red())
            else:
                embed = discord.Embed(title="🔀 Voice Channel Moved", description=f"**{member}** moved from `{before.channel.name}` to `{after.channel.name}`", color=discord.Color.blue())

        elif before.mute != after.mute or before.deaf != after.deaf:
            await asyncio.sleep(1)
            executor = "Unknown"
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if entry.target.id == member.id:
                        executor = entry.user
                        break
            except Exception:
                pass

            if before.mute != after.mute:
                status = "Server Muted" if after.mute else "Server Unmuted"
                embed = discord.Embed(title=f"🔇 {status}", color=discord.Color.orange())
                embed.add_field(name="User", value=f"{member}", inline=False)
                embed.add_field(name="Moderator", value=f"{executor}", inline=False)
            elif before.deaf != after.deaf:
                status = "Server Deafened" if after.deaf else "Server Undeafened"
                embed = discord.Embed(title=f"🎧 {status}", color=discord.Color.orange())
                embed.add_field(name="User", value=f"{member}", inline=False)
                embed.add_field(name="Moderator", value=f"{executor}", inline=False)

        elif before.self_mute != after.self_mute:
            status = "Muted" if after.self_mute else "Unmuted"
            embed = discord.Embed(title=f"🔇 Microphone Status: {status}", description=f"**{member}**", color=discord.Color.dark_grey())
        elif before.self_deaf != after.self_deaf:
            status = "Deafened" if after.self_deaf else "Undeafened"
            embed = discord.Embed(title=f"🎧 Headphone Status: {status}", description=f"**{member}**", color=discord.Color.dark_grey())

        if embed:
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logger(bot))