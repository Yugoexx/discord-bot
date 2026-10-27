import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- BAN COMMAND ---
    @commands.command(name="ban", help="Bans a specified user from the server.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot ban yourself!")
            return
        
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot ban a member with an equal or higher role!")
            return

        await member.ban(reason=reason)
        await ctx.send(f"🔨 **{member}** has been banned. Reason: {reason or 'No reason provided'}")

    # --- KICK COMMAND ---
    @commands.command(name="kick", help="Kicks a specified user from the server.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot kick yourself!")
            return

        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ You cannot kick a member with an equal or higher role!")
            return

        await member.kick(reason=reason)
        await ctx.send(f"👢 **{member}** has been kicked. Reason: {reason or 'No reason provided'}")

    # --- MUTE (TIMEOUT) COMMAND ---
    @commands.command(name="mute", help="Times out a user. Usage: w!mute @user 10m [reason]")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration_str: str, *, reason: str = None):
        if member == ctx.author:
            await ctx.send("❌ You cannot mute yourself!")
            return

        unit = duration_str[-1].lower()
        try:
            value = int(duration_str[:-1])
        except ValueError:
            await ctx.send("❌ Invalid duration format! Example: `w!mute @user 10m` or `w!mute @user 1h`")
            return

        if unit == 's':
            seconds = value
        elif unit == 'm':
            seconds = value * 60
        elif unit == 'h':
            seconds = value * 3600
        elif unit == 'd':
            seconds = value * 86400
        else:
            await ctx.send("❌ Invalid time unit! Use `s` (seconds), `m` (minutes), `h` (hours), or `d` (days).")
            return

        duration = timedelta(seconds=seconds)
        await member.timeout(duration, reason=reason)
        await ctx.send(f"🔇 **{member}** has been timed out for {duration_str}. Reason: {reason or 'No reason provided'}")

    # --- UNMUTE COMMAND ---
    @commands.command(name="unmute", help="Removes timeout from a user.")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"🔊 **{member}**'s timeout has been removed.")

    # --- ERROR HANDLERS ---
    @ban.error
    @kick.error
    @mute.error
    @unmute.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing required argument! Please check the command usage.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Specified member was not found in this server.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))